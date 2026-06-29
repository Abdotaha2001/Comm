"""Tests for the Capture Acceptance Framework (Part 35).

These lock in the safety-critical contract: certification is governed by the
lowest required sub-score (mandatory-gate logic), never by an average — and the
committed CSV checklist stays in sync with the authoritative schema.
"""
import csv
from pathlib import Path

import pytest

from app import capture_quality as cq


@pytest.fixture(scope="module")
def schema():
    return cq.load_schema()


def _perfect_platinum() -> dict:
    return {
        "resolution": 2160, "frame_rate": 120, "shutter": 0.8, "motion_blur": 0.3,
        "exposure_lock": True, "white_balance_lock": True, "lens_calibration": True,
        "reprojection_error_px": 0.3, "reconstruction_error_mm": 4.0, "calibration_age": 2.0,
        "synchronization_error": 0.3, "time_synchronization": True,
        "frame_accurate_timestamps": True, "camera_drift": 0.4, "dropped_frames": 0.01,
        "lighting_uniformity": 0.9, "lux": 1300, "flicker": 1.0, "glare": True,
        "color_temperature": 100, "occlusion": 2.0, "ball_visibility": 98.0,
        "tracking_success": 98.0, "storage_health": 70.0, "battery": 90.0,
        "temperature": 40.0, "camera_stability": 0.4, "coverage_volume": 100.0,
        "overlap_pct": 65.0, "network_latency": 50.0, "packet_loss": 0.01, "jitter": 3.0,
        "secure_network_isolation": True, "metadata_completeness": 100.0,
        "provenance": True, "tamper_evidence": True, "ground_truth_status": True,
        "versioned_calibration": True, "global_shutter": True, "environmental_sensors": True,
    }


# --------------------------------------------------------------------------- #
# Schema integrity
# --------------------------------------------------------------------------- #
def test_schema_loads_and_is_consistent(schema):
    assert schema["schema_version"]
    assert len(schema["kpis"]) >= 35
    ids = {k["id"] for k in schema["kpis"]}
    # Required KPI families from the SOP are all present.
    for required in ("resolution", "frame_rate", "synchronization_error",
                     "reconstruction_error_mm", "global_shutter", "tamper_evidence",
                     "ground_truth_status", "ball_visibility", "lux", "provenance"):
        assert required in ids
    # Level ladder is monotonic (bronze ⊂ silver ⊂ gold ⊂ platinum).
    levels = schema["certification_levels"]
    for lower, higher in (("bronze", "silver"), ("silver", "gold"), ("gold", "platinum")):
        assert set(levels[lower]["mandatory_kpis"]).issubset(levels[higher]["mandatory_kpis"])


# --------------------------------------------------------------------------- #
# Certification gate logic
# --------------------------------------------------------------------------- #
def test_perfect_capture_is_platinum(schema):
    r = cq.compute_cqs(_perfect_platinum(), schema=schema)
    assert r.certification == "platinum"
    assert r.effective_score >= 0.95
    assert r.failed_gates == []
    assert r.reliability_envelope["status"] == "verified"
    assert r.reliability_envelope["confidence"] == r.effective_score


def test_single_failed_mandatory_gate_denies_certification_no_averaging(schema):
    """The decisive safety property: an average that would pass must NOT certify
    when a single mandatory gate fails."""
    m = _perfect_platinum()
    m["ground_truth_status"] = False  # one mandatory Platinum gate fails
    r = cq.compute_cqs(m, schema=schema)
    # The informational average is still >= the Platinum threshold ...
    assert r.overall_score >= 0.95
    # ... but certification is denied because the gate (min required) is 0.
    assert r.certification != "platinum"
    assert r.per_level["platinum"]["effective_score"] == 0.0
    assert any(g["kpi"] == "ground_truth_status" for g in r.failed_gates)


def test_effective_is_min_not_mean(schema):
    m = _perfect_platinum()
    m["lux"] = 820  # Gold band: >=800 warning, <1000 threshold -> amber -> subscore 0.7
    r = cq.compute_cqs(m, schema=schema)
    # An amber on a Gold-required KPI drops Gold's effective (the min) to 0.7
    # (< 0.85), so Gold is denied and the capture settles at Silver.
    assert r.certification == "silver"
    assert r.per_level["gold"]["effective_score"] == pytest.approx(0.7)
    # Averaging would have passed Gold: the mean of Gold's required subscores is
    # still well above its 0.85 threshold. The min gate is what denies it.
    gold_req = schema["certification_levels"]["gold"]["mandatory_kpis"]
    evs = [cq.evaluate_kpi(schema["_kpi_index"][k], m.get(k), schema, level="gold")
           for k in gold_req]
    mean_gold = sum(e["subscore"] for e in evs) / len(evs)
    assert mean_gold >= 0.95            # mean would certify Gold ...
    assert r.per_level["gold"]["effective_score"] < 0.85  # ... but the gate does not


