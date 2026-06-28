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

    # The same fields are returned by GET /analysis-runs/{id}.
    got = client.get(f"/v1/analysis-runs/{body['id']}", headers=coach_headers).json()
    assert got["capture_certification"] == "platinum"


def test_analyze_requires_coach(client, player_headers):
    # players can't upload/analyze (RBAC)
    r = client.post("/v1/videos/nope/analyze", headers=player_headers)
    assert r.status_code == 403
