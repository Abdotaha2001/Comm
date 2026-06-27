# PART 19 — DOMAIN KNOWLEDGE: OFFICIAL RULES, FULL SKILL TAXONOMY & THE MATH

> Read `00_INDEX.md` first. This is the **authoritative ground-truth reference** the models, labels, and rubrics are built against. Sourced from ITTF laws + elite coaching references (see Sources). Equations are the physical/ML backbone of every engine.

---

## A. OFFICIAL ITTF RULES (the umpire engine's specification)

### A1. Equipment specs (calibration constants)
| Item | Spec |
|------|------|
| Table | 2.74 m (L) × 1.525 m (W) × 0.76 m (H) |
| Net | 15.25 cm high, posts extend 15.25 cm beyond each sideline |
| Ball | 40 mm diameter, 2.7 g, white or orange, matte |
| Racket | blade ≥ 85% natural wood; one side **black**, other **red** (or ITTF-approved green/blue/violet/pink) |
| Surface | dark, matte; coefficient constants for physics in §C |

### A2. The Service Law (the hardest officiating target → needs 3D, Part 02)
A legal serve requires **all** of:
1. Ball rests on the **open, flat palm**, stationary.
2. Ball is **behind the end line** and **above the table level** at start.
3. Ball is tossed **near-vertically, ≥ 16 cm**, without imparting spin from the hand.
4. Ball is struck **as it descends**.
5. At contact, ball is **behind the end line** and above the playing surface.
6. Ball is **not hidden** from the receiver (free arm/body removed; visible throughout).
7. On serve, ball bounces **once on server's side, then once on receiver's side**.

### A3. A good return
Returned so it touches the opponent's court **after passing over or around** the net assembly (edge "around" is legal).

### A4. Order of play / point scoring
- Serve alternates **every 2 points**; at **10–10 (deuce)** alternates **every 1 point**.
- Game to **11**, win by **2**. Match = best of odd number (best of 5 / 7).
- A **point** is lost if a player: fails a legal serve/return; lets the ball bounce twice on their side; double-hits; hits the ball before it crosses to their side; strikes with the side edge / non-racket hand; moves the table or touches the net assembly in play; (doubles) hits out of the partner sequence.

### A5. Let (replay, no point)
- Serve **touches the net** but otherwise lands correctly.
- Receiver **not ready** (no attempt to strike).
- Play disturbed by **external interference**.

### A6. Edge vs side
**Top edge** ball = good (in play). **Side** of the table = out.

### A7. Doubles
- Serve must go **diagonally**: server's **right half-court → receiver's right half-court**.
- Strict **alternation of hitters** within a rally; serve/receive **rotation** as defined per game; positions switch each game and at 5 in the deciding game.

### A8. Expedite system
- Triggers if a game is **unfinished after 10 minutes** (unless ≥ 18 points already scored), or earlier by mutual request.
- After trigger: each player **serves 1 point in turn**; if the **receiver makes 13 good returns**, the receiver **wins the point**.

---

## B. FULL SKILL TAXONOMY (the technique models' label set — Part 18 M22–M26)

### B1. Serves (with spin signature)
| Serve | Motion / spin | Rarity |
|-------|---------------|--------|
| Forehand **Pendulum** | racket tip down, R→L, sidespin breaking into BH | most common |
| **Reverse Pendulum** | reverse wrist L→R, opposite sidespin, deceptive | common (advanced) |
| **Tomahawk** | racket up/away, anti-clockwise sidespin, face table directly | moderate |
| **Reverse Tomahawk** | opposite of tomahawk, clockwise spin | rare |
| **Shovel** | arm-driven (not wrist), anti-clockwise, easier reverse-pendulum cousin | moderate |
| **Backhand sidespin** | one of the four dominant serves | common |
| **High-toss** | very high toss → extra spin/speed via gravity | moderate |
| **Ghost serve** | extreme backspin, ball returns toward net | niche |
| **No-spin / fast-long** | deception by absence of spin / sudden long | tactical |

### B2. Receive
Short push · Long push · **Flick/Flip** (compressed wrist attack of a short ball) · **Banana Flick / Chiquita** (BH side-top spin over the table) · Strawberry flick (reverse-banana) · **Stop/drop** · Block (vs serve) · Long push to wide angle.

