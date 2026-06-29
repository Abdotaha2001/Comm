# PART 42 — OBSERVABILITY, SRE & OPERATIONS (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative operability law** of the platform — the **sixth build pillar** after the data model (37), ontology (38), event contract (39), reliability law (40), and security/privacy law (41). Where 37–41 give the platform *structure, meaning, communication, honesty, and trust*, this part gives it **operability**: the contract for seeing the system, running it in production, meeting service objectives, and recovering when it breaks.
>
> Its distinctive job: the platform must observe **reliability and honesty in production**, not just CPU and latency. "Is the AI still calibrated? How often is it abstaining? Is it drifting on this venue?" are first-class operational signals (§H/§S, Part 40).
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`. It **formalizes the scattered observability/SLO conventions of Part 34 §L/§AE and Part 13 for build**; those remain the readable overview. RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` (grounded in `backend/`) · 🟡 `PARTIAL` · ⬜ `SPECIFIED` (build target). Honesty rule (Part 41 §B.5): a capability is ✅ only if it is in code. Today that is `/healthz`, the golden-set accuracy gate, and the per-run reliability/provenance telemetry; the metrics/traces/SLO/alerting stack is ⬜ and tracked (§T).

---

## A. Scope & Objectives

### A.1 Purpose
Make the platform **observable, operable, and recoverable**: every user-facing promise has a measured **SLI**, a target **SLO**, an **error budget**, an **alert**, and a **runbook**; every incident is detected fast, handled by a clear process, and learned from.

### A.2 Goals
- **G1.** Every service emits the **three pillars** — structured **logs**, **metrics**, **traces** — correlated by a shared id (§C/§D).
- **G2.** Every user-facing promise is an **SLI with an SLO + error budget** (§E); reliability/accuracy are SLIs too (§H).
- **G3.** Alerts are **symptom-based, actionable, SLO-tied** — page on user pain, not on noise (§I).
- **G4.** Every service is **operationally ready** before prod: health checks, runbook, owner, dashboards, on-call (§G/§K).
- **G5.** Incidents follow a defined **detect → respond → recover → blameless-postmortem** loop (§J), unified with Part 40 §BO + Part 41 §T.
- **G6.** Telemetry **never** leaks PII/secrets/tokens/full media URLs (§R, Part 41 §K.3) and is **cost- and cardinality-bounded**.
- **G7.** **Honesty is observable** (§S): abstention rate, calibration health, OOD rate, and capture-tier mix are dashboarded — a silently-overconfident model is an operational incident.
- **G8.** Observability invariants are **CI-enforced** (§U), not left to goodwill.

### A.3 Non-goals
- Not the reliability law (Part 40) — it **observes** Part 40's confidence/calibration in production.
- Not the security law (Part 41) — it **consumes** Part 41's audit boundary and SLO seed (§AK) and respects its telemetry-privacy rules.
- Not the event contract (Part 39) — it **monitors** the outbox/consumer lag (§P) but does not redefine it.
- Not a vendor choice — Prometheus/OTel/Grafana/Loki/Tempo are **examples**; the contract is the signals, not the tool.

### A.4 Relationship to Parts
Formalizes Part 34 §L (logging/observability) + §AE (SLOs/error budgets/runbooks) + Part 13 (health/metrics/traces, scaling); observes Part 40 (reliability/calibration/OOD → SLIs) + Part 29 (accuracy gate → SLI); monitors Part 39 (outbox/consumer lag, DLQ); inherits Part 41 §AK (SLO seeds), §T (incident response), §K (telemetry privacy), §U (BCDR signals); ties releases to Part 41 §AP (model rollout) + Part 34.AU (feature flags/kill-switch); surfaces Part 36 risks operationally.

---

## B. Principles

