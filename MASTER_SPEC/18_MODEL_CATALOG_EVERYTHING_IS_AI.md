# PART 18 — MODEL CATALOG · "EVERYTHING IS A DEDICATED TRAINED AI"

> Read `00_INDEX.md` first. This part operationalizes the core directive: **every capability is backed by its own dedicated, fully-trained model — not heuristics.**

## Design principle (3rd cross-cutting law of the platform)
Every engine output comes from a **trained model**, not an if-then rule. Heuristics may exist **only** as temporary, confidence-labeled fallbacks until that capability's model reaches its target accuracy — at which point the Reliability layer (Part 10) switches to the model.

### Critical engineering nuance (read before budgeting)
"Everything is its own AI" does **not** mean 40 from-scratch models. It means:
- **Foundation models + fine-tuning** per task (don't reinvent backbones).
- **Shared video/pose backbones** feeding multiple **task heads** (stroke + spin + footwork can share features).
- **Self-supervised pretraining** on the large pool of *unlabeled* match footage.
- **Synthetic data (sim2real)** where human labels are impossible (spin/RPM, 3D trajectory).
- Per model: `dataset → train → eval → registry → canary → deploy` (Part 12 MLOps), with a **heuristic fallback + abstention** until target accuracy.

## How to read the catalog
Each model row: **In → Out · architecture family · priority.** Datasets are specified in Part 12; reliability/abstention rules in Part 10.

---

## Group A — Perception models
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M1 | TT-ball detector | frame → ball box | small-object detector (YOLO/RT-DETR) | 🔴 |
| M2 | Ball tracker | frames → track+velocity | temporal/Kalman-augmented net | 🔴 |
| M3 | Player detector | frame → player boxes | detector | 🔴 |
| M4 | 2D pose estimator | crop → keypoints | top-down pose (HRNet/RTMPose) | 🔴 |
| M5 | 3D pose lifter | 2D kpts/multi-view → 3D | lifting/transformer | 🟠 |
| M6 | Table/net/racket segmenter | frame → masks | segmentation | 🔴 |
| M7 | Racket-face pose | racket crop → face normal/angle | keypoint/regression | 🔴 |
| M8 | Bounce detector | ball track → bounce events | temporal CNN/Transformer | 🟠 |
| M9 | Hit detector | ball+pose → hit events | temporal multi-modal | 🟠 |
| M10 | Monocular depth | frame → depth (priors) | depth net | 🟠 |
| M11 | Trajectory/landing predictor | partial track → landing+ETA | sequence model | 🟠 |

## Group B — Ball physics models
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M12 | Spin-type classifier | track+racket(+audio) → spin class | multi-modal classifier | 🔴 |
| M13 | Spin-axis & RPM regressor | 3D track/high-speed → axis+RPM | regression (sim2real) | 🔴 |
| M14 | Speed/accel estimator | 3D track → m/s + interval | regression w/ uncertainty | 🟠 |

## Group C — Identity models
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M15 | Face recognition | face → embedding | metric learning | 🟠 |
| M16 | Appearance ReID | body crop → embedding | ReID (OSNet/transformer) | 🟠 |
| M17 | Skeleton/gait embedding | pose seq → embedding | ST-GCN/transformer | 🟠 |
| M18 | Handedness classifier | pose seq → L/R | sequence classifier | 🔴 |
| M19 | Grip classifier | hand/pose → grip type | classifier | 🔴 |
| M20 | Playing-style signature | match features → style embedding | representation learning | 🟠 |
| M21 | Jersey/number OCR | crop → number | scene-text recognizer | 🟡 |

## Group D — Technique models
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M22 | Serve-type classifier | clip → serve class (7+) | video classifier | 🔴 |
| M23 | Receive-type classifier | clip → receive class | video classifier | 🔴 |
| M24 | Attack/defense classifier | clip → stroke class | video classifier | 🔴 |
| M25 | Stroke-quality scorer | clip+pose → quality 0–100 | regression vs rubric | 🟠 |
| M26 | Footwork-pattern classifier | pose seq → footwork class | sequence classifier | 🟠 |

## Group E — Biomechanics & sports-science models
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M27 | Kinetic-chain model | 3D pose seq → segment sequencing | temporal regression | 🟠 |
| M28 | Fatigue detector | kinematics over time → fatigue index | sequence model | 🟠 |
| M29 | Injury-risk model | load+asym+history → risk | tabular+sequence | 🟠 |
| M30 | Movement-asymmetry model | 3D pose → L/R asymmetry | regression | 🟠 |

## Group F — Tactical & strategy AIs
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M31 | Rally/sequence model | shot sequence → embeddings/patterns | transformer | 🔴 |
| M32 | Win-probability model | match state → P(win) | sequence/Bayesian | 🟠 |
| M33 | Shot-value (xP) model | state+shot → value | regression/RL | 🟡 |
| M34 | Opponent-style classifier | opponent footage → style class | classifier | 🔴 |
| M35 | **Matchup outcome model** | (styleA, styleB, H2H) → edge map | learned ranking | 🔴 |
| M36 | **Game-plan generator** | profiles+matchup → plan | grounded LLM + RL, evidence-cited | 🔴 |
| M37 | Opponent simulator | opponent model → rally rollouts | RL/generative | 🟠 |

## Group G — Officiating & score AIs
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M38 | Illegal-serve detector | 3D serve clip → legality+reason | multi-task classifier | 🔴 |
| M39 | Edge/net-ball classifier | 3D event → class | classifier | 🟠 |
| M40 | Violation detectors (double-hit, free-hand, obstruction) | clip → violation | classifiers | 🟠 |
| M41 | Scoreboard OCR | scoreboard crop → score | scene-text/structured OCR | 🔴 |

## Group H — Knowledge, coaching & audio AIs
| # | Model | In → Out | Arch family | Priority |
|---|-------|----------|-------------|----------|
| M42 | Causal/expert reasoner | graph context → root cause+fix | grounded LLM over KG | 🔴 |
| M43 | Drill recommender | weakness → drills | learned recommender | 🟠 |
| M44 | NL Q&A | question+graph → grounded answer | RAG over KG | 🟠 |
| M45 | Talent-stage classifier | profile → stage + promotion readiness | classifier | 🟠 |
| M46 | Ball-contact audio model | audio → hit/contact-quality | audio CNN/transformer | 🟠 |
| M47 | Umpire-speech ASR | audio → calls/score | speech recognition | 🟡 |

---

## Training strategy (how all ~47 get built feasibly)
1. **Self-supervised pretraining** of a shared video backbone on unlabeled match footage → most heads fine-tune cheaply on top.
2. **Multi-task heads** off shared backbones (perception, technique) to cut data/compute.
3. **Synthetic + sim2real** for spin/trajectory/3D (M11–M14) where labels are otherwise impossible.
4. **Active learning** (Part 12) to spend labeling budget only where the model is uncertain.
5. **Per-model lifecycle:** registry + eval gate + **canary** + golden-set regression (Parts 10, 12).
6. **Fallback + abstention:** until a model hits target accuracy, the Reliability layer uses a labeled-confidence heuristic or abstains — never silently emits low-trust output.

## Sequencing (you cannot train all at once)
- **Wave 1 (unlocks the product):** M1–M4, M41 (scoreboard), M18/M19 (handedness/grip), M22–M24 (strokes).
- **Wave 2 (accuracy & physics):** M5–M14 (3D + spin), M25/M26.
- **Wave 3 (intelligence):** M31–M37 (tactical + game plan), M42–M45 (knowledge/coaching).
- **Wave 4 (officiating):** M38–M40 in 3D.

## Honest reality
Data + training for ~47 models is the **true core cost** of the platform — a multi-year, team effort. Foundation models, self-supervision, and synthetic data make it tractable; "train everything from scratch" does not. The Reliability layer is what lets you ship value **before** all models are trained, by being honest about which outputs come from a mature model vs a fallback.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
