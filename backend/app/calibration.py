"""Calibration metrics + calibrators + the release gate (Part 40 §G/§N/§AP).

Pure-stdlib (no numpy/sklearn) so the reliability core has no heavy dependency.
Provides: ECE/MCE, Brier, reliability diagram (§N), interval coverage PICP,
binary **temperature scaling** (§G), and `passes_gate()` (the §G.4 calibration
release gate). Targets are config defaults (Part 40 §AQ).
"""
from __future__ import annotations

import math
from typing import Sequence

ECE_TARGET = 0.05
MCE_TARGET = 0.10
PICP_TOLERANCE = 0.03


def _bins(confidences: Sequence[float], correct: Sequence[bool], n_bins: int):
    bins: list[list[tuple[float, float]]] = [[] for _ in range(n_bins)]
    for c, y in zip(confidences, correct):
        idx = min(n_bins - 1, max(0, int(float(c) * n_bins)))
        bins[idx].append((float(c), 1.0 if y else 0.0))
    return bins


def ece(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> float:
    """Expected Calibration Error = Σ_b (n_b/N)·|acc(b) − conf(b)|."""
    n = len(confidences)
    if n == 0:
        return 0.0
    total = 0.0
    for b in _bins(confidences, correct, n_bins):
        if not b:
            continue
        conf = sum(c for c, _ in b) / len(b)
        acc = sum(y for _, y in b) / len(b)
        total += (len(b) / n) * abs(acc - conf)
    return total


def mce(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> float:
    """Maximum Calibration Error = max_b |acc(b) − conf(b)|."""
    worst = 0.0
    for b in _bins(confidences, correct, n_bins):
        if not b:
            continue
        conf = sum(c for c, _ in b) / len(b)
        acc = sum(y for _, y in b) / len(b)
        worst = max(worst, abs(acc - conf))
    return worst


def brier_score(confidences: Sequence[float], correct: Sequence[bool]) -> float:
    n = len(confidences)
    if n == 0:
        return 0.0
    return sum((float(c) - (1.0 if y else 0.0)) ** 2 for c, y in zip(confidences, correct)) / n


def picp(values: Sequence[float], lows: Sequence[float], highs: Sequence[float]) -> float:
    """Prediction-Interval Coverage Probability (§N)."""
    n = len(values)
    if n == 0:
        return 0.0
    return sum(1 for v, lo, hi in zip(values, lows, highs) if lo <= v <= hi) / n


def reliability_diagram(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10):
    out = []
    for i, b in enumerate(_bins(confidences, correct, n_bins)):
        if not b:
            out.append({"bin": i, "n": 0, "conf": None, "acc": None})
        else:
            out.append({
                "bin": i, "n": len(b),
                "conf": sum(c for c, _ in b) / len(b),
                "acc": sum(y for _, y in b) / len(b),
            })
    return out


# --- Temperature scaling (binary, via logit) — Part 40 §G ------------------- #
def _logit(p: float) -> float:
    p = min(1 - 1e-6, max(1e-6, float(p)))
    return math.log(p / (1 - p))


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def apply_temperature(probs: Sequence[float], temperature: float) -> list[float]:
    return [_sigmoid(_logit(p) / temperature) for p in probs]


def _nll(probs: Sequence[float], labels: Sequence[float]) -> float:
    s = 0.0
    for p, y in zip(probs, labels):
        p = min(1 - 1e-6, max(1e-6, p))
        s += -((y * math.log(p)) + ((1 - y) * math.log(1 - p)))
    return s / len(probs)


def fit_temperature(
    probs: Sequence[float], labels: Sequence[bool], lo: float = 0.05, hi: float = 10.0, iters: int = 60
) -> float:
    """Golden-section search for the temperature T minimizing NLL of
    sigmoid(logit(p)/T). T > 1 softens overconfidence (§G)."""
    y = [1.0 if v else 0.0 for v in labels]
    gr = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = _nll(apply_temperature(probs, c), y), _nll(apply_temperature(probs, d), y)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = _nll(apply_temperature(probs, c), y)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = _nll(apply_temperature(probs, d), y)
    return (a + b) / 2


def calibration_report(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> dict:
    """The reliability section of a model card (Part 40 §BE/§N)."""
    return {
        "ece": round(ece(confidences, correct, n_bins), 4),
        "mce": round(mce(confidences, correct, n_bins), 4),
        "brier": round(brier_score(confidences, correct), 4),
        "n": len(confidences),
    }


def passes_gate(
    confidences: Sequence[float],
    correct: Sequence[bool],
    *,
    ece_target: float = ECE_TARGET,
    mce_target: float = MCE_TARGET,
) -> bool:
    """Part 40 §G.4 calibration release gate: model promotion requires
    ECE ≤ target and MCE ≤ target."""
    return ece(confidences, correct) <= ece_target and mce(confidences, correct) <= mce_target
