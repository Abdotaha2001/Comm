# PART 20 — EQUIPMENT INTELLIGENCE (RUBBERS · SPONGE · PIPS · BLADES)

> Read `00_INDEX.md` first. **Why this is in the spec and not a side note:** the spin model is *wrong* if it doesn't know the equipment. Long pips and anti-spin **reverse or kill** spin — so the same swing produces the opposite ball. Equipment is a mandatory **prior** for the spin engine (M12/M13), correlates strongly with **playing style** (M34), and must be stored as **profile metadata** (Part 17).
>
> *Sourced from established domain knowledge (live web search was rate-limited at authoring time; facts here are stable/non-time-sensitive).*

## Arabic ↔ technical glossary (the user's terms)
| Term (EG) | Technical |
|-----------|-----------|
| الجلد | Inverted / smooth rubber (pips-in) |
| السريعة | Short pips (pips-out, fast) |
| الصد / الأنتي | Anti-spin |
| الحبوب الطويلة | Long pips |
| السفنجة / بسفنجة | Sponge / with sponge · **OX** = no sponge |
| تخينة / رفيعة | Sponge thickness (thick / thin) |
| خشب المضرب | Blade |

---

## A. Racket anatomy (3 layers, each tunable)
`Blade (wood/composite)` → `Sponge (foam)` → `Topsheet (rubber surface)`. The combination defines speed, spin, control, and feel. ITTF: total covering (sponge + topsheet) **≤ 4.0 mm**, one side **black**, the other a bright approved color, both from the ITTF **LARC** approved list.

---

## B. Rubber types (the 4 families)
| Family (EG) | Surface | Spin | Speed | Control | Offensive/Defensive | Typical user |
|-------------|---------|------|-------|---------|---------------------|--------------|
| **Inverted / smooth — الجلد** | pips face **in**, smooth out | ★★★★★ | ★★★★☆ | ★★★☆ | **Offensive** standard | loopers, attackers (both wings) |
| **Short pips — السريعة** | short pips **out** | ★★☆ | ★★★★☆ | ★★★★ | Offensive (flat hit/block) | close-table hitters, BH hitters, penhold |
| **Long pips — الحبوب الطويلة** | tall thin pips **out** | reverses incoming | ★☆ | ★★ (wobble) | **Defensive** | choppers, blockers, disruptors |
| **Anti-spin — الصد/الأنتي** | smooth but **slick/low-friction** | kills spin | ★☆ | ★★★ | **Defensive/deception** | blockers, twiddlers |

### Inverted sub-types (both are "الجلد" but behave differently)
- **Tacky (Chinese, e.g. Hurricane):** sticky topsheet, **max spin** but needs the player's own power; lower built-in speed. Heavy-spin loopers.
- **Tensor / grippy (European-Japanese ESN, e.g. Tenergy):** built-in **catapult/spring**, springy, faster with less effort; slightly less raw tackiness. Modern all-court loopers.

---

## C. Pips deep-dive (long vs short — the source of most spin-reading errors)
| | **Short pips (السريعة)** | **Long pips (الطويلة)** |
|---|---|---|
| Pip shape | short, wide, stiff (low aspect ratio) | **tall, thin, flexible** (high aspect ratio) |
| Mechanism | barely deform → flat, fast, **ignores incoming spin** | **bend over** on contact → return the opponent's own spin (**spin reversal**) |
| Own spin | little | almost none (OX) |
| Ball quality | fast, dead-ish, low arc | **wobble / unpredictable**, "knuckle" effect |
| Use | hitting & blocking close to table | chopping, blocking, disruption |
| Physics note | low dwell, near-elastic, low μ-transfer | tangential reversal → **spin sign flips** |

ITTF regulates pip geometry: pimple **height ≤ ~2 mm**, and the **aspect ratio** (height:diameter) is bounded so "frictionless long pips" are illegal.

---

## D. Sponge — thickness & hardness (تخينة/رفيعة + بسفنجة)
### Thickness
| Thickness | Speed | Spin | Control | Who |
|-----------|-------|------|---------|-----|
| **OX (0, no sponge)** | very low | none (own) | high disruption | long-pips/anti choppers — **max reversal & wobble** |
| **Thin (1.0–1.5 mm)** | low | low | **high** | control players, some BH, junior development |
| **Medium (1.8–1.9 mm)** | medium | medium | balanced | all-round |
| **Thick (2.0–2.1 mm)** | high | high | lower | offensive loopers (most attackers) |
| **Max (~2.2–2.5 mm)** | **highest** (catapult) | highest | hardest to control | power loopers |

