# PART 05 — STROKE, SPIN & FOOTWORK ENGINES

> Read `00_INDEX.md` first. Baseline recognizes ~8 stroke types; real TT has 40+ techniques.

## 5A. Stroke Recognition (full taxonomy + quality)

Recognize **all** techniques and score each one's quality:

- **Serves:** Pendulum · Reverse Pendulum · Tomahawk · Hook · Backhand serve · High-toss · Ghost serve
- **Receive:** Push · Flip · Banana flick · Chiquita · Stop/short · Long push
- **Attack:** Drive · Loop · Counter-loop · Smash · Kill
- **Defense:** Block · Active block · Soft block · Chop · Fish · Lob
- **Transitions/footwork strokes:** Pivot · Step-around · Cross-step · Side-step

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 5.1 | Full serve taxonomy classifier | 🔴 | L | T1/T2 |
| 5.2 | Full receive taxonomy (incl. banana/chiquita) | 🔴 | L | T2 |
| 5.3 | Full attack/defense taxonomy | 🔴 | L | T2 |
| 5.4 | **Stroke quality scoring** (vs ideal kinematics) | 🟠 | L | T2/T3 |
| 5.5 | **Intent vs execution** (intended shot vs actual outcome) | 🟡 | L | T2 |
| 5.6 | Handedness/grip-aware classification (links Part 04) | 🔴 | M | T1 |
| 5.7 | Long-tail / rare-style handling (few-shot) | 🟠 | L | all |

## 5B. Spin Engine
Topspin · Backspin · Left sidespin · Right sidespin · Cork spin · Mixed · No-spin, with RPM where possible (see Part 03 for physics).

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 5.8 | Per-shot spin-type classifier | 🔴 | L | T2/T3 |
| 5.9 | Spin from racket-face × ball-curvature fusion | 🟠 | L | T2 |
| 5.10 | Rubber-aware spin priors (long pips/anti) — links Part 14 | 🟠 | M | T2 |

## 5C. Footwork Engine (analysis, not just drills)
Side-step · Shuffle · Cross-step · Pivot · Recovery · In-out · Balance · Efficiency · Court coverage · Reaction time · Recovery time.

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 5.11 | Footwork-pattern classifier | 🟠 | L | T2 |
| 5.12 | **Reaction-time & recovery-time** measurement | 🟠 | L | T2/T3 |
| 5.13 | Court-coverage heatmap + efficiency score | 🟠 | M | T2 |
| 5.14 | Balance / center-of-mass stability (links Part 06) | 🟠 | L | T3 |
| 5.15 | Movement-quality composite score | 🟡 | M | T2 |

## Datasets / models
- Expert-labeled stroke/spin/footwork clips with **rubrics** (Part 16 defines the rubrics).
- Temporal pose+ball+racket multi-modal sequence models.

---

➡️ **NEXT FILE: `06_BIOMECHANICS_AND_SPORTS_SCIENCE.md`**
