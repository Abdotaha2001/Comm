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
| **R18** | Security breach / exfiltration of biometrics + minors' data | Security | M | H | Part 31 controls, encryption, least-privilege, pentest, IR plan (Part 34.AF/BS) |
| R19 | Model drift — accuracy decays after deploy | ML | M | H | drift monitors + scheduled re-eval; golden-set gate (Part 29/34.S) |
| **R20** | LLM gives confidently-wrong tactical/coaching advice | ML/Product | M | H | grounded-only + citations, human review, abstain (Part 34.BB / R13) |
| R21 | Pretrained-asset license change / vendor shutdown | Data/Ops | M | M | adapter isolation + license tracking + fallback model (Part 34.AE/AT) |
| R22 | Bus factor — knowledge lives in two heads | Team | H | M | ADRs + `CLAUDE.md` + runbooks; write it down (Part 34.O/BA) |
| R23 | Reputational — a wrong call / biased output goes public | Market/Legal | M | H | advisory-mode (R13), fairness gate (Part 34.BF), responsible disclosure |
| R24 | Regulatory change (EU AI Act, biometric law) | Legal | M | M | compliance-as-code + configurable controls; DPO watch (Part 34.BS/31) |
| **R25** | Competitor copies the wedge (Stupa adds a game-plan loop) | Market | M | H | ship speed + data moat + para/Arabic depth (Part 33); keep moving |
| R26 | Efficacy unproven — metrics don't predict real wins | Science/Product | M | H | efficacy study + coach validation + plan→outcome loop (Part 16) |
| R27 | Adversarial gaming / spoofed footage | Security/ML | L | M | tamper-evidence (Part 35.T), anomaly checks, provenance (Part 34.AK) |
| **R28** | Safeguarding incident — a minor's data misused | Legal/Ethics | L | H | field-level RBAC, consent gates, audit; **zero-tolerance** (Part 31/34.AJ) |
| R29 | Cash runway runs out before P1 | Business | M | H | tight scope (R16), pilots/grants, staged spend (Part 15) |
| **R30** | Scope creep — the spec is huge, product never ships | Product/Team | H | H | `BUILD_ORDER` P0/P1 discipline, reuse-first, defer P2–P4 |

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
| A7 | Real-venue capture will mostly clear the input-quality gate | invest more in the capture SOP/hardware (Part 35) or lower output ambitions |
| A8 | Federations/academies will share data under agreement | rely on synthetic + own-captured data (Part 12/34.BJ) |
| A9 | Reliability/abstain UX builds trust, doesn't frustrate | redesign how confidence is surfaced (Part 32.J) |
| A10 | The market wants TT-specific depth, not a generic sports tool | broaden sport coverage / re-position |

## D. Process
- Review this register **each phase gate**; update L/I + status; add new risks as they appear.
- Every assumption has a **validation plan** (a cheap test) before we bet big on it.
- Owners assigned per risk once the team grows beyond two.

## E. Risk scoring & heat map
- **Score = L × I** (H = 3 · M = 2 · L = 1) → 1–9; **RAG:** 6–9 **red**, 3–4 **amber**, 1–2 **green**; track a **trend (↑ / → / ↓)** at each gate.
- **Reds** get a named **owner + dated mitigation + a contingency** (Part 36.G); greens are watched, not worked. Current reds: **R1, R5, R9, R16, R30** (and R12/R13 by impact).

## F. Early-warning indicators (leading signals)
| Risk | Trip-wire that says it's materialising |
|------|----------------------------------------|
| R1 / R19 | golden-set accuracy dips below the gate, or a drift monitor alarms |
| R9 / R25 | a competitor ships an opponent-specific game-plan feature |
| R10 / R26 | coach usefulness rating < target; game plans not adopted |
| R16 / R30 | velocity < plan; P1 scope expanding; "just one more feature" |
| R12 / R28 | any consent gap or access-control finding in an audit |
| R29 | runway < 6 months |
- Each indicator has a **pre-agreed threshold + action** — decided cold, not renegotiated mid-crisis.

## G. Contingency / fallback (if mitigation fails)
- **Accuracy (R1/R5):** ship in **advisory + abstain** mode, narrow to what clears the gate; buy/partner for data.
- **Officiating (R13/R23):** stay **assistive-only, never decisive**, until externally validated.
- **Incumbent (R9/R25):** retreat to the **defensible niche** (para + Arabic + reliability), not a feature war.
- **Team / runway (R16/R29):** cut to the **flagship loop only**; pause P2–P4; pursue pilot revenue/grants.

## H. Risk appetite (where we will / won't take risk)
- **Zero tolerance:** minors' data & consent, security of biometrics, officiating-as-decisive, **honest confidence** (never fabricate a number).
- **Higher tolerance:** feature breadth, polish, non-flagship models — we ship **"preliminary" + labelled** rather than wait for perfection.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