- **B.1 Observability ≠ monitoring.** Monitoring answers known questions (dashboards for known failure modes); **observability** lets you ask **new** questions of production from high-cardinality telemetry — both are required.
- **B.2 Measure the user's pain.** SLIs measure **symptoms users feel** (errors, latency, wrong/over-confident answers), not internal vanity metrics (CPU is a cause, not an SLI).
- **B.3 SLOs over 100%.** Reliability target is an **SLO with an error budget**, never "100%"; the budget is **spent deliberately** on release velocity (§E).
- **B.4 You build it, you run it.** Every service has a **named owner** + **on-call** (Part 34.P CODEOWNERS); ops is not a separate team's problem (§K).
- **B.5 Actionable alerts only.** An alert that isn't worth waking someone for **MUST NOT** page; every page has a **runbook** and a human action (§I).
- **B.6 Telemetry is classified data.** Logs/metrics/traces are `operational` (Part 41 §C) and **MUST NOT** carry PII/secrets (§R); telemetry has a cost + retention budget.
- **B.7 Honest instrumentation.** A metric that doesn't exist is reported as **not-instrumented**, never assumed-green (Part 41 §B.5); absence of an alert is not evidence of health.
- **B.8 Degrade, don't fail.** Under stress/dependency loss, the system **degrades** (lower tier / abstain, Part 40) rather than 500s the whole analysis (§L, Part 34 §AE).

---

## C. The Three Pillars: Logs, Metrics, Traces

- **C.1 Structured logs.** Logs **MUST** be **structured (JSON)**, leveled, and machine-parseable — never bare `print`/free-text; each carries the correlation context (§D) and is sanitized (§R, Part 41 §K.6).
- **C.2 Metrics.** Services **MUST** expose metrics (e.g. a Prometheus `/metrics` endpoint) covering the **golden signals** (§F) + domain SLIs (§H); metrics are typed (counter/gauge/histogram) with **bounded-cardinality** labels (§R.3).
- **C.3 Traces.** Requests **MUST** carry a **distributed trace** (e.g. OpenTelemetry) across API → worker → CV/model → DB, so a slow/failed analysis is attributable to a span; trace context propagates through the event bus (Part 39).
- **C.4 The three pillars are linked.** A log line, a metric exemplar, and a trace span for the same request **MUST** share the correlation ids (§D) so an operator pivots between them in one click.
- **C.5 Provenance is telemetry.** The reliability `source` (model/code_sha/tier, Part 40 §J) is attached to telemetry so production behavior is tied to the exact version that produced it.

## D. Telemetry Schema & Correlation

- **D.1 Correlation ids.** Every request gets a `request_id`; tracing adds `trace_id`/`span_id`; these **MUST** appear in logs, metric exemplars, spans, **and** the audit/event records (Part 39/41) for cross-pillar pivot.
- **D.2 Standard dimensions.** Telemetry carries `service`, `version`/`code_sha`, `env`, `route`, `capture_tier`, `model_version`, and a **tenant identifier that is hashed/opaque** (never raw org names or PII, Part 41 §F/§R).
- **D.3 Time discipline.** All timestamps are UTC, monotonic where measuring duration, and clock-synced (NTP, Part 41 §L.4) so traces and audit align.
- **D.4 Semantic conventions.** Field names follow one convention (OTel semantic conventions where applicable) so dashboards/alerts are portable; names are canonical (Part 38 where a term exists).

## E. SLIs, SLOs & Error Budgets

- **E.1 Every promise → an SLI.** Define SLIs as `good events / valid events` over a window: **availability**, **latency** (p95/p99), **correctness** (accuracy gate, Part 29), **calibration** (ECE, Part 40), **freshness**, **durability**.
- **E.2 SLO targets** are explicit, owner-approved, and config (Part 34.AL). Default seeds (tighten per tier; officiating/medical stricter):

| SLI | Default SLO |
|-----|-------------|
| API availability (read paths) | **99.9 %** / 30 d (officiating/medical **99.95 %**) |
| API latency — read p95 · p99 | < **300 ms** · < **800 ms** |
| Analysis turnaround (async) p95 | < **N×** clip realtime (per tier; SLO published) |
| Correctness (golden-set gate, Part 29) | **green** — no regression past target |
| Calibration (ECE, Part 40 §G) | ≤ **0.05** for calibrated models in prod |
| Abstention rate (Part 40 §F) | within an **expected band** (alert on spike/collapse, §H) |
| Data freshness (profiles/dossiers) | < **target lag** per feature |
| Event delivery lag (outbox, Part 39) | p95 < **target**; DLQ depth ≈ 0 |