### B3. Attack
**Drive** (control/pressure, mild topspin) · **Loop / loop-drive** (grazing brush → heavy topspin, arcs and kicks forward) · **Counterloop** (loop vs incoming topspin) · **Smash / Kill** (max-speed flat finish of a high ball) · **Flat hit**.

### B4. Defense
**Block** (passive return of energy) · **Active / punch block** · **Soft block** · **Chop block** (block with backspin) · **Chop** (heavy backspin from well back, matches opp topspin) · **Fish** (soft topspin lob-defense near/mid) · **Lob** (high defensive ball from 2.5–6 m back).

### B5. Footwork (Part 18 M26) — with elite-match frequencies
| Step | Use | Elite frequency* |
|------|-----|------------------|
| **One-step** | small adjust, last-resort | **37.3%** |
| **Turn / Pivot** | BH-corner pivot to FH | **21.1%** |
| **Chassé (side-step)** | medium-distance, harder strokes | **15.2%** |
| Stroke without step | in-position | 11.5% |
| **Slide / shuffle** | short quick side-to-side | 7.5% |
| **Cross-step / crossover** | wide coverage | 7.3% |

*Source: elite-match footwork study (see Sources). These priors seed the footwork model and the "court coverage" metric.

### B6. Spin types (Part 18 M12/M13 label set)
Topspin · Backspin (underspin) · Sidespin (left / right) · **Corkspin** (drill/rotational about flight axis) · Mixed (topspin+side, back+side) · **No-spin**. Quantify by **axis** (unit vector ω̂) and **rate** (RPM).

### B7. Additional strokes & variations (found in deeper research — extends M22–M26 labels)
| Technique | What it is |
|-----------|-----------|
| **Hook loop** | loop brushing the **outside** of the ball → adds sidespin curving one way |
| **Fade loop** | loop brushing the **inside** of the ball → breaks into the opponent's crossover |
| **No-spin loop** | loop motion with minimal spin — deception even at top level |
| **Power loop vs spin (brush) loop** | speed-dominant vs spin-dominant loop (intensity classes) |
| **Counter-drive / counter-hit** | aggressive off-the-bounce counter with closed racket (between block and counterloop) |
| **Drop shot** | short, soft touch off a topspin to bring the opponent in |
| **Dig** | reflex defensive return of a smash from close to the table |
| **Hook serve** | deceptive sidespin serve (kin to reverse-pendulum/BH spin), topspin disguised as backspin |
| **Windshield-wiper serve** | wiping motion producing variable spin incl. **no-spin** by "bumping" |
| **Fast/long (deep) serve** | sudden deep fast serve to surprise / force a weak block |
| **Push variations** | short / long / **fast** / **heavy (slow)** / **sidespin** push |
| **Block variations** | passive / **active (punch)** / **soft** / **jab** / **chop** / **sidespin** block |
| **Chop variations** | heavy / **float (no-spin)** / **sidespin** chop |
| **Twiddle** | **rotating the racket in the hand** mid-rally to switch rubber sides (combination-bat choppers) — a deception skill of its own |

