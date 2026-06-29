"""Tests for calibration metrics + temperature scaling + the release gate (Part 40)."""
import pytest

from app import calibration as cal


def test_ece_zero_when_perfectly_confident_and_correct():
    confs = [1.0] * 100
    correct = [True] * 100
    assert cal.ece(confs, correct) == pytest.approx(0.0, abs=1e-9)


def test_ece_high_when_overconfident():
    # claims 0.9 confidence but only 50% correct -> large calibration error
    confs = [0.9] * 100
    correct = [True] * 50 + [False] * 50
    assert cal.ece(confs, correct) > 0.3
    assert cal.mce(confs, correct) >= cal.ece(confs, correct)


def test_brier_bounds():
    assert cal.brier_score([1.0, 1.0], [True, True]) == pytest.approx(0.0)
    assert cal.brier_score([0.0, 0.0], [True, True]) == pytest.approx(1.0)


def test_picp():
    vals = [1.0, 2.0, 3.0]
    assert cal.picp(vals, [0, 0, 0], [5, 5, 5]) == pytest.approx(1.0)
    assert cal.picp(vals, [10, 10, 10], [20, 20, 20]) == pytest.approx(0.0)


def test_temperature_scaling_reduces_overconfidence():
    # overconfident: predicts 0.99 but is right ~half the time
    probs = [0.99] * 50 + [0.99] * 50
    labels = [True] * 50 + [False] * 50
    before = cal.calibration_report(probs, labels)["ece"]
    t = cal.fit_temperature(probs, labels)
    assert t > 1.0  # softening
    after_probs = cal.apply_temperature(probs, t)
    after = cal.ece(after_probs, labels)
    assert after < before


def test_release_gate():
    # Well-calibrated: confidence 0.9 with 90% correct -> ECE ~ 0 (comfortably
    # below target; avoid sitting exactly on the 0.05 boundary).
    good_confs = [0.9] * 100
    good_correct = [True] * 90 + [False] * 10
    assert cal.passes_gate(good_confs, good_correct) is True

    bad_confs = [0.99] * 100
    bad_correct = [True] * 50 + [False] * 50
    assert cal.passes_gate(bad_confs, bad_correct) is False
