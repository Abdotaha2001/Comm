# PART 43 — DATA & ML LIFECYCLE (MLOps) (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative intelligence law** of the platform — the **seventh build pillar** after the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), and operability law (42). The platform's premise is **"everything is a dedicated, trained AI model"** (Part 18, ~47 models); this part is **how that intelligence is manufactured, evaluated, shipped, and kept good** — the data + model lifecycle.
>
> It is the build-ready formalization of Part 12 (Data & ML Infra), and the connective tissue for the model-centric laws already written: it **feeds** Part 40 (a model ships only if calibrated), **obeys** Part 41 §AP (signed, dual-control promotion) + §Q (poisoning/provenance), and **is watched by** Part 42 §H/§W (drift, calibration, LLM telemetry). Its gates **reuse** Part 29 (eval metrics) + the golden-set benchmark.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`. It **supersedes Part 12 for build**. RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` (grounded in `backend/`) · 🟡 `PARTIAL` · ⬜ `SPECIFIED`. Honesty rule (Part 41 §B.5): a capability is ✅ only if it is in code. The CV layer today is a **classical, uncalibrated baseline** (OpenCV) behind a **pluggable detector interface**; the eval gate, synthetic data, and calibration math exist (✅), but training/registry/feature-store/drift infra are ⬜ — and this part says so plainly (§S).

---

## A. Scope & Objectives

### A.1 Purpose
Guarantee that every model the platform ships is **built from governed data, reproducibly trained, gate-evaluated, calibrated, secured, versioned, and monitored** — and that a heuristic is only ever a **labeled, temporary fallback** until its model meets target accuracy (§O, Part 18).

### A.2 Goals
- **G1.** Every model has an **end-to-end lineage**: data-version + code_sha + config + seed → the exact artifact (§N), reproducing any production prediction (Part 40 §J).
- **G2.** No model reaches production without passing the **promotion gate** (§J): accuracy (Part 29) **+** calibration (Part 40) **+** fairness **+** robustness **+** security sign-off (Part 41 §AP) **+** model card.
- **G3.** Data is a **first-class, versioned, governed asset** (§D/§G) — quality, provenance, consent, and splits are managed, not ad-hoc.
- **G4.** Training is **reproducible** (§I) and experiments are **tracked** (§I.3); a result that can't be reproduced is not a result.
- **G5.** Models are **monitored for drift** and improved via a **closed feedback loop** (§M), retraining on a defined trigger — never silently decaying.
- **G6.** The **heuristic→model migration** is explicit and honest (§O): the platform never claims "AI" for a heuristic.
- **G7.** Lifecycle invariants are **CI-enforced** (§R) — the golden-set gate already is (✅).

### A.3 Non-goals
- Not the reliability law (Part 40) — it **produces** calibrated models that Part 40 governs at runtime.
- Not the model catalog (Part 18) — it is **how** each catalog model is built, not which models exist.
- Not the eval-metrics catalog (Part 29) — it **uses** Part 29's metrics + golden sets as gates.
- Not the security law (Part 41) — it **complies** with §AP (registry/promotion) + §Q (supply chain/poisoning).

### A.4 Relationship to Parts
Formalizes Part 12; realizes Part 18 (every capability → a trained model); sources from Part 26 (pretrained/datasets) + Part 30 (labeling); gates on Part 29 (metrics + golden set) + Part 40 (calibration/fairness); obeys Part 41 §AP/§Q (registry, signing, supply chain) + §C/§F (biometric data); is monitored by Part 42 §H/§M/§W (drift, retrain, LLM); emits lifecycle events on Part 39; respects Part 35 capture provenance as data lineage.

---

## B. Principles

