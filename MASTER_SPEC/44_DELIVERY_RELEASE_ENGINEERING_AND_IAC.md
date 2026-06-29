# PART 44 — DELIVERY, RELEASE ENGINEERING & INFRASTRUCTURE-AS-CODE (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative delivery law** of the platform — the **eighth build pillar** after the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), operability law (42), and intelligence law (43). Where those say *what to build and how it must behave*, this part says **how it gets from a commit to production — repeatably, safely, and reversibly.**
>
> Parts 42 (observe releases) and 43 (promote models) both **assume** a delivery system exists; this part **defines** it: CI/CD, infrastructure-as-code, build & packaging, environments, schema-migration delivery, progressive rollout, release management, rollback/DR, and the governance that keeps deploys honest.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`. It **formalizes the scattered delivery conventions of Part 34 (git/CI/Docker) + Part 13 (DR/architecture) for build**. RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` (grounded in `backend/` + `.github/`) · 🟡 `PARTIAL` · ⬜ `SPECIFIED`. Honesty rule (Part 41 §B.5): a capability is ✅ only if it is in the repo. Today a real **CI** pipeline exists (`.github/workflows/ci.yml`: secret-scan · i18n · backend tests · governance), with Alembic migrations + a build manifest; **CD, containerization, and IaC are ⬜** — and this part says so (§S).

---

## A. Scope & Objectives

### A.1 Purpose
Make every change reach production through **one automated, gated, auditable path** — built once, promoted by artifact, deployed progressively, and reversible at all times — so shipping is **boring, frequent, and safe**, never a heroic manual event.

### A.2 Goals
- **G1.** Everything is **code**: pipelines, infrastructure, config, environments, and migrations are version-controlled + reviewed (§B/§F).
- **G2.** Every change flows through the **CI/CD pipeline** (§C); **no manual production changes** (§M).
- **G3.** Builds are **reproducible + signed**; an artifact is built **once** and **promoted** across environments unchanged (§E/§G).
- **G4.** Every deploy is **reversible** (rollback) and **progressive** (canary/blue-green) by default (§J/§L).
- **G5.** Schema/data migrations are **backward-compatible + reversible** — zero-downtime by discipline (§I).
- **G6.** Infrastructure is **declarative (IaC)**, immutable, and drift-detected (§F).
- **G7.** Delivery performance is **measured** (DORA, §Q); pipeline + deploys are themselves secured (§N) + governed (§M/§R).
- **G8.** The pipeline is **honest** about what is automated vs manual (§S) — a green CI badge means what it says.

### A.3 Non-goals
- Not infra **security** (Part 41 §AG) — it **delivers** infra that complies with §AG.
- Not release **observability** (Part 42 §N) — it **emits** the deploy markers Part 42 consumes.
- Not model **promotion criteria** (Part 43 §J) — it **executes** the rollout once §J passes.
- Not the app's runtime behavior — it is the **shipping** of it.

### A.4 Relationship to Parts
Formalizes Part 34 (git/CI/Docker conventions, §L) + Part 13 (architecture/DR); executes Part 43 §L (model rollout) + Part 42 §N (progressive delivery, observed); complies with Part 41 §AG (infra), §S (supply chain), §Y (secrets), §U (BCDR), §AM (change approval), §K (deploy audit); delivers Part 37 schema via migrations (§I); carries the build manifest (Part 37 governance) as deploy provenance.

---

## B. Principles

