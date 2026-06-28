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

# Enterprise SOP extension (Y–AJ)

> Sections Y–AJ raise this SOP to production/officiating grade (comparable to pro vision systems). Every check below has a **measured threshold + pass/fail** and maps to a **certification level** (Part 35.AJ). Numbers are acceptance gates, not aspirations.

## Y. Camera intrinsics & lens-distortion model
- **Model:** OpenCV/Brown–Conrady — radial `k1,k2,k3` + tangential `p1,p2` (add rational `k4,k5,k6` and thin-prism `s1–s4` only for wide/fisheye); persist the full **3×3 intrinsic matrix `K`** + coefficients per camera (Part 02).
- **Procedure:** ChArUco/checkerboard, **≥ 20 views** spanning all four corners + centre at varied distance/tilt; iterate to convergence.
- **Pass/fail:** **RMS reprojection error ≤ 0.5 px (Gold/Platinum), ≤ 1.0 px (Silver), ≤ 1.5 px (Bronze)**; per-view max ≤ 1.5 px; undistort-and-remeasure a straight edge → residual curvature **≤ 0.3 px**. Coefficients stored in the versioned calibration record (Part 35.AH).

## Z. Rolling-shutter profiling (non-global-shutter cameras)
- **Characterise** each CMOS sensor's **line readout time** (µs/line) and total frame readout (ms); store a per-camera RS profile (phones must carry one, Part 02).
- **Correction:** apply RS de-skew from the profile **before** triangulation/physics (Part 19); keep the ball **mid-frame**, avoid fast pans.
- **Pass/fail:** readout time known to **±5%**; residual RS skew on a vertical reference at match ball-speed **≤ 1.0 px** after correction. **T3 officiating requires a global shutter** — rolling shutter is **not eligible for Platinum**.

## AA. Synchronisation validation & drift thresholds
- **Preference:** hardware **genlock / PTP (IEEE-1588)** > embedded timecode > software clap/flash (Part 02 / 35.E). Always **measure** the offset.
- **Acceptance (max pairwise inter-camera offset):** **Platinum ≤ 0.5 ms · Gold ≤ 1 ms · Silver ≤ 1 frame (≤ 8 ms @120 fps)**; PTP grandmaster sync error **< 100 µs**.
- **Drift:** monitor continuously; **re-sync if drift > 0.5 frame (or > 1 ms for officiating)** within a session; log every check (Part 35.AH). Fail → 3D + officiating outputs **abstain** (Part 10).

## AB. Exposure, white-balance, colour & dynamic range
- **Lock for the session:** manual **exposure**, fixed **ISO/gain** (lowest viable), **white-balance locked to measured CCT** — no auto drift mid-rally.
- **Colour calibration:** shoot a **24-patch reference chart (e.g. X-Rite ColorChecker)** at setup; build/verify a colour profile; **mean ΔE2000 < 3 (Gold), < 5 (Silver)**; WB error **< 200 K** (Part 20).
- **Shutter:** **≤ 1/1000 s** for 120 fps ball tracking (motion-blur, Part 35.AD); anti-flicker, mains-locked (Part 35.AC).
- **Dynamic range:** **< 1% clipped highlights and < 1% crushed blacks** on the ball/table region; log/HDR profile for high-contrast venues; the ball must stay separable from background.

## AC. Lighting QA (automatic, per session)
| Metric | Method | Pass / fail |
|--------|--------|-------------|
| **Illuminance** | lux meter at table | ≥ 1000 lux (Gold/officiating) · ≥ 800 (Silver) · ≥ 500 (Bronze) |
| **Uniformity** | min/avg over table | ≥ 0.8 (Gold) · ≥ 0.7 (Silver) |
| **Flicker** | high-fps / flicker meter | **percent-flicker < 5%**, flicker index < 0.1, no PWM in capture band |
| **CCT** | reference chart | consistent **± 300 K** across the table |
| **CRI** | luminaire spec/meter | ≥ 90 (colour tasks) · ≥ 80 min |
| **Glare** | inspection | no specular hot-spots on the table |
- Below Bronze → the input-quality gate **blocks recording** (Part 10 / 35.I). Drives ball-vs-table contrast (Part 20).

