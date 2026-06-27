"""Markerless spin estimation from trajectory curvature (the Magnus effect).

Physics (MASTER_SPEC Part 19 §C1, §C6): with no spin a ball flies ballistically
(constant horizontal velocity; vertical acceleration = gravity). Spin adds a
Magnus force that curves the path:
  - horizontal curvature (fitted a_x != 0)            -> sidespin (sign = L/R)
  - vertical accel above gravity (drops faster)       -> topspin
  - vertical accel below gravity (floats)             -> backspin

We fit constant accelerations (a_x, a_y) to a single ballistic arc by least
squares and compare a_y to a gravity reference. Honest + uncalibrated: spin RPM
needs aero constants + 3D (Part 02), so we return a sign/type + relative
magnitude with a capped confidence. A dotted-ball / high-speed method (SpinDOE,
Part 26) gives true RPM behind the same interface.
"""
from typing import List, Optional, Tuple

import numpy as np

AX_THRESH = 0.15   # px/frame^2 — horizontal curvature to call sidespin
AY_THRESH = 0.15   # px/frame^2 — vertical excess to call top/backspin
MIN_ARC = 5

Track = List[Tuple[int, float, float]]  # (frame, x, y)


def _fit_accel(frames: np.ndarray, vals: np.ndarray) -> float:
    """Least-squares constant acceleration: val = c0 + c1*t + 0.5*a*t^2 -> a."""
    A = np.vstack([np.ones_like(frames), frames, 0.5 * frames ** 2]).T
    coef, *_ = np.linalg.lstsq(A, vals, rcond=None)
    return float(coef[2])


def estimate_spin(track: Track, gravity_px: float = 0.0) -> dict:
    if len(track) < MIN_ARC:
        return {"spin_type": "no_spin", "magnitude": 0.0, "confidence": 0.0,
                "calibrated": False, "note": "insufficient track"}
    f = np.array([p[0] for p in track], dtype=float)
    f -= f[0]
    x = np.array([p[1] for p in track], dtype=float)
    y = np.array([p[2] for p in track], dtype=float)
    ax = _fit_accel(f, x)
    ay = _fit_accel(f, y)
    excess_ay = ay - gravity_px  # image y grows downward: >0 = extra drop (topspin)

    has_side = abs(ax) > AX_THRESH
    has_vert = abs(excess_ay) > AY_THRESH
    if has_side and has_vert:
        spin_type = "mixed"
    elif has_side:
        spin_type = "sidespin_right" if ax > 0 else "sidespin_left"
    elif has_vert:
        spin_type = "topspin" if excess_ay > 0 else "backspin"
    else:
        spin_type = "no_spin"

    magnitude = float(np.hypot(ax, excess_ay))
    strength = min(1.0, magnitude / 1.0)
    confidence = round(min(0.5, (len(track) / 30.0) * strength), 3)  # markerless cap 0.5
    return {
        "spin_type": spin_type,
        "axis": {"a_x": round(ax, 3), "excess_a_y": round(excess_ay, 3)},
        "magnitude": round(magnitude, 3),
        "confidence": confidence,
        "calibrated": False,
        "note": "markerless trajectory estimate",
    }


def split_arcs(track: Track) -> List[Track]:
    """Split a track into ballistic arcs at bounces (vertical-velocity reversals)."""
    arcs, cur = [], []
    for i, p in enumerate(track):
        if cur:
            pf, _, py = cur[-1]
            if p[0] - pf == 1:
                vy_prev = py - (cur[-2][2] if len(cur) >= 2 else py)
                vy_now = p[2] - py
                if vy_prev > 0 and vy_now <= 0 and len(cur) >= MIN_ARC:  # bounce
                    arcs.append(cur)
                    cur = []
        cur.append(p)
    if cur:
        arcs.append(cur)
    return arcs


def gravity_from_tracks(tracks: List[Track]) -> float:
    """Robust gravity reference = median fitted vertical accel across all arcs."""
    accs = []
    for tr in tracks:
        for arc in split_arcs(tr):
            if len(arc) >= MIN_ARC:
                f = np.array([p[0] for p in arc], dtype=float)
                f -= f[0]
                accs.append(_fit_accel(f, np.array([p[2] for p in arc], dtype=float)))
    return float(np.median(accs)) if accs else 0.0


def rally_spin(track: Track, gravity_px: float) -> dict:
    """Aggregate spin over a rally's arcs: highest-confidence non-no_spin, else no_spin."""
    best = {"spin_type": "no_spin", "confidence": 0.0, "calibrated": False}
    arcs_used = 0
    for arc in split_arcs(track):
        if len(arc) < MIN_ARC:
            continue
        arcs_used += 1
        s = estimate_spin(arc, gravity_px)
        if s["spin_type"] != "no_spin" and s["confidence"] > best["confidence"]:
            best = s
    out = dict(best)
    out["arcs_used"] = arcs_used
    return out