- **B.1 Everything as code.** Pipelines, infra, config, and environments are **declarative, version-controlled, reviewed** — no click-ops, no snowflake servers (§F).
- **B.2 Build once, promote.** An artifact is built **one time** and the **same bytes** move dev→stage→prod (§G.3); never rebuilt per environment (rebuild = unverified artifact).
- **B.3 Immutable infrastructure.** Servers/images are **replaced, not mutated**; a fix is a new version + redeploy, not an SSH patch (§F.3).
- **B.4 Every change through the pipeline.** Production changes happen **only** via the automated path (§C); a manual prod change is an incident (§M.1).
- **B.5 Reversible by default.** Every deploy has a tested **rollback**; if you can't roll it back, you can't ship it (§L).
- **B.6 Progressive by default.** Changes reach users **gradually** (canary/flag), watched by SLIs (Part 42 §H), auto-rolled-back on burn (§J).
- **B.7 Small batches, trunk-based.** Short-lived branches + frequent small merges reduce risk + lead time (§D, §Q DORA).
- **B.8 Config ≠ code.** Configuration + secrets are **separate** from the artifact (12-factor), injected per environment (§H).
- **B.9 Honesty.** A control is ✅ only if in the repo (Part 41 §B.5); "we could deploy manually" is **not** a delivery pipeline (§S).

---

## C. The CI/CD Pipeline

The single gated path from commit to production. CI exists today (✅ `.github/workflows/ci.yml`); CD is ⬜.

- **C.1 Stages (gated):** `build → test → scan → govern → package → publish → deploy(promote)`. A failed stage **stops** the pipeline — no override without a logged exception (Part 41 §AM.5).
- **C.2 CI today (✅).** On every push + PR: **secret-scan** (trufflehog), **i18n** (glossary build/validate), **backend** (install → `alembic upgrade head` → `pytest`), **governance** (spec-drift enforcement + governance tests + build-manifest artifact). These are the **build/test/scan/govern** gates (Parts 37/41/43).
- **C.3 CD (⬜).** Package (container, §E) → publish (signed, to a registry) → deploy via environment promotion (§G) with progressive rollout (§J) — **specified, not yet built**.
- **C.4 Fast + reliable.** The pipeline is **fast** (cache, parallel jobs) and **deterministic** — a flaky pipeline erodes trust (§Q); flaky tests are quarantined + fixed, not ignored.
- **C.5 One pipeline.** The same definition runs for every service; pipeline logic is **reviewed code** (no ad-hoc deploy scripts).
- **C.6 Provenance.** Each run emits a **build manifest** (✅ today: migration rev · route hash · state) → the deploy's provenance (Part 37 governance, §M.4).

## D. Source Control & Branching

- **D.1 Trunk-based.** Short-lived branches merge to a protected `main` frequently (§B.7); long-lived divergent branches are avoided.
- **D.2 Protected main.** Merges require **green CI** (§C) + **review** (CODEOWNERS, Part 34.P); no direct pushes to `main`; signed commits **SHOULD** be required.
- **D.3 PR discipline.** Small, focused PRs; conventional-commit messages; the PR is the unit of review + audit (Part 41 §K).
- **D.4 Branch → environment.** A clear mapping (e.g. `main` → stage on merge, tag → prod) is **declared**, not improvised (§G).

## E. Build & Packaging

- **E.1 Reproducible builds.** Pinned dependencies + lockfiles + pinned toolchain → the same source yields the same artifact (Part 43 §I reproducibility); hermetic where feasible.
- **E.2 Containerization (⬜).** Services ship as **OCI images**: **multi-stage, digest-pinned base, non-root, read-only FS, minimal layers** (Part 41 §AG.2); a `HEALTHCHECK` hits `/healthz` (Part 42 §G, Part 34 §L).
- **E.3 Artifact registry.** Built images/artifacts are stored in a registry with **immutable tags + digests**; "latest" is never deployed (§G.3).
- **E.4 Supply-chain integrity.** Artifacts carry an **SBOM** (Part 41 §S.2) and are **signed** (cosign-style) with **provenance** (SLSA-style); only signed artifacts deploy (§N, ties Part 43 §K model signing).
- **E.5 Build = artifact + manifest.** Every build records what it is (version, commit, deps, manifest §C.6) so a running instance is traceable to its source (Part 40 §J provenance).

