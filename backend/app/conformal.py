"""Split-conformal prediction (Part 40 §X).

Distribution-free intervals with a marginal coverage guarantee: calibrate a
nonconformity quantile on held-out residuals, then `value ± q` covers the truth
with probability >= 1-alpha (finite-sample, exchangeable data). Pure stdlib.
"""
from __future__ import annotations

import math
from typing import Sequence


def fit_quantile(residuals: Sequence[float], alpha: float = 0.10) -> float:
    """The (1-alpha) conformal quantile of |residuals| with the finite-sample
    correction `ceil((n+1)(1-alpha))/n`. Guarantees marginal coverage >= 1-alpha."""
    r = sorted(abs(float(x)) for x in residuals)
    n = len(r)
    if n == 0:
        return 0.0
    k = math.ceil((n + 1) * (1 - alpha))
    if k > n:           # not enough calibration points for the requested level
        return float("inf")
    return r[k - 1]


def interval(value: float, q: float) -> list:
    """A symmetric conformal interval [value-q, value+q]."""
    return [round(value - q, 4), round(value + q, 4)]


def coverage(values: Sequence[float], lows: Sequence[float], highs: Sequence[float]) -> float:
    """Empirical coverage = PICP (Part 40 §N) of the given intervals."""
    n = len(values)
    if n == 0:
        return 0.0
    return sum(1 for v, lo, hi in zip(values, lows, highs) if lo <= v <= hi) / n
