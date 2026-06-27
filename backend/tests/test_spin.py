import os
import tempfile

from app.cv.pipeline import analyze_video
from app.cv.spin import estimate_spin
from app.cv.synth import write_synthetic_video

G = 0.6  # gravity reference (px/frame^2)


def _arc(n=16, ax=0.0, ay=G, vx=4.0, vy=3.0, x0=40.0, y0=60.0):
    """A perfect constant-acceleration arc with known a_x / a_y."""
    return [(f, x0 + vx * f + 0.5 * ax * f * f, y0 + vy * f + 0.5 * ay * f * f) for f in range(n)]


def test_no_spin():
    assert estimate_spin(_arc(), G)["spin_type"] == "no_spin"


def test_topspin_drops_faster_than_gravity():
    assert estimate_spin(_arc(ay=1.0), G)["spin_type"] == "topspin"


def test_backspin_floats():
    assert estimate_spin(_arc(ay=0.2), G)["spin_type"] == "backspin"


def test_sidespin_right_and_left():
    assert estimate_spin(_arc(ax=0.5), G)["spin_type"] == "sidespin_right"
    assert estimate_spin(_arc(ax=-0.5), G)["spin_type"] == "sidespin_left"


def test_confidence_capped_and_uncalibrated():
    s = estimate_spin(_arc(ax=0.5), G)
    assert 0.0 < s["confidence"] <= 0.5
    assert s["calibrated"] is False


def test_pipeline_attaches_spin_per_rally():
    fd, p = tempfile.mkstemp(suffix=".avi")
    os.close(fd)
    try:
        write_synthetic_video(p, n_frames=90)
        res = analyze_video(p)
        valid = {"no_spin", "topspin", "backspin", "sidespin_left", "sidespin_right", "mixed"}
        for r in res["rallies"]:
            assert "spin" in r
            assert r["spin"]["spin_type"] in valid
    finally:
        os.remove(p)
