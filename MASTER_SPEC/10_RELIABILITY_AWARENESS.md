# PART 10 — RELIABILITY AWARENESS (cross-cutting layer)

> Read `00_INDEX.md` first. This layer touches **every** engine. It is what separates a demo from an officiating-grade system.

## Purpose
The platform must know how reliable it is, communicate it on every output, degrade gracefully, and be able to say **"I don't know"** and escalate to a human.

## Missing components

| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 10.1 | Per-decision confidence on every output (not just final score) | 🔴 | M |
| 10.2 | **Confidence calibration** (90% means right 90% of the time) | 🔴 | L |
| 10.3 | **Abstention** ("I don't know") + human escalation below threshold | 🔴 | M |
| 10.4 | Confidence **intervals** instead of point estimates | 🔴 | S |
| 10.5 | **Input Quality Score** (res/fps/angle/lighting/occlusion%) pre-run | 🔴 | M |
| 10.6 | **Graceful degradation** chains (ball lost / occlusion / feed drop) | 🔴 | L |
| 10.7 | Reliability-mode declaration to user ("low reliability because …") | 🟠 | S |
| 10.8 | Real-time per-engine self-health diagnostics | 🟠 | M |
| 10.9 | Accuracy estimation **without** ground truth (consistency checks) | 🟠 | L |
| 10.10 | **Cross-signal validation** (OCR vs computed score, etc.) | 🔴 | M |
| 10.11 | Provenance per number (which signals + their confidence) | 🟠 | M |
| 10.12 | Failure-mode taxonomy + detection | 🟠 | M |
| 10.13 | Match Reliability Index (overall trust budget) | 🟠 | M |
| 10.14 | Pre-publish reliability gate (no report below threshold) | 🟠 | M |
| 10.15 | Operator reliability dashboard (live) | 🟡 | M |
| 10.16 | Feed dropout/latency detection + recovery | 🟠 | M |
| 10.17 | Drift detection per venue/lighting + alerting | 🟠 | M |
| 10.18 | **Golden test set** (officiating models must never regress) | 🔴 | M |
| 10.19 | Explainability + **model cards** (legal defensibility of calls) | 🔴 | L |
| 10.20 | AI transparency reports for regulators | 🟠 | M |
| 10.21 | Capture-tier-aware claim limiting (T1 can't claim 16cm toss) | 🔴 | S |

## Design principle
Every value leaving any engine is a tuple: `{value, confidence, interval, provenance, tier, reliability_flag}`. The UI and APIs render these honestly; officiating refuses to emit decisive calls outside the allowed tier/confidence.

---

➡️ **NEXT FILE: `11_KNOWLEDGE_AND_EXPERT_SYSTEM.md`**
