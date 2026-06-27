# PART 35 — HARDWARE & CAPTURE SETUP (SOP)

> Read `00_INDEX.md` first. Garbage footage → garbage analysis. This is how a venue/academy/federation sets up cameras, lighting, and calibration so the platform gets data it can trust. Ties to capture tiers (Part 02), input-quality gating (Part 10), and equipment (Part 20).

## A. Capture tiers (what each needs)
| Tier | Rig | Unlocks | Limits |
|------|-----|---------|--------|
| **T1** single camera (phone OK) | 1 cam + tripod | 2D events, stats, scoreboard, coarse spin (Magnus) | no true 3D; speed/spin wider intervals |
| **T2** single cam + calibration | 1 cam + table-corner calibration | metric placement, better speed, spin-from-curvature | depth ambiguity remains |
| **T3** multi-camera | 2–4 synced cams + calibration | true 3D, real spin/RPM, **16 cm serve-toss / officiating** | setup + sync cost |

## B. Camera specs
- **Resolution:** ≥ 1080p. **Frame rate:** ≥ 60 fps; **120 fps+** for ball tracking; **high-speed (240+)** for spin/RPM.
- **Shutter:** **global shutter** preferred; phones (rolling shutter) need correction (Part 02) — keep the ball mid-frame, avoid fast pans.
- **Lens/FOV:** cover the whole table + a margin; avoid heavy distortion (or calibrate intrinsics).

## C. Placement
- **Single cam:** side-on (best for trajectory/bounce) or end/elevated; broadcast-diagonal works but is hardest. Mount on a **stable tripod**, table centred, slight elevation.
- **Multi-cam (T3):** 2 side + 1 end (or 4 corners); ensure **overlapping views** of the play volume; document positions for calibration.

## D. Lighting
- **Bright, even, flicker-free.** Avoid PWM/fluorescent flicker (Part 01) — use high-CRI continuous lighting or set shutter to match mains frequency.
- **No glare/reflections** on the table; matte surfaces; consistent across the session.
- Ensure **ball-vs-background contrast** (white vs orange ball — Part 20).

## E. Synchronisation (T3)
Hardware **genlock/PTP** is ideal. Software fallback: a shared **clap/flash** event at the start to align timestamps; verify drift; re-sync per session.

## F. Calibration
- **Per session:** table-corner calibration (PnP) — the table's known 2.74 × 1.525 m geometry sets scale (Part 19).
- **Intrinsics:** checkerboard once per camera; **re-calibrate if a camera is bumped/zoomed** (drift monitor, Part 02).

## G. Venue & background
Contrasting, static background behind the table; keep crowd motion out of the play frame where possible; consistent court colour.

## H. Audio (optional, recommended)
A simple mic captures **ball-contact sound** → improves hit timing/quality (Part 14); place to minimise crowd noise.

## I. Pre-session checklist (run every time)
1. Camera(s) mounted, table fully in frame + margin.
2. Frame rate/resolution set; storage free.
3. Lighting even, no flicker, no glare.
4. (T3) cameras synced; calibration captured.
5. Record **metadata** (below).
6. **Input-quality self-check** (the app reports res/fps/angle/lighting/occlusion before processing — Part 10). Green → record.

## J. Low-cost mode (single phone — academies)
One phone on a tripod, side-on, ~table-height, whole table in frame, good even light, 60 fps. The guided in-app capture flow does one-tap table calibration (Part 02). Honest: T1 confidence is lower — labelled as such.

## K. Metadata to record (stored with the video — Part 12/27)
Venue · date · lighting type · camera model/config (fps/res/shutter) · tier (T1/T2/T3) · players + handedness/grip · **equipment** (rubbers/blade) · ball type/colour. This context feeds the models' priors and the reliability layer.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
