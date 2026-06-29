"""Tests for split-conformal prediction (Part 40 §X)."""
import random

from app import conformal


def test_quantile_gives_target_coverage():
    random.seed(0)
    cal = [random.gauss(0, 1) for _ in range(500)]
    q = conformal.fit_quantile(cal, alpha=0.10)
    assert q > 0
    # Fresh draws: |x| <= q should hold ~90% of the time (>= 1-alpha, with slack).
    test = [random.gauss(0, 1) for _ in range(3000)]
    cov = conformal.coverage(test, [-q] * len(test), [q] * len(test))
    assert cov >= 0.86, cov


def test_interval_symmetric():
    assert conformal.interval(78.0, 6.0) == [72.0, 84.0]


def test_insufficient_calibration_is_infinite():
    # Cannot guarantee 99% coverage from a single point.
    assert conformal.fit_quantile([1.0], alpha=0.01) == float("inf")
