# PART 02 — CAPTURE TIERS & 3D RECONSTRUCTION

> Read `00_INDEX.md` first. Three capture tiers (T1/T2/T3) drive what the platform can claim.

## Purpose
Define the three operating modes and everything needed to support them. Officiating-grade measurements (e.g. the 16 cm serve toss) are **physically impossible without depth** → require T3.

## 2A. SINGLE CAMERA — 2D (`T1`) and 3D-lift (`T2`)

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 2.1 | Table-geometry calibration (PnP from known table corners) | 🔴 | M | T1 |
| 2.2 | Camera-angle classifier (end / side / broadcast-diagonal) + per-angle logic | 🔴 | M | T1 |
| 2.3 | Broadcast diagonal-angle handling | 🟠 | M | T1 |
| 2.4 | **Rolling-shutter correction** (phones) | 🟠 | M | T1 |
| 2.5 | Lens-distortion correction (intrinsic) | 🟠 | M | T1 |
| 2.6 | Monocular depth estimation with physical priors | 🟠 | L | T2 |
| 2.7 | 2D→3D lifting using known table/net dimensions as scale | 🟠 | L | T2 |
| 2.8 | **Spin-from-trajectory-curvature (Magnus)** — spin without high-speed cam | 🟠 | L | T2 |
| 2.9 | Explicit confidence **penalties** when in single-camera mode | 🔴 | S | T2 |
| 2.10 | Documented assumptions & limitations per mode | 🟠 | S | T1 |
| 2.11 | Guided mobile capture flow + one-tap table calibration | 🟠 | M | T1 |
| 2.12 | **Low-cost mode** (single phone, no GPU) | 🟠 | L | T1 |
| 2.13 | Auto camera-angle/quality validation before processing | 🟠 | M | T1 |

## 2B. MULTI-CAMERA — true 3D (`T3`)

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 2.14 | Intrinsic + extrinsic calibration per camera (board/table-based) | 🔴 | L | T3 |
| 2.15 | **Time synchronization** (genlock/PTP or audio/event sync) | 🔴 | L | T3 |
| 2.16 | Triangulation + bundle adjustment | 🔴 | L | T3 |
| 2.17 | True 3D ball trajectory + physics fit (drag + Magnus) | 🔴 | L | T3 |
| 2.18 | Multi-view 3D pose reconstruction | 🟠 | L | T3 |
| 2.19 | Optimal camera-placement guide + venue setup SOP | 🟠 | M | T3 |
| 2.20 | Cross-camera ReID consistency | 🟠 | L | T3 |
| 2.21 | Best-view selection per moment | 🟡 | M | T3 |
| 2.22 | **Calibration-drift monitoring** (bumped cameras) | 🟠 | M | T3 |
| 2.23 | Heterogeneous cameras (mixed res/fps) handling | 🟡 | M | T3 |
| 2.24 | **Auto re-calibration** when a camera moves mid-match | 🟠 | L | T3 |
| 2.25 | Hardware spec: global-shutter + frame-rate + sync rig | 🔴 | M | T3 |
| 2.26 | **3D measurement of serve toss height (16 cm)** + hidden-serve detection | 🔴 | L | T3 |

## Outputs this part unlocks
- Calibrated metric speed/spin/height with confidence intervals.
- Officiating-grade 3D events (serve legality, edge/net) — feeds Part 09.
- 3D replay / free-viewpoint (feeds Part 14).

---

➡️ **NEXT FILE: `03_BALL_INTELLIGENCE.md`**
