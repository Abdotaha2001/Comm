# PART 22 — TRAINING DRILLS & METHODOLOGY (the coaching engine's content base)

> Read `00_INDEX.md` first. This is the structured knowledge that powers the **drill recommender (M43)**, the **coaching/periodization engine (Part 08)**, and the **closed loop** (detected weakness → prescribed drill → tracked improvement, Parts 16/17).

## A. Methodology framework — the learning progression
Elite development moves through stages; the platform must know **which stage** a drill belongs to:
1. **Technique** (shadow practice, block/repetitive multiball) — groove the stroke.
2. **Consistency** (long rallies, e.g. 80+ FH drives, 60+ BH drives).
3. **Placement** (target zones, depth control).
4. **Footwork** (movement drills under control).
5. **Semi-random** (one decision: where, or which shot).
6. **Fully random / match-like** (read + decide spin, placement, shot — game transfer).

### The motor-learning core (block vs random practice)
- **Block (repetitive) practice:** removes reading/planning → fast grooving of a single skill. Best **early** and for technique changes.
- **Random (variable) practice:** restores reading/planning → **better retention & match transfer** (contextual-interference effect). Best for **refinement & match prep**.
- **Progression of randomization:** 1 placement decision → choice between shots → fully random spin+placement+selection.
> A standalone skill ≠ the same skill in a match (affected by ball position, spin, speed, opponent). The platform should **prescribe random practice** as a player matures, not endless block drills.

## B. Multiball training (the engine of systematic training)
Coach/robot feeds many balls (**~80+ /min**) → builds correct muscle memory **faster** than rallying, plus reaction speed, footwork, fitness, balance.
- **Periodization of multiball:** **off-season** → technique changes/refinement; **pre-season buildup** → footwork repetition; **in-season** → sharpening.
- **Variants:** technique multiball · footwork multiball · semi-random · random (match-simulation) · weighted-ball / eye-closed (research-backed for stroke effect & posture control).

## C. The essential drill library (M43's catalog — structured)
| Drill | Targets | Type | Level |
|-------|---------|------|-------|
| **Falkenberg (BH–pivot FH–wide FH)** | the 3 key moves: wide FH, wide BH, step-around FH | regular footwork | int–adv |
| FH-to-FH crosscourt | forehand technique/consistency | regular | beg+ |
| BH-to-BH crosscourt | backhand technique/consistency | regular | beg+ |
| FH–BH alternation (transition) | switching/transition point | regular→semi | beg–int |
| Figure-8 / butterfly | diagonal footwork + control | regular | int |
| Two-point / one-point footwork | lateral movement + recovery | regular→random | int–adv |
| **Third-ball attack** (serve→return→step-around FH to elbow) | serve+3rd-ball system (Part 21) | semi-random | int–adv |
| Serve practice + serve-and-attack | serve quality + follow-up | block→semi | all |
| Receive drills (push/flick/banana) | neutralize serve | semi-random | int–adv |
| **Loop vs block (counterloop)** | open-up + counter | regular→random | int–adv |
| Block-to-attack | defense→offense transition | progressive | int |
| Drop-shot / short game | touch + bring-in (vs choppers) | semi | adv |
| **Solo:** shadow, robot, serve practice, wall | technique groove without partner | block | all |

## D. Drill classification (the schema fields)
Each drill is tagged: `targets_skill` (Part 19 taxonomy) · `regular|semi|random` · `multiball_capable` · `solo|partner|robot` · `level` · `phase` (off/pre/in-season) · `progression_next`.

## E. The closed loop (why this part exists)
```
Match analysis → detected weakness (e.g. "loses 7/9 vs heavy backspin to BH")
       → M43 prescribes drill (e.g. "BH push→loop multiball, random spin")
       → scheduled in the plan (Part 08 periodization)
       → re-analyze next match → did the metric improve? (Parts 16.6 efficacy / 17.7)
```
This is the single most valuable coaching feature: **analysis that prescribes, and verifies, the right practice.**

## F. Platform implications
| Need | Mechanism |
|------|-----------|
| Drill recommender (M43) | weakness (detected) + skill taxonomy (Part 19) → drill from this catalog, grounded + evidence-cited |
| Periodization (Part 08) | place drills by phase (off/pre/in-season) and load (Part 06) |
| Robot integration (Part 14) | execute prescribed multiball patterns automatically |
| Efficacy loop (Part 16) | track metric before/after the prescribed block → prove it worked |
| Talent pathway (Part 08) | stage-appropriate progression (block→random as the player matures) |

## Sources
- [The Falkenberg Drill — Expert Table Tennis](https://www.experttabletennis.com/the-falkenberg-drill/) · [100+ drills — Expert Table Tennis](https://www.experttabletennis.com/table-tennis-drills/)
- [Motor learning: block vs random practice — iCoachTableTennis](http://www.icoachtabletennis.com/motor-learning-block-vs-random-practice-in-table-tennis/)
- [Multiball training fundamentals — JOOLA](https://joola.com/blogs/updates/multiball-training-is-fundamental-to-early-success-in-table-tennis) · [Weighted/eye-closed multiball study — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7039024/)
- [First-five-shots drills — TableTennisCoach.me.uk](https://www.tabletenniscoach.me.uk/10-training-drill-ideas-for-the-first-five-shots-in-a-rally/)

---

➡️ **NEXT FILE: `23_ATHLETE_DEVELOPMENT_PHYSICAL_AND_MENTAL.md`**