### B8. Playing styles (the **matchup taxonomy** — powers Part 17 + models M34/M35)
| Style | Signature |
|-------|-----------|
| Shakehand **FH looper** | wins with fast spinny forehand loops (dominant men's style) |
| Shakehand **two-winged attacker** | backhand loop as a primary weapon too |
| **Counter-driver / blocker** | close to table, blocks & drives, changes angle/rhythm |
| **All-rounder** | reflexes + defensive placement, adapts |
| **Chopper / modern defender** | heavy backspin chops from distance, twiddles, varies spin |
| Penhold **FH looper** | penhold grip, forehand-dominant |
| Penhold **two-sided looper (RPB)** | reverse-penhold-backhand for both wings |
| **Short-pips hitter** | flat fast hitting over the table, negates spin |
| **Combination-bat chopper** | inverted one side + long pips/anti other side + twiddle |

### B9. Grips (technique interpretation — model M19, Part 04)
Shakehand · Penhold (Japanese/Korean traditional) · Penhold (Chinese, with **RPB**) · **Seemiller** (American) · rare: V-grip / others. Grip changes stroke mechanics → the classifier must condition on it.

### B10. Rubber / material types (spin-reading **priors** — links Part 14 equipment + M12 spin)
**Inverted / smooth** (standard spin) · **Short pips** (flat, fast, low spin) · **Long pips** (spin-reversal, insensitive) · **Anti-spin** (negates spin). The spin model must know the rubber, because **long pips/anti invert the expected spin** — a major source of error if ignored.

---

## C. THE MATH (the "strongest approach" — physics + CV + ML)

### C1. Ball flight (aerodynamics) — drives spin/speed/landing models
Newton's 2nd law on the ball (mass m, radius r=0.02 m):

```
m·dv/dt = m·g  −  ½·ρ·C_d·A·|v|·v  +  F_Magnus
```
- Gravity `g = 9.81 m/s² (−ĵ)`; air density `ρ ≈ 1.21 kg/m³`; area `A = πr²`.
- **Drag:** `F_D = −½·ρ·C_d·A·|v|·v` (opposes velocity).
- **Magnus (spin lift):** `F_M = ½·ρ·C_L·A·|v|²·n̂`, with `n̂ = (ω×v)/|ω×v|`.
- **Spin parameter:** `S = r·|ω| / |v|`  →  `C_L = f(S)`, `C_d = f(Re, S)`.
- **Reynolds:** `Re = ρ·|v|·(2r)/μ` (μ ≈ 1.81e-5). For 40 mm ball at match speeds Re ≈ 10⁴–10⁵.

This ODE (integrate with RK4) is the **forward model** for trajectory + landing prediction (M11) and the basis for **spin-from-curvature** inference (below).

### C2. Bounce on the table (event + post-bounce state)
- Normal restitution: `v_n' = −e_n·v_n`, with `e_n ≈ 0.85–0.90` (ball/table).
- Hollow-sphere inertia `I = (2/3)·m·r²`. Tangential coupling (spin↔surface):
  - **Sliding** case: `v_t' = v_t − μ(1+e_n)|v_n|`, `ω' = ω − (5μ(1+e_n)|v_n|)/(2r)`.
  - **Rolling** (no-slip) limit: `v_t' = (v_t − (2/5 effective)·rω)/(1+2/5)` (use hollow-sphere factor). 
- These give the **kick** of a topspin loop and the **sit** of backspin → labels for spin verification.

### C3. Single-camera geometry (Tier T1/T2)
- **Homography** (planar table → metric): `λ·[u v 1]ᵀ = H·[X Y 1]ᵀ`, H ∈ ℝ³ˣ³ from ≥4 known corners. Gives `px_per_m` and image↔table mapping.
- **PnP** (camera pose): `s·[u v 1]ᵀ = K·[R|t]·[X Y Z 1]ᵀ`; solve `R,t` from the known table geometry (4+ corners) → enables pseudo-3D + the toss-height attempt with explicit confidence penalty.
- **Speed:** `v_kmh = (Δp_px / px_per_m)/Δt · 3.6`.

### C4. Multi-camera 3D (Tier T3)
- **Triangulation (DLT):** for cameras with projection `P_i`, point `X` satisfies `x_i × (P_i·X)=0`; stack rows → `A·X=0`, solve via **SVD null-space**.
- **Bundle adjustment:** `min_{X,P} Σ_i ‖x_i − π(P_i, X)‖²` (Levenberg–Marquardt). Enables true 3D trajectory → real spin/RPM and **16 cm toss measurement** for officiating.

### C5. Tracking (ball + players)
- **Kalman (constant-acceleration)** state `s=[x,y,vx,vy,ax,ay]`:
  - Predict: `s⁻=F·s`, `P⁻=F·P·Fᵀ+Q`.
  - Update: `K=P⁻Hᵀ(H·P⁻·Hᵀ+R)⁻¹`, `s=s⁻+K(z−H·s⁻)`, `P=(I−K·H)·P⁻`.
- **Data association (Hungarian):** `min Σ C_ij·x_ij` over assignments, cost `C = 1−IoU` (or `α·motion + β·appearance`).

### C6. Spin from monocular trajectory curvature (T2 — spin without high-speed cam)
- Lateral acceleration from Magnus: `a_⊥ ≈ (ρ·A·C_L(S)·|v|²)/(2m)`.
- Trajectory curvature `κ = |v×a|/|v|³`. Fit observed `κ(t)` to the C1 model → solve `|ω|, ω̂`. Confidence scales with track length/SNR (Part 10).

### C7. Biomechanics (pose → kinetics, Part 18 M27)
- **Joint angle:** `θ = arccos((a·b)/(|a|·|b|))` for limb vectors a,b. Angular velocity `ω_j = Δθ/Δt`.
- **Kinetic-chain sequencing:** peak angular-velocity timestamps must order **proximal→distal**: `t_hip < t_trunk < t_shoulder < t_elbow < t_wrist`. Efficiency ∝ ratio of distal:proximal peak speeds and tightness of the timing cascade.
- **Center of mass** from segment masses (Dempster ratios); **balance** = COM projection within base of support.

### C8. Machine-learning objectives & reliability math
| Need | Formulation |
|------|-------------|
| Detection | IoU `=|A∩B|/|A∪B|`; mAP over IoU thresholds |
| Class (rare: ball, rare serves) | **Focal loss** `L=−α(1−p)^γ·log p` |
| Regression (speed/angle/RPM) | **Huber / Smooth-L1** |
| ID embeddings (face/style/ReID) | **Triplet** `max(0,d(a,p)−d(a,n)+m)`; **ArcFace** additive-margin softmax |
| Calibration (Part 10) | **Temperature scaling** `p=softmax(z/T)`; **ECE** `=Σ_b (n_b/N)·|acc_b−conf_b|` |
| Uncertainty / abstain | predictive entropy `H=−Σ p·log p`; deep-ensemble / MC-dropout variance; **abstain if H>τ** |
| Win probability | calibrated `P(win|state)=σ(wᵀφ(state))` or sequence model |
| Pattern mining | Markov `P(s_{t+1}|s_t)`; PrefixSpan / n-gram for rally sequences; transformer rally embeddings |

---

## D. DOMAIN → MODEL → MATH MAP
| Domain target | Model (Part 18) | Key features / equations |
|---------------|-----------------|--------------------------|
| Serve legality (16 cm, hidden) | M38 | C4 triangulation + toss-height; visibility geometry |
| Spin type / axis / RPM | M12/M13 | C1 Magnus, C6 curvature, C2 bounce coupling |
| Stroke class | M22–M24 | pose+ball+racket temporal features; C7 |
| Stroke quality | M25 | C7 kinetic-chain sequencing vs elite rubric |
| Footwork | M26 | step classification; B5 priors; C7 balance |
| Speed | M14 | C3/C4 calibration |
| Landing/ETA | M11 | C1 forward ODE (RK4) |
| Scoring/point | rules engine | A4 conditions + reliability cross-check (Part 10) |
| Win prob / xP | M32/M33 | C8 calibrated sequence model |

---

## Sources
- [ITTF Statutes / Laws of Table Tennis (2024–2025)](https://documents.ittf.sport/sites/default/files/public/2024-02/2024_ITTF_Statutes_clean_version.pdf) · [ITTF rules (megaspin mirror)](https://cdn.megaspin.net/rules/pdf/2025/ittf-rules-2.pdf)
- [Rules for Table Tennis — Racket Insiders](https://racketinsiders.com/rules-for-table-tennis/)
- [Every Ping Pong Serve — Table Tennis Teacher](https://tabletennisteacher.com/serves/) · [Reverse pendulum — PingSunday](https://pingsunday.com/reverse-pendulum-serve/)
- [Types of shots — Ping Pong Wiki](https://pingpong.fandom.com/wiki/Types_of_shots) · [Advanced techniques — Megaspin](https://www.megaspin.net/info/advanced.asp)
- [Footwork patterns — Table Tennis Teacher](https://tabletennisteacher.com/footwork/) · [Chassé vs one-step biomechanics (elite study, PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12131136/)
- [Glossary of table tennis — Wikipedia](https://en.wikipedia.org/wiki/Table_tennis_terminology) · [Table tennis styles & grips — Wikipedia](https://en.wikipedia.org/wiki/Table_tennis_styles)
- [Hooks and fades (sidespin loops) — Expert Table Tennis](https://www.experttabletennis.com/hooks-and-fades/) · [Twiddling — Samson Dubina Academy](https://samsondubina.com/coaching/twiddling) · [Advanced techniques — Megaspin](https://www.megaspin.net/info/advanced.asp)

---

➡️ **NEXT FILE: `20_EQUIPMENT_INTELLIGENCE.md`**
