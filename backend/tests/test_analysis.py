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
    mid = body["match_id"]
    assert mid

    match = client.get(f"/v1/matches/{mid}", headers=coach_headers).json()
    assert len(match["rallies"]) >= 1
    assert any(len(r["events"]) > 0 for r in match["rallies"])


def test_analyze_requires_coach(client, player_headers):
    # players can't upload/analyze (RBAC)
    r = client.post("/v1/videos/nope/analyze", headers=player_headers)
    assert r.status_code == 403
