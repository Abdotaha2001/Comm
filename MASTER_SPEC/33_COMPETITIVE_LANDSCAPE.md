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

## M. Market sizing (TAM / SAM / SOM) — *estimates to validate*
- **Footprint:** ITTF has **~226 member associations**; table tennis has **hundreds of millions** of players globally (China-dominant). *(figures to verify.)*
- **TAM:** all TT federations + pro clubs + academies + serious players worldwide.
- **SAM:** federations/clubs/academies that buy analytics + the coaches who pay for tools.
- **SOM (near-term):** MENA academies/federations + global para programs + Arabic-speaking coaches — our beachhead.
- Action: replace these with sourced numbers before any fundraising.

## N. China / Asia — the heartland (research gap)
TT is **China-centric** (national-team R&D, smart tables, robots, likely domestic CV/analytics tools). This is the largest market **and** a strong-competitor region we under-know. **TODO:** dedicated research on Chinese/Japanese/Korean products and national-team internal tools before entering Asia.

## O. Battlecards (sell-against)
| vs | Their pitch | Our counter | Trap to set |
|----|-------------|-------------|-------------|
| **Stupa** | ITTF-official, pro-proven stats | "stats ≠ a plan — we close analyze→**prescribe→verify**, with honest confidence + para + Arabic" | ask: *do they tell you **how to beat this specific opponent** and verify it worked?* |
| **OSAI** | best CV + championship data | "great CV — we **reuse** it; our value is the coaching loop + reliability, not raw tracking" | ask: *is it a coaching platform or event analytics?* |
| **Dartfish/Hudl** | mature, multi-sport | "manual tagging vs **auto** TT-aware events + spin + game plans" | ask: *how much coach time per match to tag manually?* |

## P. Positioning
- **Statement:** *"For coaches and federations who need to **win the next match**, TT-OS is the AI platform that turns analysis into an **opponent-specific game plan + training** — and proves it worked — with honest confidence, para support, and Arabic."*
- **Positioning map (2×2):** *stats-only ↔ full coaching loop* × *closed app ↔ open/honest*. Incumbents cluster in **stats-only/closed**; we own **full-loop/open-honest**.

## Q. Win/loss & objection handling
- *"Why not Stupa?"* → not a coaching loop; closed; no para/Arabic.
- *"Is the AI accurate?"* → we **show confidence and abstain** instead of bluffing; reuse proven CV (Part 26); golden-set gate (Part 29).
- *"You're 2 people."* → reuse-first scope; partner for CV; the loop is the moat, not the pixels.

## R. Defense & unfair advantages
- **If incumbents copy the loop:** out-execute on **reliability + knowledge graph + region + para + data flywheel** (deepens with use — hard to copy fast).
- **Unfair advantages:** domain depth (Parts 19–25), para-first, Arabic/MENA access, open architecture.

## S. Competitive-intelligence process
This is a **living doc** — review quarterly; monitor competitor releases/pricing/partnerships; log moves; update the battlecards. Assign an owner once the team grows.

## T. Pricing strategy (*anchors to validate*)
- **Value metric:** per active player/seat (scales with the customer); not per-minute (penalizes use).
- **Tiers:** Free (1 player, watermark) · Coach/Academy (subscription) · Club · **Federation** (contract + SSO + white-label + officiating). Premium gates = the **game-plan loop** + multi-cam/officiating.
- **Anchoring:** price below a federation's cost of a manual analyst; benchmark vs Stupa's app price. *(Get real competitor price points before launch.)*

## U. Credibility & the ITTF moat
The incumbent edge is **ITTF endorsement + pro logos**. Counter with: **pilot programs** (a federation/academy), **independent validation studies** (Part 16 — published accuracy + AI-vs-expert agreement), case studies, and pursuing **ITTF/continental-federation recognition** ourselves. Trust is earned with evidence, not claims (our reliability layer is the proof).

## V. Switching costs & migration
Incumbents create stickiness via accumulated data. **Win switchers** by importing their footage/history, **no lock-in** (open export, our own data portability), and a fast "first game plan in a day" wow-moment.

## W. Open-source & ecosystem strategy
A wedge vs **closed** incumbents: keep the **glossary/ontology + API/SDK open** (Parts 27/28) and build a community/ecosystem; keep the **trained models + reliability + intelligence** proprietary. Openness lowers adoption friction and recruits contributors.

## X. Scenario planning (and our response)
- **Stupa acquired by / deepens with ITTF** → lean harder on the loop + para + region; seek continental-federation partners.
- **Big tech (DeepMind-style) enters** → partner/ride their CV; compete on the coaching loop + domain depth they won't build.
- **Free Chinese/giant entrant** → differentiate on reliability + para + Arabic + service; don't compete on price for commodity tracking.

## Y. Anti-personas (focus)
Not (yet) for: casual recreational players wanting a toy app; broadcast-graphics-only buyers; markets we can't support linguistically/operationally. Focus beats breadth for a 2-person team.

## Z. Competitive KPIs
Track **head-to-head win rate** in deals, displacement of incumbents, feature-parity gap closing, share of voice in target regions — so "differentiation" is measured, not assumed.

## AA. Alternative-tech & non-obvious competitors
Different approaches and buyers we must not ignore:
| Competitor | Approach | Why it matters / our angle |
|------------|----------|----------------------------|
| **Smart tables / IoT scoring** | sensors in table/net (not CV) | rival data path; we win on richer CV analysis + coaching, no special hardware |
| **Racket / wearable IMU sensors** | stroke/spin from device on bat/wrist | accurate spin/swing — **partner** for ground truth (Part 14) rather than fight |
| **Equipment brands (Butterfly/DHS/Stiga)** | could bundle an app with gear | strong distribution → **partner** (equipment intelligence, Part 20) before they compete |
| **Federation / national-team in-house tools** (esp. China) | internal R&D — they **don't buy** | target federations without internal teams; sell where build-vs-buy favors buy |
| **Status quo: "do nothing"** | coach intuition + plain video | ⭐ **the real #1 competitor** — beat it with speed, the prescribe→verify loop, and an honest free tier |

> **Honest note:** beyond this, competitive depth needs **primary research** — competitor trials, customer/coach interviews, real price points — not more spec. This doc is now a strong framework to fill with field data.

## Sources
- [Stupa Analytics (App Store)](https://apps.apple.com/us/app/stupa-analytics/id1480094754) · [OSAI — championship CV analytics](https://medium.com/@osai.ai/osai-empowered-russian-table-tennis-championship-with-cv-and-ai-analytics-e7d52a6d8a5c) · [TTNet paper](https://arxiv.org/pdf/2004.09927)
- [TT Match Analyzer](https://ttmatchanalyzer.com/) · [Dartfish](https://www.dartfish.com/) · [SmartScorer (ITTF-compliant umpire app)](https://crocodilesandwichapps.com/index.php/en/smartscorer-for-table-tennis) · [avaTTAR (AR stroke training)](https://arxiv.org/pdf/2407.15373)
- [SwingVision (tennis AI)](https://swing.tennis/) · [Stats Perform](https://www.statsperform.com/) · [DeepMind competitive robot TT](https://sites.google.com/view/competitive-robot-table-tennis/home)

---

➡️ **NEXT FILE: `34_ENGINEERING_CONVENTIONS.md`**
