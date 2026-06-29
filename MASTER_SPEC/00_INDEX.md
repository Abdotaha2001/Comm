# 🏓 TT-OS — World-Class AI Table Tennis Platform · MASTER SPECIFICATION

> **ملاحظة (بالعربي):** ده مرجع حيّ متقسّم لأجزاء مترابطة. كل ملف بيخلص بإسم الملف اللي بعده عشان تكمل بالترتيب.
> الهدف: تحويل مشروع `TT ANALYSIS` (نوتبوك تحليل ماتش فردي) إلى **نظام تشغيل متكامل لكرة الطاولة** بمستوى الاتحاد الدولي (ITTF) واللجان الأولمبية والمنتخبات والأكاديميات.

This document is the single source of truth for **everything the platform must contain**. It is written as a directive specification (prompt-style) so it can be fed to engineers or AI agents part-by-part.

> ⭐ **Flagship product loop (Part 17):** a persistent profile for every player (pro/junior) built from their own videos, plus a "send me the opponent → here's how this player beats them" game-plan generator. It is the headline feature coaches buy the platform for; it composes Parts 04, 07, 08, 10, 11 into one workflow.

---

## 0. How to read this spec (the chain)

Read the files **in order**. Each part ends with a `➡️ NEXT FILE:` pointer. Do not stop until you reach `16_VALIDATION_EFFICACY_AND_ROADMAP.md`.

| # | File | Domain |
|---|------|--------|
| 00 | `00_INDEX.md` | Overview, legend, architecture concept (this file) |
| 01 | `01_COMPUTER_VISION.md` | Detection, tracking, table/net/racket, occlusion, calibration |
| 02 | `02_CAPTURE_TIERS_AND_3D.md` | Single-camera, multi-camera 3D, sync, triangulation |
| 03 | `03_BALL_INTELLIGENCE.md` | Speed, spin, trajectory, bounce, landing prediction, aero |
| 04 | `04_PLAYER_REID_AND_IDENTITY.md` | Face/body/skeleton/style ReID, handedness, grip, player passport |
| 05 | `05_STROKE_SPIN_FOOTWORK.md` | Full stroke taxonomy, stroke quality, spin & footwork engines |
| 06 | `06_BIOMECHANICS_AND_SPORTS_SCIENCE.md` | Kinetic chain, fatigue, injury, load, asymmetry |
| 07 | `07_TACTICAL_AND_OPPONENT_AI.md` | Patterns, sequence mining, win-prob, scouting, psychology |
| 08 | `08_COACHING_AND_TALENT.md` | Periodization, plans, drills, talent-development framework |
| 09 | `09_RULES_UMPIRE_SCORE.md` | ITTF rules engine, scoreboard OCR, doubles/para/team, authority |
| 10 | `10_RELIABILITY_AWARENESS.md` | Confidence, calibration, abstention, graceful degradation |
| 11 | `11_KNOWLEDGE_AND_EXPERT_SYSTEM.md` | Knowledge graph, causal/expert engine, NL Q&A |
| 12 | `12_DATA_AND_ML_INFRA.md` | Datasets, annotation, synthetic data, MLOps, edge optimization |
| 13 | `13_PLATFORM_ARCHITECTURE.md` | Engines, APIs, DB schema, multi-tenancy, streaming, DR |
| 14 | `14_INTEGRATIONS_MEDIA_ENGAGEMENT.md` | Audio, equipment, IoT/robots, broadcast, AR/VR, fan products |
| 15 | `15_FEDERATION_OPS_AND_GOVERNANCE.md` | Federation mgmt, logistics, integrity, privacy, sustainability |
| 16 | `16_VALIDATION_EFFICACY_AND_ROADMAP.md` | Testing, efficacy proof, metrics, final roadmap |
| 17 | `17_FLAGSHIP_PLAYER_PROFILE_AND_GAMEPLAN.md` | ⭐ Flagship: player profiles + "how to beat your opponent" game plan |
| 18 | `18_MODEL_CATALOG_EVERYTHING_IS_AI.md` | Model catalog — every capability is its own dedicated trained AI (~47 models) |
| 19 | `19_DOMAIN_KNOWLEDGE_RULES_SKILLS_AND_MATH.md` | Official ITTF rules + full skill taxonomy + the physics & ML equations |
| 20 | `20_EQUIPMENT_INTELLIGENCE.md` | Rubbers/sponge/pips/blades — equipment as a mandatory spin prior |
| 21 | `21_TACTICAL_SYSTEMS_AND_MATCH_STRATEGY.md` | Serve+3rd-ball systems + how-to-beat-each-style playbook (grounds M35/M36) |
| 22 | `22_TRAINING_DRILLS_AND_METHODOLOGY.md` | Drill library + multiball + motor-learning methodology (grounds M43 / Part 08) |
| 23 | `23_ATHLETE_DEVELOPMENT_PHYSICAL_AND_MENTAL.md` | LTAD stages + windows of trainability + physical conditioning + mental training |
| 24 | `24_PARA_TABLE_TENNIS_CLASSIFICATION.md` | Para classes 1–11 + impairment types + rules + assign-a-disability-to-any-player |
| 25 | `25_ANATOMY_AND_MOVEMENT_DYNAMICS.md` | Anatomy, kinetic chain, joint actions & full-body stroke biomechanics |
| 26 | `26_EXISTING_ASSETS_PRETRAINED_AND_DATASETS.md` | ⭐ Reuse map: open pretrained models, datasets & repos (TTNet/TrackNet/SpinDOE/TTStroke-21…) |
| 27 | `27_DATA_MODEL_AND_API_CONTRACT.md` | 🔧 Build artifact: DB schema + REST API + reliability envelope (→ `schema/`, `api/`) |
| 28 | `28_ONTOLOGY_AND_GLOSSARY.md` | EN↔AR controlled vocabulary: entity/event taxonomy + full bilingual term glossary |
| 29 | `29_EVALUATION_METRICS_CATALOG.md` | Per-model metric · target · eval set · golden-set gate (enforced by `backend/app/benchmark.py`) |
| 30 | `30_ANNOTATION_LABELING_PROTOCOL.md` | How to label every data type + rubrics + inter-annotator agreement gate |
| 31 | `31_SECURITY_PRIVACY_THREAT_MODEL.md` | Data classification, auth/tenancy, privacy/consent, STRIDE+ML threat model |
| 32 | `32_PRODUCT_UX_AND_USER_JOURNEYS.md` | Personas, core journeys, screen map, UX principles, screen→API map |
| 33 | `33_COMPETITIVE_LANDSCAPE.md` | Existing products (Stupa/OSAI/Dartfish/SmartScorer), capability matrix, our wedge |
| 34 | `34_ENGINEERING_CONVENTIONS.md` | Code/API/DB/test/CV/git conventions (quick-start in root `CLAUDE.md`) |
| 35 | `35_HARDWARE_AND_CAPTURE_SOP.md` | Camera/lighting/calibration setup per tier + pre-session checklist + metadata |
| 36 | `36_RISK_REGISTER_AND_ASSUMPTIONS.md` | Living risk register (L/I/mitigation) + the assumptions we're betting on |
| 37 | `37_DATA_MODEL_AND_API_CONTRACT_BUILD_SPEC.md` | 🔧 Authoritative backend build spec: domain model · schema · API/event contracts · traceability · governance (RFC-style; supersedes Part 27 for build) |
| 38 | `38_ONTOLOGY_AND_GLOSSARY_CANONICAL.md` | 🔧 Authoritative ontology & controlled vocabulary: canonical_ids · entity/event/stroke/spin/pose/equipment/AI ontologies · KG relationships · EN↔AR glossary (184 terms; supersedes Part 28 for semantics; SoT `i18n/glossary.json`) |
| 39 | `39_EVENT_CONTRACT_AND_EVENT_DRIVEN_ARCHITECTURE.md` | 🔧 Authoritative event contract: canonical envelope · full event catalog · transactional outbox · delivery/ordering/idempotency · webhooks · audit/officiating integrity · governance (third build pillar after 37/38) |
| 40 | `40_RELIABILITY_CONFIDENCE_AND_CALIBRATION.md` | 🔧 Authoritative reliability law: reliability envelope · calibrated-confidence semantics · abstention policy · uncertainty propagation (no averaging) · capture-tier cap · calibration (ECE/PICP) gates · governance (formalizes Part 10) |