- **B.1 Data-centric.** Most model gains come from **better data**, not bigger models; data quality, coverage, and labels are the primary lever (§D/§F).
- **B.2 Everything versioned.** Data, labels, features, code, config, and models are **immutably versioned** so any artifact is reproducible (§N) — "which data trained this?" always has an answer.
- **B.3 Eval-gated promotion.** A model is promoted **only** by passing every gate (§J); "looks better on a notebook" is not promotion.
- **B.4 Reproducibility is non-negotiable.** Fixed seeds + pinned data/code/config (Part 34.AD) — a model that can't be rebuilt can't be trusted, debugged, or defended (officiating, Part 41 §L).
- **B.5 Honesty about training state.** A capability backed by a **heuristic** is labeled as such (§O, Part 40 §M); the platform never overstates a classical baseline as a trained model.
- **B.6 No leakage.** Train/val/test discipline is sacred (§G); a leak (subject, time, or label) makes every metric a lie.
- **B.7 Consent + provenance flow into training.** Training data carries its consent + provenance (Part 41 §C/§H); withdrawn-consent data is excluded (§F.5 / Part 41 §AE.3), and unlearning is tracked (Part 41 §AJ.5).
- **B.8 Closed loop.** Production feedback (human overrides, officiating reviews, OOD) flows back as labels (§M, Part 42 §S.4) — the system learns from where it was wrong.

---

## C. The Model Lifecycle (stage gates)

Every model moves through stages, each with an **entry gate** — no skipping:

```
problem → data → label → train → evaluate → calibrate → security-review
        → register → deploy(shadow→canary→full) → monitor → {retrain | retire}
```

- **C.1** Each stage **MUST** record its inputs/outputs + versions (§N) and emit a lifecycle event (Part 39).
- **C.2 Gates:** data passes quality/consent (§D/§F) → eval passes Part 29 + Part 40 (§J) → security passes Part 41 §AP/§Q → deploy is canaried (§L) → monitoring is wired (§M, Part 42 §H) **before** full traffic.
- **C.3** A model **MUST NOT** advance a stage with a failed gate; a failed gate is a tracked blocker, not a waiver (waivers follow Part 41 §AM.5).
- **C.4 Retirement** is a managed stage: deprecate → shadow replacement → cut over → archive the artifact + card (kept for reproducibility/audit, Part 41 §K).

## D. Data Sourcing & Datasets

- **D.1 Provenance + licensing.** Every dataset (open — Part 26: OpenTTGames/TTStroke-21/TrackNet/SpinDOE…; purchased; platform-collected) records **source, license, and usage rights**; a license-incompatible dataset **MUST NOT** train a shipped model.
- **D.2 Consent for athlete data.** Platform-collected video/biometric is governed by Part 41 §C/§H (consent, minors, biometric); training use is a **declared purpose** (Part 41 §H.1).
- **D.3 Dataset cards.** Each dataset has a card: contents, collection method, demographics/coverage, known biases, license, version (parallels model cards, §K).
- **D.4 Coverage + bias audit.** Datasets are audited for **coverage gaps** (equipment, lighting, play styles, para classes — Part 24, handedness, skin tone for CV) that would cause subgroup failures (Part 40 fairness / Part 41 §AC.7).
- **D.5 Pretrained provenance.** Reused weights (Part 26) are checksum/signature-verified + weight-scanned (Part 41 §Q.5/§AF.1) — a backdoored or license-tainted base model is a supply-chain defect.

## E. Data Engineering & Pipelines

- **E.1 Data contracts.** Pipelines enforce a **schema/contract** (types, ranges, nullability) at ingest; contract violations are quarantined, not silently trained on (Part 42 §P.4).
- **E.2 Validation.** Automated data-quality checks (distribution, missingness, drift vs prior, label sanity) gate data into the training set.
- **E.3 Lineage.** Every derived dataset traces to its raw sources (Part 40 §J, Part 35 capture provenance); a bad model is traceable to a bad batch.
- **E.4 Freshness.** Pipelines track freshness/lag (Part 42 §P.2); stale or late data is flagged, not silently used.
- **E.5 Reproducible transforms.** Feature/preprocessing transforms are versioned code (§N), identical in train + serve (§H.1 no skew).

## F. Annotation & Labeling (Part 30)

