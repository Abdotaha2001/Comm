# PART 29 — EVALUATION METRICS CATALOG

> Read `00_INDEX.md` first. The **measurement contract**: every model (Part 18) and capability has a defined **metric · target · eval dataset (Part 26) · acceptance gate**. This is what makes "measure before you trust" (Part 10) concrete and what the **benchmark harness** (`backend/app/benchmark.py`) + golden-set tests (`backend/tests/test_benchmark.py`) enforce in CI.

## A. Principles
- **One primary metric per model** (+ secondary diagnostics). No model ships without a target met on a held-out set.
- **Golden-set regression gate:** the metric may **never silently drop** — CI fails if it does (Part 10.18).
- **Calibration is a first-class metric** for any confidence that drives a decision (ECE ≤ 0.05).
- **Abstention-aware:** officiating models are scored *with* an "I don't know" option; a wrong confident call is worse than an abstention.
- **Per capture-tier:** speed/spin/3D targets apply only at the tier that supports them (T2/T3); T1 reports wider intervals.

## B. Metric definitions (glossary)
| Metric | Used for | Definition |
|--------|----------|-----------|
| **mAP@0.5 / IoU** | detection | mean average precision at IoU 0.5 |
| **Localisation RMSE (px)** | ball/keypoints | root-mean-square centre error vs GT |
| **MOTA / IDF1** | tracking | multi-object tracking accuracy / identity F1 |
| **Event F1 (±k frames)** | bounce/hit/serve | F1 with temporal tolerance of k frames |
| **Top-1 / macro-F1** | classification (stroke/spin/style) | accuracy / class-balanced F1 |
| **MAE / RMSE** | regression (speed/RPM/angle) | mean / root-mean-square error |
| **Exact-match / per-digit acc** | scoreboard OCR | whole-score and per-digit accuracy |
| **ECE** | calibration | expected calibration error |
| **Brier / log-loss** | win-probability | proper scoring rule |
| **Cohen's κ / agreement** | officiating | agreement with human expert |
| **PCK@0.2 / MPJPE** | pose 2D / 3D | % correct keypoints / mean joint position error |

## C. Per-model catalog (targets to clear before production)
Grouped by Part 18 model IDs. Datasets reference Part 26.

### Perception
| Model | Primary metric | Target | Eval set |
|-------|----------------|--------|----------|
| M1 ball detector | mAP@0.5 · loc-RMSE | ≥ 0.90 · ≤ 3 px | OpenTTGames / Roboflow |
| M2 ball tracker | **HOTA** · IDF1 · MOTA | ≥ 0.75 · ≥ 0.85 · ≥ 0.80 | OpenTTGames |
| M3 player detector | mAP@0.5 | ≥ 0.95 | COCO-person + TT |
| M4 2D pose | PCK@0.2 | ≥ 0.90 | TT pose set |
| M5 3D pose | MPJPE | ≤ 30 mm | multi-cam (T3) |
| M6 segmentation (table/net/score) | mIoU | ≥ 0.90 | OpenTTGames masks |
| M8 bounce | Event F1 (±2f) | ≥ 0.90 | OpenTTGames events |
| M9 hit | Event F1 (±2f) | ≥ 0.85 | TTStroke-21 |

### Ball physics
| Model | Primary metric | Target | Eval set |
|-------|----------------|--------|----------|
| M12 spin type | macro-F1 | ≥ 0.80 | SpinDOE + labelled |
| M13 spin RPM · **axis** | RPM MAE · axis angular err | ≤ 5 rps · ≤ 10° | SpinDOE (high-speed GT) |
| M14 speed | MAE | ≤ 5 km/h (T2/T3) | calibrated rig |
| M11 landing predictor | MAE (cm) | ≤ 10 cm | 3D track set |

### Technique / identity
| Model | Primary metric | Target | Eval set |
|-------|----------------|--------|----------|
| M22–M24 stroke class | top-1 · macro-F1 | ≥ 0.85 · ≥ 0.80 | TTStroke-21 |
| M25 stroke quality | corr. vs expert | ρ ≥ 0.7 | expert-rated (Part 16) |
| M26 footwork | macro-F1 | ≥ 0.80 | footwork set |
| M16 ReID | rank-1 · mAP | ≥ 0.90 · ≥ 0.80 | multi-match ReID |
| M18 handedness | accuracy | ≥ 0.98 | labelled |
| M19 grip | top-1 | ≥ 0.90 | labelled |
| M34 style class | top-1 | ≥ 0.75 | labelled matches |

### Tactical / coaching
| Model | Primary metric | Target | Eval set |
|-------|----------------|--------|----------|
| M32 win-probability | Brier · ECE | ≤ 0.18 · ≤ 0.05 | match outcomes |
| M35 matchup | ranking acc | ≥ 0.65 | historical H2H |
| M36 game-plan | expert usefulness | ≥ 4/5 rating | coach panel (Part 16) |
| M43 drill recommender | precision@3 | ≥ 0.80 | expert-labelled |

### Officiating (higher bars + abstention + human agreement)
| Model | Primary metric | Target | Eval set |
|-------|----------------|--------|----------|
| M38 illegal serve | precision · recall · κ vs umpire | ≥ 0.99 · ≥ 0.90 · ≥ 0.90 | umpire-annotated (T3) |
| M39 edge/net ball | precision · recall | ≥ 0.98 · ≥ 0.95 | annotated |
| M40 violations | precision | ≥ 0.98 | annotated |
| M41 scoreboard OCR | per-digit · exact-match | ≥ 0.99 · ≥ 0.98 | scoreboard set |

