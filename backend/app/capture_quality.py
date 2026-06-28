"""Capture Acceptance Framework — backend engine.

Authoritative implementation of the acceptance logic described in the Hardware &
Capture SOP (Part 35). The machine-readable single source of truth is
``MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json``; this module loads it at runtime
so documentation and implementation cannot diverge. The CSV operator checklist and
the example quality report are *generated* from the same schema
(``python -m app.capture_quality --generate``).

Philosophy (safety-critical / officiating — see Part 10, Part 31, Part 34.AL):
  * Certification is governed by the **lowest required sub-score**, never an average.
  * A single mandatory gate in red / critical / missing state denies the level
    outright, regardless of every other score.
  * Averages are informational only; they never determine certification.

Cross-references: Part 02 (calibration/sync/3D), Part 10 (reliability envelope),
Part 12 (infra/edge), Part 14 (latency), Part 19 (physics/units), Part 20
(equipment/contrast), Part 31 (officiating isolation / tamper-evidence),
Part 32 (operator dashboard), Part 34.AK (provenance), Part 35 (SOP).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

SCHEMA_FILENAME = "35_CAPTURE_ACCEPTANCE_SCHEMA.json"
CHECKLIST_FILENAME = "35_CAPTURE_ACCEPTANCE_CHECKLIST.csv"
REPORT_FILENAME = "capture_quality_report.md"

# Dashboard states, worst-first. Index = severity ordering.
STATE_ORDER = ["green", "amber", "red", "critical", "missing"]
STATE_TO_SEVERITY = {
    "green": "info",
    "amber": "warning",
    "red": "major",
    "critical": "critical",
    "missing": "critical",
}
FAILED_STATES = {"red", "critical", "missing"}
LEVEL_RANK = {"fail": 0, "bronze": 1, "silver": 2, "gold": 3, "platinum": 4}
LEVELS_HIGH_TO_LOW = ["platinum", "gold", "silver", "bronze"]


# --------------------------------------------------------------------------- #
# Schema loading
# --------------------------------------------------------------------------- #
def _repo_root() -> Path:
    """Walk up from this file to the repository root (the dir holding MASTER_SPEC)."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "MASTER_SPEC").is_dir():
            return parent
    return Path.cwd()


def schema_path(path: Optional[str] = None) -> Path:
    """Resolve the schema path: explicit arg > env override > repo MASTER_SPEC."""
    if path:
        return Path(path)
    env = os.environ.get("CAPTURE_ACCEPTANCE_SCHEMA")
    if env:
        return Path(env)
    return _repo_root() / "MASTER_SPEC" / SCHEMA_FILENAME


def load_schema(path: Optional[str] = None) -> dict[str, Any]:
    """Load + minimally validate the acceptance schema. Returns the schema dict
    with an added ``_kpi_index`` mapping kpi id -> kpi definition."""
    p = schema_path(path)
    with open(p, encoding="utf-8") as fh:
        schema = json.load(fh)

    required_top = {"schema_version", "kpis", "certification_levels", "scoring"}
    missing = required_top - set(schema)
    if missing:
        raise ValueError(f"capture acceptance schema missing keys: {sorted(missing)}")

    index: dict[str, dict] = {}
    required_kpi_fields = {
        "id", "name", "description", "units", "direction", "threshold",
        "warning_threshold", "critical_threshold", "pass_condition",
        "fail_condition", "measurement_method", "priority", "required_tier",
        "certification_dependency", "automatic_fail_action",
        "recommended_operator_action",
    }
    for kpi in schema["kpis"]:
        miss = required_kpi_fields - set(kpi)
        if miss:
            raise ValueError(f"KPI '{kpi.get('id')}' missing fields: {sorted(miss)}")
        index[kpi["id"]] = kpi

    # Every mandatory KPI referenced by a level must exist.
    for level, ldef in schema["certification_levels"].items():
        for kid in ldef.get("mandatory_kpis", []):
            if kid not in index:
                raise ValueError(f"level '{level}' references unknown KPI '{kid}'")
    schema["_kpi_index"] = index
    return schema


# --------------------------------------------------------------------------- #
# Scoring primitives
# --------------------------------------------------------------------------- #
def _subscore_map(schema: dict) -> dict[str, float]:
    return schema["scoring"]["subscore_by_state"]


