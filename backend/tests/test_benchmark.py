"""Golden-set regression gate — accuracy must not silently drop (Part 10.18)."""
from app.benchmark import (
    run_calibration_benchmark,
    run_detector_benchmark,
    run_scoreboard_benchmark,
)


def test_detector_meets_golden_thresholds():
    m = run_detector_benchmark(n_clips=2, n_frames=50)
    assert m["detection_rate"] >= 0.9, m
    assert m["mean_loc_error_px"] is not None
    assert m["mean_loc_error_px"] <= 5.0, m  # sub-5px localisation on synthetic


def test_scoreboard_ocr_perfect_on_synthetic():
    assert run_scoreboard_benchmark()["accuracy"] == 1.0


def test_calibration_benchmark_reports_and_temperature_helps():
    m = run_calibration_benchmark(n_clips=2, n_frames=50)
    assert m["n"] > 0, m
    for k in ("ece", "mce", "brier", "ece_after_temperature"):
        assert 0.0 <= m[k] <= 1.0, m
    assert m["temperature"] > 0, m
    # NLL is what temperature scaling minimises (T=1 is in the search range),
    # so calibration must never get worse on the golden set.
    assert m["calibration_improved"] is True, m
    assert m["nll_after"] <= m["nll_before"] + 1e-9, m