## F. Infrastructure-as-Code (IaC)

- **F.1 Declarative IaC (⬜).** All infrastructure (compute, network, DB, storage, queues, secrets scaffolding) is defined as **code** (Terraform/Pulumi/CloudFormation), version-controlled + reviewed — **no console click-ops** (§B.1).
- **F.2 Plan → review → apply.** IaC changes show a **plan/diff**, are reviewed, and applied **only** via the pipeline (least-priv CI identity, Part 41 §AG.3); humans don't `apply` from laptops.
- **F.3 Immutable + modular.** Infra is replaced not mutated (§B.3); reusable **modules** keep environments consistent (§G parity).
- **F.4 Drift detection.** Actual infra is continuously diffed against IaC; **drift is an alert** (Part 42 §V) + reconciled — manual infra changes are caught (§R).
- **F.5 Policy-as-code.** Guardrails (no public buckets, encryption-on, tagging, region pinning — Part 41 §AG/§W) are enforced as **code** in the plan stage (OPA/Sentinel), not by review vigilance.

## G. Environments & Promotion

- **G.1 Tiered environments.** `dev → stage → prod` with **parity** (Part 42 §O.1): stage is representative enough to catch regressions; prod-like data is governed (Part 41 §C — no raw PII in lower envs).
- **G.2 Ephemeral preview envs.** Each PR **SHOULD** spin up an isolated, disposable environment (IaC §F) for review + integration tests, torn down on merge (cost-bounded, §P).
- **G.3 Promotion = artifact promotion.** The **same** signed artifact (§E.3) is promoted across environments by changing config (§H), **not rebuilt** (§B.2); promotion is gated (tests/approvals §M).
- **G.4 Isolation.** Environments are network- + credential-isolated (Part 41 §Y per-env secrets, §F tenant isolation); a lower env cannot reach prod data.

## H. Configuration & Secrets Delivery

- **H.1 12-factor config.** Configuration is **environment-injected** (env vars / config service), never baked into the artifact (§B.8); the same image runs everywhere, configured per env.
- **H.2 Secrets at deploy.** Secrets come from a **secrets manager** (Part 41 §Y), injected at deploy/runtime — **never** in the image, repo, IaC state, or CI logs (Part 41 §S.3); rotation is non-disruptive (Part 41 §Y.2).
- **H.3 Config validation.** Config is **schema-validated at boot**; a bad/missing value **fails fast** at startup, not at first request (Part 42 §O.2).
- **H.4 Config is auditable.** Config changes are versioned + are **change events** (deploy markers, Part 42 §N); the dev-default secret (e.g. `JWT_SECRET`, Part 41 §D.3) is **forbidden** in prod — enforced at boot.

## I. Database & Schema-Migration Delivery

Concrete to the repo: Alembic owns the schema (✅ `backend/migrations/`, CI runs `alembic upgrade head`).

- **I.1 Migrations are code + reviewed.** Schema changes are **versioned migrations** (✅ Alembic) — never manual DDL on prod; Part 37 owns the data model, migrations deliver it.
- **I.2 Backward-compatible (expand → migrate → contract).** A deploy's migration **MUST** be compatible with the **currently-running** code (the old version still works mid-deploy), enabling **zero-downtime**: add columns/tables (expand), backfill, switch code, then remove the old (contract) in a **later** release — never expand+contract in one step.
- **I.3 Reversible.** Migrations provide a tested **down-path** or a forward-fix plan; an irreversible migration (data loss) needs explicit approval (§M, Part 41 §AM.5) + a backup (Part 41 §U).
- **I.4 Data migrations** (large backfills) run **online/batched** with backpressure (Part 41 §O), monitored (Part 42), and resumable — not a blocking transaction.
- **I.5 Migration safety in CI.** CI runs migrations (✅) and the governance gate checks **ORM↔migration drift + round-trip** (✅ Part 37); a destructive migration is flagged for review.
- **I.6 Decouple migrate from deploy.** Migrations run as a **distinct, ordered step** (not implicit at app boot in prod) so they're observable + reversible independently.