def _thresholds_for_level(kpi: dict, level: Optional[str]) -> tuple:
    """Return (threshold, warning_threshold, critical_threshold) for a level.

    Per-level overrides *inherit upward*: a higher level with no override of its
    own uses the strictest override defined at or below its rank (so Platinum is
    never looser than Gold). ``level=None`` returns the informational base
    thresholds with no override applied.
    """
    thr = kpi["threshold"]
    warn = kpi["warning_threshold"]
    crit = kpi["critical_threshold"]
    overrides = kpi.get("certification_thresholds") or {}
    if level and overrides:
        want = LEVEL_RANK.get(level, 0)
        best, best_rank = None, -1
        for name, override in overrides.items():
            rank = LEVEL_RANK.get(name, 0)
            if rank <= want and rank > best_rank:
                best, best_rank = override, rank
        if best:
            thr = best.get("threshold", thr)
            warn = best.get("warning_threshold", warn)
            crit = best.get("critical_threshold", crit)
    return thr, warn, crit


def _state_for_value(direction: str, value: Any, thr, warn, crit) -> str:
    """Map a measured value to a dashboard state given the KPI direction."""
    if direction == "boolean":
        return "green" if bool(value) else "critical"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "missing"
    if direction == "higher_is_better":
        if v >= thr:
            return "green"
        if warn is not None and v >= warn:
            return "amber"
        if crit is not None and v >= crit:
            return "red"
        return "critical"
    # lower_is_better
    if v <= thr:
        return "green"
    if warn is not None and v <= warn:
        return "amber"
    if crit is not None and v <= crit:
        return "red"
    return "critical"


def evaluate_kpi(
    kpi: dict, value: Any, schema: dict, level: Optional[str] = None
) -> dict[str, Any]:
    """Evaluate one KPI. ``level`` selects per-level thresholds; omit for the
    informational (base-threshold) per-KPI subscore."""
    submap = _subscore_map(schema)
    thr, warn, crit = _thresholds_for_level(kpi, level)
    if value is None:
        state = "missing"
    else:
        state = _state_for_value(kpi["direction"], value, thr, warn, crit)
    subscore = submap.get(state, 0.0)
    return {
        "kpi": kpi["id"],
        "name": kpi["name"],
        "category": kpi["category"],
        "units": kpi["units"],
        "measured": value,
        "threshold": thr,
        "warning_threshold": warn,
        "critical_threshold": crit,
        "direction": kpi["direction"],
        "state": state,
        "severity": STATE_TO_SEVERITY[state],
        "subscore": subscore,
        "passed": state not in FAILED_STATES,
    }


def _failed_gate(kpi: dict, ev: dict) -> dict[str, Any]:
    """Build an explicit failed-gate record (reason, threshold, measured,
    severity, corrective action, retry)."""
    if ev["state"] == "missing":
        reason = "measurement missing"
    elif kpi["direction"] == "boolean":
        reason = "boolean requirement not met (false)"
    elif ev["state"] == "critical":
        reason = "beyond critical threshold"
    else:
        reason = "outside acceptance threshold"
    return {
        "kpi": kpi["id"],
        "name": kpi["name"],
        "category": kpi["category"],
        "reason": reason,
        "threshold": ev["threshold"],
        "measured": ev["measured"],
        "units": kpi["units"],
        "severity": ev["severity"],
        "corrective_action": kpi["recommended_operator_action"],
        "automatic_fail_action": kpi["automatic_fail_action"],
        "auto_retry_allowed": bool(kpi.get("auto_retry_allowed", False)),
    }