- **F.1 Protocol + rubrics.** Labeling follows the Part 30 protocol with explicit rubrics; ambiguous cases route to expert adjudication.
- **F.2 Inter-annotator agreement (IAA) gate.** Labels ship only above an **IAA threshold** (Part 30); low-agreement items are re-specified — a noisy label set caps achievable accuracy (Part 40 §AG label-noise floor).
- **F.3 Label provenance.** Each label records annotator, time, tool version, and guideline version (auditable, Part 41 §K); **gold questions** + audits detect bad annotators (poisoning defense, Part 41 §Q.4).
- **F.4 Active learning.** Labeling effort is prioritized by **model uncertainty + disagreement + OOD/novelty** (Part 40 §W/§Y, Part 42 §H) — label what the model is worst at, not random.
- **F.5 Labeler access control.** Annotators see only the data their task needs (Part 41 §E field-level); biometric/minor data labeling is consent- + access-gated (Part 41 §C); withdrawn-consent items are pulled.

## G. Dataset Versioning & Splits

- **G.1 Immutable versions.** Datasets are **content-addressed + versioned**; a model pins the exact dataset version it trained on (§N).
- **G.2 Split discipline.** Train/val/test are fixed + documented; the **test (golden/holdout) set is sacred** — never trained on, never tuned against (Part 29). The benchmark golden set (✅ `backend/app/benchmark.py`) is the reference pattern.
- **G.3 No leakage.** Splits prevent **subject leakage** (same player/match across splits → inflated metrics), **temporal leakage**, and **label leakage**; CV splits are by match/session, not random frames.
- **G.4 Temporal/holdout for non-stationarity.** For drift-prone tasks, a **time-based holdout** estimates real-world generalization (equipment/rules/venues evolve, Part 36).
- **G.5 Subgroup slices.** Test sets carry **subgroup slices** (Part 40 fairness) so promotion can check per-group performance (§J), not just aggregate.

## H. Feature & Embedding Store

- **H.1 No train/serve skew.** Features are computed by **shared, versioned code** for both training and serving; skew is a top cause of silent production failure — detected + alerted (Part 42 §H).
- **H.2 Point-in-time correctness.** Feature lookups for training use **as-of** values (no future leakage, §G.3).
- **H.3 Embedding governance.** Biometric/style embeddings (Part 04 ReID) live in an access-controlled, encrypted store (Part 41 §C/§F), separate from operational data; they are `biometric` class and non-anonymizable (Part 41 §B.9).
- **H.4 Consent-aware.** The store **MUST NOT** serve features derived from withdrawn-consent data (Part 41 §AE.3); deletions propagate (Part 41 §I.2).

## I. Training & Experimentation

- **I.1 Reproducible runs.** A run pins **data-version + code_sha + config + seed + environment** (container digest, Part 41 §AG.2); the same inputs reproduce the same model (§N, Part 34.AD).
- **I.2 Foundation-model strategy.** Feasible via **foundation models + fine-tuning + shared backbones + self-supervision + synthetic data** (Part 18) — not 47 models trained from scratch; shared backbones are versioned dependencies.
- **I.3 Experiment tracking.** Every experiment logs config + metrics + artifacts (params, curves, eval); results are comparable + searchable — no lost notebooks (§B.4).
- **I.4 Compute discipline.** GPU training is scheduled + budgeted (cost §Q, Part 42 §L.6/§M); long runs checkpoint + resume.
- **I.5 Hyperparameter search** is logged + reproducible; the search space + selection criterion are recorded (no cherry-picking).

## J. Evaluation & The Promotion Gate (the heart)

A model is promoted **only** when **all** gates are green — the multi-gate checklist:

