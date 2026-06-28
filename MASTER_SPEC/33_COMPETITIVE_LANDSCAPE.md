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

## F. Adjacent & analog competitors (could enter TT / set the playbook)
| Player | Domain | Why it matters |
|--------|--------|----------------|
| **SwingVision / PlaySight / Hawk-Eye** | Tennis AI (phone & pro) | proven phone-camera analysis + line-calling UX; could extend to TT |
| **Stats Perform / Second Spectrum / Sportlogiq** | Pro sports AI analytics | deep tracking/tactics tech + broadcast deals; potential entrant/acquirer |
| **Catapult / Kinexon** | Athlete load/wearables | physical-side data; partner or compete on sports science |
| **Google DeepMind — robot TT** | Big-tech research | signals serious interest; perception + RL talent |
| **Open-source (TTNet/OpenTTGames/SpinDOE)** | Free CV | **lowers the barrier** — anyone can build basic ball/event detection |

## G. Business models, pricing & segments
- **Models in market:** app subscription (Stupa), enterprise/federation contracts (OSAI), freemium/free (TT Match Analyzer), hardware bundle (robots), per-event broadcast.
- **Segments & willingness-to-pay:** federations/Olympic (high, contract) · pro clubs (medium) · academies (medium, price-sensitive) · coaches (low-medium, subscription) · players (low, freemium).
- **Our model:** tiered SaaS (academy→club→federation) + a free/low tier for individuals; price the **game-plan loop** as the premium value.

## H. Five Forces
- **Rivalry:** moderate-high (Stupa/OSAI established) — differentiate, don't clone.
- **New entrants:** **high** — open-source CV + big-tech interest lower the barrier; our moat must be the loop + data + partnerships, not the CV.
- **Substitutes:** manual coaching, Dartfish tagging, "just watch the video" — beat with speed + the prescribe→verify loop.
- **Buyer power:** federations are few & powerful → land-and-expand; academies are many & price-sensitive.
- **Supplier power:** datasets/cloud/GPU — mitigated by reuse (Part 26) + multi-cloud.

## I. SWOT (TT-OS)
- **Strengths:** the analyze→prescribe→verify loop · reliability honesty · para + Arabic · open architecture.
- **Weaknesses:** 2-person team · no ITTF partnership yet · CV accuracy not yet proven on real footage.
- **Opportunities:** underserved MENA/para · coaching-loop white space · reuse open CV to move fast.
- **Threats:** Stupa/OSAI expansion · big-tech entry · data/partnership moats hardening.

## J. Make / buy / partner
- **Buy/reuse** the CV layer (Part 26: TTNet/TrackNet/SpinDOE) — don't out-CV the incumbents early.
- **Partner** where possible: dataset/CV (OSAI), equipment (Butterfly), robots (Power Pong), and pursue **ITTF/federation endorsement** (the key credibility moat Stupa holds).
- **Build** our differentiators: the game-plan/training loop, reliability layer, knowledge graph, para + Arabic.
- **Data flywheel** (Part 12) is our long-term moat — every analysis improves the models.

## K. Table-stakes vs differentiation
- **Must match (credibility):** accurate ball/event tracking, clean stats, doubles + para support, fast turnaround. Below par here = no trust.
- **Sustainable differentiation:** the **coaching loop + reliability + knowledge graph + region** — harder to copy than a feature; deepens with data.

## L. Go-to-market & exit landscape
- **GTM:** land MENA/para academies + a federation pilot → expand; coach-network + app-store + direct federation sales.
- **Potential acquirers/exits:** ITTF-aligned partners, Stats Perform-type analytics firms, equipment brands (Butterfly), or a broadcast/Hawk-Eye player.

## Sources
- [Stupa Analytics (App Store)](https://apps.apple.com/us/app/stupa-analytics/id1480094754) · [OSAI — championship CV analytics](https://medium.com/@osai.ai/osai-empowered-russian-table-tennis-championship-with-cv-and-ai-analytics-e7d52a6d8a5c) · [TTNet paper](https://arxiv.org/pdf/2004.09927)
- [TT Match Analyzer](https://ttmatchanalyzer.com/) · [Dartfish](https://www.dartfish.com/) · [SmartScorer (ITTF-compliant umpire app)](https://crocodilesandwichapps.com/index.php/en/smartscorer-for-table-tennis) · [avaTTAR (AR stroke training)](https://arxiv.org/pdf/2407.15373)
- [SwingVision (tennis AI)](https://swing.tennis/) · [Stats Perform](https://www.statsperform.com/) · [DeepMind competitive robot TT](https://sites.google.com/view/competitive-robot-table-tennis/home)

---

➡️ **NEXT FILE: `34_ENGINEERING_CONVENTIONS.md`**