def _evaluate_level(level_id: str, schema: dict, measurements: dict) -> dict:
    """Evaluate a single certification level against the measurements using that
    level's thresholds. Returns pass/fail + effective score + failed gates."""
    index = schema["_kpi_index"]
    ldef = schema["certification_levels"][level_id]
    required = ldef.get("mandatory_kpis", [])
    subs: dict[str, float] = {}
    failed: list[dict] = []
    for kid in required:
        kpi = index[kid]
        ev = evaluate_kpi(kpi, measurements.get(kid), schema, level=level_id)
        subs[kid] = ev["subscore"]
        if ev["state"] in FAILED_STATES:
            failed.append(_failed_gate(kpi, ev))

    # Hard requirements (e.g. Platinum) must each independently pass.
    hard_ok = True
    for kid in ldef.get("hard_requirements", []):
        kpi = index[kid]
        ev = evaluate_kpi(kpi, measurements.get(kid), schema, level=level_id)
        if ev["state"] in FAILED_STATES:
            hard_ok = False

    effective = min(subs.values()) if subs else 1.0
    min_required = ldef.get("min_effective_score", 0.0)
    passed = (not failed) and hard_ok and effective >= min_required
    return {
        "level": level_id,
        "passed": passed,
        "effective_score": effective,
        "min_effective_score": min_required,
        "hard_requirements_ok": hard_ok,
        "subscores": subs,
        "failed_gates": failed,
    }


# --------------------------------------------------------------------------- #
# Result container
# --------------------------------------------------------------------------- #
@dataclass
class CQSResult:
    schema_version: str
    timestamp: str
    capture_tier: Optional[str]
    certification: str
    reliability_level: str
    overall_state: str
    overall_score: float          # informational mean — never gates certification
    effective_score: float        # min(required subscores) for the awarded level
    target_certification: str
    subscores: dict[str, Any]
    failed_gates: list[dict]
    warnings: list[dict]
    recommended_actions: list[str]
    reliability_envelope: dict[str, Any]
    provenance: dict[str, Any]
    per_level: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Core: compute_cqs
# --------------------------------------------------------------------------- #
def compute_cqs(
    measurements: dict[str, Any],
    *,
    context: Optional[dict[str, Any]] = None,
    target_certification: str = "platinum",
    schema: Optional[dict] = None,
    now: Optional[datetime] = None,
) -> CQSResult:
    """Compute the Capture Quality Score and certification.

    Certification uses mandatory-gate logic only: the highest level whose
    mandatory gates all pass, hard requirements all hold, and whose effective
    score (= min of its required subscores) meets the level threshold. Averages
    are reported for information but never drive certification.
    """
    schema = schema or load_schema()
    context = dict(context or {})
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = schema["_kpi_index"]

    # 1) Informational per-KPI evaluation (base thresholds), for all KPIs.
    subscores: dict[str, Any] = {}
    measured_values: list[float] = []
    for kid, kpi in index.items():
        ev = evaluate_kpi(kpi, measurements.get(kid), schema, level=None)
        subscores[kid] = ev
        if measurements.get(kid) is not None:
            measured_values.append(ev["subscore"])
    overall_score = round(sum(measured_values) / len(measured_values), 4) if measured_values else 0.0

    # 2) Certification walk (high -> low); award the first level that passes.
    per_level: dict[str, Any] = {}
    awarded = "fail"
    effective_score = 0.0
    for level_id in LEVELS_HIGH_TO_LOW:
        ev = _evaluate_level(level_id, schema, measurements)
        per_level[level_id] = {
            "passed": ev["passed"],
            "effective_score": round(ev["effective_score"], 4),
            "min_effective_score": ev["min_effective_score"],
            "hard_requirements_ok": ev["hard_requirements_ok"],
            "failed_gate_kpis": [g["kpi"] for g in ev["failed_gates"]],
        }
        if ev["passed"] and awarded == "fail":
            awarded = level_id
            effective_score = round(ev["effective_score"], 4)
    if awarded == "fail":
        effective_score = round(_evaluate_level("bronze", schema, measurements)["effective_score"], 4)

    # 3) Failed gates: evaluated at the target level (default platinum = the most
    #    conservative, audit-friendly view of everything blocking the top grade).
    #    If the awarded level already meets the target, there are no blocking gates.
    if LEVEL_RANK[awarded] >= LEVEL_RANK.get(target_certification, 4):
        failed_gates: list[dict] = []
    else:
        failed_gates = _evaluate_level(target_certification, schema, measurements)["failed_gates"]

    # 4) Warnings = amber KPIs among measured values.
    warnings = [
        {
            "kpi": ev["kpi"], "name": ev["name"], "measured": ev["measured"],
            "threshold": ev["threshold"], "units": ev["units"], "severity": "warning",
            "note": f"{ev['name']} is in the warning band ({ev['measured']} vs {ev['threshold']} {ev['units']})",
        }
        for ev in subscores.values()
        if ev["state"] == "amber"
    ]

    # 5) Recommended actions (critical/major first, then warnings), de-duplicated.
    recommended: list[str] = []
    for g in sorted(failed_gates, key=lambda x: 0 if x["severity"] == "critical" else 1):
        action = f"{g['name']}: {g['corrective_action']} (auto: {g['automatic_fail_action']})"
        if action not in recommended:
            recommended.append(action)
    for w in warnings:
        kpi = index[w["kpi"]]
        action = f"{w['name']}: {kpi['recommended_operator_action']}"
        if action not in recommended:
            recommended.append(action)

    # 6) Overall dashboard state = worst state among the full mandatory KPI set.
    full_mandatory = schema["certification_levels"]["platinum"].get("mandatory_kpis", [])
    overall_state = "green"
    for kid in full_mandatory:
        st = subscores[kid]["state"]
        if STATE_ORDER.index(st) > STATE_ORDER.index(overall_state):
            overall_state = st
    if overall_state == "missing":
        overall_state = "critical"

    # 7) Tier + reliability mapping.
    level_tier = schema["certification_levels"].get(awarded, {}).get("tier")
    capture_tier = context.get("capture_tier") or level_tier
    reliability_level = schema["reliability_mapping"].get(awarded, "unreliable")

    # 8) Provenance + reliability envelope (Part 34.AK / Part 10).
    provenance = build_provenance(measurements, context, awarded, effective_score, schema, ts)
    envelope = build_reliability_envelope(
        measurements, context, awarded, capture_tier, effective_score,
        reliability_level, overall_state, provenance["hash"], schema, ts,
    )

    return CQSResult(
        schema_version=schema["schema_version"],
        timestamp=ts,
        capture_tier=capture_tier,
        certification=awarded,
        reliability_level=reliability_level,
        overall_state=overall_state,
        overall_score=overall_score,
        effective_score=effective_score,
        target_certification=target_certification,
        subscores=subscores,
        failed_gates=failed_gates,
        warnings=warnings,
        recommended_actions=recommended,
        reliability_envelope=envelope,
        provenance=provenance,
        per_level=per_level,
    )


