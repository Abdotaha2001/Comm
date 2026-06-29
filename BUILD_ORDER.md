# 🧭 BUILD ORDER — what to do, in order

> Companion to `PROJECT_PLAN.md` and `MASTER_SPEC/`. The MASTER_SPEC files are numbered **00–26 by topic (reading order)**; this file re-ranks them **1..27 by build order** (when you actually engage each one). Tailored to the **2-person** plan (reuse-first, single camera, Wave-1 models).
>
> **Type:** 🔧 build (write code) · 📖 ground (reference that grounds a model/logic) · ⚙️ cross-cutting (touches everything).

## PHASE 0 — Foundation
| # | File | Type | Why now |
|---|------|------|---------|
| **1** | `PROJECT_PLAN.md` | ⚙️ | the driver — milestones, KPIs, 2-person mode. Read first. |
| **2** | `MASTER_SPEC/26` Existing assets | 📖 | decide **what to reuse before writing anything** (TTNet, TrackNet, OpenTTGames…). Saves months. |
| **3** | `MASTER_SPEC/13` Platform architecture | 🔧 | scaffold: modules, Postgres schema, API, GPU worker, storage. |
| **4** | `MASTER_SPEC/10` Reliability awareness | ⚙️ | v0 from day one — every output gets `{value, confidence, provenance}`. |
| **5** | `MASTER_SPEC/19` Rules + skills + math | 📖 | ground truth for labels, scoring logic, equations. |

## PHASE 1 — Flagship MVP + Wave-1 models
| # | File | Type | Why now |
|---|------|------|---------|
| **6** | `MASTER_SPEC/17` Flagship profile + game plan | 🔧 | the product spine: player profiles → opponent → game plan. |
| **7** | `MASTER_SPEC/18` Model catalog | 📖 | pick the **Wave-1** subset to build/fine-tune. |
| **8** | `MASTER_SPEC/01` Computer vision | 🔧 | ball / player / pose / table / net (start from reused models). |
| **9** | `MASTER_SPEC/09` Rules / umpire / score | 🔧 | **Scoreboard OCR** quick win + scoring + cross-check. |
| **10** | `MASTER_SPEC/04` ReID / identity | 🔧 | player DB + **handedness/grip**. |
| **11** | `MASTER_SPEC/05` Stroke / spin / footwork | 🔧 | Wave-1 stroke classifier (TTStroke-21). |
| **12** | `MASTER_SPEC/20` Equipment | 📖 | mandatory **spin prior** (long pips/anti reversal). |
| **13** | `MASTER_SPEC/21` Tactics | 📖 | grounds the **game-plan generator (M36)**. |
| **14** | `MASTER_SPEC/07` Tactical / opponent AI | 🔧 | matchup model + scouting. |
| **15** | `MASTER_SPEC/08` Coaching / talent | 🔧 | training plans + talent stages. |
| **16** | `MASTER_SPEC/22` Drills & methodology | 📖 | grounds the **drill recommender (M43)**. |

## PHASE 2 — Accuracy & Physics (Wave-2)
| # | File | Type | Why now |
|---|------|------|---------|
| **17** | `MASTER_SPEC/02` Capture tiers & 3D | 🔧 | single→multi-camera, calibration, triangulation. |
| **18** | `MASTER_SPEC/03` Ball intelligence | 🔧 | **spin** (SpinDOE), true trajectory, landing. |
| **19** | `MASTER_SPEC/25` Anatomy & biomechanics | 📖 | grounds the biomech model (M27) + injury (M29). |
| **20** | `MASTER_SPEC/06` Biomechanics & sports science | 🔧 | kinetic chain, fatigue, injury, load. |
| **21** | `MASTER_SPEC/12` Data & ML infra | 🔧 | datasets, annotation, synthetic, benchmark, MLOps (ramps here). |

## PHASE 3 — Intelligence (Wave-3)
| # | File | Type | Why now |
|---|------|------|---------|
| **22** | `MASTER_SPEC/11` Knowledge graph + expert system | 🔧 | the reasoning brain (grounded LLM). |
| **23** | `MASTER_SPEC/23` LTAD / physical / mental | 📖 | grounds talent standards + junior pathway. |
| **24** | `MASTER_SPEC/14` Integrations / media | 🔧 | audio, robots, broadcast, highlights, AR/VR. |

## PHASE 4 — Officiating, Federation & Inclusion (Wave-4)
| # | File | Type | Why now |
|---|------|------|---------|
| **25** | `MASTER_SPEC/24` Para classification | 🔧 | inclusive profiles + per-class rules/movement. |
| **26** | `MASTER_SPEC/15` Federation ops & governance | 🔧 | multi-tenant, tournaments, integrity, privacy. |
| **27** | `MASTER_SPEC/16` Validation & efficacy | ⚙️ | tests + accuracy + causal-impact proof (ongoing, formalized here). |

## Always-on
| # | File | Type | Note |
|---|------|------|------|
| **0** | `MASTER_SPEC/00` Index | 📖 | map + the 3 design laws; keep open throughout. |

---

### Why I did NOT renumber the files
The MASTER_SPEC numbering (00–26) is a **reading order** and the files cross-reference each other (chain pointers, `Part 18`, model IDs `M1…M47`). Renumbering would break all of that. This `BUILD_ORDER.md` gives the **execution priority** without touching the spec — the correct practice for a cross-referenced spec.

### Start here
Build-order **#3 + #9**: scaffold the project & DB (Phase-0) and prototype **Scoreboard OCR** (the fastest reliability win). Those two unblock everything after.