| Gate | Requirement | Source |
|------|-------------|--------|
| **Accuracy** | meets per-model target on the golden/holdout set; **no regression** | Part 29 · ✅ `benchmark.py` |
| **Calibration** | ECE ≤ 0.05, MCE ≤ 0.10 (calibrated models); PICP for intervals | Part 40 §G/§N · ✅ `calibration.py` |
| **Fairness** | no subgroup materially worse (slices §G.5) | Part 40 fairness / Part 41 §AC.7 |
| **Robustness** | adversarial/evasion + OOD behavior acceptable; degrades to abstain | Part 41 §Q.1 · Part 40 §Y |
| **Reliability behavior** | abstains below threshold; honest confidence (no overclaim) | Part 40 §F/§M |
| **Security** | signed, provenance-verified, dual-control approved | Part 41 §AP |
| **Model card** | present + complete (limits, scope, metrics) | §K · Part 40 §BE |

- **J.1 No partial promotion.** A failed gate **blocks** promotion (§C.3); the gate set is the **min-gate** (Part 40 §H.4) — all required, weakest governs.
- **J.2 Offline + online.** Offline gates precede deploy; **online evaluation** (shadow/canary §L) confirms real-world behavior before full traffic.
- **J.3 Regression gate.** Promotion **MUST NOT** regress the golden-set metrics (the existing ✅ gate, Part 10.18); accuracy + calibration are both regression-gated.
- **J.4 Eval honesty.** Eval sets are representative + leakage-free (§G); a gate passed on a tainted set is a defect, not a pass.

## K. Model Registry, Versioning & Cards

- **K.1 Registry.** All models live in a **registry** with stage (dev/staging/prod/archived), access control + signed promotion (Part 41 §AP.1/§AP.3).
- **K.2 Semantic versions.** Model versions are explicit; a version binds its **lineage** (data/code/config, §N) + eval results (§J) + card.
- **K.3 Model cards** (Part 40 §BE): intended use, scope/limits, training data summary, metrics (incl. calibration + subgroup), failure modes, capture-tier validity, and known biases — shipped **with** the model, surfaced in evidence (Part 32/40).
- **K.4 Provenance + signing.** Every registered model is checksum-verified + signed (Part 41 §AP.2); unsigned models can't deploy.
- **K.5 Safe serialization.** Artifacts use **safetensors** (non-executable) where possible; untrusted pickle is never loaded in-process (Part 41 §AF.1).

## L. Deployment & Serving

- **L.1 Pluggable serving.** The detector/model interface is **pluggable** (✅ `backend/app/cv/detector.py` `BallDetector`); deep models (TTNet/YOLO, Part 26) drop in behind the same contract without pipeline changes.
- **L.2 Progressive rollout.** Models deploy **shadow → canary → full**, with **calibration + abstention SLIs as the canary signal** (Part 42 §N.4/§H), not just latency; auto-rollback on burn (Part 42 §N.2).
- **L.3 Online evaluation.** Shadow scoring + A/B compares a candidate against incumbent on live traffic before cutover (§J.2).
- **L.4 Serving infra.** Batch (analysis worker) vs real-time paths; GPU serving observability (Part 42 §L.6); autoscale on saturation (Part 42 §F.3).
- **L.5 Edge/on-device.** Distilled/quantized models for edge/courtside (Part 02) ship through the same gates; edge models report health offline (Part 42 §X).
- **L.6 Tier-aware deployment.** A model declares the capture tiers it is valid on (Part 35/40 §I); it **MUST NOT** be served outputs on a tier it wasn't validated for (abstain instead).

## M. Monitoring, Drift & Continuous Learning

- **M.1 Drift detection.** Monitor **data drift** (input distribution) + **concept drift** (input→label relationship) in production (Part 42 §H.2/§P); a venue/equipment shift surfaces as OOD (Part 40 §Y).
- **M.2 Calibration monitoring.** Production calibration is tracked; drift past threshold triggers **recalibration or rollback** (Part 40 §AJ/§AO, Part 42 §H.2).
- **M.3 Retrain trigger.** Retraining fires on a **defined trigger** — drift threshold, accuracy decay, new labeled volume, or cadence — not vibes; each retrain re-enters the gate (§J).
- **M.4 Closed feedback loop.** Human overrides, officiating reviews, corrections, and high-uncertainty/OOD cases flow back as **prioritized labels** (§F.4, Part 42 §S.4) — the system improves where it failed.
- **M.5 No catastrophic forgetting.** Continual/retraining **MUST** validate that old capabilities don't regress (the golden-set gate, §J.3) — a retrain that fixes A by breaking B is blocked.
- **M.6 Shadow-validate retrains.** A retrained model is shadow-evaluated (§L.2) before replacing the incumbent.

