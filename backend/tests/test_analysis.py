import os
import tempfile

from app.cv.pipeline import analyze_video
from app.cv.synth import write_synthetic_video


def _synth_to_bytes(n_frames=90):
    fd, path = tempfile.mkstemp(suffix=".avi")
    os.close(fd)
    try:
        write_synthetic_video(path, n_frames=n_frames, w=320, h=240, fps=30)
        with open(path, "rb") as f:
            return f.read()
    finally:
        os.remove(path)


def test_pipeline_detects_ball():
    fd, path = tempfile.mkstemp(suffix=".avi")
    os.close(fd)
    try:
        write_synthetic_video(path, n_frames=90)
        res = analyze_video(path)
        assert res["detection_rate"] > 0.8
        assert res["reliability_index"] > 0
        assert len(res["rallies"]) >= 1
        # bounce/serve events derived from real motion
        assert any(len(r["events"]) > 0 for r in res["rallies"])
    finally:
        os.remove(path)


def test_upload_analyze_get_match(client, coach_headers):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "P"}
    ).json()["id"]

    up = client.post(
        f"/v1/players/{pid}/videos",
        headers=coach_headers,
        files={"file": ("ball.avi", _synth_to_bytes(), "video/avi")},
    )
    assert up.status_code == 201, up.text
    vid = up.json()["id"]

    run = client.post(f"/v1/videos/{vid}/analyze", headers=coach_headers)
    assert run.status_code == 200, run.text
    body = run.json()
    assert body["status"] == "done", body
    assert body["reliability_index"] is not None
    # No capture report supplied -> capture certification is not asserted.
    assert body["capture_certification"] is None
    # Run carries an OOD / domain-shift signal (Part 40 §Y).
    assert body["input_quality"]["ood"]["signal"] == "detection_rate"
    assert "is_ood" in body["input_quality"]["ood"]
    mid = body["match_id"]
    assert mid

    match = client.get(f"/v1/matches/{mid}", headers=coach_headers).json()
    assert len(match["rallies"]) >= 1
    assert any(len(r["events"]) > 0 for r in match["rallies"])


def _platinum_capture_report() -> dict:
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


def test_analyze_with_capture_report_certifies(client, coach_headers):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "P"}
    ).json()["id"]
    vid = client.post(
        f"/v1/players/{pid}/videos",
        headers=coach_headers,
        files={"file": ("ball.avi", _synth_to_bytes(), "video/avi")},
    ).json()["id"]

    run = client.post(
        f"/v1/videos/{vid}/analyze",
        headers=coach_headers,
        json={
            "capture_measurements": _platinum_capture_report(),
            "capture_context": {"operator_id": "op-1", "camera_ids": ["A", "B", "C"],
                                "calibration_version": "cal-1", "capture_tier": "T3"},
        },
    )
    assert run.status_code == 200, run.text
    body = run.json()
    assert body["status"] == "done"
    # Operator-supplied measurements override the low-res synthetic footage.
    assert body["capture_certification"] == "platinum"
    acc = body["capture_acceptance"]
    assert acc["reliability_envelope"]["status"] == "verified"
    assert acc["reliability_envelope"]["provenance_hash"].startswith("sha256:")
    assert acc["failed_gates"] == []
    # Platinum capture (ceiling 1.0) does not down-weight analysis reliability.
    iq = body["input_quality"]
    assert iq["reliability_status"] == "verified"
    assert iq["reliability_capped_by_capture"] is False

    # The same fields are returned by GET /analysis-runs/{id}.
    got = client.get(f"/v1/analysis-runs/{body['id']}", headers=coach_headers).json()
    assert got["capture_certification"] == "platinum"


