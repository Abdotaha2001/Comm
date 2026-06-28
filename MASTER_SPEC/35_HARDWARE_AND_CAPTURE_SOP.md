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

## L. Power, cabling & connectivity
- **Power:** UPS / battery backup for cameras + control so a brownout never kills a session; phones **charged + thermal-aware** (long 120 fps records overheat and throttle); label & route cables to remove **trip hazards**.
- **Connectivity:** plan upload **bandwidth** or **record-local-then-sync**; an **offline buffer** so capture never blocks on the network (Part 32.P); an **NTP/time source** for trustworthy timestamps (Part 35.E).

## M. On-site storage, files & chain of custody
- **Redundant capture** for officiating / important sessions (two cards or mirrored); verify **free space + write speed** first — no dropped frames.
- **File-naming convention** (`venue_date_table_tier_camera`) + the metadata sidecar (Part 35.K); for officiating, an **unbroken chain of custody** (who handled the footage + content **hashes**, Part 31 / 34.BK).

## N. Sensor fusion & IoT (optional — raises confidence/tier)
- **Radar/speed gun**, **smart paddle / IMU**, **force plates**, **ball-machine/robot** (Part 14), and the **contact mic** (Part 35.H) can fuse with vision — each stream is **time-synced** (Part 35.E) and carries **its own confidence** (Part 10).
- **Environmental sensors** (temp/humidity) feed the **aero priors** (Part 19) — a measured value beats an assumed one.

## O. Environmental factors
- **Temperature / humidity / altitude** shift ball aerodynamics (drag & Magnus, Part 19) — record them so the physics isn't run on the wrong air density; **AC drafts** disturb the ball → shield the play volume.
- **Table & ball condition** (clean, matte, ITTF-approved, Part 20) kept consistent within a session.

## P. Multi-table / tournament-scale deployment
- A **camera fleet** with central control, per-table calibration, **synchronised clocks**, and **monitored health** (a down camera is flagged, Part 34.AS); a **schedule** maps tables ↔ matches ↔ storage.
- **Bandwidth + storage budgeted** for N tables; **graceful degradation** (a table drops to T1 if a camera fails) — never lose the match.

## Q. Phone / mobile capture SOP (the academy default)
- **Lock exposure & focus**, clean the lens, **≥ 60 fps**, airplane-mode to avoid interruptions, table fully framed + margin, ~table-height side-on; **thermal breaks** on long sessions.
- The **guided in-app flow** does one-tap table calibration + the input-quality gate (Part 35.I/J) before recording.

## R. Rig maintenance & QA
- **Periodic re-calibration** + a per-session **drift check** (Part 02 / 35.F); lens cleaning; firmware pinned and updated deliberately; **spares** (cable, card, battery) on hand.
- A short **monthly rig audit** (mounts, sync accuracy, lighting) stops quality decaying silently.

## S. Safety, consent & safeguarding at capture
- **Electrical / rigging safety**; frame to the **play volume**, minimising crowd capture (data minimisation at source, Part 31).
- **Filming consent + venue signage**; **minors → guardian consent before capture**; footage of children is extra access-controlled (Part 31 / 34.AJ).

## T. Officiating-grade capture (T3)
- For decisive use: a **certified setup**, **redundant cameras** (no single point of failure), **frame-accurate synced timestamps**, and **tamper-evidence** (hashes/signing, Part 31) producing the **evidence package** (Part 09 / 32.J).
- The **16 cm serve-toss / net-clearance** checks need the calibrated multi-cam volume (Part 02); below that, officiating **abstains** rather than guesses.

## U. Bill of materials & cost per tier
| Tier | Kit | Rough cost |
|------|-----|-----------|
| **T1** | 1 phone + tripod + clip light | `$` — academy-affordable |
| **T2** | 1 mirrorless/action-cam (120 fps) + tripod + calibration board + lighting | `$$` |
| **T3** | 2–4 synced global-shutter cams + mounts + sync gear + lighting + capture PC | `$$$` |
- Pick the **lowest tier that unlocks the needed outputs** (Part 35.A); the platform is **honest about that tier's confidence** instead of forcing expensive kit.

## V. Use-case capture protocols
- **Match:** broadcast/side view, full rallies, scoreboard in frame. **Training / multiball:** closer on the player for stroke & footwork (Part 22). **Talent-ID:** standardised angle + fixed drills for comparability (Part 23). **Para:** frame for the **wheelchair / standing class**, no able-bodied footwork assumptions (Part 24).

## W. Troubleshooting (symptom → fix)
| Symptom | Likely cause → fix |
|---------|-------------------|
| Motion-blurred ball | shutter too slow → raise shutter / add light / higher fps |
| Flicker / banding | mains or PWM light → match shutter to mains, or high-CRI continuous |
| Ball lost behind player | bad angle → raise/side the camera; add a second view (T2/T3) |
| Dropped frames | slow card / overheating → faster card, thermal break |
| Wrong placement metrics | calibration drift → re-run table-corner calibration |

## X. Post-setup acceptance test
Before the real session, record a **30-second test rally** and run the **input-quality self-check** (res / fps / angle / lighting / occlusion + a sample detect-and-track). **Green → proceed**; amber → fix the flagged item first (Part 10 / 35.I). Never capture a full event on an unverified rig.

---

➡️ **NEXT FILE: `36_RISK_REGISTER_AND_ASSUMPTIONS.md`**