# --------------------------------------------------------------------------- #
# Reliability envelope + provenance
# --------------------------------------------------------------------------- #
def reliability_ceiling_for(certification: str, schema: dict) -> float:
    """Upper bound the analysis reliability may take given the capture grade.
    Applied downstream as a cap (min), never an average (Part 10)."""
    ceiling = schema.get("reliability_ceiling", {})
    try:
        return float(ceiling.get(certification, 1.0))
    except (TypeError, ValueError):
        return 1.0


def _sync_status(measurements: dict) -> str:
    if not measurements.get("time_synchronization", False):
        return "unlocked"
    err = measurements.get("synchronization_error")
    if err is None:
        return "unknown"
    if err <= 0.5:
        return "locked_officiating"
    if err <= 1.0:
        return "locked_competition"
    return "out_of_tolerance"


def build_reliability_envelope(
    measurements, context, certification, capture_tier, effective_score,
    reliability_level, overall_state, provenance_hash, schema, ts,
) -> dict[str, Any]:
    """Capture-level reliability envelope (Part 10). ``status`` becomes 'abstain'
    when the capture is not accepted."""
    status = "abstain" if certification == "fail" else reliability_level
    evidence_integrity = bool(measurements.get("tamper_evidence", False)) and bool(
        measurements.get("provenance", False)
    )
    return {
        "capture_tier": capture_tier,
        "certification": certification,
        "confidence": effective_score,           # capped by the min gate, never an average
        "status": status,
        "input_quality": overall_state,
        "ground_truth_status": bool(measurements.get("ground_truth_status", False)),
        "calibration_version": context.get("calibration_version"),
        "synchronization_status": _sync_status(measurements),
        "evidence_integrity": evidence_integrity,
        "timestamp": ts,
        "provenance_hash": provenance_hash,
        "operator_id": context.get("operator_id"),
        "camera_ids": context.get("camera_ids", []),
        "environmental_conditions": context.get("environment", {}),
        "software_version": context.get("software_version"),
        "model_version": context.get("model_version"),
        "schema_version": schema["schema_version"],
    }


