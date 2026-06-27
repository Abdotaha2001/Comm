# PART 33 — COMPETITIVE LANDSCAPE

> Read `00_INDEX.md` first. Who already exists, what they do, and where the white space is — so we don't rebuild what's shipped and we aim at a real gap. *(Web-researched; sources at the end.)*

## A. The players
| Product | Category | Strengths | Limits |
|---------|----------|-----------|--------|
| **Stupa Analytics** | Commercial TT analytics app | **Official ITTF performance partner**; phone-camera ball tracking + speed + stats; used by federations (BRA/SWE/POR/HUN/FRA/GER) and pros (Diaz, Kanak Jha) | match **stats/analytics**; not an opponent-specific game-plan + training engine; closed |
| **OSAI / TTNet** | CV analytics + broadcast | Real-time events (97%) + 2px ball; championship deployments; **OpenTTGames** dataset | broadcast/event analytics; not a coaching/development platform |
| **TT Match Analyzer** | Free AI lite tool | free; coaching-style feedback on clips | lightweight; limited depth/accuracy |
| **Dartfish / Hudl** | General sports video analysis | mature tagging, telestration, teams | **manual** tagging; not TT-aware (no ball/spin/auto-events) |
| **SmartScorer** | Umpire/scoring app | ITTF-compliant scoring, serve rotation, timeouts | **rule/manual** scoring; **no computer vision** |
| **Power Pong / Newgy / Butterfly Amicus** | Training robots | drills, multiball | hardware only; no analysis/intelligence |
| **avaTTAR / TTNet / BlurBall / SpinDOE** | Academic/AR | SOTA components (stroke AR, ball, blur, spin) | research, not a product |

## B. Capability matrix (✅ strong · ◑ partial · ✗ none)
| Capability | Stupa | OSAI | Dartfish | SmartScorer | **TT-OS (this)** |
|-----------|:----:|:----:|:-------:|:-----------:|:----------------:|
| Auto ball tracking | ✅ | ✅ | ✗ | ✗ | ◑ (baseline→Part 26) |
| Events / scoring | ✅ | ✅ | ◑ | ✅(manual) | ◑ |
| Stroke / **spin** | ◑ | ◑ | ✗ | ✗ | ◑ **spin-aware** |
| Player profiles + longitudinal | ✅ | ◑ | ◑ | ✗ | ✅ |
| **Opponent-specific game plan** | ✗ | ✗ | ✗ | ✗ | ✅ **(flagship)** |
| Training prescription + verify loop | ✗ | ✗ | ◑ | ✗ | ✅ |
| **Reliability / confidence surfaced** | ✗ | ✗ | ✗ | n/a | ✅ **(core)** |
| **Para / inclusivity first-class** | ◑ | ✗ | ✗ | ◑ | ✅ |
| Officiating-grade defensibility (evidence) | ✗ | ◑ | ✗ | ◑ | ◑ (T3 target) |
| Federation multi-tenant + RBAC | ◑ | ◑ | ✅ | ✗ | ✅ |
| **Bilingual / Arabic (RTL)** | ✗ | ✗ | ◑ | ✗ | ✅ |

## C. Where the white space is (our wedge)
1. **The "beat this opponent" loop** — profile × opponent → **opponent-specific game plan + training block + verify-it-worked**. Competitors stop at stats; nobody closes analyze→prescribe→verify.
2. **Reliability awareness** — every number carries calibrated confidence and can say "not sure". Incumbents present numbers without honest uncertainty.
3. **Spin + equipment awareness** — long-pips/anti spin-reversal modelled (Part 20); most tools ignore spin entirely.
4. **Para + inclusivity** first-class (Part 24).
5. **Region** — Arabic/RTL + MENA federations & academies (underserved by EU/global incumbents).
6. **Open architecture** — pluggable models (Part 18/26) + open glossary/API, vs closed apps.

## D. Honest competitive risks
- **Stupa** has an **ITTF partnership + pro adoption** — a real incumbent moat; we need a differentiated wedge (the game-plan loop + region + para), not a feature-for-feature clone.
- **OSAI** owns strong CV tech + the dataset everyone uses — partner-or-differentiate, don't out-CV them head-on early.
- Accuracy bar is high and proven (Stupa/OSAI) — our reliability-honesty is the counter-positioning, but the underlying models must still get good (Part 26/29).

## E. Strategic takeaways
- **Don't** rebuild generic ball-tracking/stats as the headline — it exists and is good.
- **Do** lead with the **opponent-specific coaching loop + reliability + para + Arabic** — the unoccupied space.
- **Reuse** OpenTTGames/TTNet/SpinDOE (Part 26) for the CV layer; spend our effort on the intelligence + reliability + product loop.

## Sources
- [Stupa Analytics (App Store)](https://apps.apple.com/us/app/stupa-analytics/id1480094754) · [OSAI — championship CV analytics](https://medium.com/@osai.ai/osai-empowered-russian-table-tennis-championship-with-cv-and-ai-analytics-e7d52a6d8a5c) · [TTNet paper](https://arxiv.org/pdf/2004.09927)
- [TT Match Analyzer](https://ttmatchanalyzer.com/) · [Dartfish](https://www.dartfish.com/) · [SmartScorer (ITTF-compliant umpire app)](https://crocodilesandwichapps.com/index.php/en/smartscorer-for-table-tennis) · [avaTTAR (AR stroke training)](https://arxiv.org/pdf/2407.15373)

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
