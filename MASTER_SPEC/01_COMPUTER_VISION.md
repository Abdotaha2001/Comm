# PART 01 — COMPUTER VISION FOUNDATION

> Read `00_INDEX.md` first. Legend (Priority/Complexity/Tier/Status) is defined there.

## Purpose
Every pixel-level perception module the platform needs. This is the foundation every other engine depends on. The current baseline uses a **generic COCO YOLO** ("sports ball" class 32) — inadequate for a 40mm ball moving 100+ km/h.

## Required modules
- Player detection · Ball detection · High-speed ball tracking · Ball trajectory estimation
- Bounce detection · Hit detection · Table detection · **Net detection** · Racket detection · **Racket-face pose/angle**
- Camera calibration (intrinsic + extrinsic) · Homography · Court mapping · 3D reconstruction
- Occlusion handling · Motion-blur handling · Multi-camera fusion (see Part 02)

## Missing components

| # | Component | Priority | Complexity | Tier | Notes |
|---|-----------|----------|-----------|------|-------|
| 1.1 | **TT-specific ball detector** (replace generic class 32) | 🔴 | L | T1 | Tiny fast object; needs custom-trained model |
| 1.2 | High-speed tracking robust to **motion blur** | 🔴 | L | T1 | Deblur + sub-pixel localization |
| 1.3 | **Occlusion handling** (ball behind player/net) | 🔴 | L | T1 | Trajectory inpainting + re-acquisition |
| 1.4 | **Net detection** + net-cross/net-touch geometry | 🔴 | M | T1 | Missing entirely today |
| 1.5 | **Racket detection + racket-face angle** | 🔴 | L | T1 | Prerequisite for spin & intent |
| 1.6 | Bounce detection (mm-accurate impact point) | 🟠 | M | T2 | Today heuristic on pixel-Δy |
| 1.7 | Hit detection (multi-signal, low false-positive) | 🟠 | M | T1 | Baseline ~30% FP by its own logs |
| 1.8 | Table detection robust to color/angle/lighting | 🟠 | M | T1 | Today HSV ranges only |
| 1.9 | Intrinsic camera calibration (lens distortion) | 🟠 | M | T1 | Per-device |
| 1.10 | Court/table coordinate mapping (world frame) | 🟠 | M | T2 | Homography exists; needs robustness |
| 1.11 | **Two-balls-in-frame** disambiguation (warm-up/dropped ball) | 🟠 | M | T1 | Common false detection |
| 1.12 | **Shadow vs ball** separation | 🟠 | M | T1 | False positives |
| 1.13 | Ball vs **white/light background** (low contrast) | 🟠 | M | T1 | Hardest detection moment |
| 1.14 | **Ball-color adaptation** (white vs orange) | 🟠 | S | T1 | Contrast model per ball |
| 1.15 | **Ball-wear detection** (ball degrades over a match) | 🟡 | M | T1 | Affects bounce/spin priors |
| 1.16 | Camera-shake / pan / zoom compensation | 🟠 | M | T1 | Broadcast feeds |
| 1.17 | **Lighting flicker** robustness (LED/fluorescent) | 🔴 | M | T1 | Corrupts high-speed capture |
| 1.18 | Glare/reflection suppression on table | 🟠 | M | T1 | Hides ball & contact |
| 1.19 | 3D reconstruction (see Part 02) | 🔴 | XL | T3 | True geometry |

## Datasets required (see Part 12 for the master dataset list)
- TT-ball bounding boxes across venues/lighting/ball colors.
- Net & racket segmentation.
- Bounce/hit event-localized clips with frame-accurate labels.

## Models suggested
- Custom small-object detector (YOLO/RT-DETR variant) fine-tuned on TT-ball.
- Deblur/super-resolution front-end for high-speed frames.
- Segmentation (table/net/racket) + keypoint head for racket-face.

---

➡️ **NEXT FILE: `02_CAPTURE_TIERS_AND_3D.md`**
