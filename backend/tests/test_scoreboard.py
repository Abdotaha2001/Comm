import cv2
import numpy as np

from app.cv.scoreboard import read_scoreboard, render_scoreboard
from app.cv.sevenseg import decode_digit, render_digit
from app.cv.synth import write_synthetic_video


def test_sevenseg_all_digits():
    for d in range(10):
        img = np.zeros((40, 30, 3), dtype=np.uint8)
        render_digit(img, 5, 5, 18, 30, d)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        got, conf = decode_digit(gray, 5, 5, 18, 30)
        assert got == d, (d, got)
        assert conf == 1.0


def test_scoreboard_render_read():
    for p1, p2 in [(7, 2), (21, 19), (0, 0), (11, 9)]:
        img = np.zeros((48, 200, 3), dtype=np.uint8)
        render_scoreboard(img, p1, p2)
        res = read_scoreboard(img)
        assert res is not None
        assert (res[0], res[1]) == (p1, p2)


def test_blank_frame_has_no_score():
    img = np.zeros((48, 200, 3), dtype=np.uint8)
    assert read_scoreboard(img) is None


def test_analysis_reads_scoreboard(client, coach_headers, tmp_path):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "P"}
    ).json()["id"]

    path = str(tmp_path / "m.avi")
    write_synthetic_video(path, n_frames=60, score=(3, 1))
    with open(path, "rb") as f:
        data = f.read()

    vid = client.post(
        f"/v1/players/{pid}/videos",
        headers=coach_headers,
        files={"file": ("m.avi", data, "video/avi")},
    ).json()["id"]

    run = client.post(f"/v1/videos/{vid}/analyze", headers=coach_headers).json()
    assert run["status"] == "done", run

    match = client.get(f"/v1/matches/{run['match_id']}", headers=coach_headers).json()
    assert match["score"] is not None
    assert match["score"]["p1"] == 3
    assert match["score"]["p2"] == 1
    assert match["score"]["source"] == "ocr_7seg"
