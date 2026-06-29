"""Tests for the per-value reliability engine (Part 40)."""
import pytest

from app import reliability as rel


def test_status_bands():
    assert rel.status_for(0.96, validated=True) == "verified"
    assert rel.status_for(0.92) == "high"
    assert rel.status_for(0.80) == "moderate"
    assert rel.status_for(0.60) == "preliminary"
    assert rel.status_for(0.40) == "abstain"  # below default threshold


def test_uncalibrated_capped_to_preliminary():
    # An uncalibrated estimate cannot claim more than preliminary (Part 40 §M).
    assert rel.status_for(0.99, calibrated=False) == "preliminary"


def test_compose_is_product_or_min_never_average():
    assert rel.compose([0.95, 0.90, 0.85], "chain") == pytest.approx(0.95 * 0.90 * 0.85)
    assert rel.compose([0.95, 0.90, 0.85], "required_all") == 0.85
    # averaging is explicitly forbidden
    with pytest.raises(ValueError):
        rel.compose([0.9, 0.9], "avg")


def test_tier_cap_is_a_minimum():
    assert rel.apply_cap(0.92, tier="T1") == 0.6
    assert rel.apply_cap(0.92, tier="t3") == 0.9   # case-insensitive
    assert rel.apply_cap(0.50, tier="T3") == 0.50  # below ceiling unchanged


def test_certification_cap_uses_part35_single_source():
    # 'fail' capture ceiling is 0.3 in the Part-35 schema; 'gold' is 0.9.
    assert rel.apply_cap(0.99, certification="fail") <= 0.3
    assert rel.apply_cap(0.99, certification="gold") == pytest.approx(0.9)


def test_build_abstains_with_null_value():
    env = rel.build(78.0, 0.30, tier="T2", unit="km/h")
    assert env.status == "abstain" and env.value is None


def test_build_high_with_cap_and_ci():
    env = rel.build(78.0, 0.92, tier="T3", unit="km/h", ci=[72, 84])
    assert env.value == 78.0 and env.status == "high"
    assert env.confidence == 0.9  # capped by T3 ceiling
    d = env.to_dict()
    for k in ("value", "confidence", "status", "tier", "ci", "unit", "calibrated", "source"):
        assert k in d


def test_abstain_helper_records_reason():
    env = rel.abstain("occlusion", tier="T1")
    assert env.status == "abstain" and env.value is None
    assert env.source["abstain_reason"] == "occlusion"


def test_decide_is_selective():
    assert rel.decide(0.6) is True
    assert rel.decide(0.3) is False


def test_summarize_shape():
    s = rel.summarize(0.92, tier="T1", calibrated=False)
    assert s["confidence"] == 0.6 and s["status"] == "preliminary" and s["calibrated"] is False