## N. Reproducibility & Lineage

- **N.1 End-to-end lineage.** `data_version + code_sha + config + seed + base_model + env_digest` → a **deterministic** artifact; recorded in the registry (§K) + model card.
- **N.2 Reproduce any prediction.** A production output is reproducible from its provenance (Part 40 §J) — required for debugging, audit, and **officiating defensibility** (Part 41 §L).
- **N.3 Immutable artifacts.** Datasets, features, and models are immutable once versioned (§B.2); "latest" is a pointer, never a mutable thing trained against.

## O. The Heuristic → Model Path ("everything is a model")

- **O.1 Honest fallback.** A heuristic exists **only** as a labeled-confidence fallback until its model reaches target accuracy (Part 18); its output is flagged uncalibrated/preliminary (Part 40 §M) — never presented as a trained model (§B.5).
- **O.2 Today's reality.** The CV ball detector is a **classical OpenCV baseline** (uncalibrated) behind the pluggable interface (§L.1); scoreboard OCR + markerless spin are heuristic. This is **stated, not hidden** (§S).
- **O.3 Migration discipline.** Replacing a heuristic with a model requires the full gate (§J) + a measured **improvement** over the heuristic on the golden set (Part 29) — and parity/rollback if it regresses.
- **O.4 Coexistence.** Heuristic + model can run in **shadow** (§L.2) so the model proves itself on live data before it takes over.

## P. Synthetic Data & Simulation

- **P.1 Synthetic is a tool, flagged as such.** The platform uses synthetic clips (✅ `backend/app/cv/synth.py`) for the golden-set harness; synthetic-trained/evaluated results carry a **sim provenance** flag (Part 40 §J).
- **P.2 Domain randomization** (lighting, angle, equipment, ball speed) broadens coverage where real data is thin (§D.4).
- **P.3 Sim-to-real gap.** A model gated **only** on synthetic data is `preliminary` for real use until validated on a real holdout (§G); the gap is measured, not assumed away (§T).
- **P.4 No synthetic in the golden truth of record.** Real-world claims require real eval sets; synthetic augments, it doesn't replace (Part 29).

## Q. Compute, Cost & Efficiency

- **Q.1 Training cost** is tracked per run + attributed (Part 42 §M); large runs need budget approval (Part 41 §AM.5).
- **Q.2 Efficiency.** Distillation/quantization/pruning produce **edge-deployable** models (§L.5) within accuracy + calibration gates (§J).
- **Q.3 Carbon.** Training + serving energy/carbon is measured (Part 42 §M.4, Part 15 sustainability) — efficiency reports carbon, not only $.
- **Q.4 Shared backbones** amortize compute across the ~47 models (§I.2, Part 18).

## R. Governance & CI Enforcement (lifecycle invariants)

CI **MUST** enforce the lifecycle (the MLOps analogue of Parts 37/39/40/41/42 governance); target home `backend/tools/governance/`.

| Check | Invariant | Status |
|-------|-----------|--------|
| `golden-set-gate` | accuracy gate runs + must not regress | ✅ (`benchmark.py`) |
| `calibration-measured` | calibration metrics computed on the eval set | ✅ (`calibration.py`, Part 40) |
| `data-version-pinned` | a model records the dataset version it trained on | ⬜ |
| `promotion-gate` | no deploy without accuracy+calibration+fairness+security+card green (§J) | ⬜ |
| `model-card-present` | every registered model has a complete card | ⬜ |
| `model-signed` | registered models are signed + provenance-verified (Part 41 §AP) | ⬜ |
| `no-leakage` | split discipline checked (subject/temporal/label, §G) | ⬜ |
| `repro-lineage` | run records data+code+config+seed (§N) | ⬜ |

