"""Out-of-distribution / novelty gate (Part 40 §Y).

A lightweight, honest OOD signal: a 1-D standardized-distance gate over a
reference signal (e.g. detection-confidence or brightness distribution). An
input beyond `z` std-devs from the reference is novel → epistemic uncertainty
spikes → the caller MUST cap or abstain (§W/§F). Multivariate detectors
(Mahalanobis / energy / ensemble disagreement) implement the same interface.
"""
from __future__ import annotations

import statistics
from typing import Sequence


class OODGate:
    def __init__(self, mean: float, std: float, z: float = 3.0):
        self.mean = float(mean)
        self.std = float(std) or 1e-9
        self.z = float(z)

    @classmethod
    def fit(cls, samples: Sequence[float], z: float = 3.0, min_std: float = 0.0) -> "OODGate":
        """Fit the reference mean/std from samples. `min_std` floors the dispersion:
        a too-clean reference (near-zero variance — e.g. synthetic golden clips) would
        otherwise yield a hypersensitive gate that flags any deviation as OOD, so the
        floor injects a prior on the minimum plausible spread (Part 40 §Y)."""
        if not samples:
            raise ValueError("OODGate.fit needs at least one reference sample")
        mean = statistics.fmean(samples)
        std = statistics.pstdev(samples) if len(samples) > 1 else 1e-9
        return cls(mean, max(std or 1e-9, min_std), z)

    def score(self, x: float) -> float:
        """Standardized distance from the reference (|z|)."""
        return abs(float(x) - self.mean) / self.std

    def is_ood(self, x: float) -> bool:
        """True if the input is novel (beyond z std-devs)."""
        return self.score(x) > self.z

    def to_dict(self) -> dict:
        return {"mean": round(self.mean, 4), "std": round(self.std, 4), "z": self.z}
