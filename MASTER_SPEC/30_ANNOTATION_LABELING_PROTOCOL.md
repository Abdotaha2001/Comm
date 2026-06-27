# PART 30 — ANNOTATION & LABELING PROTOCOL

> Read `00_INDEX.md` first. **Garbage labels → garbage models.** This is the protocol annotators follow so every dataset (Part 12) is consistent, frame-accurate, and trustworthy. Label *values* are the **canonical_ids** of Part 28; the metrics that consume these labels are Part 29.

## A. Principles
- **Controlled values only:** every categorical label is a `canonical_id` from Part 28 — never free text.
- **Frame-accurate:** events carry the exact frame (and ms); segments carry start/end frames.
- **Uncertainty is data:** annotators may mark `uncertain` / `occluded` / `motion_blur` rather than guess.
- **Rubrics for subjective labels:** quality scores follow expert-anchored scales (§C).
- **Two-pass QA:** a sample is double-labelled; inter-annotator agreement gates acceptance (§E).
- **Versioned guidelines:** this protocol is versioned; an edge-case catalog grows with decisions.

## B. Annotation tasks (per data type)
| Task | What to label | Value space | Tier needed |
|------|---------------|-------------|-------------|
| **Ball** | centre point (+ box) per frame, visibility | `visible/occluded/motion_blur` | crowd |
| **Bounce/net/serve** | event frame + side + position | event taxonomy (Part 28) | trained |
| **Hit** | frame + player + wing | `fh/bh` | trained |
| **Stroke** | start/end frame + type + wing | `stroke_type` (Part 28) | expert-reviewed |
| **Spin** | type (+ magnitude class) | `spin_type` | **expert + slow-mo** |
| **Footwork** | step segments | footwork ids | trained |
| **Player ReID** | bbox + identity across clips | player id | trained |
| **Handedness / grip** | per player | `left/right`, grip ids | trained |
| **Scoreboard** | digit regions + values | 0–9 | crowd |
| **Equipment / para** | rubber types, blade, para_class | Part 20/24 ids | metadata entry |

## C. Rubrics for subjective labels (expert-anchored, 1–5)
Subjective metrics need **anchored** scales so different experts agree (validity — Part 16).
- **Stroke quality (1–5):** 1 = all-arm, no kinetic chain, off-balance · 3 = partial chain, adequate · 5 = full proximal→distal chain, balanced, elite timing (Part 25 §B).
- **Footwork quality (1–5):** 1 = late/off-balance/no recovery · 5 = early split, efficient path, balanced, fast recovery.
- Each rubric ships with **reference video clips** per anchor so annotators calibrate.

## D. Annotation record schema
```json
{
  "clip_id": "...", "frame": 1234, "ts_ms": 41133,
  "task": "stroke",
  "value": "banana_flick",          // canonical_id (Part 28)
  "span": [1220, 1240],              // for segments
  "attributes": {"wing": "bh", "quality": 4},
  "flags": ["uncertain"],           // optional
  "annotator_id": "...", "confidence": 0.8, "created_at": "..."
}
```
Stored/versioned with the clip (Part 12 DVC). Boxes use `[x,y,w,h]`; points `{x,y}`.

## E. Quality process (the gate)
1. **Calibration:** annotators pass a qualification set before live work.
2. **Double-labelling:** ≥ 15% of every batch is labelled by 2+ annotators.
3. **Inter-annotator agreement (IAA) targets:**
   - categorical (stroke/spin/event-type): **Cohen's κ ≥ 0.80**
   - boxes/points: **IoU ≥ 0.70** / centre error ≤ ball radius
   - event timing: within **±2 frames**
4. **Adjudication:** disagreements resolved by an **expert**; result added to the gold set.
5. **Reject & retrain** annotators below threshold; batches failing IAA are re-done.

## F. Workforce & tooling
- **Tiers:** crowd (boxes, scoreboard) · trained (events, strokes, footwork) · **experts** (spin, quality rubrics, adjudication).
- **Tool must support:** frame-step, slow-mo/loop, configurable hotkeys per `canonical_id`, segment marking, occlusion flags, and showing the **equipment context** (rubber type) when labelling spin (long-pips reverses spin — Part 20).
- **Spin is special:** requires slow-motion + the player's rubber type; label the *effective* spin on the ball.

## G. Active-learning loop (Part 12)
Models flag **low-confidence / high-disagreement** frames → these are pushed to the front of the labelling queue, so human effort goes where it matters most. Human overrides of model output are captured as new labels (Part 11 feedback loop).

## H. Governance
- **Versioned guidelines** + a public **edge-case catalog** (e.g., "ball clipped by net post → mark occluded").
- Every guideline change bumps the protocol version and is logged.
- Datasets record which protocol version produced them (reproducibility — Part 13).

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