- **E.3 Error budget.** `budget = 1 − SLO`. Burn is tracked; **fast-burn** + **slow-burn** alerts (multi-window) page before the budget is exhausted.
- **E.4 Error-budget policy.** When the budget is **exhausted**, non-essential **releases freeze** and reliability work takes priority until recovered (§N); spending the budget on velocity is fine **until** it runs out (Part 34 §AE).
- **E.5 SLO ≠ SLA.** Internal SLOs are stricter than any external **SLA**; breaching an SLO is an internal signal, not automatically a customer-facing breach.

## F. Golden Signals (RED / USE)

- **F.1 RED** per service/endpoint: **R**ate (traffic), **E**rrors, **D**uration (latency distribution).
- **F.2 USE** per resource: **U**tilization, **S**aturation, **E**rrors (CPU, memory, GPU, queue depth, DB connections).
- **F.3 Saturation is a leading indicator** — queue depth/backpressure (Part 39), GPU saturation on the CV path, and DB pool exhaustion **MUST** be alertable before they cause latency-SLO burn (§L).

## G. Health, Readiness & Liveness

- **G.1 Liveness** (`/healthz`, ✅ `backend/app/routers/health.py`) — "the process is up"; a failed liveness restarts the instance.
- **G.2 Readiness** — "ready to serve": checks critical **dependencies** (DB, queue, object store, model load) before joining the load balancer; a not-ready instance is pulled, not killed. ⬜ (split from `/healthz`).
- **G.3 Startup** — slow model/CV warmup uses a startup probe so liveness doesn't kill a still-initializing worker.
- **G.4 Dependency health** is a **first-class signal**: each external dependency (DB, broker, KMS, model store) has a health check + circuit breaker (Part 41 §U); degrade per §B.8 on failure.
- **G.5 Graceful shutdown** — drain in-flight requests, commit/abort cleanly (Part 39 process-then-commit §BD), deregister, then exit; no dropped work on deploy/scale-down.

## H. Domain SLIs: Reliability, Calibration & ML Telemetry (the distinctive layer)

This is what makes the platform's observability **more than generic SRE**: production telemetry of **truthfulness**.

- **H.1 Abstention rate.** The fraction of outputs that **abstain** (Part 40 §F) is a tracked SLI per domain/tier; a **spike** signals degradation/OOD, a **collapse** signals possible over-confidence — both alert (§I).
- **H.2 Calibration drift.** Where ground truth/feedback exists, **ECE/MCE/PICP** (Part 40 §N) are monitored over time; drift past threshold pages and can trigger **recalibration/rollback** (Part 40 §AJ, §AO).
- **H.3 OOD / novelty rate.** The OOD-gate firing rate (Part 40 §Y) per venue/equipment/lighting surfaces **domain shift**; a new venue lighting up OOD is an operational event, not a silent wrong answer.
- **H.4 Confidence + reliability distributions.** Distributions of `confidence`, `reliability_index` (✅ on `AnalysisRun`), and capture-tier mix are dashboarded — a shift is a leading indicator of input or model change.
- **H.5 Golden-set gate as a release SLI.** The benchmark gate (✅ `backend/app/benchmark.py`, Part 29) is the **correctness SLI** at release; production correctness is sampled via feedback/audit where available.
- **H.6 Speed/spin significance health.** The rate of low-SNR speed **abstains** (Part 40 §BH) and markerless-spin caps (Part 40 §M) are tracked — a jump means capture/quality regression upstream (Part 35).
- **H.7 Human-override rate.** For decisive calls (Part 41 §AC/§L), the rate at which humans override the model is an SLI of model trustworthiness; a rising override rate is a model-quality incident.

## I. Alerting & On-Call

- **I.1 Symptom-based.** Page on **SLO burn** / user-visible symptoms (§E/§F/§H), not on causes (high CPU alone never pages).
- **I.2 Actionable + runbook.** Every paging alert links a **runbook** (§K) and a clear action; non-actionable signals go to dashboards/tickets, not pages (§B.5).
- **I.3 Severity + escalation.** Severity ladder (SEV1–SEV4) with defined response times (Part 41 §AK MTTD/MTTR); auto-escalation if unacknowledged.
- **I.4 On-call hygiene.** Sustainable rotation, follow-the-sun where possible, **alert-fatigue** review (delete/auto-resolve noisy alerts), and **toil** tracked + reduced.
- **I.5 Multi-window burn alerts.** Fast-burn (page now) + slow-burn (ticket) per SLO (§E.3) to catch both outages and slow degradations.

