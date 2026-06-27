"""Golden-set regression gate — accuracy must not silently drop (Part 10.18)."""
from app.benchmark import run_detector_benchmark, run_scoreboard_benchmark


def test_detector_meets_golden_thresholds():
    m = run_detector_benchmark(n_clips=2, n_frames=50)
    assert m["detection_rate"] >= 0.9, m
    assert m["mean_loc_error_px"] is not None
    assert m["mean_loc_error_px"] <= 5.0, m  # sub-5px localisation on synthetic


def test_scoreboard_ocr_perfect_on_synthetic():
    assert run_scoreboard_benchmark()["accuracy"] == 1.0
