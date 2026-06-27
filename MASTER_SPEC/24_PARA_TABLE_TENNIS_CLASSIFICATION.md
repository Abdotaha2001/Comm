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

## G. Class-by-class detail (the per-class reference label set)
| Class | Group | Defining function |
|-------|-------|-------------------|
| **1** | WC | **No sitting balance**, **severely affected playing arm** (spinal-cord lesion / polio) |
| **2** | WC | No sitting balance; playing arm **less affected** than Class 1 |
| **3** | WC | No sitting balance (upper trunk may show activity); **near-normal arms** (slight playing-hand loss, no real effect); non-playing arm holds trunk |
| **4** | WC | **Sitting balance exists** but not optimal (no pelvic anchorage) |
| **5** | WC | **Normal trunk-muscle function** (best wheelchair class) |
| **6** | ST | **Severe impairment of legs AND arms** |
| **7** | ST | Very severe leg impairment (poor balance), or severe-moderate playing-arm, or a milder arms+legs combo than C6 |
| **8** | ST | Moderate leg impairment, or moderate playing-arm, or moderate CP / hemiplegia / diplegia with a good playing arm |
| **9** | ST | Mild impairment of legs or playing arm, or moderate impairment of the non-playing arm |
| **10** | ST | **Very mild** leg or playing-arm impairment, or severe-moderate non-playing-arm, or moderate trunk |
| **11** | ID | **Intellectual impairment** meeting sport-specific criteria (cognition, not physical) |

> WC = wheelchair (1–5) · ST = standing (6–10) · ID = intellectual (11). These per-class descriptors seed class-aware expectations in the profile (§E) and the matchup logic.

## H. Para doubles rules
- **Wheelchair pair:** server serves → receiver returns → **thereafter either partner may return** (no strict alternation). But if **any part of a wheelchair protrudes beyond the imaginary extension of the table's centre line**, the point goes to the opponents.
- **Mixed pair (one standing + one wheelchair):** same return freedom after serve+return, but **each player must stay in their own half** of the court.

## I. Classification status & integrity
- Status codes: **N (New)** · **R (Review)** · **C (Confirmed)**.
- A **Confirmed** classification has **no protest procedure** — only a documented request to the federation can trigger an ITTF-initiated protest.
- **Intentional misrepresentation** of ability is an integrity offence → sanctions. (Relevant to the platform's integrity monitoring, Part 15.)

## J. Adaptive equipment & example conditions
- **Adaptive equipment:** a player who **cannot grip** may have the **racket strapped/bandaged to the hand** (permitted); serving adaptations for those who cannot do a standard ball-toss.
- **Example underlying conditions** (mapped to IPC types): spinal-cord injury / polio (impaired muscle power), **cerebral palsy** (hypertonia/ataxia/athetosis), amputation (limb deficiency), **dwarfism** (short stature), "**Les Autres**" (other locomotor conditions, e.g. MS, muscular dystrophy, arthrogryposis).
- **Deaflympics:** Deaf athletes compete in a **separate** stream (Deaflympics) — hearing impairment is **not** a Paralympic/Para-TT class.

## Sources
- [Para table tennis — Wikipedia](https://en.wikipedia.org/wiki/Para_table_tennis) · [Para-TT classification breakdown — Paralympic.org](https://www.paralympic.org/news/para-table-tennis-classification-breakdown) · [ITTF Para classification](https://www.ittf.com/para-table-tennis-classification/)
- [IPC Classification & eligible impairment types](https://www.paralympic.org/classification) · [ITTF PTT Rules & Regulations (PDF)](http://www.ipttc.org/rules/ITTF-PTT-Rules-and-Regulations.8th-edition.feb.2010-update.pdf) · [Para classification process — USATT](https://www.usatt.org/athlete-resources/para-classification)

---

➡️ **NEXT FILE: `25_ANATOMY_AND_MOVEMENT_DYNAMICS.md`**
