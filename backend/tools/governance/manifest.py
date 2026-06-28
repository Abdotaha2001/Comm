"""Build-manifest generator (Part 37 §7 / §Y).

Produces the canonical build fingerprint: schema version, migration head,
OpenAPI checksum, entity checksum, route checksum, specification fingerprint,
build timestamp, git commit, and repository cleanliness.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    BACKEND_ROOT,
    CAPTURE_SCHEMA_PATH,
    OPENAPI_PATH,
    PART37_PATH,
    REPO_ROOT,
    operation_set,
    orm_metadata,
)


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _alembic_head() -> str | None:
    versions = BACKEND_ROOT / "migrations" / "versions"
    revisions, downs = set(), set()
    for f in versions.glob("*.py"):
        text = f.read_text(encoding="utf-8")
        rev = re.search(r'^revision\s*=\s*"([^"]+)"', text, re.M)
        down = re.search(r'^down_revision\s*=\s*"?([^"\n]+)"?', text, re.M)
        if rev:
            revisions.add(rev.group(1))
        if down and down.group(1) != "None":
            downs.add(down.group(1).strip().strip('"'))
    heads = revisions - downs
    return sorted(heads)[-1] if heads else None


def _git(args: list[str]) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def _entity_checksum() -> str:
    meta = orm_metadata()
    parts = []
    for table in sorted(meta.tables):
        cols = ",".join(sorted(meta.tables[table].columns.keys()))
        parts.append(f"{table}({cols})")
    return _sha256_text("|".join(parts))


def _route_checksum() -> str:
    from app.main import app

    ops = sorted(f"{m} {p}" for m, p in operation_set(app.openapi().get("paths", {})))
    return _sha256_text("|".join(ops))


def _capture_schema_version() -> str | None:
    if not CAPTURE_SCHEMA_PATH.exists():
        return None
    return json.loads(CAPTURE_SCHEMA_PATH.read_text(encoding="utf-8")).get("schema_version")


def build_manifest() -> dict[str, Any]:
    commit = _git(["rev-parse", "HEAD"])
    dirty = bool(_git(["status", "--porcelain"]))
    return {
        "specification": "PART-37",
        "specification_fingerprint": _sha256_file(PART37_PATH),
        "capture_schema_version": _capture_schema_version(),
        "migration_revision": _alembic_head(),
        "openapi_checksum": _sha256_file(OPENAPI_PATH),
        "entity_checksum": _entity_checksum(),
        "route_checksum": _route_checksum(),
        "build_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": commit or None,
        "repository_state": "dirty" if dirty else "clean",
    }


def write_manifest(path: Path) -> dict[str, Any]:
    manifest = build_manifest()
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
