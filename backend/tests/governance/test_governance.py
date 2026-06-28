"""Tests for the Part 37 governance validators.

Positive tests assert the live repository conforms. Negative tests feed crafted
bad inputs to the pure diff/validate functions to prove each validator *detects*
drift (so the gate is real, not decorative).
"""
import json

import pytest

from tools.governance import (
    check_entities,
    check_openapi,
    check_shared_fields,
    check_traceability,
    run_all,
)
from tools.governance.db_drift import diff_schema
from tools.governance.entities import CatalogRow, parse_catalog, validate_catalog
from tools.governance.manifest import build_manifest, write_manifest
from tools.governance.openapi_drift import diff_operations
from tools.governance.shared_fields import missing_shared
from tools.governance.traceability import trace_errors


# --------------------------------------------------------------------------- #
# Positive: the live repository conforms (integration; includes migration round-trip)
# --------------------------------------------------------------------------- #
def test_run_all_passes_on_clean_repo():
    ok, checks = run_all()
    failures = {c.name: c.errors for c in checks if not c.ok}
    assert ok, f"governance failures: {failures}"


def test_individual_checks_pass():
    assert check_openapi().ok
    assert check_entities().ok
    assert check_shared_fields().ok
    assert check_traceability().ok


# --------------------------------------------------------------------------- #
# Negative: OpenAPI drift detected
# --------------------------------------------------------------------------- #
def test_openapi_detects_undocumented_and_stale():
    undocumented, stale = diff_operations({("GET", "/x")}, set())
    assert ("GET", "/x") in undocumented and not stale
    undocumented, stale = diff_operations(set(), {("GET", "/y")})
    assert ("GET", "/y") in stale and not undocumented
    assert diff_operations({("GET", "/z")}, {("GET", "/z")}) == (set(), set())


# --------------------------------------------------------------------------- #
# Negative: migration / schema drift detected
# --------------------------------------------------------------------------- #
def test_migration_drift_detected():
    assert diff_schema({"t": {"id", "a"}}, {"t": {"id", "a"}}) == []
    errs = diff_schema({"t": {"id", "a"}}, {"t": {"id"}})
    assert any("a: column in model but not migrated" in e for e in errs)
    errs = diff_schema({"t": {"id"}}, {"t": {"id"}, "x": {"id"}})
    assert any("'x' is in migrations but missing from models" in e for e in errs)


# --------------------------------------------------------------------------- #
# Negative + parser: entity catalog
# --------------------------------------------------------------------------- #
_CATALOG_MD = """## E. Complete Entity Catalog
| # | Entity | Tbl | Context | PK | rel | Delete | Status | Parts |
|---|--------|-----|---------|----|-----|--------|--------|-------|
| 1 | Foo | `foo` | X | uuid | a | soft | ✅ | 01 |
| 2 | Bar | `bar` | X | uuid | a | soft | ⬜ | 02 |
## F. Next
"""


def test_parse_catalog_reads_rows():
    rows = parse_catalog(_CATALOG_MD)
    assert {r.table for r in rows} == {"foo", "bar"}


def test_entity_validator_detects_problems():
    rows = parse_catalog(_CATALOG_MD)
    # clean: foo implemented & present, bar specified & absent
    assert validate_catalog(rows, {"foo"}) == []
    # orphan ORM table (not catalogued)
    assert any("orphan table" in e for e in validate_catalog(rows, {"foo", "baz"}))
    # implemented entity with no ORM table
    assert any("marked IMPLEMENTED" in e for e in validate_catalog(rows, set()))
    # duplicate + missing status + missing parts
    bad = [
        CatalogRow("foo", "uuid", "✅", "01", 0),
        CatalogRow("foo", "uuid", "", "—", 1),
    ]
    errs = validate_catalog(bad, {"foo"})
    assert any("duplicate" in e for e in errs)
    assert any("no/invalid status" in e for e in errs)
    assert any("no traceable Parts" in e for e in errs)


# --------------------------------------------------------------------------- #
# Negative: shared fields
# --------------------------------------------------------------------------- #
def test_shared_fields_detects_missing():
    full = {"id", "created_at", "updated_at", "version", "provenance_hash", "schema_version"}
    assert missing_shared({"organizations": full}) == {}
    miss = missing_shared({"foo": {"id", "created_at"}})
    assert "foo" in miss and "version" in miss["foo"]
    # append-only needs only id
    assert missing_shared({"rallies": {"id"}}) == {}
    assert missing_shared({"rallies": set()}) == {"rallies": ["id"]}


# --------------------------------------------------------------------------- #
# Negative: traceability
# --------------------------------------------------------------------------- #
def test_traceability_detects_broken_chain():
    rows = [CatalogRow("foo", "uuid", "✅", "01", 0)]
    errs, report = trace_errors(rows, {"foo"})
    assert errs == [] and "entity:foo" in report
    # orphan table (no catalog row)
    errs, _ = trace_errors(rows, {"bar"})
    assert any("no entity in the catalog" in e for e in errs)
    # table traces to no Part
    rows2 = [CatalogRow("foo", "uuid", "✅", "—", 0)]
    errs, _ = trace_errors(rows2, {"foo"})
    assert any("traces to no Part" in e for e in errs)


# --------------------------------------------------------------------------- #
# Manifest
# --------------------------------------------------------------------------- #
def test_manifest_has_required_fields(tmp_path):
    m = build_manifest()
    for key in ("specification", "capture_schema_version", "migration_revision",
                "openapi_checksum", "entity_checksum", "route_checksum",
                "build_timestamp", "git_commit", "repository_state"):
        assert key in m, key
    assert m["migration_revision"]  # a head revision was resolved

    out = tmp_path / "build_manifest.json"
    write_manifest(out)
    assert json.loads(out.read_text())["entity_checksum"] == m["entity_checksum"]