def test_critical_floor_fails_and_abstains(schema):
    m = _perfect_platinum()
    m["lux"] = 200  # below the critical floor (300) -> critical on a Bronze-mandatory KPI
    r = cq.compute_cqs(m, schema=schema)
    assert r.certification == "fail"
    assert r.reliability_envelope["status"] == "abstain"
    assert r.overall_state == "critical"


def test_missing_mandatory_measurement_fails(schema):
    m = _perfect_platinum()
    del m["resolution"]  # a Bronze-mandatory KPI is unmeasured
    r = cq.compute_cqs(m, schema=schema)
    assert r.certification == "fail"
    assert any(g["kpi"] == "resolution" and g["reason"] == "measurement missing"
               for g in r.failed_gates)


# --------------------------------------------------------------------------- #
# Output contract
# --------------------------------------------------------------------------- #
def test_compute_cqs_returns_full_contract(schema):
    r = cq.compute_cqs(_perfect_platinum(), schema=schema).to_dict()
    for key in ("overall_score", "effective_score", "capture_tier", "certification",
                "subscores", "failed_gates", "warnings", "recommended_actions",
                "reliability_level", "provenance", "reliability_envelope"):
        assert key in r
    env = r["reliability_envelope"]
    for key in ("capture_tier", "certification", "confidence", "ground_truth_status",
                "calibration_version", "synchronization_status", "evidence_integrity",
                "input_quality", "timestamp", "provenance_hash", "operator_id",
                "camera_ids", "environmental_conditions", "software_version",
                "model_version"):
        assert key in env


def test_every_failed_gate_has_required_fields(schema):
    m = _perfect_platinum()
    m["lux"] = 200
    r = cq.compute_cqs(m, schema=schema)
    assert r.failed_gates
    for g in r.failed_gates:
        for key in ("reason", "threshold", "measured", "severity",
                    "corrective_action", "auto_retry_allowed"):
            assert key in g


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_provenance_hash_is_deterministic_and_tamper_evident(schema):
    m = _perfect_platinum()
    r1 = cq.compute_cqs(m, context=cq.EXAMPLE_CONTEXT, schema=schema,
                        now=cq.datetime(2026, 6, 28, tzinfo=cq.timezone.utc))
    r2 = cq.compute_cqs(m, context=cq.EXAMPLE_CONTEXT, schema=schema,
                        now=cq.datetime(2026, 6, 28, tzinfo=cq.timezone.utc))
    assert r1.provenance["hash"] == r2.provenance["hash"]
    m2 = dict(m)
    m2["lux"] = 1299  # any change to inputs changes the hash
    r3 = cq.compute_cqs(m2, context=cq.EXAMPLE_CONTEXT, schema=schema,
                        now=cq.datetime(2026, 6, 28, tzinfo=cq.timezone.utc))
    assert r3.provenance["hash"] != r1.provenance["hash"]


# --------------------------------------------------------------------------- #
# Doc <-> implementation consistency (Part 34.AP drift gate)
# --------------------------------------------------------------------------- #
def test_committed_checklist_matches_schema(schema):
    csv_path = cq._repo_root() / "MASTER_SPEC" / cq.CHECKLIST_FILENAME
    assert csv_path.exists(), "run: python -m app.capture_quality --generate"
    with open(csv_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0].keys()) == cq.CSV_COLUMNS
    csv_kpis = {row["KPI"] for row in rows}
    schema_kpis = {k["name"] for k in schema["kpis"]}
    assert csv_kpis == schema_kpis, "checklist CSV is stale — regenerate from the schema"


def test_committed_checklist_is_freshly_regenerable(schema, tmp_path: Path):
    fresh = tmp_path / cq.CHECKLIST_FILENAME
    cq.write_checklist_csv(fresh, schema)
    committed = (cq._repo_root() / "MASTER_SPEC" / cq.CHECKLIST_FILENAME).read_text(encoding="utf-8")
    assert fresh.read_text(encoding="utf-8") == committed, \
        "committed checklist differs from generated — run --generate and commit"