def compute_provenance_hash(payload: dict) -> str:
    """Deterministic SHA-256 over the canonical provenance payload (Part 34.AK)."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_provenance(
    measurements, context, certification, effective_score, schema, ts
) -> dict[str, Any]:
    """Immutable provenance record (Part 34.AK). The hash covers every field
    except the hash itself, so any tampering is detectable."""
    payload = {
        "framework": "capture_acceptance",
        "schema_version": schema["schema_version"],
        "session_id": context.get("session_id"),
        "calibration_version": context.get("calibration_version"),
        "camera_ids": context.get("camera_ids", []),
        "camera_firmware": context.get("camera_firmware", {}),
        "capture_settings": context.get("capture_settings", {}),
        "operator": context.get("operator_id"),
        "device": context.get("device"),
        "environment": context.get("environment", {}),
        "evidence_chain": context.get("evidence_chain", []),
        "certification": certification,
        "effective_score": effective_score,
        "measurements": measurements,
        "timestamp": ts,
    }
    record = dict(payload)
    record["hash"] = compute_provenance_hash(payload)
    return record


# --------------------------------------------------------------------------- #
# CSV checklist generation
# --------------------------------------------------------------------------- #
CSV_COLUMNS = [
    "Category", "KPI", "Measured Value", "Expected Value", "Status", "Severity",
    "Required Tier", "Certification Impact", "Fail Action", "Operator Notes",
    "Timestamp", "Operator",
]


def _certification_impact(kpi: dict) -> str:
    deps = kpi.get("certification_dependency", [])
    if not deps:
        return "informational"
    lowest = min(deps, key=lambda d: LEVEL_RANK.get(d, 99))
    return "Platinum only" if lowest == "platinum" else f"{lowest.capitalize()}+"


def build_checklist_rows(
    schema: dict, result: Optional[CQSResult] = None, context: Optional[dict] = None
) -> list[dict]:
    """Build CSV rows. With no ``result`` this is a blank operator checklist
    template; with a result it is filled with measured values + states."""
    context = context or {}
    rows = []
    for kpi in schema["kpis"]:
        ev = result.subscores.get(kpi["id"]) if result else None
        rows.append({
            "Category": kpi["category"],
            "KPI": kpi["name"],
            "Measured Value": ("" if ev is None or ev["measured"] is None else ev["measured"]),
            "Expected Value": kpi["pass_condition"],
            "Status": (ev["state"] if ev else ""),
            "Severity": (ev["severity"] if ev else ""),
            "Required Tier": kpi["required_tier"],
            "Certification Impact": _certification_impact(kpi),
            "Fail Action": kpi["automatic_fail_action"],
            "Operator Notes": "",
            "Timestamp": (result.timestamp if result else ""),
            "Operator": (context.get("operator_id", "") if result else ""),
        })
    return rows


def write_checklist_csv(
    path: Path, schema: dict, result: Optional[CQSResult] = None,
    context: Optional[dict] = None,
) -> None:
    rows = build_checklist_rows(schema, result, context)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# Markdown report generation
# --------------------------------------------------------------------------- #
_STATE_BADGE = {"green": "🟢 GREEN", "amber": "🟡 AMBER", "red": "🔴 RED",
                "critical": "⛔ CRITICAL", "missing": "❓ MISSING"}


def _fmt(value: Any, units: str) -> str:
    """Render a measured/threshold value for a report cell."""
    if value is None:
        return "—"
    if units == "boolean":
        return "yes" if bool(value) else "no"
    return f"{value} {units}"


def render_report_markdown(result: CQSResult, schema: dict, context: Optional[dict] = None) -> str:
    context = context or {}
    cert = result.certification.upper()
    accepted = result.certification != "fail"
    lines: list[str] = []
    a = lines.append

    a("# Capture Quality Report")
    a("")
    a("> Generated by the Capture Acceptance Framework (Part 35). Authoritative logic: "
      "`backend/app/capture_quality.py`; schema: `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json`. "
      "Certification uses the **lowest required sub-score** (no averaging, Part 10 / 34.AL).")
    a("")
    a("## Acceptance decision")
    a("")
    a(f"- **Decision:** {'✅ ACCEPTED' if accepted else '❌ NOT ACCEPTED'}")
    a(f"- **Certification:** **{cert}** ({schema['certification_levels'].get(result.certification, {}).get('label', '-')})")
    a(f"- **Capture tier:** {result.capture_tier}")
    a(f"- **Reliability status:** {result.reliability_level}")
    a(f"- **Overall dashboard state:** {_STATE_BADGE.get(result.overall_state, result.overall_state)}")
    a(f"- **Effective score (governing):** {result.effective_score:.3f}")
    a(f"- **Overall score (informational only):** {result.overall_score:.3f}")
    a(f"- **Target certification:** {result.target_certification}")
    a(f"- **Timestamp:** {result.timestamp}")
    a("")
    if not accepted or result.effective_score < result.overall_score:
        a(f"> Note: the informational average ({result.overall_score:.3f}) is higher than the "
          f"governing effective score ({result.effective_score:.3f}). Per the safety-critical "
          f"policy, the average is **not** used — the lowest required gate governs.")
        a("")

    a("## Certification ladder")
    a("")
    a("| Level | Passed | Effective | Min required | Hard reqs | Failing gates |")
    a("|-------|--------|-----------|--------------|-----------|---------------|")
    for lvl in LEVELS_HIGH_TO_LOW:
        pl = result.per_level[lvl]
        a(f"| {lvl.capitalize()} | {'✅' if pl['passed'] else '❌'} | {pl['effective_score']:.3f} | "
          f"{pl['min_effective_score']:.2f} | {'✅' if pl['hard_requirements_ok'] else '❌'} | "
          f"{', '.join(pl['failed_gate_kpis']) or '—'} |")
    a("")

    a("## Failed gates")
    a("")
    if result.failed_gates:
        a("| KPI | Reason | Measured | Threshold | Severity | Corrective action | Auto action | Retry |")
        a("|-----|--------|----------|-----------|----------|-------------------|-------------|-------|")
        for g in result.failed_gates:
            a(f"| {g['name']} | {g['reason']} | {_fmt(g['measured'], g['units'])} | "
              f"{_fmt(g['threshold'], g['units'])} | {g['severity']} | {g['corrective_action']} | "
              f"{g['automatic_fail_action']} | {'yes' if g['auto_retry_allowed'] else 'no'} |")
    else:
        a("None — all mandatory gates for the target certification pass.")
    a("")

    a("## Warnings")
    a("")
    if result.warnings:
        for w in result.warnings:
            a(f"- 🟡 {w['note']}")
    else:
        a("None.")
    a("")

    a("## Recommended actions")
    a("")
    if result.recommended_actions:
        for i, act in enumerate(result.recommended_actions, 1):
            a(f"{i}. {act}")
    else:
        a("None.")
    a("")

    a("## All KPI values & sub-scores")
    a("")
    a("| Category | KPI | Measured | Pass threshold | State | Sub-score |")
    a("|----------|-----|----------|----------------|-------|-----------|")
    for kpi in schema["kpis"]:
        ev = result.subscores[kpi["id"]]
        a(f"| {ev['category']} | {ev['name']} | {_fmt(ev['measured'], ev['units'])} | "
          f"{_fmt(ev['threshold'], ev['units'])} | {_STATE_BADGE.get(ev['state'], ev['state'])} "
          f"| {ev['subscore']:.2f} |")
    a("")

    a("## Reliability envelope (Part 10)")
    a("")
    a("```json")
    a(json.dumps(result.reliability_envelope, indent=2, default=str))
    a("```")
    a("")

    a("## Provenance (Part 34.AK)")
    a("")
    a("```json")
    prov_view = {k: v for k, v in result.provenance.items() if k != "measurements"}
    a(json.dumps(prov_view, indent=2, default=str))
    a("```")
    a("")

    a("## Sign-off")
    a("")
    a(f"- **Operator:** {context.get('operator_id', '________________')}")
    a("- **Operator signature:** ____________________________")
    a(f"- **Decision:** {'ACCEPTED at ' + cert if accepted else 'NOT ACCEPTED'}")
    a(f"- **Timestamp:** {result.timestamp}")
    a(f"- **Provenance hash:** `{result.provenance['hash']}`")
    a("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Example data (used to generate the committed example report)
# --------------------------------------------------------------------------- #
EXAMPLE_MEASUREMENTS: dict[str, Any] = {
    "resolution": 2160, "frame_rate": 120, "shutter": 0.8, "motion_blur": 0.4,
    "exposure_lock": True, "white_balance_lock": True, "lens_calibration": True,
    "reprojection_error_px": 0.4, "reconstruction_error_mm": 8.0, "calibration_age": 6.0,
    "synchronization_error": 0.9, "time_synchronization": True,
    "frame_accurate_timestamps": False, "camera_drift": 0.5, "dropped_frames": 0.02,
    "lighting_uniformity": 0.85, "lux": 1200, "flicker": 2.0, "glare": True,
    "color_temperature": 150, "occlusion": 4.0, "ball_visibility": 97.0,
    "tracking_success": 96.0, "storage_health": 60.0, "battery": 80.0,
    "temperature": 45.0, "camera_stability": 0.5, "coverage_volume": 100.0,
    "overlap_pct": 60.0, "network_latency": 80.0, "packet_loss": 0.02, "jitter": 5.0,
    "secure_network_isolation": False, "metadata_completeness": 100.0,
    "provenance": True, "tamper_evidence": False, "ground_truth_status": False,
    "versioned_calibration": True, "global_shutter": False, "environmental_sensors": True,
}
EXAMPLE_CONTEXT: dict[str, Any] = {
    "session_id": "sess-2026-0001",
    "calibration_version": "cal-2026-06-28-001",
    "camera_ids": ["cam-A", "cam-B", "cam-C"],
    "camera_firmware": {"cam-A": "1.4.2", "cam-B": "1.4.2", "cam-C": "1.4.2"},
    "capture_settings": {"fps": 120, "resolution": "3840x2160", "shutter_ms": 0.8},
    "operator_id": "op-117",
    "device": "capture-pc-01",
    "environment": {"temperature_c": 24.0, "humidity_pct": 45.0},
    "evidence_chain": [],
    "capture_tier": "T3",
    "software_version": "tt-os-backend@0.1.0",
    "model_version": "cv-baseline@0.1.0",
}


# --------------------------------------------------------------------------- #
# CLI: generate the checklist CSV + example report from the schema
# --------------------------------------------------------------------------- #
def generate_artifacts(schema: Optional[dict] = None, out_dir: Optional[Path] = None) -> dict[str, Path]:
    schema = schema or load_schema()
    out_dir = out_dir or (_repo_root() / "MASTER_SPEC")
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / CHECKLIST_FILENAME
    write_checklist_csv(csv_path, schema)  # blank operator template

    # Deterministic timestamp for a reproducible committed example.
    result = compute_cqs(
        EXAMPLE_MEASUREMENTS, context=EXAMPLE_CONTEXT, schema=schema,
        now=datetime(2026, 6, 28, 12, 0, 0, tzinfo=timezone.utc),
    )
    report_path = out_dir / REPORT_FILENAME
    report_path.write_text(render_report_markdown(result, schema, EXAMPLE_CONTEXT), encoding="utf-8")
    return {"csv": csv_path, "report": report_path}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Capture Acceptance Framework")
    parser.add_argument("--generate", action="store_true",
                        help="(re)generate the checklist CSV + example report from the schema")
    parser.add_argument("--schema", default=None, help="path to the acceptance schema JSON")
    parser.add_argument("--measurements", default=None,
                        help="path to a measurements JSON file to score")
    args = parser.parse_args(argv)

    schema = load_schema(args.schema)
    if args.generate:
        paths = generate_artifacts(schema)
        print(f"wrote {paths['csv']}")
        print(f"wrote {paths['report']}")
        return 0
    if args.measurements:
        data = json.loads(Path(args.measurements).read_text(encoding="utf-8"))
        result = compute_cqs(data.get("measurements", data),
                             context=data.get("context"), schema=schema)
        print(json.dumps(result.to_dict(), indent=2, default=str))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
