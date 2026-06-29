"""Measurement-uncertainty propagation (Part 40 §AP/§BH; GUM first-order).

Replaces fabricated intervals with intervals derived from the actual sources of
error. For speed `v = K·||Δp||` (K = fps / px_per_m · 3.6, Δp = inter-frame ball
displacement in px), the dominant uncertainties are:

  * localisation: each endpoint has std σ_px ⇒ the displacement magnitude has
    σ_d = √2·σ_px (difference of two independent 2-D points), so the *relative*
    contribution is √2·σ_px / ||Δp||;
  * scale: px_per_m is a calibration quantity with relative uncertainty ε_scale,
    large on T1 (a nominal guess), small on a calibrated T2/T3 rig.

Combined (independent, first-order):  σ_v = v · √( (√2·σ_px/||Δp||)² + ε_scale² ).
The reported half-width is the GUM **expanded uncertainty** U = k·σ_v (k=2 ≈ 95%,
frequentist coverage — Part 40 §BP). Pure stdlib.
"""
from __future__ import annotations

import math

# Detector localisation std in px (≈ golden-set mean localisation error, Part 29).
LOCALIZATION_STD_PX = 2.0

# Relative uncertainty of the pixel→metre scale per capture tier (§I/§L).
SCALE_REL_UNCERTAINTY = {"t1": 0.25, "t2": 0.08, "t3": 0.05, "t3_officiating": 0.03}


def combine_relative(*relatives: float) -> float:
    """Combine independent relative uncertainties in quadrature (GUM)."""
    return math.sqrt(sum(r * r for r in relatives))


def localization_sigma_from_track(points, *, min_points: int = 5,
                                  lo: float = 0.5, hi: float = 15.0):
    """Estimate the per-coordinate localisation std σ_px (px) **from the data**
    (Part 40 §AP/§AG) as the residual of a degree-2 fit to the trajectory — the
    ball follows a smooth (near-ballistic) path, so deviations are measurement
    noise. Returns ``None`` when there are too few points to estimate; callers
    then fall back to the measured default. Result is clamped to [lo, hi]."""
    pts = list(points)
    if len(pts) < min_points:
        return None
    import numpy as np

    t = np.array([p[0] for p in pts], dtype=float)
    t = t - t.mean()
    x = np.array([p[1] for p in pts], dtype=float)
    y = np.array([p[2] for p in pts], dtype=float)
    try:
        rx = x - np.polyval(np.polyfit(t, x, 2), t)
        ry = y - np.polyval(np.polyfit(t, y, 2), t)
    except Exception:  # noqa: BLE001 — degenerate fit
        return None
    dof = max(1, len(pts) - 3)  # a degree-2 fit consumes 3 parameters
    var = (float((rx ** 2).sum()) + float((ry ** 2).sum())) / (2.0 * dof)
    return min(hi, max(lo, var ** 0.5))


def speed_uncertainty(
    speed_kmh: float,
    disp_px: float,
    *,
    tier: str = "t1",
    sigma_px: float = LOCALIZATION_STD_PX,
    k: float = 2.0,
) -> tuple[float, dict]:
    """First-order propagation for speed. Returns (half_width, components).

    `half_width` is the expanded uncertainty U = k·σ_v in km/h; build the interval
    as [v - U, v + U]. Returns (0, {}) when speed/displacement is undefined.
    """
    if not speed_kmh or not disp_px:
        return 0.0, {}
    rel_disp = (math.sqrt(2.0) * sigma_px) / abs(disp_px)
    rel_scale = SCALE_REL_UNCERTAINTY.get(str(tier).lower(), 0.25)
    rel = combine_relative(rel_disp, rel_scale)
    sigma = abs(speed_kmh) * rel
    half = round(k * sigma, 2)
    return half, {
        "method": "gum_first_order",
        "k": k,
        "coverage": "~0.95" if k == 2.0 else None,
        "sigma_px": sigma_px,
        "rel_disp": round(rel_disp, 4),
        "rel_scale": rel_scale,
        "rel_combined": round(rel, 4),
        "sigma_kmh": round(sigma, 2),
        "frame_semantics": "frequentist",  # §BP
    }
