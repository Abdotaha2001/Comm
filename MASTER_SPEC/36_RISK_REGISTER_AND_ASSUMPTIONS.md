# PART 36 — RISK REGISTER & ASSUMPTIONS

> Read `00_INDEX.md` first. A living register of the risks that can sink this, the bets we're making, and how we mitigate. Expands `PROJECT_PLAN §9`. **L/I = Likelihood / Impact (H/M/L).**

## A. Risk register
| ID | Risk | Cat | L | I | Mitigation |
|----|------|-----|---|---|-----------|
| **R1** | Real-footage CV accuracy ≪ synthetic baseline | Technical | H | H | reuse Part 26 models + fine-tune; benchmark gate (Part 29); honest confidence |
| R2 | Markerless spin unreliable | Technical | H | M | SpinDOE calibration + high-speed cam (T3); cap confidence; flag uncalibrated |
| R3 | Per-player stats need ReID (not built) | Technical | M | M | Part 04 models; until then aggregate per-video with a stated caveat |
| R4 | Real-time / officiating latency without GPU | Technical | M | H | GPU workers + model optimisation (Part 12); offline first |
| **R5** | Labelled data scarce (esp. spin) | Data | H | H | synthetic/sim2real, active learning, annotation protocol (Part 30) |
| R6 | Pro-match footage rights | Data | M | M | license; use research datasets for dev (Part 26/12) |
| R7 | Annotation cost/quality | Data | M | M | IAA gate + tiered workforce (Part 30) |
| R8 | Dataset bias (lighting/venue/skin/body) | Data | M | M | bias audit (Part 12); diverse capture (Part 35) |
| **R9** | Incumbent moat (Stupa = ITTF partner) | Market | H | H | **don't clone** — wedge on game-plan loop + reliability + para + Arabic (Part 33) |
| R10 | Coaches distrust / slow to adopt AI | Market | M | H | reliability honesty, expert validation, change management (Part 15) |
| R11 | Rule-based game plan not useful enough | Product | M | M | coach-panel usefulness rating (Part 16); upgrade to grounded LLM (Part 11) |
| **R12** | Minors' biometric data — legal exposure | Legal | M | H | guardian consent, GDPR, safeguarding, edge-private (Part 31/15) |
| **R13** | Officiating liability (wrong call) | Legal | M | H | advisory-not-decisive until validated; abstention + evidence packages (Part 09/10) |
| R14 | GPU cost at scale | Ops | M | M | spot + batching + edge; cost reporting (Part 13/15) |
| R15 | Scale to tournament load | Ops | L | M | queue + autoscale (Part 13) |
| **R16** | 2-person bandwidth | Team | H | H | strict scope (P0+P1, reuse-first); defer P2–P4; one part-time coach |
| R17 | Funding / sustainability | Business | M | H | pricing tiers, grants, federation/academy pilots (Part 15) |

## B. Top risks to watch (the ones that actually kill it)
1. **R9 incumbent moat** — win on the unoccupied wedge, not feature parity.
2. **R1 / R5 real-world accuracy + data** — the hard core; reuse + fine-tune + measure.
3. **R16 two-person bandwidth** — ruthless scope discipline.
4. **R12 / R13 minors & officiating liability** — get consent + advisory-mode right early.

## C. Assumptions log (the bets — revisit each quarter)
| ID | Assumption | If wrong → |
|----|-----------|-----------|
| A1 | Part 26 open assets are license-OK + accurate enough for the CV layer | must train from scratch (much slower) |
| A2 | The opponent-specific game-plan loop is a real differentiator coaches want | re-position the product |
| A3 | A 2-person team can reach a shippable P1 via foundation models + grounded LLM | need to hire/fund earlier |
| A4 | Reliability-honesty is an advantage, not a turn-off | rethink how confidence is surfaced |
| A5 | Arabic/MENA + para is an underserved, winnable wedge | broaden/re-target market |
| A6 | Rule-based intelligence is "good enough" for MVP value | accelerate ML/LLM upgrade |

## D. Process
- Review this register **each phase gate**; update L/I + status; add new risks as they appear.
- Every assumption has a **validation plan** (a cheap test) before we bet big on it.
- Owners assigned per risk once the team grows beyond two.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
