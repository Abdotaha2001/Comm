# PART 21 — TACTICAL SYSTEMS & MATCH STRATEGY (the game-plan knowledge base)

> Read `00_INDEX.md` first. This is the **grounding knowledge for the game-plan generator (M36)** and the **edges encoded by the matchup model (M35)**. It maps opponent **style + equipment** (Parts 19–20) → **how to beat them**. This is the brain behind the flagship feature (Part 17).

## A. The core offensive system — Serve + 3rd ball
The dominant scoring pattern in modern TT:
1. **Serve** short & low (or sudden long) to limit the opponent's attack.
2. Opponent makes a **controlled return** (push/flick).
3. **3rd-ball attack** — the server opens with a loop/flick to a pre-planned spot.
- Variations: serve→receiver flicks→**block/counter**; serve long→**bait** the attack→counterloop.
- The matrix that powers this: **serve type → likely return → planned 3rd ball**. Model M31/M35 learns it; M36 prescribes it.

## B. Receive system
- **Short ball:** push short, **banana/chiquita** flick, or stop. Goal: deny the 3rd-ball attack.
- **Long ball:** open with a loop / drive. Goal: take the initiative first.
- Principle: **never give the same receive twice** — vary spin/placement to break the server's plan.

## C. Placement principles (the 3 hardest targets)
1. **Wide forehand** (pull them off the corner).
2. **Wide backhand** (open the diagonal).
3. **The crossover / "middle" (playing elbow)** — the transition point between FH and BH; the single highest-value target, especially vs two-winged loopers and penholders.
- Plus: **depth control** (deep to push back; short to bring in) and **down-the-line vs cross-court** changes.

## D. The matchup playbook — how to beat each style (feeds M35/M36)

### vs Two-winged Looper / Attacker
- **Take time away:** quick blocks, take the ball early, redirect angles.
- **Target the crossover (elbow)** — forces an awkward FH/BH decision.
- **Don't feed clean topspin** to their strong wing; vary spin & depth.

### vs Chopper / Modern Defender
- **Vary spin sharply:** alternate **heavy** loops with **no-spin/soft** balls — choppers need your pace/spin to work with.
- **Avoid medium-pace attacks** (most comfortable for them to chop).
- **Bring them in with a drop shot, then attack** the next ball with timing & placement (the classic Ma Lin pattern).
- Attack **wide** and change pace; be **patient** — build the point.

### vs Short-pips Hitter (close-table)
- **Take them away from the table:** deep balls, **heavy spin**, **wide angles** → short pips are strongest close/over the table and weak when pushed back.
- **Don't serve/receive short-into-short** (their comfort zone), especially vs short-pips penholders.

### vs Long-pips / Anti (spin reversal)
- **Understand reversal:** their rubber **converts your topspin → backspin** and vice-versa; read the **returned** ball, not your own stroke.
- **DO NOT serve sidespin** to the pips/anti; use **topspin and backspin** serves; prefer **long/varied** placement.
- **Loop with LESS spin** — heavy topspin gets amplified into a nasty underspin return.
- **Sometimes give no spin/pace** — very hard for pips to work with.
- **Set up the 3rd ball:** e.g. a **long backspin serve to the long-pips side**, then attack the weak return.
- Attack **after** forcing a weak return through placement variation — not immediately.

### vs Penhold (incl. RPB)
- Penholders are often **strong loopers**, especially forehand; pressure the **backhand/transition** and the **wide BH**.
- Against **RPB**, target the **switch point** between RPB and FH (the crossover) and rush their transition.

## E. Score-situation & psychological tactics
- **Pressure points (deuce, game points):** go to your **highest-percentage** serve/pattern, not your fanciest.
- **Momentum:** when losing 3+ in a row → **change something** (serve, placement, pace) or call a **timeout**.
- **Read tells:** pre-serve routine, recovery position, repeated patterns → exploit predictability.

## F. Platform implications
| Need | Mechanism |
|------|-----------|
| Game-plan generation (M36) | **grounded** on this playbook + the opponent's detected style/equipment (Parts 19–20) → opponent-specific plan (Part 17) |
| Matchup edges (M35) | style-vs-style priors seeded here, refined by data (style A vs B outcomes) |
| Pattern detection (M31) | serve→return→3rd-ball matrices; sequence mining |
| Reliability (Part 10) | every tactic carries **evidence** ("opponent lost 7/9 vs no-spin to the middle") + confidence; thin data → "preliminary" |

> The matchup model starts with these **expert priors** (so it works on day one, cold-start), then **learns** the real edges from accumulated match data — exactly the fallback→model pattern of Part 18.

## Sources
- [Playing against pips/anti — Butterfly](https://butterflyonline.com/playing-against-pipsanti/) · [Playing against choppers — Butterfly](https://butterflyonline.com/playing-against-choppers/)
- [How to beat long pips — Table Tennis Teacher](https://tabletennisteacher.com/how-to-beat-long-pips-in-table-tennis/) · [How to beat choppers — Table Tennis Teacher](https://tabletennisteacher.com/how-to-beat-choppers-in-table-tennis/)
- [Play with & against long pips & anti — Paddle Palace](https://blog.paddlepalace.com/2025/01/how-to-play-with-against-long-pips-anti-full-tutorial/) · [Long pimples overview — Pong.sg](https://www.pong.sg/blog/long-pimples-overview)

---

➡️ **NEXT FILE: `22_TRAINING_DRILLS_AND_METHODOLOGY.md`**
