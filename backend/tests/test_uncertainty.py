"""Tests for GUM first-order measurement-uncertainty propagation (Part 40 §AP/§BH)."""
import pytest

from app import uncertainty as unc


def test_positive_and_tiered():
    # Same displacement: T1 (nominal pixel->metre scale) is far more uncertain than T3.
    h1, c1 = unc.speed_uncertainty(60.0, 20.0, tier="t1", k=2.0)
    h3, c3 = unc.speed_uncertainty(60.0, 20.0, tier="t3", k=2.0)
    assert h1 > h3 > 0
    assert c1["rel_scale"] > c3["rel_scale"]


def test_localisation_term_shrinks_with_displacement():
    # The localisation contribution scales ~ 1/||Δp||.
    small = unc.speed_uncertainty(60.0, 5.0, tier="t1")[1]["rel_disp"]
    large = unc.speed_uncertainty(60.0, 50.0, tier="t1")[1]["rel_disp"]
    assert large < small


def test_zero_speed_has_no_interval():
    assert unc.speed_uncertainty(0.0, 0.0) == (0.0, {})


def test_expanded_uncertainty_scales_linearly_with_k():
    h1 = unc.speed_uncertainty(60.0, 20.0, tier="t2", k=1.0)[0]
    h2 = unc.speed_uncertainty(60.0, 20.0, tier="t2", k=2.0)[0]
    assert h2 == pytest.approx(2 * h1, rel=1e-6)


def test_combine_relative_is_quadrature():
    assert unc.combine_relative(0.3, 0.4) == pytest.approx(0.5)
