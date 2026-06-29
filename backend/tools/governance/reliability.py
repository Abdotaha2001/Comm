"""Reliability-law governance gate (Part 40 §T/§AO).

Enforces in CI that the reliability engine upholds the non-negotiables:
no averaging of uncertainty, status bands honored, tier cap is a minimum,
certification ceilings come from the Part-35 single source, and the calibration
release gate actually discriminates good vs miscalibrated models.
"""
from __future__ import annotations

from .common import Check


def check_reliability() -> Check:
    chk = Check("reliability")
    try:
        from app import calibration as cal
        from app import reliability as rel
    except Exception as exc:  # noqa: BLE001
        chk.fail(f"reliability/calibration modules not importable: {exc}")
        return chk

    # Required engine API exists.
    for name in ("build", "status_for", "compose", "apply_cap", "abstain", "decide", "summarize"):
        if not callable(getattr(rel, name, None)):
            chk.fail(f"reliability.{name} missing")
    for name in ("ece", "mce", "brier_score", "picp", "fit_temperature", "passes_gate"):
        if not callable(getattr(cal, name, None)):
            chk.fail(f"calibration.{name} missing")
    if not chk.ok:
        return chk

    # §B.3/§H — averaging uncertainty is forbidden.
    try:
        rel.compose([0.9, 0.9], "avg")
        chk.fail("compose() must reject averaging mode (Part 40 §B.3)")
    except ValueError:
        pass
    if rel.compose([0.95, 0.9, 0.85], "required_all") != 0.85:
        chk.fail("required_all composition must be the minimum (§H.4)")

    # §E — status bands.
    if rel.status_for(0.96, validated=True) != "verified":
        chk.fail("status_for: validated >=0.95 must be 'verified'")
    if rel.status_for(0.40) != "abstain":
        chk.fail("status_for: below threshold must be 'abstain'")
    if rel.status_for(0.99, calibrated=False) != "preliminary":
        chk.fail("status_for: uncalibrated must cap at 'preliminary' (§M)")

    # §I — tier cap is a minimum; certification ceilings are the Part-35 SoT.
    if rel.apply_cap(0.92, tier="T1") != 0.6:
        chk.fail("apply_cap: T1 ceiling must cap to 0.6 (§I)")
    if rel.apply_cap(0.99, certification="fail") > 0.3:
        chk.fail("apply_cap: 'fail' capture must cap to <=0.3 (Part 35 single source)")

    # §G.4 — calibration release gate discriminates (well-calibrated: 0.9 conf,
    # 90% correct -> ECE ~ 0, comfortably below target).
    if not cal.passes_gate([0.9] * 100, [True] * 90 + [False] * 10):
        chk.fail("passes_gate: a well-calibrated set must pass")
    if cal.passes_gate([0.99] * 100, [True] * 50 + [False] * 50):
        chk.fail("passes_gate: an overconfident set must fail (§G.4)")

    chk.info["engine"] = "ok"
    return chk
