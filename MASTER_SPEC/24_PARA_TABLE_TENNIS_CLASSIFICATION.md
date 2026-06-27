# PART 24 — PARA TABLE TENNIS: CLASSIFICATION & INCLUSIVE PROFILES

> Read `00_INDEX.md` first. Extends the rules engine (Part 09), the player profile (Part 17), and the movement/biomech models (Parts 06, 25). **Rule:** higher class number = **more function**.

## A. The 11 sport classes
| Group | Classes | Who |
|-------|---------|-----|
| **Wheelchair** | **1 – 5** | play seated; 1 = most impairment, 5 = least |
| **Standing** | **6 – 10** | physical disability, play standing; 6 = most, 10 = least |
| **Intellectual** | **11** | intellectual impairment meeting sport-specific criteria |

## B. What distinguishes the groups (the assessment axes)
- **Wheelchair (1–5):** sitting balance · range of motion · manual muscle testing · reaction time · range of reach · hand function. (No standing/footwork component.)
- **Standing (6–10):** all upper-limb motor skills of 1–5 **plus** standing balance · footwork · rate of movement to reach the ball. May use orthotics, canes, crutches, prosthetics.
- **Class 11 (intellectual):** physical abilities largely intact; impairment affects **processing speed, decision-making, anticipation, tactical adaptation** — i.e. cognition, which is critical for strategy, pattern recognition, and in-match adjustment.

## C. The IPC eligible impairment types (the underlying framework)
Para sport recognizes **10 eligible impairment types** (8 physical + vision + intellectual): impaired muscle power · impaired passive range of movement · limb deficiency · leg-length difference · short stature · hypertonia · ataxia · athetosis · vision impairment · intellectual impairment.
- **For Para TT:** the **8 physical** types map to classes **1–10**; **intellectual** → class **11**. (Vision impairment is **not** currently a Paralympic TT class.)
- Eligibility = at least one type meeting **Minimum Impairment Criteria**, and the impairment is **permanent / long-term**.

## D. Rules differences (Para vs standard — extends Part 09)
- **Standing (6–10):** **standard ITTF rules, no modifications.**
- **Wheelchair (1–5):**
  - Service requirements may be **relaxed** by the umpire if disability prevents compliance (toss & visibility still apply; struck behind the end line).
  - **Wheelchair service-let rule:** a serve is a **let** if the ball, after bouncing on the receiver's side, **returns toward the net**, **comes to rest** on the receiver's court, or (singles) **leaves over a sideline** — unless the receiver strikes it first.
  - Point lost if a wheelchair player: doesn't keep **minimum thigh contact** with the seat/cushion when striking; **touches the table with a hand** before striking; or **footrest/foot touches the floor** during play.
  - **Chair spec:** ≥ 2 large wheels + 1 small wheel; cushion(s) height ≤ **15 cm**; nothing above the knees attached to the chair (no balance aid) in team/class events.

## E. ⭐ FEATURE — assign a disability / class to ANY player
The platform lets a coach attach an impairment to **any** player profile (pro, junior, or para). Profile fields (extends Part 17 schema):
```
player.para_class        # 1–11, or null (able-bodied)
player.impairment_type   # one of the 10 IPC types (+ notes)
player.disability_notes  # free text (e.g. "C6, right-side hemiplegia")
player.mobility_mode      # wheelchair | standing | n/a
```
When set, the platform **adapts**:
- Movement/footwork models switch to the right reference (wheelchair has **no able-bodied footwork**; reach zones differ).
- The **service-legality engine** applies the relaxed wheelchair rules (Part 09).
- Coaching expectations, drills (Part 22), and standards (Part 23) adjust to the class.
- Matchup & game plan (Part 17/21) compare **within class**.

## F. Platform implications
| Need | Mechanism |
|------|-----------|
| Para-aware perception | wheelchair pose/movement differs → dedicated reference/model variant (Part 25) |
| Reachability zones | seated reach envelope vs standing → different "out of position" logic |
| Service legality | per-class mode (relaxed for wheelchair) in the umpire engine (Part 09) |
| Movement scoring | wheelchair = chair-handling & upper-body reach, **not** footwork steps (Part 19 B5 N/A) |
| Class-11 coaching | cognitive-load-aware plans: pattern recognition, decision speed, simplified tactics |
| Inclusive talent ID | maturation- **and** impairment-adjusted (Part 23) — never compare across classes |

## Sources
- [Para table tennis — Wikipedia](https://en.wikipedia.org/wiki/Para_table_tennis) · [Para-TT classification breakdown — Paralympic.org](https://www.paralympic.org/news/para-table-tennis-classification-breakdown) · [ITTF Para classification](https://www.ittf.com/para-table-tennis-classification/)
- [IPC Classification & eligible impairment types](https://www.paralympic.org/classification) · [ITTF PTT Rules & Regulations (PDF)](http://www.ipttc.org/rules/ITTF-PTT-Rules-and-Regulations.8th-edition.feb.2010-update.pdf)

---

➡️ **NEXT FILE: `25_ANATOMY_AND_MOVEMENT_DYNAMICS.md`**
