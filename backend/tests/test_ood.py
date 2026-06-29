"""Tests for the out-of-distribution / novelty gate (Part 40 §Y)."""
import pytest

from app import ood


def test_ood_gate_flags_novel_inputs():
    g = ood.OODGate.fit([10, 10.1, 9.9, 10.05, 9.95, 10.0], z=3.0)
    assert g.is_ood(11.0) is True          # far from the reference -> novel
    assert g.is_ood(10.05) is False        # in-distribution
    assert g.score(11.0) > g.score(10.05)  # score is monotonic in distance


def test_fit_requires_samples():
    with pytest.raises(ValueError):
        ood.OODGate.fit([])


def test_min_std_floor_prevents_degenerate_gate():
    # A near-constant (too-clean) reference would give std~0 and flag everything as
    # OOD; the min_std floor injects a prior spread so the gate stays sane (§Y).
    g = ood.OODGate.fit([0.99, 1.0, 0.995, 1.0, 0.99], z=3.0, min_std=0.1)
    assert g.std >= 0.1
    assert g.is_ood(0.95) is False   # within the floored band
    assert g.is_ood(0.5) is True     # genuinely far -> novel