## J. Incident Management

- **J.1 Declare.** Clear criteria to **declare an incident**; an **Incident Commander (IC)** coordinates; comms + scribe roles for SEV1/2.
- **J.2 Unified flow.** detect → triage → **contain/mitigate** → recover → **blameless postmortem** → prevent — the same loop as Part 40 §BO (reliability incidents) and Part 41 §T (security incidents); a single incident process, three lenses.
- **J.3 Reliability/officiating incidents** (a public wrong or over-confident call) are **high severity** (Part 40 §BO) and use the immutable evidence (Part 39 §L / Part 41 §K).
- **J.4 Communication.** Internal updates on cadence; a **status page** for customers/federations on customer-impacting incidents; honest, no over-claim.
- **J.5 Postmortems** are **blameless**, produce tracked **action items** with owners + due dates, and feed the gate/risk register (Part 36); repeat incidents are a process defect.

## K. Runbooks & Operational Readiness

- **K.1 Runbook per service** (Part 34 §AE): **symptoms → checks → fixes → escalation**, kept current; an alert without a runbook is incomplete (§I.2).
- **K.2 Ownership.** Every service/endpoint has an owner (CODEOWNERS, Part 34.P) accountable for its SLOs, dashboards, and on-call.
- **K.3 Operational-readiness review (ORR)** before a service reaches prod: SLOs defined, dashboards + alerts wired, runbook written, on-call staffed, load-tested (§L), DR tested (Part 41 §U), telemetry-privacy reviewed (§R).
- **K.4 Game days.** Periodic on-call training + **chaos/failure-injection** drills (dependency loss, region failover) validate runbooks and degrade paths (§B.8).

## L. Capacity, Performance & Load

- **L.1 Latency budgets** (p95/p99) are SLOs (§E); the API is **stateless + horizontally scalable** (Part 13), the heavy CV/model work is **queued** (Part 39) with autoscaling on saturation (§F.3).
- **L.2 Load/stress/soak/spike testing** before prod and on major change; a **performance-regression gate** (latency/throughput) complements the accuracy gate (Part 29) — a change that doubles p99 fails.
- **L.3 Backpressure.** Saturation triggers graceful backpressure (429 + queue, Part 41 §O / Part 39), never silent drops or unbounded queues; per-tenant quotas bound noisy neighbors (Part 41 §F.5).
- **L.4 Capacity planning.** Forecast from growth telemetry; headroom targets; GPU capacity for the CV/model path is a tracked constraint (Part 12/13).

## M. Cost & FinOps Observability

- **M.1 Cost is a signal.** Cost **per tenant / per analysis / per model** is measured + attributed (tags), with **budget alerts** (Part 39 §BC); expensive analysis is a **financial-DoS** vector (Part 41 §O/§F.5).
- **M.2 Unit economics.** Track $/analysis and $/active-player so pricing + efficiency are data-driven; cold telemetry/events tier to cheap storage (Part 39 §AI; local §R.4).
- **M.3 Efficiency vs reliability** trade-offs are explicit; cost-cutting **MUST NOT** silently breach an SLO or the reliability law (Part 40).

## N. Deployment & Release Observability

- **N.1 Progressive delivery.** Releases use **canary / blue-green**; deploys emit **markers** on dashboards so regressions are tied to a version (§C.5).
- **N.2 Automated rollback.** A canary that **burns error budget** (§E) or trips an SLI (latency/error/calibration §H) **auto-rolls-back**; humans are notified, not required to catch it.
- **N.3 Feature flags + kill-switch.** Risky features ship behind flags with an instant **kill-switch** (Part 34.AU, Part 41 §T.4); flag state is telemetry.
- **N.4 Model rollout.** Model promotions follow Part 41 §AP (signed, dual-control, canary + rollback) with calibration/abstention SLIs (§H) as the **canary signal** — not just latency.
- **N.5 Deploys are reversible + observed.** No deploy without a tested rollback and live release-health dashboards.