## AD. Motion-blur, ball-visibility & occlusion metrics
- **Motion-blur length** `L_blur(px) = v_ball(px/s) × t_exposure(s)`; **accept ≤ 0.5 × ball-Ø (Gold), ≤ 1.0 × (Silver)** — else raise shutter/light or fps (Part 19).
- **Ball visibility:** apparent **diameter ≥ 12 px (Gold), ≥ 8 px (min)**; **Weber contrast ≥ 0.3** vs background; **trajectory visibility rate ≥ 95% (Gold), ≥ 90% (Silver)** of expected frames.
- **Occlusion heatmap:** accumulate per-zone frames where the ball/player is occluded; **max single-zone occlusion < 10%** of the play volume; persisted with the run for the reliability layer (Part 10).

## AE. Extrinsics, capture-volume validation & multi-camera overlap
- **Capture volume:** define the play volume (≈ **4.0 × 3.0 × 2.5 m** = table + margins + vertical for toss/loop); **every voxel seen by ≥ 2 cameras** for 3D (Part 02).
- **Overlap:** adjacent-camera FOV overlap **≥ 50% (Gold), ≥ 30% (min)**; **100% of the play volume double-covered**.
- **Verification object:** sweep a **known-length bar** (plus the table 2.74 × 1.525 m, net 15.25 cm) through the volume; **3D reconstruction error of the known length ≤ 5 mm (Platinum), ≤ 10 mm (Gold)**; epipolar/triangulation residual **≤ 1.0 px** (Part 19).

## AF. Camera & rig health monitoring
- **Persistent camera ID:** every unit has a stable **UUID + physical label**, bound to its calibration record (Part 35.AH / 34.AK).
- **Live telemetry per camera (sampled every few seconds):** fps stability **± 0.5 fps**, **dropped-frame rate < 0.1%**, exposure/gain stability, **sensor temperature**, sync offset, link status (Part 34.AS).
- **Thermal:** warn at **sensor ≥ 60 °C**, throttle/break before the spec limit; ambient operating **10–35 °C**; long high-fps records scheduled with cooling breaks (Part 35.L/Q).

## AG. Network, latency/jitter & edge-to-cloud pipeline
- **Live monitoring:** **glass-to-decision latency < 100 ms (officiating), < 200 ms (live coaching) · jitter < 10 ms · packet loss < 0.1%**; keep **≥ 20% bandwidth headroom** (Part 14 / 12).
- **Pipeline:** edge capture → local buffer / store-and-forward → cloud ingest → analysis (Part 12); capture **never blocks on the network** (Part 32.P / 35.L).
- **Officiating isolation:** decisive systems run on an **isolated VLAN / air-gapped segment**, **no internet egress**, allow-listed peers only (Part 31 / 34.AE). Fail → officiating disabled.

## AH. Calibration lifecycle: versioned records, recalibration triggers & drift
- **Versioned calibration record** per camera/session: camera ID · `K` + distortion · extrinsics · timestamp · operator · residuals · validity window — **immutable, stored with provenance** (Part 12 / 34.AK).
- **Auto-recalibration triggers:** detected bump (feature drift), **temp change > 10 °C**, **reprojection residual > 1.0 px**, or validity window elapsed (Part 02).
- **Long-session drift monitor:** re-check residual every **≤ 15 min**; **periodic ground-truth validation** — reconstruct net height (15.25 cm) / table dims and require **measured-vs-truth ≤ 5 mm**. Breach → flag + recalibrate; downstream outputs **abstain** until green (Part 10).

## AI. Operator dashboard & AI-guided capture assistance
- **Operator dashboard:** per-camera RAG health (sync · fps · drops · temp · residual · lighting · ball-visibility), capture-volume coverage, current **certification level** + any failing KPI (Part 32 / 34.BA).
- **AI-guided setup:** a real-time assistant flags misframing, drift, glare, occlusion, and under-exposure and gives the **corrective action** (raise shutter, re-aim, add light) before/while recording (Part 10 / 32); the in-app input-quality gate (Part 35.I) is its entry point.