def test_failed_capture_caps_analysis_reliability(client, coach_headers):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "P"}
    ).json()["id"]
    vid = client.post(
        f"/v1/players/{pid}/videos",
        headers=coach_headers,
        files={"file": ("ball.avi", _synth_to_bytes(), "video/avi")},
    ).json()["id"]

    report = _platinum_capture_report()
    report["lux"] = 200  # below the critical floor -> Bronze-mandatory KPI fails -> certification fail
    run = client.post(
        f"/v1/videos/{vid}/analyze",
        headers=coach_headers,
        json={"capture_measurements": report},
    ).json()

    assert run["capture_certification"] == "fail"
    # A failed capture forces the analysis reliability down (cap 0.3) and to abstain,
    # even though the footage itself tracked the ball well.
    assert run["reliability_index"] <= 0.3
    assert run["input_quality"]["reliability_status"] == "abstain"


def test_outputs_carry_reliability_envelope(client, coach_headers):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "P"}
    ).json()["id"]
    vid = client.post(
        f"/v1/players/{pid}/videos",
        headers=coach_headers,
        files={"file": ("ball.avi", _synth_to_bytes(), "video/avi")},
    ).json()["id"]
    mid = client.post(f"/v1/videos/{vid}/analyze", headers=coach_headers).json()["match_id"]

    match = client.get(f"/v1/matches/{mid}", headers=coach_headers).json()
    rallies = match["rallies"]

    # Events are reliably produced and each carries a tier-capped reliability status.
    events = [e for r in rallies for e in r["events"]]
    assert events, "synthetic analysis should produce events"
    er = events[0]["provenance"]["reliability"]
    for k in ("confidence", "status", "tier", "calibrated"):
        assert k in er, er
    assert er["calibrated"] is False and er["tier"] == "t1" and er["confidence"] <= 0.6

    # Shots aren't guaranteed by every synthetic clip; when present they carry
    # keyed speed + spin envelopes (Part 40 §C/§K).
    for sh in (s for r in rallies for s in r["shots"]):
        rel = sh["reliability"]
        assert rel and "speed" in rel and "spin" in rel, rel
        sp = rel["speed"]
        assert sp["calibrated"] is False and sp["tier"] == "t1" and sp["confidence"] <= 0.6
        assert sp["status"] in ("preliminary", "abstain")


def _shot(*, snr_significant, speed=70.0, ci=8.0, conf=0.8, snr=5.0):
    return {
        "speed_kmh": speed, "speed_ci": ci, "confidence": conf,
        "provenance": {
            "speed_inputs_conf": [conf, conf],
            "speed_uncertainty": {"snr": snr, "significant": snr_significant},
        },
    }


def test_low_snr_speed_abstains_regardless_of_confidence():
    # High detection confidence but an insignificant displacement (SNR below the gate):
    # the speed envelope MUST abstain (Part 40 §BH) — value null, no fabricated number.
    from app.worker import _speed_envelope

    env = _speed_envelope(_shot(snr_significant=False, snr=1.2), "t1", "opencv")
    d = env.to_dict()
    assert d["status"] == "abstain" and d["value"] is None
    assert d["unit"] == "km/h" and d["calibrated"] is False
    assert d["source"]["snr"] == 1.2 and d["source"]["measure"] == "speed"


def test_significant_speed_composes_endpoints_by_min():
    # A significant measurement reports a value; the two correlated, both-required
    # endpoint detections compose by required_all (min), not an independence product.
    from app.worker import _speed_envelope

    env = _speed_envelope(_shot(snr_significant=True, conf=0.8), "t1", "opencv")
    d = env.to_dict()
    assert d["status"] in ("preliminary", "abstain")  # uncalibrated/tier-capped
    assert d["source"]["composition"] == "required_all"
    # T1 cap (0.6) and the uncalibrated cap (0.7) both bound the confidence.
    assert d["confidence"] <= 0.6


def test_analyze_requires_coach(client, player_headers):
    # players can't upload/analyze (RBAC)
    r = client.post("/v1/videos/nope/analyze", headers=player_headers)
    assert r.status_code == 403
