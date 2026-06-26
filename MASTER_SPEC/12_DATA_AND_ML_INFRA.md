# PART 12 — DATA & ML INFRASTRUCTURE

> Read `00_INDEX.md` first. Without data and MLOps, none of the models above reach world-class accuracy.

## 12A. Datasets required (master list)
Ball tracking · Spin recognition · Stroke classification · Footwork · Biomechanics · Racket pose · Referee events · **Illegal serves** · **Scoreboards** · Player ReID · Match events · Training videos · Youth development · Handedness/grip · Equipment/rubber.

| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 12.1 | Build/acquire each dataset above with frame-accurate labels | 🔴 | XL |
| 12.2 | **Annotation tooling** specialized per task (spin labeling is hard) | 🟠 | M |
| 12.3 | Annotation **workforce mgmt** (expert tiers, QA, pay) | 🟠 | M |
| 12.4 | Inter-annotator agreement + label QA | 🟠 | M |
| 12.5 | **Synthetic data + physics simulator** (sim2real, domain randomization) | 🔴 | L |
| 12.6 | **Active learning** loop (model requests uncertain frames) | 🟠 | L |
| 12.7 | Auto-labeling / weak supervision | 🟠 | L |
| 12.8 | Data versioning (DVC) + lineage | 🟠 | M |
| 12.9 | **Bias & fairness audit** (skin tone/body/lighting/venue) | 🟠 | M |
| 12.10 | Footage **rights/licensing** acquisition (pro matches) | 🔴 | M |
| 12.11 | Historical archive digitization | 🟡 | M |
| 12.12 | **Data flywheel** design (usage → better models) | 🟠 | L |

## 12B. MLOps & model lifecycle
| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 12.13 | Training pipelines + experiment tracking + model registry | 🟠 | M |
| 12.14 | Vector DB (embeddings) + feature store | 🟠 | M |
| 12.15 | Benchmark suite + **open "TT-Bench" leaderboard** | 🟠 | M |
| 12.16 | **Canary / champion-challenger** for officiating models | 🟠 | M |
| 12.17 | Per-venue fine-tuning / adaptation | 🟠 | M |
| 12.18 | Cold-start / few-shot / long-tail strategies | 🟠 | L |
| 12.19 | Standardized evaluation protocol (links Part 16) | 🟠 | M |

## 12C. Edge & inference optimization
| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 12.20 | Model **quantization / distillation / pruning** | 🟠 | M |
| 12.21 | TensorRT/ONNX export + GPU serving (Triton) + dynamic batching | 🟠 | M |
| 12.22 | Defined **hardware tiers** (phone / Jetson / server) per capability | 🟠 | M |
| 12.23 | Edge inference box (courtside, offline) | 🟠 | L |

---

➡️ **NEXT FILE: `13_PLATFORM_ARCHITECTURE.md`**