---

## 1. Legend (used in every part)

**Priority**
- 🔴 **CRITICAL** — the world-class vision is impossible without it.
- 🟠 **IMPORTANT** — needed for a credible production platform.
- 🟡 **ENHANCEMENT** — differentiator / long tail.

**Complexity (effort):** `S` (days) · `M` (weeks) · `L` (1–3 months) · `XL` (quarter+ / research).

**Capture Tier** (where a capability becomes possible):
- `T1` Single camera 2D · `T2` Single camera + 3D-lift · `T3` Multi-camera true 3D.

**Status (to be tracked):** `MISSING` · `WIP` · `DONE`.

---

## 2. Core architectural concept (read before everything)

The platform is **not** a video analyzer. It is a federation of independent **engines** coordinated by an **event bus**, with two cross-cutting layers that touch every other engine:

1. **Capture-Tier Awareness** — the system always knows whether it is running on `T1`, `T2`, or `T3`, and adjusts which outputs it is allowed to produce and at what confidence.
2. **Reliability Awareness** — every single number the platform emits carries a calibrated confidence and provenance, and the platform can say **"I don't know"** and escalate to a human.
3. **Everything-is-a-Model** — every engine is backed by its own **dedicated, fully-trained AI model**, never heuristics. Heuristics exist only as labeled-confidence fallbacks until each model reaches target accuracy. Built feasibly via foundation models + fine-tuning + shared backbones + self-supervision + synthetic data. See **Part 18** for the full ~47-model catalog.

```
            ┌──────────────── RELIABILITY AWARENESS (layer) ────────────────┐
            │                                                                │
 Capture →  CV → Ball → ReID → Stroke/Spin/Footwork → Biomech → Tactical →   │
            Rules/Umpire → Coaching → Knowledge Graph → Expert System →      │
            Reports / APIs / UI / Federation Ops                             │
            │                                                                │
            └──────────────── CAPTURE-TIER AWARENESS (layer) ───────────────┘
```

---

## 3. Current baseline (what exists today — V21.0.0)

A single Colab notebook: YOLO11 detection + IoU/ReID tracking, homography table, hybrid ball detector + Kalman, a 12-guard game state machine with heuristic ITTF detectors, a shallow pose/shot classifier (~8 stroke types), rule-based coaching/training templates, charts, and a results.json. **Estimated coverage of the full vision: ~15%.** Everything beyond that is specified in parts 01–16.

---

➡️ **NEXT FILE: `01_COMPUTER_VISION.md`**
