# PART 09 — RULES, UMPIRE ENGINE & SCORE INTELLIGENCE

> Read `00_INDEX.md` first. Officiating-grade claims require T3 (Part 02) + Reliability (Part 10).

## 9A. ITTF Rules / Umpire Engine
Detect: illegal serve · **16 cm toss** · **hidden serve** · double hit · obstruction · edge ball · net ball · table touch · **free-hand touch** · scoring rules · timeout rules · **expedite system**.

| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 9.1 | Illegal-serve detection (toss height, behind line, open palm, not hidden) | 🔴 | L | T3 |
| 9.2 | 16 cm toss measurement (needs depth) | 🔴 | L | T3 |
| 9.3 | Hidden-serve detection (free hand/body obscuring ball) | 🔴 | L | T3 |
| 9.4 | Edge-ball / net-ball precise classification | 🟠 | M | T3 |
| 9.5 | Double-hit / free-hand-touch / table-touch / obstruction | 🟠 | L | T3 |
| 9.6 | **Expedite system** logic | 🟡 | M | — |
| 9.7 | Timeout / towel / between-games timing rules | 🟡 | M | T1 |
| 9.8 | Auto umpire report + **evidence package** per call | 🔴 | M | all |
| 9.9 | **Rule-set versioning over time** (which rules applied to which match) | 🟠 | M | — |
| 9.10 | Equipment legality check (ITTF LARC, boosting) — links Part 14 | 🟠 | M | T1 |
| 9.11 | Player-clothing-color legality (≠ ball color) | 🟡 | S | T1 |

## 9B. Authority & Governance (human-AI)
| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 9.12 | Authority model (advisory vs decisive + override hierarchy) | 🔴 | M |
| 9.13 | Dispute-resolution protocol + liability/insurance framework | 🟠 | M |
| 9.14 | Umpire-training mode (AI as certification tool) | 🟠 | L |
| 9.15 | Manual fallback if system fails mid-point | 🔴 | M |
| 9.16 | Referee-AI agreement logging (continuous officiating calibration) | 🟠 | M |

## 9C. Score Intelligence
| # | Component | Priority | Complexity | Tier |
|---|-----------|----------|-----------|------|
| 9.17 | **Scoreboard OCR** (read on-screen score) | 🔴 | M | T1 | free ground-truth |
| 9.18 | Point/game/match status detection | 🟠 | M | T1 |
| 9.19 | Cross-check OCR score vs computed score (disagreement flag) | 🔴 | S | T1 | links Part 10 |
| 9.20 | Pressure-point identification + point-by-point analytics | 🟠 | M | T2 |
| 9.21 | Live scoring-system integration (official feeds) — Part 14 | 🟠 | M | — |

## 9D. Match Formats (baseline assumes singles only)
| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 9.22 | **Doubles** (4 players, diagonal serve, rotation) | 🔴 | L |
| 9.23 | **Para / wheelchair TT** (rules + classification) | 🟠 | L |
| 9.24 | **Team events** (Swaythling/Corbillon, tie formats) | 🟠 | M |
| 9.25 | National/league rule variants | 🟡 | M |

---

➡️ **NEXT FILE: `10_RELIABILITY_AWARENESS.md`**