## J. Progressive Delivery

- **J.1 Strategies.** Default to **canary** or **blue-green** or **rolling** — never a big-bang replace; the strategy is per-service + declared (§F).
- **J.2 Feature flags.** Risky changes ship **dark** behind flags (Part 34.AU), decoupling **deploy** from **release**; flag flips are audited + reversible (§L) with an instant **kill-switch** (Part 41 §T.4).
- **J.3 Automated rollback.** A canary that burns **error budget** or trips an SLI — latency/errors **or calibration/abstention** (Part 42 §H/§N.2) — **auto-rolls-back**; humans are notified, not required to catch it.
- **J.4 Model rollout.** Model promotions execute Part 43 §L (shadow→canary, calibration as canary signal) through this same machinery — code and models ship the same safe way.
- **J.5 Bounded blast radius.** Canary exposure is a small %/segment first; tenant/region-scoped rollout limits a bad deploy's reach (Part 41 §F).

## K. Release Management & Versioning

- **K.1 Semantic versioning.** Artifacts + APIs use **semver**; a breaking change bumps major + follows the deprecation policy (Part 37 §API versioning / Part 39 event versioning).
- **K.2 Release process.** Releases are **tagged, changelog'd, and reproducible** from the tag (§E.1); a release bundles the artifact + its manifest (§C.6) + migration set (§I).
- **K.3 Coordinated versions.** API (37), event (39), schema (I), and model (43) versions are **compatible by release** — a deploy never ships an API expecting a schema/migration that isn't applied (§I.2).
- **K.4 Cadence + trains.** A predictable cadence (continuous or release-train) with **freeze windows** (§M.3) for high-stakes periods (e.g. a live tournament, Part 09).
- **K.5 Deprecation.** Removing an API/event/field follows a **announced, dual-version, sunset** path (Part 37/39) — never a silent break.

## L. Rollback, Recovery & DR/BCP

- **L.1 Every deploy reversible.** Rollback is **automated + tested** (§J.3); roll back to the **last-good artifact** (§E.3) — forward-only "fixes" under pressure are forbidden unless rollback is impossible (then §I.3 forward-fix).
- **L.2 Stateful rollback care.** A code rollback **MUST** stay compatible with the already-applied migration (§I.2 expand/contract makes this safe); never roll a schema back under live traffic without the compat window.
- **L.3 DR execution.** Disaster recovery is **practiced**: multi-region/failover, **tested restores** (Part 41 §U.2), and **RTO/RPO** targets met (Part 41 §AK / Part 42 §U); an untested DR plan is a hope, not a plan.
- **L.4 Runbooks + game days.** Rollback + DR have runbooks (Part 42 §K) exercised in **game days** (Part 42 §K.4); failover is muscle memory, not improvisation.

## M. Deployment Governance & Change Management

- **M.1 No manual prod changes.** Production changes happen **only** through the pipeline (§B.4); an out-of-band change is an **incident** + audited (Part 41 §K).
- **M.2 Approvals.** Prod deploys carry the right **approval** (Part 41 §AM RACI); high-risk deploys (officiating/medical models, irreversible migrations) need **dual-control** (Part 41 §AP.3 / §AM.3).
- **M.3 Freeze windows.** Change-freeze during high-stakes events (live matches, Part 09) — only break-glass fixes, audited.
- **M.4 Deploy provenance.** Every deploy records **what (artifact+manifest §C.6), who, when, why, and approval** → an immutable deploy log (Part 41 §K), tying a running version to its commit + reviewers (Part 40 §J).
- **M.5 Auditable + reproducible.** Any production state is reproducible from the deploy record (artifact + config + migration) — required for incident forensics (Part 42) + officiating defensibility (Part 41 §L).