> Officiating models **must** prefer **abstain → human** over a wrong confident call; every decisive call carries calibrated confidence and an evidence package (Part 09).

## D. Cross-cutting metrics
| Metric | Applies to | Target |
|--------|-----------|--------|
| **ECE (calibration)** | any decision-driving confidence | ≤ 0.05 |
| **Reliability index** | per analysis run | reported; gate report below threshold |
| **Input-quality score** | pre-run | gate processing below threshold |
| **End-to-end latency** | real-time officiating | < 33 ms/frame (T3 live) |
| **Throughput** | batch | ≥ 1× real-time per GPU worker |
| **Determinism** | reproducibility | identical results on re-run (Part 13.4) |

## E. Efficacy metrics (does it actually help — Part 16)
| Metric | Definition |
|--------|-----------|
| **Plan→outcome effectiveness** | win-rate change after following the game plan |
| **Causal impact (RCT-style)** | improvement vs control over a training block |
| **Metric validity** | correlation of platform scores with expert judgement |

## F. Regression gate & cadence
- **Gate:** every model's primary metric has a golden test set; CI runs it; a drop **fails the build**.
- **Cadence:** re-evaluate on each model change; full benchmark on each release; track in an experiment registry (Part 12).
- **Executable today:** `backend/app/benchmark.py` measures ball detection + scoreboard OCR; `tests/test_benchmark.py` is the live gate.

## G. Measured now (scaffold baseline — honest)
| Capability | Metric | Measured | Note |
|-----------|--------|----------|------|
| Ball detection (OpenCV baseline) | detection-rate · loc-error | **1.0 · 0.0 px** | on synthetic clips (clean); real footage will be lower → deep model (M1) |
| Scoreboard OCR (7-seg) | exact-match | **100%** | synthetic 7-seg; general fonts need a deep OCR model |
| Spin estimator | physics validation | **correct sign/type** | crafted arcs; uncalibrated, conf ≤ 0.5 |
| Game plan | generated + evidence-cited | ✅ | rule-based; needs coach-panel usefulness rating |

> These baselines are **synthetic-clean** — they prove the pipeline and gate, not world-class accuracy. Real targets in §C are met by the deep models + real datasets (Part 26).

## H. Evaluation methodology (rigor)
- **Fixed train/val/test splits** per dataset; **no leakage** — the same match/player/clip never appears across splits.
- Report every metric with a **95% confidence interval** (bootstrap) **and** the sample size; don't claim an improvement whose CIs overlap.
- Small sets → k-fold cross-validation; the **golden test set is frozen** and never trained on.
- **Human ceiling:** report expert inter-rater agreement (Part 30) as the achievable upper bound — a model cannot meaningfully beat its label noise.

## I. Stratified & robustness metrics (report, don't average away)
- Break **every** metric down by condition: lighting, venue/background, **ball colour**, **occlusion / motion-blur**, capture tier, player level, **handedness/grip**, **rubber type (long-pips/anti)**, camera angle.
- Report the **worst-stratum** value, not just the mean — a healthy average can hide a fully broken condition.
- Robustness delta: clean vs degraded input (compression, blur, low light).

## J. Fairness / parity
- Performance **parity** across skin tone, body type, gender, and **para class** — max absolute gap ≤ **5%**.
- Equal abstention/error rates across groups; published fairness report (ties Part 12 bias audit).

## K. Uncertainty & calibration depth
- **Reliability diagram** + ECE/MCE per model; **per-class** calibration for classifiers.
- Regression: **prediction-interval coverage (PICP)** — a stated "78±6" must contain truth ~the claimed % of the time.
- Abstention quality: **risk–coverage curve** (accuracy vs % of cases answered).

## L. System-level (end-to-end) metrics — the real product accuracy
- **Final-score accuracy** (computed score vs scoreboard OCR / official) — cross-check (Part 09/10).
- Point-attribution accuracy · rally-segmentation F1 · event-timeline alignment to the official clock.
- **Plan→outcome effectiveness** (efficacy, Part 16) — does following the plan change results.

## M. Efficiency / cost metrics
- **Latency p50/p95/p99** per stage; throughput (× real-time per GPU); **model size**; energy & **cost per analysis**.
- Targets **per hardware tier** (phone / Jetson / server) — Part 12.

## N. Production monitoring & drift
- **Population Stability Index (PSI)** on inputs; **performance-over-time**; alert on drift (Part 10/12).
- **Champion–challenger / canary** with shadow evaluation before any promotion; online metrics tracked.

## O. Release gate (ship only if ALL hold)
1. Primary metric ≥ target **on the frozen test set**, within CI.
2. **No stratum** below its floor (§I); fairness gap within bound (§J).
3. Calibration ECE ≤ 0.05; latency within the tier budget (§M).
4. Golden-set regression green; **model card + eval report** attached.
5. **Officiating only:** human-agreement κ ≥ target **and** the abstain→human path verified.

---

➡️ **NEXT FILE: `30_ANNOTATION_LABELING_PROTOCOL.md`**