## AJ. Capture-quality certification & acceptance KPIs
- **Composite Capture-Quality Score (CQS):** a weighted roll-up of sync, reprojection, lighting, motion-blur, ball-visibility, overlap, network, and drift — each normalised 0–1; the **lowest sub-score caps the tier** (no averaging a failure away, Part 10 / 34.AL).
- **Certification levels (the audit-ready gate):**

| Level | Tier | Gate (all must pass) | Unlocks |
|-------|------|----------------------|---------|
| **Bronze** | T1 | input-quality green · lighting ≥ Bronze · ball-visibility ≥ 90% | 2D events/stats, labelled low-confidence |
| **Silver** | T2 | + reprojection ≤ 1.0 px · calibration valid · sync ≤ 1 frame | metric placement, better speed/spin |
| **Gold** | T3 | + sync ≤ 1 ms · overlap ≥ 50% · recon ≤ 10 mm · flicker < 5% · ΔE < 3 | true 3D, RPM, real spin |
| **Platinum** | T3 + officiating | + global shutter · sync ≤ 0.5 ms · recon ≤ 5 mm · redundant cams · tamper-evident · isolated network · ground-truth validated | **decisive officiating** (Part 35.T) |

- **Quantitative acceptance KPIs (pass/fail summary):**

| KPI | Target | Fail action |
|-----|--------|-------------|
| Inter-camera sync offset | ≤ 0.5 / 1 ms (Plat/Gold) | abstain 3D + officiating |
| RMS reprojection error | ≤ 0.5 px | recalibrate |
| 3D reference-length error | ≤ 5 / 10 mm | recalibrate / drop tier |
| Multi-camera overlap | ≥ 50% | re-aim / add camera |
| Illuminance / uniformity | ≥ 1000 lux / ≥ 0.8 | fix lighting |
| Percent flicker | < 5% | fix lighting / shutter |
| Colour ΔE2000 | < 3 | re-WB / re-profile |
| Motion-blur | ≤ 0.5 × ball-Ø | raise shutter / fps |
| Ball-visibility rate | ≥ 95% | re-aim / add view |
| Dropped frames | < 0.1% | faster media / cooling |
| Live latency / jitter | < 100 ms / < 10 ms | fix network |
| Sensor temperature | < 60 °C | cooling break |
| Drift re-check | ≤ 15 min · ≤ 5 mm | recalibrate |

- A capture is **production-accepted only at the certification level whose KPIs all pass**; the level + the KPI snapshot are stored with the session (provenance, Part 34.AK) and surfaced in the reliability envelope (Part 10).

## AK. Machine-readable acceptance framework (authoritative)
The acceptance logic in Y–AJ is implemented as a **single source of truth** so documentation and code cannot diverge:

| Artifact | Path | Role |
|----------|------|------|
| Schema (SoT) | `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json` | versioned KPI table + certification levels + thresholds |
| Engine | `backend/app/capture_quality.py` | `compute_cqs()` — gate logic, reliability envelope, provenance |
| Operator checklist | `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_CHECKLIST.csv` | **generated** from the schema |
| Example report | `MASTER_SPEC/capture_quality_report.md` | **generated** from the schema |

- **Certification = lowest required sub-score** (min gate), never an average; a single failed mandatory gate denies the level (Part 10 / 34.AL).
- **Five levels:** Fail · Bronze (academy/T1) · Silver (production/T2) · Gold (competition/T3) · Platinum (officiating/T3). Platinum requires global shutter, sync ≤ 0.5 ms, 3D recon ≤ 5 mm, ground-truth + tamper-evidence + isolated network + versioned calibration + frame-accurate timestamps, and **zero failed mandatory KPI**.
- **Outputs:** a `CQSResult` (certification · effective + overall score · per-KPI sub-scores · failed gates · warnings · recommended actions · reliability level), a **reliability envelope** (Part 10) and an immutable **provenance** record + hash (Part 34.AK).
- **Consistency enforced in CI:** a test asserts the committed checklist regenerates from the schema; rebuild with `python -m app.capture_quality --generate`. The schema is **extensible + versioned** — add a KPI / sensor / tier / certification without a code change.

---

➡️ **NEXT FILE: `36_RISK_REGISTER_AND_ASSUMPTIONS.md`**