## N. Pipeline & Supply-Chain Security

- **N.1 The pipeline is a target.** CI/CD has **least-privilege, short-lived** credentials (no long-lived cloud keys); a compromised pipeline = a compromised prod (Part 41 §S.3).
- **N.2 Signed, provenanced artifacts.** Build provenance (SLSA-style) + **signing** (§E.4); deploy **verifies signatures** — an unsigned/unverified artifact **MUST NOT** deploy (ties Part 41 §AP, Part 43 §K).
- **N.3 No secrets in the pipeline.** Secret-scan (✅ trufflehog) + secrets-manager injection (§H.2); CI logs are scrubbed (Part 42 §R.1).
- **N.4 Dependency + image scanning.** SBOM + vuln scan (Part 41 §S.2) + image scan (Part 41 §AG.2) gate the package stage; a critical CVE blocks release (Part 41 §AK SLA).
- **N.5 Protected pipeline definition.** Changes to the pipeline/IaC are reviewed like prod code (§D.2); the pipeline can't be edited to bypass its own gates.

## O. GitOps & Declarative Deploys

- **O.1 Desired state in git.** Deployments + infra are **declared in git**; a reconciler converges actual→desired (GitOps) — git is the single source of truth + audit (§M.4).
- **O.2 Declarative over imperative.** Prefer declared end-state over deploy scripts; reconciliation is **idempotent + self-healing** (drift §F.4).
- **O.3 Rollback = git revert.** Reverting the desired-state commit rolls back the deploy — auditable, reviewable, reversible (§L.1).

## P. Cost & Efficiency of Delivery

- **P.1 Fast pipelines.** Build/test **caching**, parallelism, and incremental builds keep lead time low (§Q); slow pipelines tax every change.
- **P.2 Ephemeral-env cost.** Preview envs (§G.2) are **time-boxed + right-sized + torn down** (Part 42 §M); delivery infra is itself cost-observed.
- **P.3 Efficient artifacts.** Small images (§E.2) cut registry, transfer, and cold-start cost (Part 42 §L.6).

## Q. DORA Metrics & Delivery Performance

- **Q.1 Measure delivery.** Track the four **DORA** metrics: **deployment frequency**, **lead time for changes**, **change-failure rate**, **time-to-restore** (MTTR) — delivery is a product with SLIs (Part 42 §E).
- **Q.2 Improve by data.** A low deploy frequency / high change-failure rate is a **process defect** to fix (smaller batches §B.7, better tests §C); targets per Part 41 §AK cadence.
- **Q.3 Stability + throughput together.** Speed **and** safety are co-optimized — progressive delivery (§J) + rollback (§L) make frequent deploys **low-risk**, not reckless.

## R. Governance & CI Enforcement (delivery invariants)

CI **MUST** enforce delivery hygiene (the delivery analogue of Parts 37/39/40/41/42/43 governance); the existing pipeline (§C.2) is the seed.

| Check | Invariant | Status |
|-------|-----------|--------|
| `ci-required` | every change runs build/test/scan/govern before merge | ✅ (`ci.yml`) |
| `secret-scan` | no secret reaches the repo (trufflehog) | ✅ |
| `migration-applies` | migrations apply cleanly (`alembic upgrade head`) | ✅ |
| `migration-roundtrip` | ORM↔migration drift + round-trip (Part 37) | ✅ (governance) |
| `build-manifest` | each build emits a provenance manifest | ✅ |
| `no-manual-prod` | prod changes only via pipeline (deploy log shows it) | ⬜ |
| `iac-no-drift` | actual infra matches IaC (§F.4) | ⬜ |
| `signed-artifact` | only signed, SBOM'd artifacts deploy (§E.4/§N.2) | ⬜ |
| `migration-safety` | destructive/irreversible migrations flagged for approval (§I.3) | ⬜ |
| `rollback-tested` | each release has a verified rollback path (§L.1) | ⬜ |

