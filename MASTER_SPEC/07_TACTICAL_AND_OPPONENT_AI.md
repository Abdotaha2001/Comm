# PART 07 — TACTICAL AI & OPPONENT INTELLIGENCE

> Read `00_INDEX.md` first. Baseline does shot **counts**, not patterns or strategy.

## 7A. Tactical AI
Playing style · Match strategy · Tactical patterns · Winning/losing patterns · Shot selection · Decision making · Pressure behavior · Momentum changes · Psychological trends → recommend adjustments.

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 7.1 | **Pattern modeling** (serve+3rd-ball, real sequences) | 🔴 | L | T2 |
| 7.2 | **Sequence mining** (Markov chains / frequent patterns) | 🟠 | L | T2 |
| 7.3 | **3rd-ball / 5th-ball attack analysis** | 🔴 | M | T2 | classic TT KPI |
| 7.4 | Serve→receive→outcome matrix | 🟠 | M | T2 |
| 7.5 | Shot-placement zone maps (6/9-zone table) per shot type | 🟠 | M | T2 |
| 7.6 | Table-distance / positioning over time | 🟠 | M | T2 |
| 7.7 | Stroke tempo / timing-window analysis | 🟡 | L | T2 |
| 7.8 | **Predictive strategy engine** (if you do X, opponent does Y) | 🔴 | XL | T2 |
| 7.9 | **Live win-probability model** | 🟡 | L | T2 |
| 7.10 | **Expected-points (xP) / shot-value model** | 🟡 | L | T2 |
| 7.11 | Pressure-point / clutch behavior analysis (deuce, set points) | 🟠 | M | T2 |
| 7.12 | Momentum-shift detection + psychological trend modeling | 🟠 | L | T2 |
| 7.13 | Decision-making quality scoring (was the shot choice right?) | 🟡 | L | T2 |
| 7.14 | Deception/variation detection in serves | 🟡 | L | T2 |
| 7.15 | Tactical-adjustment recommender | 🟠 | L | T2 |

## 7B. Opponent Intelligence
Auto-identify: strengths · weaknesses · preferred serves · weak returns · preferred rally length · favorite patterns · pressure weaknesses → **pre-match tactical report**.

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 7.16 | Multi-match opponent aggregation | 🟠 | M | all |
| 7.17 | **Opponent simulation** (pre-match preparation) | 🟠 | XL | T2 |
| 7.18 | Auto pre-match scouting report (per opponent) | 🟠 | M | T2 |
| 7.19 | Anti-exploit (what the opponent does well vs us) | 🟠 | M | T2 |
| 7.20 | Counterplan generator (actionable match prep) | 🟠 | M | T2 |

## Datasets / models
- Labeled rally-sequence corpus; outcome-annotated points.
- Sequence/transformer models; Bayesian win-prob; RL for simulation.

---

➡️ **NEXT FILE: `08_COACHING_AND_TALENT.md`**
