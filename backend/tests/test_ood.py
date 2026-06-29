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