- **R.1** Each ✅/🟡 invariant has a test; 🟡→✅ means the CI assertion exists, not just intent.
- **R.2** The build manifest (✅) is the deploy-provenance record (§M.4); CD checks extend the same gate.

## S. Build-Artifacts Status (honest, grounded in repo)

| Capability | Artifact | Status |
|------------|----------|--------|
| CI pipeline (build/test/scan/govern) | `.github/workflows/ci.yml` (4 jobs) | ✅ |
| Secret scanning in CI | trufflehog job | ✅ |
| Schema-migration delivery | Alembic `backend/migrations/` + CI `upgrade head` | ✅ |
| Migration round-trip / drift gate | `tools/governance` (Part 37) | ✅ |
| Build/deploy provenance manifest | `build_manifest.json` (CI artifact) | ✅ |
| i18n build gate | `i18n/build.py` job | ✅ |
| Containerization (Dockerfile, OCI image) | — | ⬜ |
| Artifact registry + signing + SBOM | — | ⬜ |
| Infrastructure-as-code (Terraform/Pulumi) | — | ⬜ |
| CD / deploy automation | — | ⬜ |
| Multi-environment (dev/stage/prod) + parity | sqlite-dev / Postgres-prod noted | 🟡 |
| Ephemeral preview environments | — | ⬜ |
| Progressive delivery (canary/blue-green) | — | ⬜ |
| Automated rollback + DR execution | — | ⬜ |
| DORA metrics | — | ⬜ |

The truthful seed **exists**: a real CI pipeline that tests, scans, governs, and migrates on every change, with build provenance — a strong **CI** foundation. **CD, containerization, and IaC are ⬜** — the platform can be *built + verified* automatically but not yet *shipped* automatically. Stating that is the point (§B.9).

## T. Open Problems & Roadmap (honest)

- **The CD gap** (§C.3) — CI is solid; the package→publish→deploy half is ⬜; roadmap: container + registry + IaC + a CD controller (GitOps §O).
- **Zero-downtime at scale** (§I.2) — expand/contract migrations + stateful rollback are disciplined but error-prone; tooling + checks (§R `migration-safety`) reduce risk.
- **Multi-region DR** (§L.3) — true active-active failover with data residency (Part 41 §AJ) is operationally hard; roadmap, tested incrementally.
- **Stateful/data migrations** (§I.4) — large online backfills without user impact remain delicate; batching + monitoring is the bridge.

## U. Glossary & Notation

Canonical via Part 38 where applicable: **CI / CD** (continuous integration / delivery-deployment) · **IaC** (infrastructure-as-code) · **artifact / registry / image digest** · **SBOM / signing / provenance (SLSA)** · **build-once-promote** · **immutable infrastructure** · **drift detection** · **trunk-based / protected branch / CODEOWNERS** · **semver / changelog / release train** · **expand→migrate→contract** (zero-downtime migration) · **blue-green / canary / rolling / feature flag** (progressive delivery) · **kill-switch** · **rollback / forward-fix** · **DR / BCP / RTO / RPO** (Part 41) · **GitOps / reconciler / desired state** · **policy-as-code** (OPA/Sentinel) · **ephemeral / preview environment** · **12-factor config** · **DORA** (deploy frequency · lead time · change-failure rate · MTTR) · **freeze window / break-glass** (Part 41) · **build manifest** (deploy provenance, §C.6). These notations are used across Parts 13/34/37/41/42/43/44.

This document is the authoritative delivery law for TT-OS; with the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), operability law (42), and intelligence law (43), it forms the ship-it core of the platform's build foundation — **structure, meaning, communication, honesty, trust, operability, intelligence, and delivery.** Part 45 adds the ninth pillar — **experience** (the human-facing client).

---

➡️ **NEXT FILE: `45_FRONTEND_AND_CLIENT_ARCHITECTURE.md`**
