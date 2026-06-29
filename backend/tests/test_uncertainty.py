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


def test_localization_sigma_is_data_driven():
    # A clean parabola has ~zero residual -> small sigma; noise raises it.
    clean = [(i, 2.0 * i, 0.5 * i * i) for i in range(10)]
    noisy = [(i, 2.0 * i + (3 if i % 2 else -3), 0.5 * i * i) for i in range(10)]
    s_clean = unc.localization_sigma_from_track(clean)
    s_noisy = unc.localization_sigma_from_track(noisy)
    assert s_clean is not None and s_noisy is not None
    assert s_noisy > s_clean


def test_localization_sigma_needs_enough_points():
    assert unc.localization_sigma_from_track([(0, 0, 0), (1, 1, 1)]) is None


def test_snr_significance_gate():
    # SNR = ||Δp|| / (√2·σ_px). A tiny displacement vs the localisation noise is NOT
    # significant (GUM linearisation invalid + Rician bias) -> the caller must abstain.
    small = unc.speed_uncertainty(60.0, 1.0, tier="t1", sigma_px=2.0)[1]
    big = unc.speed_uncertainty(60.0, 60.0, tier="t1", sigma_px=2.0)[1]
    assert small["significant"] is False and small["snr"] < unc.SNR_MIN
    assert big["significant"] is True and big["snr"] >= unc.SNR_MIN
    # snr is the reciprocal of the relative localisation term (both 2-dp rounded).
    assert small["snr"] == pytest.approx(1.0 / small["rel_disp"], abs=0.01)


def test_snr_boundary_is_snr_min():
    # At ||Δp|| = SNR_MIN·√2·σ_px the measurement sits exactly on the threshold.
    sigma = 2.0
    disp = unc.SNR_MIN * (2 ** 0.5) * sigma
    comps = unc.speed_uncertainty(60.0, disp, tier="t1", sigma_px=sigma)[1]
    assert comps["snr"] == pytest.approx(unc.SNR_MIN, rel=1e-6)
    assert comps["significant"] is True  # >= is significant


def test_rel_scale_override():
    # A measured calibration residual can override the per-tier default scale term.
    base = unc.speed_uncertainty(60.0, 20.0, tier="t1")[1]["rel_scale"]
    over = unc.speed_uncertainty(60.0, 20.0, tier="t1", rel_scale=0.02)[1]["rel_scale"]
    assert over == 0.02 and over < base