- **R.1** Each ✅/🟡 invariant has a test; 🟡→✅ means the CI assertion exists.
- **R.2** The build manifest (Part 37 governance) **SHOULD** record the lifecycle-gate result.

## S. Build-Artifacts Status (honest, grounded in `backend/`)

| Capability | Artifact | Status |
|------------|----------|--------|
| Golden-set accuracy gate (regression) | `app/benchmark.py` + `tests/test_benchmark.py` | ✅ |
| Calibration math + Calibrator artifact | `app/calibration.py` (Part 40) | ✅ |
| Synthetic data generation | `app/cv/synth.py` | ✅ |
| Pluggable model/detector interface | `app/cv/detector.py` `BallDetector` | ✅ |
| Classical baseline (honest fallback) | `app/cv/opencv_detector.py` (uncalibrated) | ✅ (heuristic, §O) |
| Calibration record / model card seed | `benchmark.calibration_record` (Part 40 §BE) | 🟡 |
| Trained models (TTNet/YOLO etc.) | — (classical baseline today) | ⬜ |
| Dataset versioning + splits + lineage | — | ⬜ |
| Annotation pipeline + IAA gate (Part 30) | — | ⬜ |
| Feature/embedding store (no train/serve skew) | — | ⬜ |
| Model registry + signed promotion | — (ties Part 41 §AP) | ⬜ |
| Experiment tracking + reproducible training | — | ⬜ |
| Drift monitoring + retrain trigger | Part 40/42 signals exist; loop not built | ⬜ |

The truthful seed **exists**: a regression-gated golden set, calibration math, synthetic data, and a pluggable interface so trained models drop in. The platform is **"everything-is-a-model" in vision but classical-baseline in fact today** — the training/registry/feature-store/drift stack is ⬜ and tracked. Stating that is the point (§B.5).

## T. Open Problems & Roadmap (honest)

- **Markerless ground truth.** Spin/3D on T1/T2 have **no cheap ground truth** (Part 40 §M/§BQ) — gating is hard; roadmap: SpinDOE + high-speed capture (Part 26/35).
- **Sim-to-real gap** (§P.3) — synthetic coverage doesn't guarantee real performance; roadmap: real holdouts + domain adaptation.
- **Continual learning without forgetting** (§M.5) — updating on new data while preserving old skills is unsolved in general; the golden-set gate is the backstop.
- **Labeling cost at scale** (§F) — expert TT labels are expensive; active learning (§F.4) + synthetic (§P) reduce but don't eliminate it.
- **The classical→trained migration** (§O) — most of the catalog (Part 18) is still ⬜; honest status + the gate keep the transition trustworthy.

## U. Glossary & Notation

Canonical via Part 38 where applicable: **MLOps** (ML lifecycle ops) · **lineage** (data→model→prediction provenance) · **promotion gate** (multi-gate pass-to-prod, §J) · **train/val/test · holdout · golden set** · **leakage** (subject/temporal/label) · **IAA** (inter-annotator agreement) · **active learning** (label the uncertain) · **feature store · train/serve skew · point-in-time correctness** · **embedding** (Part 04 ReID; `biometric`) · **model registry · model card · dataset card** · **data/concept drift** · **retrain trigger** · **closed feedback loop** · **shadow / canary / A-B** (rollout, Part 42 §N) · **distillation / quantization** (edge efficiency) · **domain randomization · sim-to-real gap** · **catastrophic forgetting** · **safetensors** (non-executable weights, Part 41) · **foundation model / fine-tuning / shared backbone** (Part 18) · **ECE/PICP** (calibration, Part 40). These notations are used across Parts 12/18/26/29/30/40/41/42/43.

This document is the authoritative intelligence (data + ML lifecycle) law for TT-OS; with the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), and operability law (42), it completes the platform's build foundation — **structure, meaning, communication, honesty, trust, operability, and intelligence.**

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
