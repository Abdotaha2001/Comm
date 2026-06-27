# PART 26 — EXISTING OPEN ASSETS TO REUSE (PRETRAINED MODELS · DATASETS · REPOS)

> Read `00_INDEX.md` first. **For a 2-person team this is the most important part of the whole spec:** almost every Wave-1 capability already exists as open code/data. **Reuse and fine-tune — do not build from scratch.** Each asset is mapped to the Model Catalog (Part 18).

## A. Table-tennis-specific datasets
| Dataset | What it gives | Feeds (Part 18) | Link |
|---------|---------------|-----------------|------|
| **OpenTTGames** (OSAI) | Full-HD **120 fps** TT videos; **ball coordinates**, **events** (bounce / net), **segmentation** (players/table/**scoreboard**). 5 train + 7 test. | M1, M6, M8, M9, M41 | [lab.osai.ai](https://lab.osai.ai/) |
| **Extended OpenTTGames** | adds **fine-grained shot type** + **point-outcome** labels | M22–M24, M31 | [arxiv 2512.19327](https://arxiv.org/html/2512.19327v1) |
| **TTStroke-21** (Univ. Bordeaux) | **20+ stroke classes**, 120 fps, expert-annotated, natural conditions | M22–M24, M25 | [MediaEval Sport Task](https://multimediaeval.github.io/editions/2022/tasks/sportsvideo/) |
| **P2A** | **dense action detection** from broadcast TT video | M31, broadcast robustness | [P2A paper](https://www.researchgate.net/publication/362277248) |
| **SpinDOE dataset** | ball **position + spin + speed** (dotted-ball ground truth) | **M12, M13, M14** | [github cogsys-tuebingen/spindoe](https://github.com/cogsys-tuebingen/spindoe) |
| **Roboflow** TT-ball sets | ~620 TT-ball images, YOLOv5–v11 ready (varied lighting/tables) | M1 | [Roboflow Universe](https://universe.roboflow.com/madianou-kqrfk/table-tennis-ball-detection/dataset/1) |
| **Kaggle** TT ball position | ball positions, YOLOv5 format | M1 | [Kaggle](https://www.kaggle.com/datasets/ketzoomer/table-tennis-ball-position-detection-dataset) |

## B. Table-tennis-specific models & repos
| Repo / model | What it does | Feeds | Link |
|--------------|--------------|-------|------|
| **TTNet** (CVPR 2020) | multi-task: **ball detect (2px RMSE)** + **event spotting (97%)** + segmentation; **pretrained weights** | M1, M6, M8, M9 | [maudzung impl](https://github.com/maudzung/TTNet-Real-time-Analysis-System-for-Table-Tennis-Pytorch) · [demo](https://github.com/4kasha/TTNet_demo) |
| **TrackNet / V2 / V4** | heatmap-based **tiny fast-ball tracking** (handles blur/invisible) | M1, M2 | [yastrebksv/TrackNet (PyTorch, pretrained)](https://github.com/yastrebksv/TrackNet) |
| **BlurBall** | **joint ball + motion-blur** estimation for TT | M1, M2 | [arxiv 2509.18387](https://arxiv.org/pdf/2509.18387) |
| **TT3D** | **3D reconstruction** of TT (ball trajectory/table) | M5, M11, Part 02 | [arxiv 2504.10035](https://arxiv.org/pdf/2504.10035) |
| **SpinDOE** | **spin estimation** (orientation err 2.4°, spin err <1%, up to 175 rps) | M12, M13 | [github + dataset](https://github.com/cogsys-tuebingen/spindoe) |
| **TSTCNN / CRISP** | twin spatio-temporal CNN for **stroke recognition** (TTStroke-21) | M22–M24 | [github P-eMartin/CRISP](https://github.com/P-eMartin/CRISP) |
| **TennisProject / tennis-tracking** | full analogous pipelines (court, ball, players) to adapt | M1–M6, Part 02 | [yastrebksv/TennisProject](https://github.com/yastrebksv/TennisProject) · [ArtLabss/tennis-tracking](https://github.com/ArtLabss/tennis-tracking) |
| **Google DeepMind — competitive robot TT** (2024) | amateur **human-level** agent; perception + RL methods to study | M37 (sim), Part 14 robots | [project site](https://sites.google.com/view/competitive-robot-table-tennis/home) |

## C. General-purpose pretrained foundations (reuse directly)
| Asset | Use | Feeds |
|-------|-----|-------|
| **Ultralytics YOLO11** | person + sports-ball detection baseline | M1, M3 |
| **RTMPose / MMPose**, **MediaPipe BlazePose** (Google) | human 2D pose | M4 |
| **OSNet / torchreid** | person re-identification | M16 |
| **SAM / SAM2** (Meta) | zero-shot **table/net/scoreboard** segmentation | M6 |
| **ByteTrack / BoT-SORT** | multi-object tracking | M2, M3 |
| **PaddleOCR / TrOCR** | scoreboard text | M41 |

## D. Reuse map — what to start each Wave-1 model from
| Model | Start from | Then |
|-------|-----------|------|
| M1 ball detector | Roboflow/Kaggle TT-ball + YOLO11; TrackNet for tracking; **BlurBall** for blur | fine-tune on your footage |
| M4 pose | RTMPose / MediaPipe (no training) | use as-is |
| M6 segmentation | TTNet seg + **SAM**; OpenTTGames masks | fine-tune if needed |
| M8/M9 bounce/hit | **TTNet event spotting** + OpenTTGames events | fine-tune |
| M22–M24 strokes | **TTStroke-21** + TSTCNN/CRISP; Extended OpenTTGames | fine-tune to your taxonomy (Part 19) |
| M12/M13 spin | **SpinDOE** (method + data) | adapt to markerless via Magnus (Part 19 §C6) |
| M41 scoreboard | OpenTTGames scoreboard masks + PaddleOCR | wire OCR |
| 3D (Part 02) | **TT3D**, TennisProject | extend |

## E. Licensing & honest caveats (read before shipping)
- **Check each license** before *commercial* use — many datasets/repos are **research / non-commercial**. Permissive (MIT/Apache) repos are safe to build on; others need permission.
- **SpinDOE uses a dotted/marked ball** → great for **calibration & ground truth**, not directly for broadcast (markerless) spin → use it to **train/validate** the Magnus-based markerless model (Part 19 §C6).
- **OpenTTGames / TTStroke-21** are research datasets recorded in specific conditions → expect a **domain gap** vs your footage → fine-tune + active learning (Part 12).
- **Broadcast footage** of pro matches is **rights-restricted** (Part 12.10) — datasets above are licensed for research; clearing match video is separate.
- Validate every reused model on **your** held-out set before trusting it (Part 10 reliability).

## F. Recommended first pulls (P1 Wave-1, day one)
1. **TTNet (pretrained)** + **OpenTTGames** → instant ball + events + segmentation + scoreboard baseline.
2. **TrackNet** → robust ball tracking through blur/occlusion.
3. **RTMPose** + **YOLO11** → players + pose with zero training.
4. **SpinDOE** → spin ground truth to bootstrap the spin model.
5. **TTStroke-21 + CRISP** → stroke-recognition starting point.
> This stack gets a 2-person team to a working perception pipeline in **weeks, not years** — exactly the leverage the plan (PROJECT_PLAN §6.1) depends on.

## Sources
- [OpenTTGames / OSAI](https://lab.osai.ai/) · [TTNet (arxiv 2004.09927)](https://arxiv.org/pdf/2004.09927) · [TrackNet PyTorch](https://github.com/yastrebksv/TrackNet) · [TTStroke-21 / MediaEval](https://multimediaeval.github.io/editions/2022/tasks/sportsvideo/) · [SpinDOE](https://github.com/cogsys-tuebingen/spindoe) · [BlurBall](https://arxiv.org/pdf/2509.18387) · [TT3D](https://arxiv.org/pdf/2504.10035) · [DeepMind robot TT](https://sites.google.com/view/competitive-robot-table-tennis/home) · [Roboflow TT tracking](https://blog.roboflow.com/tracking-table-tennis/)

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