## O. Environments & Configuration

- **O.1 Parity.** dev/stage/prod parity (Part 41 §Y per-env secrets); stage is representative enough to catch perf/behavior regressions.
- **O.2 Config as data.** Configuration (SLO targets, thresholds, flags) is versioned, validated on load, and auditable (Part 34.AL); a bad config fails fast at startup, not at runtime.
- **O.3 No secrets/PII in config telemetry** (Part 41 §Y/§K.3; local §R); config changes are change-events (§N markers).

## P. Data & Pipeline Observability

- **P.1 Pipeline health.** Outbox dispatch rate, **consumer lag**, and **DLQ depth** (Part 39 §AJ/§BD) are SLIs; a growing DLQ or lag pages (§I).
- **P.2 Data quality + freshness.** Monitor input quality (✅ `input_quality` on runs), detection-rate distribution, capture-tier mix, and derived-data freshness (§H.4); a quality drop is a leading indicator.
- **P.3 Lineage.** Telemetry ties a derived artifact to its sources (Part 40 §J provenance) so a bad output is traceable to a bad input/model.
- **P.4 Schema drift.** Event/data schema drift is caught by the governance gates (Part 37/39) and surfaced operationally.

## Q. Synthetic Monitoring & RUM

- **Q.1 Black-box probes.** Synthetic checks exercise **critical user journeys** (Part 32: upload→analyze→profile, login, game-plan) from outside, 24/7, alerting on the user-visible promise — not just internal health.
- **Q.2 White-box** (the three pillars §C) explains **why** a synthetic probe failed.
- **Q.3 RUM.** Real-user monitoring captures actual client-side latency/errors for the web/app surfaces (privacy-respecting, §R).

## R. Telemetry Privacy, Retention & Cost

- **R.1 No sensitive data in telemetry.** Logs/metrics/traces **MUST NOT** contain PII, tokens, secrets, raw biometric, or full signed media URLs (Part 41 §K.3); scrub + allow-list fields (§C.1).
- **R.2 Sampling.** High-volume traces/logs are **sampled** (head/tail) — tail-based sampling keeps the interesting (slow/error) traces; metrics aggregate, not per-event.
- **R.3 Cardinality control.** Metric labels are **bounded** (no user-id/free-text labels) — unbounded cardinality is an outage + cost risk; enforced in CI (§U).
- **R.4 Retention tiers.** Telemetry retention is tiered (hot→cold→expire, Part 39 §AI); audit (Part 41 §K) has its own longer, tamper-evident retention — **operational telemetry is not the audit log**.
- **R.5 Telemetry has a budget.** Observability cost is itself monitored (§M); over-instrumentation is a cost + privacy liability.

## S. Observing Reliability & Honesty (the platform's conscience)

- **S.1 Honesty dashboards.** A standing dashboard shows **abstention rate (§H.1), calibration health (§H.2), OOD rate (§H.3), confidence/tier distributions (§H.4), and human-override rate (§H.7)** — the operational answer to "is the system still honest?"
- **S.2 Over-confidence is an incident.** A measured drop in abstention with no accuracy gain, or calibration drift, is a **reliability incident** (Part 40 §BO) — paged, contained (kill-switch/recalibrate/rollback), disclosed, postmortem'd.
- **S.3 Fairness in production.** Subgroup SLIs (Part 40 fairness / Part 41 §AC.7) are monitored where labels allow; a subgroup served materially worse reliability is an incident, not a backlog item.
- **S.4 Feedback loop.** Human corrections/overrides + officiating reviews feed back as production labels (Part 30) for monitoring + recalibration (Part 40 §AJ).

## T. Build-Artifacts Status (honest, grounded in `backend/`)