### Hardness (degrees, ESN/Chinese scale)
- **Soft sponge (~35–42°):** more dwell, more control & spin at slow speed, forgiving; favored on backhand / by developing players.
- **Hard sponge (~45–50°+):** more top-end speed for strong strokes, needs power to "engage"; Chinese tacky rubbers run hard (37–41° on the *Chinese* scale ≈ harder).
- **Rule of thumb:** thicker + harder = faster/spinnier but less control → only for players who can generate the swing.

---

## E. Blades (خشب المضرب)
### Construction
- **Plies:** 1 / 3 / 5 / 7 **wood** plies, or wood **+ composite** layers (carbon, **ALC** arylate-carbon, **ZLC** zylon-carbon, Texalium, etc.).
- **Composite (carbon/ALC):** faster, **bigger sweet spot**, stiffer → less dwell/feel. **All-wood:** more control, dwell, and feedback (better for spin feel and choppers).
- **Outer ply wood (feel):** **Limba** (soft, control, spin feel) · **Koto** (hard, fast, crisp) · **Hinoki** (penhold, soft+fast) · **Ayous** (light core).

### Speed classes (slow → fast)
`DEF  <  ALL-  <  ALL  <  ALL+  <  OFF-  <  OFF  <  OFF+`
- **DEF:** slow, flexible, often larger head → **choppers** (paired with long pips/anti).
- **ALL / ALL+:** balanced → **all-rounders**, developing players.
- **OFF- / OFF / OFF+:** fast, stiff (often ALC like the classic Viscaria) → **loopers/attackers**.

### Other variables
Weight (light = control/maneuver, heavy = power), stiffness (stiff = speed, flex = dwell/control), handle shape (FL/ST/AN/CS-penhold).

---

## F. Equipment ↔ playing style map (feeds M34 style classifier)
| Style | Typical blade | FH rubber | BH rubber |
|-------|---------------|-----------|-----------|
| Two-winged looper (attacker) | OFF / OFF+ (ALC) | thick inverted (tensor/tacky) | thick inverted (tensor) |
| Penhold FH looper | OFF (hinoki/ALC) | thick inverted | RPB inverted / short pips |
| Close-table hitter / blocker | ALL+/OFF- | inverted or **short pips** | short pips / inverted |
| All-rounder | ALL | medium inverted | medium inverted |
| **Modern defender / chopper** | **DEF** (big, flexible) | inverted (to attack) | **long pips or anti** (OX/thin) + **twiddle** |

> This table is a **prior**: detecting "DEF blade + long pips + chopping motion + back-from-table position" → high-confidence "chopper" classification, which then sets the spin engine to expect **reversal**.

---

## G. Platform implications (how the AI uses all this)
| Need | Mechanism |
|------|-----------|
| Spin prior (M12/M13) | condition on rubber family; **flip spin sign** for long pips/anti |
| Equipment recognition (Part 14) | visual cues (topsheet sheen, visible pips on close-ups, color) **+ profile metadata input** (broadcast can't always see it → ask the coach to enter it) |
| Style correlation (M34) | equipment + motion + court position → style (Part 19 B8) |
| Player profile (Part 17) | store `blade`, `fh_rubber`, `bh_rubber`, thickness, hardness, OX flag as metadata |
| Contact physics (Part 19 §C2) | effective friction μ and tangential coupling differ per rubber → the imparted-spin model `ω_out ≈ f(μ, v_tangential, dwell)` uses **negative/near-zero μ_eff** for long-pips/anti |

### The physics link (why it can't be ignored)
Spin transfer at contact scales with the tangential friction impulse. Inverted tacky → high μ → `ω_out` large, same sense as the brush. **Long pips bend and release** → the relative tangential velocity reverses → **`ω_out` flips sign** vs an inverted rubber doing the identical stroke. **Anti** → μ_eff ≈ 0 → `ω_out ≈ 0` (dead ball). A spin model blind to rubber type will systematically misread every chopper.

---

## H. ITTF equipment rules (officiating — links Part 09)
- Covering ≤ **4.0 mm** total (sponge + topsheet). · Two sides **different colors** (black + bright approved). · Only **LARC-approved** rubbers. · Pip height/aspect-ratio limits (no frictionless long pips). · Blade ≥ **85% natural wood** by thickness. · **Boosting** (illegal speed-glue-like tuning) is banned → detection is a Part 14 target.

---

## Sources
Established table-tennis equipment domain knowledge (ITTF technical regulations; standard manufacturer/coaching references). Live citations to be appended when web search is available (rate-limited at authoring time).

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
