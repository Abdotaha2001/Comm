# PART 40 — RELIABILITY, CONFIDENCE & CALIBRATION (Authoritative Specification)

> Read `00_INDEX.md` first. This is the **authoritative reliability law** of the platform — the build-ready formalization of the *Reliability Awareness* cross-cutting layer (00_INDEX §2). It turns "every number carries calibrated confidence + provenance, and the system can say *I don't know*" (Part 10) into a precise, enforceable contract.
>
> It is the SSoT for: the reliability envelope, confidence semantics, calibration methodology, abstention policy, uncertainty propagation, capture-tier coupling, and the governance that keeps the platform **honest**.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`. RFC-2119 keywords are normative. Status: ✅ `IMPLEMENTED` (in `backend/app/capture_quality.py` + analysis `reliability_index`) · 🟡 `PARTIAL` · ⬜ `SPECIFIED` (calibration of trained models, since the CV layer is the classical baseline today).

---

## A. Scope & Objectives

### A.1 Purpose
Guarantee that **no platform output overstates its certainty**. Every measured value carries a calibrated confidence and provenance; below threshold the system **abstains** rather than guesses.

### A.2 Goals
- **G1.** Every *measured* value **MUST** be wrapped in the reliability envelope (§C).
- **G2.** Every `confidence` **MUST** be **calibrated** — it means what it says (§D/§G).
- **G3.** Uncertainty **MUST** propagate and **MUST NOT** be averaged away (§H).
- **G4.** Capture tier **MUST** cap reliability (§I, Part 35).
- **G5.** Abstention **MUST** be a first-class result, never a fabricated number (§F).

### A.3 Non-goals
- Not a model catalog (Part 18) nor an eval-metrics catalog (Part 29) — it **uses** Part 29 metrics as gates.
- Not the capture acceptance schema (Part 35) — it **consumes** the capture grade as a ceiling.

### A.4 Relationship to Parts
Formalizes Part 10; binds Part 27/37 (envelope on measured fields), Part 29 (calibration metrics + gates), Part 35 (capture grade → reliability ceiling), Part 39 (reliability events), Part 34.AL (reliability as a first-class type), Part 34.AK (provenance).

---

## B. Principles

- **B.1 Honesty over completeness.** A correct "I don't know" is **better** than a confident wrong answer. The system **MUST** prefer abstention to fabrication.
- **B.2 Calibrated, not raw.** A `confidence` **MUST** be a calibrated estimate of correctness, **not** a raw softmax/score (§D/§G).
- **B.3 No averaging away uncertainty.** Aggregations **MUST** preserve the weakest link; a result built from thin/low-confidence inputs **MUST** stay low-confidence (§H; cf. the capture min-gate, Part 35.AJ).
- **B.4 Tier-aware.** Confidence is bounded by the capture tier + certification (§I).
- **B.5 Provenance-bound.** Every envelope **MUST** be traceable to the model/code/data versions that produced it (§J, Part 34.AK).
- **B.6 Markerless honesty.** Uncalibrated/markerless estimates (e.g. spin from a single phone) **MUST** cap confidence and flag themselves (§M).

---

## C. The Reliability Envelope

Every measured value **MUST** be emitted as the canonical envelope (Part 10/27). Bare numbers are forbidden (§R).

| Field | Type | Req | Meaning |
|-------|------|-----|---------|
| `value` | number\|enum\|null | MUST | The estimate; `null` **iff** `status = abstain` |
| `confidence` | number `[0,1]` | MUST | Calibrated correctness/coverage probability (§D) |
| `ci` | `[low, high]`\|null | SHOULD | Confidence interval for continuous values (units, Part 34.AC) |
| `tier` | enum `T1\|T2\|T3\|T3_OFFICIATING` | MUST | Capture tier the value was produced under (§I) |
| `source` | object | MUST | Provenance: `{model, model_version, code_sha, signals}` (§J) |
| `status` | enum (§E) | MUST | Reliability status |
| `calibrated` | bool | SHOULD | Whether `confidence` came from a calibrated model (§D/§M) |
| `unit` | string | MUST³ | Physical unit for continuous values (Part 34.AC) |

³ Required for continuous physical quantities (speed, spin). The reference implementation is `build_reliability_envelope()` in `backend/app/capture_quality.py` (capture-level) ✅; the per-value envelope on analysis outputs (speed/spin/placement) is 🟡 and **MUST** converge to this schema.

## D. Confidence Semantics

- **D.1** `confidence ∈ [0,1]` **MUST** be interpretable as a probability: for a **classification**, P(prediction correct); for a **continuous** value with a `ci`, the interval's **coverage** probability (e.g. 0.9 → the true value lies in `ci` ~90% of the time).
- **D.2** A raw model score (softmax, IoU, blob brightness) **MUST NOT** be reported as `confidence` unless it has been **calibrated** (§G); if uncalibrated, `calibrated=false` and confidence **MUST** be capped (§M).
- **D.3** Confidence **MUST NOT** be hand-set to a flattering constant; it **MUST** derive from the model + calibration + tier (§I).
- **D.4** Two different quantities **MUST NOT** share one confidence; each measured value carries its own.

## E. Status Taxonomy

`status` is the human/dashboard-facing reliability state (dashboard colors, Part 32.J / Part 39 §AF). Canonical set + mapping:

| status | Confidence band | Meaning | UX |
|--------|-----------------|---------|----|
| `verified` | ≥ 0.95 **and** ground-truth/officiating-validated | externally validated (Platinum capture, Part 35) | green |
| `high` | ≥ 0.90 | strong evidence | green |
| `moderate` | 0.70–0.90 | usable, caveated | amber |
| `preliminary` | 0.50–0.70 **or** thin data | indicative only; "preliminary" badge | amber/grey |
| `unreliable` | < 0.50 (reported only with a warning) | weak; SHOULD prefer abstain | grey |
| `abstain` | below the per-domain decision threshold | the system declines to assert; `value = null` | "not sure — needs review" |

Bands are defaults; per-domain thresholds (§K) **MAY** be stricter. `verified` **MUST NOT** be claimed without external/ground-truth validation.

## F. Abstention Policy

- **F.1** The system **MUST** `abstain` when confidence is below the domain's decision threshold (§K), when inputs are missing/occluded, when calibration is invalid (§G), or when the capture grade forbids the output (§I/Part 35).
- **F.2** Abstention is a **successful result**, not an error: API returns `200` with `status="abstain"` and `value=null` (Part 37 §Q, code `abstained`); it **MUST NOT** be an HTTP error.
- **F.3** An abstained value **MUST NOT** be silently coerced to a default, zero, or last-known value.
- **F.4** Abstention **SHOULD** emit `tt.analysis.run.abstained` (Part 39 §M/§AP) and **MAY** trigger human escalation (§Q).
- **F.5** Repeated abstention on a stream **MUST** surface an input-quality prompt (Part 32.K) rather than degrade silently.

## G. Calibration Methodology

- **G.1** Each model whose outputs carry confidence **MUST** be **calibrated** on a held-out set and ship a **calibration record** (method, date, dataset version, ECE) with its model card (Part 29).
- **G.2** Permitted methods: **temperature scaling** (default for neural classifiers), **Platt scaling**, **isotonic regression**; the chosen method **MUST** be recorded (§J).
- **G.3** Calibration quality **MUST** be measured by a **reliability diagram** + **Expected Calibration Error (ECE)** and **Maximum Calibration Error (MCE)**; for intervals, **PICP** (prediction-interval coverage) vs nominal (§N, Part 29).
- **G.4 Gate:** a model **MUST NOT** be promoted (Part 39 `tt.ml.model.approved`) if **ECE > target** (default ECE ≤ 0.05) or PICP deviates from nominal beyond tolerance (Part 29 release gate).
- **G.5 Recalibration triggers:** drift (Part 29/39 `drift_detected`), a new data regime, or a capture-condition shift **MUST** trigger recalibration; stale calibration **MUST** down-weight confidence (§M).
- **G.6** The classical baseline detectors (today) are **uncalibrated** → they **MUST** report `calibrated=false` and capped confidence (§M) until a calibrated model replaces them.

## H. Uncertainty Propagation & Aggregation

- **H.1 Composition.** When a result depends on a chain (detection → tracking → physics → statistic → profile), its confidence **MUST** reflect the chain — by **multiplication** of independent stage confidences or the **minimum** of required stages, **never** their average.
- **H.2 Intervals.** Continuous `ci`s **MUST** propagate via analytic error-propagation or Monte-Carlo; the output `ci` **MUST NOT** be narrower than its inputs justify.
- **H.3 No dilution.** Aggregating many low-confidence items **MUST NOT** manufacture a high-confidence aggregate; sample size + per-item confidence bound the aggregate (e.g. a profile stat over 5 thin rallies stays `preliminary`).
- **H.4 Min-gate for required components.** Where a result requires several components to all hold (e.g. an officiating call, a capture certification), the result confidence **MUST** be the **minimum** of the required components (Part 35.AJ). A single failed/abstained required component → the result abstains.
- **H.5 Determinism.** Propagation **MUST** be deterministic (fixed seeds, Part 34.AD) so the same inputs yield the same envelope.

## I. Capture-Tier Coupling

- **I.1** The capture **tier** + **certification** (Part 35) set a **reliability ceiling**; the final confidence **MUST** be `min(model_confidence, tier_ceiling)` — never an average (Part 35.AK).
- **I.2** Default ceilings (the `reliability_ceiling` SoT, Part 35 schema): Platinum 1.0 · Gold 0.9 · Silver 0.75 · Bronze 0.6 · **Fail → abstain**.
- **I.3** A `fail` capture **MUST** force dependent outputs to `abstain` regardless of model confidence.
- **I.4** Outputs that a tier physically cannot support **MUST** be withheld (e.g. true 3D spin on T1) — the envelope `status` is `abstain` with a tier reason (§L).

## J. Provenance Binding

- **J.1** Every envelope's `source` **MUST** record `{model, model_version, code_sha, calibration_version, capture_tier, signals}` and tie to a provenance record + hash (Part 34.AK).
- **J.2** A measured value **MUST** be reproducible from its provenance (same model+code+inputs+seed → same envelope, Part 34.AD).
- **J.3** Provenance **MUST** be carried through events (Part 39 §C `provenance_hash`) and persisted with the result (Part 37 §I).

## K. Per-Domain Reliability Rules

| Domain | Rule | Default abstain threshold |
|--------|------|---------------------------|
| Ball detection (CV) | classical baseline uncalibrated → cap; below visibility → abstain (Part 35.AD) | conf < 0.5 or visibility < 90% |
| Tracking | broken track → abstain that segment | track continuity < 0.8 |
| Speed (physics) | requires calibration (T2+); uncalibrated → cap + `preliminary` | no calibration on T1 |
| Spin / RPM | markerless → cap; true RPM needs T3/high-speed (Part 35) | T1/T2 cap to `preliminary`; below → abstain |
| Scoreboard OCR | low-confidence digit → abstain the read | per-digit conf < 0.9 |
| Stroke classification | below margin → abstain the label | top-1 margin < threshold |
| Profile / dossier | thin data → `preliminary`; confidence bounded by sample (§H.3) | < min_sample |
| Officiating call | advisory-only until validated; min-gate (§H.4); below → abstain (Part 09) | any required component abstains |

Thresholds are **config**, not magic numbers (Part 34.AL), and tie to the Part 29 targets.

## L. Reliability Across Capture Tiers

| Tier | Allowed outputs | Confidence bound |
|------|-----------------|------------------|
| **T1** (single cam 2D) | 2D events, stats, scoreboard, **coarse** spin/speed | capped (Bronze/Silver ceiling); spin/speed `preliminary`, uncalibrated flagged |
| **T2** (single cam + calibration) | metric placement, better speed, spin-from-curvature | up to Gold ceiling; calibrated speed |
| **T3** (multi-cam 3D) | true 3D, real spin/RPM | up to Gold/Platinum; officiating-eligible only at Platinum |
| **T3_OFFICIATING** (Platinum) | decisive officiating | `verified` permitted (ground-truth validated, Part 35.T) |

An output requested above the active tier's capability **MUST** `abstain` with a tier reason, never approximate silently.

## M. Honesty Flags & "Preliminary"

- **M.1** Uncalibrated, markerless, or stale-calibration estimates **MUST** set `calibrated=false` and **MUST** be capped at `preliminary` (≤ 0.7) regardless of raw score.
- **M.2** Thin-data results **MUST** carry a "preliminary" status + the sample size (Part 32.J).
- **M.3** The UI **MUST** render the band + interval ("78 ± 6 km/h", amber) and **MUST NOT** show a bare number (§R, Part 32.J).
- **M.4** A "preliminary" output **MUST** prompt the action that would raise confidence (add footage, raise tier — Part 32.K).

## N. Measurement & Metrics (calibration catalog)

The reliability layer is itself measured (ties Part 29):

| Metric | Measures | Target (default) |
|--------|----------|------------------|
| **ECE** / **MCE** | calibration error (gap between confidence and accuracy) | ECE ≤ 0.05 |
| **Reliability diagram** | confidence vs empirical accuracy | on diagonal |
| **Brier score** | probabilistic accuracy | minimized |
| **PICP** | interval coverage vs nominal | within ± tolerance of nominal |
| **AURC / risk-coverage** | quality of the abstain ranking | low area |
| **Abstention rate** | how often the system declines | tracked per domain |
| **Selective accuracy** | accuracy on non-abstained outputs | ≥ target |

These **MUST** be reported in model cards and enforced at the release gate (Part 29 / §G.4).

## O. API & Persistence Representation

- **O.1 API:** measured fields **MUST** serialize as the envelope (§C); abstain → `200` with `status="abstain"`, `value=null` (Part 37 §Q).
- **O.2 Persistence:** the envelope **MUST** persist with the result (analysis `reliability_index` + per-value envelopes; capture `capture_acceptance.reliability_envelope`, Part 37 §H). The reference shape is `capture_quality.build_reliability_envelope()`.
- **O.3 Events:** reliability transitions emit Part 39 events (`abstained`, `reliability.reduced`, `reliability.capped`).
- **O.4** The envelope is **read-only** output; clients **MUST NOT** be able to set confidence.

## P. Reliability Events

- `tt.analysis.run.abstained` (EV-0019) — emitted on abstention; `data.confidence`+`reason` MUST be present.
- `tt.reliability.reduced` (EV-0046) — confidence lowered (e.g. drift, stale calibration).
- `tt.reliability.capped` (EV-0047) — capture-tier cap applied (§I, Part 35.AK).
- `tt.reliability.model.drift_detected` (EV-0053) — drift gate breach (Part 29).
These are AI/ML-taxonomy events (Part 39 §AF) carrying `provenance_hash`.

## Q. Human Escalation

- **Q.1** Abstention on a **consequential** decision (officiating, injury/medical, talent selection) **MUST** escalate to a human (Part 34.BQ); the system **MUST NOT** auto-decide (Part 34.BQ "AI assists, humans decide").
- **Q.2** Escalation **MUST** carry the evidence (frames/stats/envelope, Part 32.D) so a human can adjudicate.
- **Q.3** Contestability: a coach/player **MAY** challenge any value; the challenge path **MUST** surface the provenance + confidence (Part 34.BQ).

## R. Anti-Patterns (forbidden)

The following **MUST NOT** occur and **SHOULD** be lint/CI-detectable (§T):
- **R.1** Emitting a measured value as a **bare number** (no envelope).
- **R.2** Reporting a **raw, uncalibrated** score as `confidence` (without `calibrated=false` + cap).
- **R.3** **Averaging away** uncertainty (mean of confidences for a required-all result) (§H/§B.3).
- **R.4** **Hiding** abstention (coercing to default/zero/last value).
- **R.5** A **fabricated/constant** confidence not derived from model+calibration+tier.
- **R.6** Claiming `verified` without ground-truth validation; exceeding the **tier ceiling** (§I).
- **R.7** An interval `ci` narrower than inputs justify (false precision).

## S. Build Artifacts

| Artifact | Path | Owns | Status |
|----------|------|------|--------|
| Reliability envelope + cap | `backend/app/capture_quality.py` (`build_reliability_envelope`, `reliability_ceiling_for`) | envelope + tier cap | ✅ |
| Per-value envelope helper | `backend/app/reliability.py` | wrap measured outputs; status/abstain logic | ⬜ |
| Calibration store + calibrators | `backend/app/calibration.py` (+ model cards) | temperature/Platt/isotonic; ECE | ⬜ |
| Calibration metrics | `backend/app/benchmark.py` (extend) | ECE/MCE/PICP/Brier (Part 29) | 🟡 |
| Thresholds config | settings / per-model config | abstain thresholds (no magic numbers) | 🟡 |

`reliability.py` **MUST** expose: the envelope constructor, the status mapper (§E), the abstain decision (§F/§K), and the tier cap (§I) — and producers **MUST** route measured outputs through it.

## T. Governance & CI

CI **MUST** (ties Part 37 §Z / Part 34.AL):
- **T.1** assert every measured API field serializes the **envelope shape** (§C) — a schema test.
- **T.2** assert **abstain paths** exist + behave (a unit/integration test that a below-threshold/failed-capture input yields `status=abstain`, `value=null`, `200`).
- **T.3** enforce the **calibration gate** at model promotion (ECE/PICP, §G.4) — fail the release if breached.
- **T.4** lint for **anti-patterns** (§R): bare measured returns, constant confidences, averaging of required confidences (heuristic).
- **T.5** assert the **capture cap** holds: a fail/low capture caps `reliability_index` (already tested, Part 35) and forces abstain.
- **T.6** keep abstention/selective-accuracy metrics in the golden report (Part 29).

## U. Acceptance Criteria

Conforms **iff**:
- **U.1** No measured output is a bare number; all carry the envelope (§C) with provenance (§J).
- **U.2** Every reported `confidence` is calibrated **or** flagged `calibrated=false` + capped (§D/§M).
- **U.3** Uncertainty propagates by product/min, never average; aggregates of thin data stay low-confidence (§H).
- **U.4** Capture grade caps confidence; a fail capture abstains (§I).
- **U.5** Abstention is a first-class `200` result with `value=null`; never fabricated, never hidden (§F/§R).
- **U.6** Calibrated models pass the ECE/PICP gate before promotion (§G.4).
- **U.7** Consequential abstentions escalate to a human with evidence (§Q).

## V. Traceability

| Concept | Entity (37) | Event (39) | Ontology (38) | Parts |
|---------|-------------|------------|---------------|-------|
| envelope | analysis_run, shot, event | abstained/reduced/capped | `reliability_envelope`,`confidence` | 10/27/37 |
| calibration | model | drift_detected, calibration.updated | `calibration`,`benchmark` | 29/12 |
| tier cap | analysis_run, capture | reliability.capped | `capture_certification`,`capture_tier` | 35 |
| abstain | analysis_run | abstained | `abstain` | 10 |
| provenance | provenance_records | (all) | `provenance` | 34.AK |

---

## W. Aleatoric vs Epistemic Uncertainty

- Confidence **MUST** distinguish **aleatoric** uncertainty (irreducible input noise — occlusion, motion blur, low light) from **epistemic** uncertainty (model ignorance — OOD inputs, thin data).
- More data/training reduces **epistemic** only; **aleatoric** is bounded by capture quality (Part 35). The system **MUST** therefore route aleatoric problems to **capture improvement** (§M.4) and epistemic to **data/model improvement**.
- The envelope **SHOULD** expose both components in `source.signals`; their abstention reasons differ — high aleatoric → "improve capture", high epistemic → "out of distribution / needs review" (§F/§Y).

## X. Conformal Prediction

- For coverage **guarantees** without distributional assumptions, continuous estimates (speed, spin) and classifications **SHOULD** use **split-conformal prediction**: a held-out calibration set fixes a nonconformity threshold so the interval/set achieves a **target coverage** (e.g. 90%).
- The `ci` (continuous) or the prediction **set** (classification) **MUST** carry its nominal coverage; empirical coverage **MUST** be validated by **PICP** (§N) within tolerance.
- Conformal sets that grow large (high uncertainty) **MUST** down-weight confidence or abstain (§F). Conformal **complements** calibration (§G); it does not replace it.

## Y. Out-of-Distribution & Novelty Detection

- Each model **MUST** have an **OOD/novelty gate**: inputs unlike its training regime (new rubber/paddle, unseen lighting, wheelchair play scored by an able-bodied model, a foreign sport) raise **epistemic** uncertainty → cap or **abstain**.
- Methods: feature-space distance/density, energy/logit scores, or **ensemble disagreement** (§Z); the OOD score **MUST** appear in `source.signals`.
- An OOD input is a distinct **"novel — needs review"** state; it **MUST NOT** be silently reported as a low-confidence in-distribution value (§F).

## Z. Ensembles, Bayesian & Sampling Methods

- Epistemic uncertainty for trained models **SHOULD** be estimated by **deep ensembles**, **MC-dropout**, or Bayesian posteriors; **ensemble disagreement** is a primary uncertainty + OOD signal (§Y).
- The method + its latency/cost trade-off **MUST** be recorded per model (a real-time path **MAY** use a cheaper proxy); estimates **MUST** stay deterministic given fixed seeds (Part 34.AD).
- Disagreement **MUST NOT** be collapsed into a falsely confident point estimate (§B.3) — spread widens the `ci`.

## AA. Selective Prediction & Risk–Coverage

- The abstain decision **MUST** be framed as **selective prediction**: maximize **coverage** (fraction answered) subject to a **risk** bound (error among answered) per domain (§K).
- Each model **MUST** publish its **risk–coverage curve** and a chosen operating point; **selective accuracy** at that point **MUST** meet the Part 29 target.
- Lowering the abstain threshold trades coverage for risk; the operating point is **config + reviewed** (§AB), never silently shifted.

## AB. Cost-Sensitive Decisions & Thresholds

- Abstain/decision thresholds **MUST** derive from a **cost/utility model** (cost of false-positive vs false-negative vs abstain) per decision type — not a global constant.
- **High-stakes** decisions (officiating, injury/medical, selection) **MUST** use conservative thresholds (lower risk, more abstain, §AK); low-stakes (cosmetic stats) **MAY** answer more freely.
- Thresholds are versioned config tied to model + tier (§I); a change **MUST** be reviewed and re-evaluated on the golden set (Part 29).

## AC. Multi-Sensor / Multi-Model Fusion Reliability

- When fusing sources (vision + radar + IMU + audio + environment, Part 35.N), **agreement MUST raise** confidence and **disagreement MUST raise** uncertainty — disagreement is a **signal**, never averaged away (§B.3).
- Fusion **MUST** be principled (Bayesian / inverse-variance weighting / Dempster–Shafer); each source carries its own envelope + provenance (§J); a failed or OOD source is **dropped, not blended**.
- Cross-source contradiction beyond tolerance **MUST** abstain or escalate (§Q) and **SHOULD** flag possible tampering (Part 35.T).

## AD. Temporal Reliability & Consistency

- For tracks/sequences, confidence **MUST** be temporally coherent: a filter (e.g. Kalman) propagates state + covariance; an isolated high-uncertainty frame is interpolated, a sustained one abstains.
- **Physical-consistency checks** **MUST** gate outputs — a ball cannot teleport, exceed energy bounds, or reverse without contact (Part 19); a violation **MUST** down-weight/abstain (`tt.physics.validation.failed`, Part 39 §AQ).
- Per-rally/-match confidence **MUST** reflect **temporal coverage** (how much of the rally was reliably tracked), not just the peak-frame confidence.

## AE. Reliability of Derived & Longitudinal Artifacts

- Profiles, dossiers, matchups, and trends are **derived**; their confidence **MUST** be bounded by (a) the inputs' confidence (§H), (b) **sample size** (§AF), and (c) **recency** (stale footage decays confidence).
- A longitudinal claim ("player improved", "weakness fixed") **MUST** meet **statistical significance** (§AF); it **MUST NOT** be asserted on a within-noise difference.
- Each derived artifact **MUST** expose evidence count + aggregate confidence + a "preliminary" badge when thin (Part 32.J / §M).

## AF. Statistical Significance & Sample Size

- Any **comparative** or **trend** claim **MUST** report sample size `n`, effect size, and a confidence interval; a difference inside the CI **MUST NOT** be claimed as real.
- Minimum-sample gates per claim **MUST** be config (`MIN_SAMPLE`, Part 34.AL); below them the claim is `preliminary`/abstain.
- **Multiple-comparison correction** **MUST** be applied when scanning many statistics (so the system does not invent "weaknesses"); A/B + efficacy analyses follow Part 34.BL (no peeking).

## AG. Ground-Truth & Label Reliability

- Ground truth is **not** infallible — labels carry uncertainty (annotation error, ambiguity). A model's achievable reliability is **bounded by its label quality** (Part 30).
- Datasets **MUST** record **inter-annotator agreement (IAA)**, gold-check pass rates, and an adjudication trail (Part 30); low-IAA classes **MUST** widen confidence / cap claims.
- Label noise **MUST** be modeled, not ignored; evaluation on noisy labels **MUST** acknowledge the noise floor (Part 29).

## AH. Robustness & Adversarial Reliability

- Confidence **MUST** drop under input corruption (compression, blur, occlusion, lighting shift) and adversarial/spoofed inputs (Part 36 R27); robustness **MUST** be tested with perturbation suites (§AB testing / Part 34.AZ).
- Tamper-evidence (Part 35.T) + provenance (§J) **MUST** detect manipulated footage; a suspected manipulation **MUST** abstain + escalate (§Q), never silently score.
- A model that stays **overconfident under corruption MUST NOT** pass the release gate (§G.4 / Part 29).

## AI. Graceful Degradation Ladder

- Each capability **MUST** define an explicit ladder — **full → reduced → coarse → abstain** — with the trigger and the resulting envelope at each rung.
- Example (spin): T3 calibrated RPM (`high`) → T2 curvature estimate (`moderate`) → T1 coarse class (`preliminary`) → occluded/below-threshold (`abstain`).
- Degradation **MUST** be automatic, signaled (Part 39 `reliability.reduced`/`capped`), and **reversible** when conditions improve — never a hard failure (Part 34.AM).

## AJ. Production Calibration Monitoring

- Calibration **MUST** be monitored **in production**, not only at training: track online **ECE**, **population stability** (input drift), and selective accuracy on a labeled trickle / shadow set.
- Drift beyond the gate → `tt.reliability.model.drift_detected` + a recalibration trigger (§G.5, Part 29/39); until recalibrated, affected outputs **MUST** be down-weighted (§M).
- **Canary/shadow** deployment **MUST** compare a new model's calibration to the incumbent before promotion (Part 39 §BB / 34.AU).

## AK. Model Risk Tiers & Governance

- Every model **MUST** be assigned a **risk tier** by stakes: **High** (officiating, injury/medical, selection), **Medium** (game-plan, profiling), **Low** (cosmetic stats).
- Higher tiers **MUST** carry stricter calibration targets (§G), conservative thresholds (§AB), mandatory **human-in-the-loop** (Part 34.BQ), and a named accountable owner (model-risk management).
- A model **MUST NOT** be used above the risk tier it was validated for; tier + validation status are part of provenance (§J).

## AL. Reliability of LLM / Generative Outputs

- An LLM/generative feature **MUST** be **grounded** — it may state only engine-produced numbers (with their envelopes) and **MUST** cite evidence (Part 34.BB); **token probability is NOT a reliability measure**.
- LLM confidence **MUST** come from grounding + self-consistency / verification against the engines, not from fluency; an ungrounded claim **MUST** abstain.
- A generative output inherits the **reliability of its sources** (§H) and **MUST NOT** upgrade a `preliminary` fact into a confident statement.

## AM. Precision, Significant Figures & Reporting

- Reported precision **MUST** match the uncertainty: "78 ± 6 km/h", **not** "78.3194 ± 6"; significant figures **MUST** be consistent with the `ci` (no false precision).
- Units **MUST** accompany every continuous value (Part 34.AC); rounding rules **MUST** be deterministic and documented.
- A point estimate **MUST NOT** be displayed without its band/interval where one exists (§M.3 / Part 32.J).

## AN. Explainable Confidence ("why this number")

- Every confidence **MUST** be **explainable**: its drivers (which signals, tier, calibration, sample size, OOD/agreement scores) **MUST** be retrievable via the evidence drill-down (Part 32.D) + provenance (Part 10/34.AK).
- An abstention **MUST** state **why** (occlusion / OOD / thin data / tier / capture-fail), not a generic "unknown" (§F).
- Explanations **MUST** be **faithful** to the actual computation — no post-hoc rationalization.

## AO. Reliability Error Budget

- The platform **MUST** maintain a **reliability error budget** (accuracy + calibration headroom vs the Part 29 targets) analogous to an SLO budget; regressions consume it.
- Exhausting the budget (golden-set / calibration gate breach) **MUST** block releases (Part 29 / Part 37 §Z) until restored — reliability is a **release gate**, not best-effort.
- The budget + burn rate **SHOULD** be visible on the MLOps dashboard (§AJ / Part 34.BA).

---

## AP. Mathematical Foundations & Formal Definitions

- **Envelope type:** an estimate is a tuple `E = (v, c, [lo,hi], τ, σ, s)` with `c ∈ [0,1]`, tier `τ`, source `σ`, status `s` (§C).
- **Perfect calibration (classification):** `P(Y = ŷ | C = c) = c` for all `c`. Deviation is **ECE** `= Σ_b (n_b/N)·|acc(b) − conf(b)|` over confidence bins `b`; **MCE** `= max_b |acc(b) − conf(b)|`.
- **Proper scoring rules:** **Brier** `= (1/N) Σ (c_i − y_i)²`; **log-loss** `= −(1/N) Σ [y_i ln c_i + (1−y_i) ln(1−c_i)]`. Lower is better; both **MUST** be reported (§N).
- **Interval coverage:** `PICP = (1/N) Σ 1{ lo_i ≤ y_i ≤ hi_i }`, target ≈ nominal.
- **Error propagation (continuous):** for `f(x₁..xₙ)` with independent `xᵢ` of std `σᵢ`, `σ_f² ≈ Σ (∂f/∂xᵢ)² σᵢ²` (add covariance terms if correlated). **Monte-Carlo MAY** replace linearization for nonlinear `f` (Magnus/trajectory, Part 19).
- **Confidence composition:** independent chain `c_out = Π_k c_k`; required-all (min-gate) `c_out = min_k c_k` (§H/§AA).
- **Bayesian update:** `p(θ | D) ∝ p(D | θ)·p(θ)` (skill updating, §AW).
- **Conformal coverage (split):** with nonconformity scores on a calibration set, the level-`(1−α)` set satisfies `P(Y ∈ set) ≥ 1−α`, distribution-free (§X).
- **Temperature scaling:** calibrated probabilities `= softmax(z / T)`, `T` fit by minimizing held-out NLL; `T > 1` softens overconfidence (§G).

## AQ. Reference Constants & Default Thresholds

Consolidated defaults (all are **config**, not magic numbers — Part 34.AL; this is the registry of defaults).

| Constant | Default |
|----------|---------|
| Status bands | high ≥ 0.90 · moderate 0.70–0.90 · preliminary 0.50–0.70 · abstain < domain threshold |
| `verified` | confidence ≥ 0.95 **and** ground-truth validated |
| ECE target / MCE | ECE ≤ 0.05 · MCE ≤ 0.10 |
| PICP tolerance | ± 0.03 of nominal |
| Conformal default coverage | 0.90 |
| Tier ceilings (§I) | Platinum 1.0 · Gold 0.9 · Silver 0.75 · Bronze 0.6 · Fail → abstain |
| `MIN_SAMPLE` (claims) | profile stat 30 · trend 100 (per §AF) |
| Abstain thresholds | per domain (§K); default conf < 0.5 |
| Real-time UQ latency budget | within the Critical event SLA (Part 39 §AL) |

## AR. Worked Examples (end-to-end)

1. **Spin, T1 phone (uncalibrated):** model conf 0.80 → uncalibrated cap 0.70 (§M) → Bronze ceiling 0.60 (§I) → `min(0.70, 0.60) = 0.60` → `status = preliminary`, `calibrated=false`; below 0.50 → abstain.
2. **Speed, T2 Gold (calibrated):** conf 0.92, `ci = 78 ± 6 km/h`, Gold ceiling 0.90 → `min(0.92, 0.90) = 0.90` → `high`.
3. **Independent chain:** detection 0.95 × tracking 0.90 × physics 0.85 = **0.727** → `moderate` (§AP composition).
4. **Officiating min-gate:** components `{sync 0.99, recon 0.97, ground_truth = abstain}` → `min → abstain` (one required component abstained, §H.4) → escalate to umpire (§Q).
5. **Profile aggregation:** 5 rallies → wide Wilson/t-interval → `preliminary`; 200 rallies → narrows → `moderate/high`; "improved vs last season" requires significance (§AF/§AU), else not claimed.

## AS. Reliability Status Lifecycle

- A value's status is a **function** of (confidence, calibration, tier, sample, drift), recomputed on each input — it **MUST NOT** be sticky.
- Upward path: `preliminary →(more data) moderate →(calibrated + tier) high →(ground-truth) verified`.
- Downward path: `high →(drift / stale calibration) reduced`; `any →(capture fail / OOD / occlusion) abstain`.
- Each transition **MUST** emit the matching Part 39 reliability event (`reduced`/`capped`/`abstained`) and **MUST** be explainable (§AN).

## AT. Geometric & Spatial Uncertainty

- Spatial estimates (ball position, placement, 3D point) **MUST** carry a **covariance** (2D/3D) or an error radius — not a bare point; placement heatmaps render the distribution (Part 32.V).
- 3D reconstruction uncertainty **MUST** propagate from calibration residual + triangulation geometry (Part 35.AE); poor geometry (small baseline, low overlap) widens the covariance → **MAY** abstain.
- Court-frame/homography uncertainty (Part 35.BD) **MUST** propagate into placement; an uncalibrated frame **MUST** cap spatial confidence.

## AU. Statistical-Estimator Uncertainty

- **Proportions** (win %, % topspin): **Wilson** or Agresti–Coull intervals (never naive normal), especially at small `n`.
- **Counts** (loops per match): **Poisson** interval.
- **Means** (average speed): **t-interval** with sample std; always report `n`.
- The estimator + interval method **MUST** be recorded in `source`; a statistic with `n < MIN_SAMPLE` is `preliminary`/abstain (§AF).

## AV. Hierarchical & Coarse-to-Fine Confidence

- For hierarchical labels (Part 38: `stroke → loop → hook_loop`; `spin → sidespin → sidespin_left`), confidence **MUST** be reported at each level; the system **MUST** answer at the **finest level it is confident** and abstain below that — never guess the leaf.
- A parent's confidence **MUST** be ≥ its child's (a leaf cannot be more certain than its category). Coarse-to-fine abstention ("it's a loop, sub-type uncertain") is a valid, useful result.

## AW. Bayesian Skill Updating (Longitudinal)

- A player's latent skill/style **MUST** be updated **Bayesianly** across matches: `posterior = f(prior, new_evidence)`, **recency-weighted** (older footage decays) with **shrinkage** toward a population prior for thin data (so one match cannot swing the estimate).
- Longitudinal confidence **MUST** widen when footage is stale/sparse (§AE) and **MUST** express trend uncertainty (§AF) — a point estimate alone is forbidden.

## AX. Decision-Making Under Uncertainty

- Recommendations (game plans, Part 21) **MUST** be made under **expected utility**, not point estimates: weigh each option by its outcome distribution × confidence; under high uncertainty prefer **robust** options (minimize worst-case regret).
- A recommendation **MUST** surface its confidence + the dominant uncertainty (Part 32.O "why this plan"); a low-confidence plan **MUST** be labelled preliminary and **MUST NOT** be presented as decisive.
- The system **MUST NOT** recommend an action whose expected benefit is within the noise of the alternative (§AF).

## AY. Real-Time vs Batch Reliability

- **Real-time** paths (live officiating/coaching, Part 39 SLAs) **MAY** use cheaper UQ (single calibrated model, no full ensemble) but **MUST** still carry the envelope and abstain under uncertainty — **speed MUST NOT buy false confidence**.
- **Batch** paths **MUST** use the full UQ stack (ensembles/conformal/consistency) and **MAY** revise a real-time result later; a revision **MUST** be versioned + provenance-tracked (§BF) and **MUST NOT** silently overwrite an officiating record (Part 39 §L).

## AZ. Confidence Failure Modes

Each **MUST** be monitored (§AJ) with a detection signal + remedy; an unaddressed mode **MUST** block release (§AO):

| Failure mode | Signal | Remedy |
|--------------|--------|--------|
| Overconfidence | ECE high, conf > acc | recalibrate (§G) |
| Underconfidence | conf < acc, needless abstain | recalibrate; lower threshold (§AB) |
| Confidence collapse | all probs near 0/1 | temperature/retrain |
| Calibration drift | online ECE rising | recalibrate (§AJ) |
| Shortcut confidence | high on spurious cues | robustness tests (§AH), retrain |
| Shift miscalibration | OK in-dist, broken OOD | OOD gate (§Y), abstain |

## BA. Measurement Tolerances & Acceptance Bands

- Each measured quantity **MUST** declare an **acceptance tolerance** (the error the platform commits to at a tier), tied to Part 29 targets — e.g. speed ± X% (T2+), spin RPM ± Y% (T3), placement ± Z cm (calibrated).
- A value whose `ci` exceeds its tolerance **MUST** be `preliminary`/abstain. Tolerances are the **accuracy contract** with users and **MUST** appear in reports + the reliability model card (§BE).

## BB. Missing Data & Imputation

- Missing inputs **MUST** trigger **abstain by default**; imputation is permitted only where principled, **MUST** be flagged (`imputed=true`), and **MUST** carry a confidence penalty.
- An imputed value **MUST NOT** feed a high-stakes decision (§AK) without human review (§Q).

## BC. Ranking & Comparison Uncertainty

- A ranking/comparison output (best shot, stronger player, top weakness) **MUST** express **P(A > B)** and a "too close to call" band; rank stability under input perturbation **MUST** be reported.
- An ordering whose pairwise differences fall within noise **MUST NOT** be presented as definitive (§AF).

## BD. Persona-Aware Reliability Presentation

- The **same** envelope **MUST** drive **persona-appropriate** rendering (Part 32 personas): coach → band + evidence; player → simplified ("solid" / "needs more data"); umpire → decisive-or-abstain (advisory, Part 09); scientist → full distribution + metrics.
- Presentation **MUST NOT** alter the underlying confidence — only its rendering; **abstain MUST remain visible** to every persona.

## BE. Reliability Audit, Certification & Model Card

- Every model's **model card** **MUST** include a reliability section: calibration metrics (§N), risk tier (§AK), tolerances (§BA), failure modes (§AZ), OOD scope, and known limitations.
- Reliability claims **MUST** be **independently auditable** — the eval set, calibration record, and golden-set results **MUST** be reproducible (§BF, Part 29); officiating-grade reliability **MUST** be externally validated (Part 35.T).

## BF. Reproducibility & Versioning of Confidence

- A confidence value **MUST** be reproducible from `{model_version, calibration_version, code_sha, inputs, seed}` (§J, Part 34.AK/AD): identical inputs → identical envelope.
- When a model/calibration changes, historical confidences **MUST** remain attributable to the version that produced them; re-scoring old data **MUST** create a **new versioned** result, never mutate the old (Part 34.BE).

---

## BG. Calibration Fairness & Subgroup Parity

- Confidence **MUST** be calibrated **per subgroup**, not only in aggregate — across para classes, junior vs senior, sex, **left- vs right-handed**, and skin tone for detection (Part 34.BF / Part 29 fairness).
- Per-group **ECE** + selective accuracy **MUST** be reported; a subgroup whose calibration or accuracy is materially worse **MUST** block release — a model that is confident-but-wrong for one group is a fairness defect (§AO).
- No subgroup may be silently served lower reliability; where data for a group is thin, the system **MUST** widen confidence / abstain rather than overclaim (§W epistemic).

## BH. Standards Alignment

- Physical-quantity uncertainty (speed, spin, placement) **SHOULD** follow the **ISO/IEC GUM** (Guide to the Expression of Uncertainty in Measurement): combined standard uncertainty `u_c`, coverage factor `k`, expanded uncertainty `U = k·u_c`; the `ci` **MUST** state its coverage (§AP/§BP).
- Trustworthy-AI practice **SHOULD** align with the **NIST AI RMF** (govern · map · measure · manage) and ISO/IEC AI standards (e.g. 42001 management system, 24028 trustworthiness); the controls in this Part map to those functions.
- Standards alignment is an **auditable claim** (§BE), never a marketing label.

## BI. Calibrated Regression & Quantile Outputs

- Continuous outputs **MUST** be calibrated as **regression** (distinct from classification calibration §G): e.g. **quantile regression** giving calibrated `[lo,hi]` at a target coverage, or a calibrated predictive distribution.
- **Quantile crossing** (`lo > hi`) **MUST** be prevented; coverage **MUST** be validated by PICP (§N); the training loss **SHOULD** be the pinball/quantile loss.
- A point estimate without a calibrated interval is `preliminary` at best (§AM).

## BJ. Confidence in Absence / Negative Results

- A negative finding ("no weakness found", "no service fault") **MUST** distinguish **"examined and found none" (high confidence)** from **"insufficient data to tell" (abstain)** — absence of evidence is not evidence of absence without coverage.
- A negative result **MUST** carry its own confidence + the **coverage** it rests on (how much was examined); thin coverage → the negative is `preliminary`/abstain.

## BK. Systematic Bias vs Random Variance

- Error **MUST** be decomposed into **systematic bias** (a consistent offset — e.g. a camera over-reading speed) and **random variance**; measurable bias **MUST** be calibrated out and the correction tracked + validated (§BF).
- Residual (uncorrected) bias **MUST** bound the accuracy claim (§BA); confidence **MUST NOT** ignore a known bias.

## BL. Active Learning & Uncertainty Sampling

- Model **epistemic** uncertainty (§W) and OOD scores (§Y) **MUST** drive **what to label next** (Part 30): high-uncertainty, high-disagreement, and novel samples are prioritized for annotation.
- This closes the loop — uncertainty → targeted labels → retrain/recalibrate (§AJ) → reduced uncertainty; coverage of the uncertain regions over time **MUST** be tracked.

## BM. Use-Case Reliability Matrix

The admissible reliability bar **MUST** vary by use case:

| Use case | Minimum admissible status | Rule |
|----------|---------------------------|------|
| Officiating (decisive) | `verified` only | else abstain → human (Part 09 / §Q) |
| Coaching / game-plan | `moderate`+ | `preliminary` labelled (§M) |
| Player self-serve | `preliminary`+ | friendly framing (§BD) |
| Broadcast / fan | `preliminary`+ | confidence badge required |
| Betting integrity | `verified` only | forbidden otherwise (Part 33) |
| Medical / injury | `high`+ and human-in-loop | never autonomous (§AK) |

An output **MUST NOT** be consumed by a use case whose bar it does not meet.

## BN. Per-Output Reliability Appendix

Consolidated reference (method · tier availability · tolerance §BA · abstain rule). Exact numbers live in config + Part 29 targets; this is the index.

| Output | Method | Tier | Tolerance | Abstain when |
|--------|--------|------|-----------|--------------|
| Ball position | detector + track | T1+ | ± px / cm (calibrated) | visibility < 90% |
| Speed | trajectory + calibration | T2+ | ± X% | uncalibrated on T1 |
| Spin axis / RPM | curvature (T2) / high-speed (T3) | T2 coarse · T3 true | ± Y% | markerless below threshold |
| Placement | homography → court frame | T2+ | ± Z cm | uncalibrated frame |
| Bounce / event | detector + physics consistency | T1+ | — | physics violation (§AD) |
| Stroke class | hierarchical classifier (§AV) | T1+ | — | top-1 margin < threshold |
| Score | scoreboard OCR | T1+ | — | digit conf < 0.9 |
| Profile stat | aggregate (§AU) | T1+ | CI-bounded | n < `MIN_SAMPLE` |
| Win-probability | tactical model | T1+ | calibrated `[0,1]` | thin head-to-head |
| Game-plan | decision under uncertainty (§AX) | T1+ | — | low evidence |

## BO. Reliability Incident Response

- A **reliability incident** (a shipped over/under-confident output causing harm — e.g. a public wrong officiating call) **MUST** follow: **detect** (monitoring §AJ / report) → **contain** (kill-switch the feature, Part 34.AU) → **correct** (recalibrate / rollback) → **disclose** (responsible disclosure, Part 31) → **postmortem** (blameless, Part 34.BA) → **prevent** (gate update §AO).
- Officiating/medical reliability incidents are **High severity** (§AK) and **MUST** page immediately; the immutable evidence (Part 39 §L) supports the review.

## BP. Frequentist vs Bayesian Interval Semantics

- Every `ci` **MUST** declare its semantics — a **frequentist confidence interval** (coverage over repeated sampling) or a **Bayesian credible interval** (posterior probability mass); they answer different questions and **MUST NOT** be conflated.
- The choice **MUST** be consistent per output and recorded in `source`; coverage claims (§X/§N) are interpreted accordingly.

## BQ. Reliability Open Problems & Research Roadmap

Honest acknowledgment (ties Part 36 risks) — these are hard and partially unsolved; the platform **MUST** abstain/cap rather than overclaim until they are:
- **Markerless spin uncertainty** on T1/T2 (no ground truth) — cap + flag (§M); roadmap: SpinDOE calibration + high-speed (Part 26 / 36 R2).
- **Single-camera 3D** depth ambiguity — T1 cannot yield true 3D (§L); roadmap: T2 lift, T3 multi-cam.
- **Calibration under domain shift** (new venues/equipment) — OOD gate (§Y) + production monitoring (§AJ); roadmap: continual recalibration.
- **Real-time UQ** within latency budgets (§AY) — cheaper proxies today; roadmap: distilled uncertainty heads.
- **Label-noise floor** (§AG) — bounds achievable accuracy; roadmap: better annotation protocols (Part 30).

## BR. Reliability Glossary & Notation

Symbols/terms (canonical via Part 38 where applicable): `c` confidence · `ci=[lo,hi]` interval · `τ` capture tier · `σ` source/provenance · `s` status · **ECE/MCE** calibration error · **PICP** interval coverage · **aleatoric** (data noise) vs **epistemic** (model ignorance) · **OOD** out-of-distribution · **selective accuracy** (accuracy on non-abstained) · **`abstain`** (Part 38) the decline-to-assert state · **`u_c` / `k` / `U`** GUM uncertainties (§BH). This notation is used across Parts 10/29/35/39/40.

This document is the authoritative reliability law for TT-OS; together with the data model (37), ontology (38), and event contract (39), it completes the platform's build foundation: **structure, meaning, communication, and honesty.**

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