| Capability | Artifact | Status |
|------------|----------|--------|
| Liveness endpoint | `app/routers/health.py` `/healthz` + test | ✅ |
| Correctness SLI gate (golden set) | `app/benchmark.py` + `tests/test_benchmark.py` | ✅ |
| Per-run reliability/quality telemetry | `AnalysisRun.reliability_index` / `input_quality` / provenance | ✅ |
| Operational run state | `status`/`error`/`started_at`/`finished_at` on runs | ✅ |
| Governance/observability CI gates | `tools/governance/` | 🟡 |
| Readiness/liveness split + dependency checks | — | ⬜ |
| Metrics endpoint (`/metrics`, golden signals) | — | ⬜ |
| Distributed tracing (OTel) + correlation ids | — | ⬜ |
| Structured (JSON) logging + scrubbing | — | ⬜ |
| SLO/SLI definitions + error-budget tracking | §E targets | ⬜ |
| Alerting + on-call + runbooks | Part 34 §AE (prose) | ⬜ |
| Honesty dashboards (abstention/calibration/OOD) | Part 40 signals exist; not dashboarded | ⬜ |
| Load/perf-regression gate · synthetic monitoring | — | ⬜ |
| Cost/FinOps observability | — | ⬜ |

The core that **exists** is the truthful seed: a health check, a correctness gate, and per-run reliability/provenance signals. The metrics/traces/logs/SLO/alerting stack is **specified and tracked** (⬜) — production-blocking, earned by code, not by intent (Part 41 §B.5).

## U. Governance & CI Enforcement (observability invariants)

CI **MUST** keep the platform observable by construction (the observability analogue of Parts 37/39/40/41 governance); target home `backend/tools/governance/` (e.g. an `observability.py` check).

| Check | Invariant | Status |
|-------|-----------|--------|
| `health-endpoint` | every deployable service exposes a liveness check | ✅ (`/healthz`) |
| `correctness-gate` | the golden-set accuracy gate runs + must stay green | ✅ (benchmark) |
| `metrics-present` | every service exposes `/metrics` with golden signals | ⬜ |
| `structured-logs` | no bare `print`; logs are JSON + scrubbed (no PII) | ⬜ |
| `trace-context` | correlation/trace ids propagated API→worker→event | ⬜ |
| `slo-defined` | every user-facing route has an SLI/SLO + an alert + a runbook | ⬜ |
| `label-cardinality` | metric labels are bounded (no user-id/free-text labels) | ⬜ |
| `no-pii-telemetry` | telemetry fields are allow-listed (Part 41 §R/§K.3) | ⬜ |

- **U.1** Each ✅/🟡 invariant has a test; 🟡→✅ means the CI assertion exists, not just the behavior.
- **U.2** The build manifest (Part 37 governance) **SHOULD** record the observability-gate result alongside the others.

## V. Open Problems & Roadmap (honest)

- **Real-time uncertainty telemetry** (Part 40 §AY) is expensive within latency budgets — distilled UQ heads are the roadmap; until then, sample.
- **Production correctness without ground truth** — markerless reliability (Part 40 §M) can't be directly verified live; rely on calibration drift (§H.2), OOD (§H.3), and human-override (§H.7) as proxies.
- **Multi-tenant cardinality/cost** — per-tenant observability at federation scale strains cardinality + cost (§R.3/§M); aggregation + sampling is the bridge.
- **Subgroup SLIs need labels** — fairness monitoring (§S.3) is gated on subgroup-labeled production feedback (Part 30/40).

## W. Glossary & Notation

Canonical via Part 38 where applicable: **SLI / SLO / SLA** (indicator / objective / agreement) · **error budget** (`1−SLO`) · **burn rate** (budget-consumption speed) · **RED** (rate/errors/duration) · **USE** (utilization/saturation/errors) · **golden signals** · **p95/p99** (latency percentiles) · **OTel** (OpenTelemetry) · **trace / span / correlation id** · **cardinality** (label-value count) · **DLQ** (dead-letter queue) · **MTTD/MTTR** (detect/respond, Part 41) · **toil** (manual repetitive ops) · **runbook** · **IC** (incident commander) · **blameless postmortem** · **ORR** (operational-readiness review) · **canary / blue-green** (progressive delivery) · **RUM** (real-user monitoring) · **synthetic monitoring** (black-box probes) · **abstention rate / calibration drift / OOD rate** (honesty SLIs, §H, Part 40). These notations are used across Parts 13/29/34/39/40/41/42.

This document is the authoritative operability law for TT-OS; with the data model (37), ontology (38), event contract (39), reliability law (40), and security law (41), it completes the platform's build foundation — **structure, meaning, communication, honesty, trust, and operability.**

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
