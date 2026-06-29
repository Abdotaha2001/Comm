# PART 03 — BALL INTELLIGENCE ENGINE

> Read `00_INDEX.md` first. Spin is the soul of table tennis and is **entirely absent** today.

## Purpose
A complete physics-aware ball engine: kinematics, spin, and prediction. Today the notebook produces a roughly-calibrated speed honestly labeled "not precisely calibrated" — and nothing about spin.

## Required estimates
Speed · Acceleration · Spin · Spin axis · Spin type · Spin efficiency · Height · Trajectory · Bounce position · Impact point · **Time-to-bounce** · **Expected landing position** · Rally dynamics.

## Missing components

| # | Component | Priority | Complexity | Tier | Notes |
|---|-----------|----------|-----------|------|-------|
| 3.1 | **Spin detection** (topspin/backspin/side/cork/mixed/no-spin) | 🔴 | XL | T2/T3 | The single biggest gap in the whole platform |
| 3.2 | **Spin axis** estimation | 🔴 | XL | T3 | Direction of rotation in 3D |
| 3.3 | **RPM estimation** (high-speed cam or Magnus inference) | 🟠 | XL | T2/T3 | Wearable/IMU can ground-truth (Part 14) |
| 3.4 | Spin efficiency (energy transferred vs swing) | 🟡 | L | T3 | Elite metric |
| 3.5 | True 3D trajectory (replace pixel approximation) | 🔴 | L | T3 | Honest metric speed |
| 3.6 | **Aerodynamic model** (drag + Magnus force) | 🟠 | L | T2 | Links spin↔curvature |
| 3.7 | Ball height profile over rally | 🟠 | M | T2 | Tactical (over-the-table height) |
| 3.8 | **Time-to-bounce** prediction | 🟠 | M | T2 | Enables anticipatory officiating/coaching |
| 3.9 | **Expected landing position** prediction | 🟠 | L | T2 | Placement & in/out pre-call |
| 3.10 | mm-accurate impact point + in/out classification | 🔴 | L | T3 | Officiating foundation |
| 3.11 | Acceleration / deceleration profile per shot | 🟡 | M | T2 | Shot quality |
| 3.12 | Rally dynamics summary (pace, depth, tempo over time) | 🟠 | M | T2 | Feeds tactical AI |
| 3.13 | Speed/spin reported as **confidence intervals** not point values | 🔴 | S | all | Reliability (Part 10) |
| 3.14 | Equipment-aware priors (ball type/wear affect physics) | 🟡 | M | T2 | Links Part 14 |

## Datasets / models
- High-speed clips with **measured** spin (IMU/optical ground truth) — see Part 12.
- Physics simulator for sim2real spin/trajectory data (Part 12).
- Sequence models (temporal CNN/Transformer) for spin from trajectory + racket-face.

---

➡️ **NEXT FILE: `04_PLAYER_REID_AND_IDENTITY.md`**
