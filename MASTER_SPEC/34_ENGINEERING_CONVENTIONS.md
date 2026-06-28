# PART 34 — ENGINEERING CONVENTIONS

> Read `00_INDEX.md` first. The rules of the codebase. The practical quick-start lives in the root `CLAUDE.md`; this is the canonical detail.

## A. Code style
- Python: PEP 8, **type hints** on public functions, short docstrings on modules/classes. Keep lines readable (~100 cols).
- **Match the surrounding code** — naming, structure, comment density. No drive-by reformatting.
- Names use the **`canonical_id`s** of Part 28 (e.g. `banana_flick`, `long_pips`) — never ad-hoc strings.

## B. Project structure
- **Engines are packages** (`app/cv/`, `app/analytics/`) with narrow interfaces; **routers stay thin** (validate → call engine → serialize).
- **Analytics are pure functions** where possible (input data → dict) so they're trivially testable and later swappable for ML/LLM.
- **Pluggable interfaces** for models (`BallDetector`, future `StrokeClassifier`, …) so deep models (Part 26) drop in without touching callers.

## C. API conventions
- REST under `/v1`; resource-oriented; plural nouns.
- Every **measured** value uses the **reliability envelope** `{value, confidence, ci, tier, source, status}` (Part 10/27).
- Errors: `401` (no/blacked token), `403` (RBAC), `404` (not found / not in tenant), `422` (validation), `429` (rate limit).
- **Org-scope every query**; derive tenant from the token, never the body. Writes get a `require_roles(...)` dependency.

## D. Database & migrations
- **Alembic owns the schema.** ORM in `app/models.py` mirrors migrations. Never use `create_all` outside tests.
- One migration per schema change; `alembic upgrade head` must run clean on SQLite **and** Postgres (use `render_as_batch`).
- IDs UUID; times `timestamptz`; nested/flexible data `JSON`/`jsonb`; `0..1` confidences as numeric with a check.

## E. Testing
- `pytest`; in-memory SQLite via the shared-engine fixtures (`tests/conftest.py`).
- Every endpoint: a happy-path + an auth/RBAC + a validation test.
- Accuracy-bearing code is covered by the **golden-set gate** (`tests/test_benchmark.py`) — it must stay green.
- CI runs migrations + tests + glossary build on every push (`.github/workflows/ci.yml`).

## F. CV / model conventions
- Every model output carries **`confidence` + `provenance` (source, tier, signals)**.
- **Honesty flags** are mandatory: uncalibrated speed/spin say so; markerless estimates cap confidence; below threshold → **abstain**, don't guess.
- New detectors implement the existing interface and ship with a benchmark + target (Part 29).

## G. i18n
- All user-facing strings come from the glossary by `canonical_id`. Add the term to `i18n/glossary.json` first, then `build.py`. Arabic is RTL.

## H. Git & reviews
- Feature branches; small, focused commits with a clear subject + body.
- **Definition of done:** tests pass · migrations clean · golden gate green · reliability/RBAC respected · docs/glossary updated if needed.
- PR checklist: what changed · how tested · any migration · any new term · reliability impact.

## I. Security defaults (always on)
- Deny-by-default RBAC; org-scoped queries; no secrets in code/logs; validate & sandbox uploads; never log PII/tokens (Part 31).

## J. Tooling & dependencies
- **Format/lint/type:** `ruff` + `black` + `isort` + **`mypy`**, enforced by **pre-commit** and CI.
- **Dependencies:** pinned + a lockfile; isolated virtualenv; scheduled vuln-scanned updates (Part 31).

## K. Configuration (12-factor)
- Config from **env / `pydantic-settings`** only — **no hardcoded config or secrets**; fail-fast on bad/missing prod config (e.g. the JWT-secret guard).

## L. Logging, errors & observability
- **Structured logs** (JSON) with **correlation IDs**; levels used correctly; **never log PII/tokens**.
- **Custom exception types** → mapped to the right HTTP code centrally (no leaking stack traces).
- Expose **health/readiness**, metrics, and traces (OpenTelemetry) — Part 13.

## M. Performance & concurrency
- Avoid **N+1 queries**; index hot paths; **paginate** lists; cache where safe.
- **Async I/O** for network/DB in the API; CPU/GPU work in workers (Part 13). Worker code is **thread-safe**; the analysis pipeline is **deterministic** (fixed seeds — Part 13.4).

## N. Versioning & compatibility
- **SemVer** for the package; **`/v1`** for the API. **Changelog** maintained.
- **Deprecation policy** (announce → grace period → remove); **migrations are backward-compatible & reversible** — no destructive change without a backup/expand-contract.

## O. Documentation & decisions
- Module docstrings + a README per package; **OpenAPI is the API contract** (keep it in sync).
- **ADRs** (Architecture Decision Records) for significant choices — short, dated, with context + consequences.

## P. Branching, commits & review
- Short-lived **feature branches** off the dev branch; **small PRs**.
- **Conventional-style commits** with a clear body; keep the project's **co-author / session footer**.
- PRs need green CI + at least one review; **CODEOWNERS** for sensitive areas (auth, officiating, migrations).

## Q. Testing depth
- Types: **unit · integration · e2e**; coverage target ~**80%** on logic (not a vanity 100%).
- **Property-based tests** for CV/math (e.g. spin on generated arcs); deterministic, **no flaky** tests; clean, isolated test data.

## R. CI/CD & environments
- Pipeline gates: **lint + type + tests + secret-scan + golden-set** must pass to merge.
- Environments **dev → staging → prod**; migrations run before deploy; **documented rollback**.

## S. MLOps conventions (ties Part 12)
- **Model registry** + **experiment tracking**; **reproducible training** (seeds, pinned data); **datasets versioned** (DVC). A model ships only with its **eval report + model card** (Part 29).

## T. Naming conventions (concrete)
| Thing | Style | Example |
|-------|-------|---------|
| files/modules | `snake_case` | `opponent_dossier.py` |
| classes | `PascalCase` | `BallDetector` |
| funcs/vars | `snake_case` | `aggregate_profile` |
| constants | `UPPER_SNAKE` | `MIN_SAMPLE` |
| DB tables/cols | `snake_case`, plural tables | `player_profiles.style_class` |
| API paths | plural nouns | `/v1/players/{id}` |
| env vars | `UPPER_SNAKE` | `JWT_SECRET` |
| domain values | `canonical_id` (Part 28) | `banana_flick` |

## U. Module boundaries & layering
- Layering: **routers → engines (cv/analytics) → models**; **never** the reverse. Routers don't import each other; **analytics never imports routers/DB session** (pure functions take data in).
- **No circular imports**; shared helpers live in a low-level module. Vendor types are wrapped, not leaked across layers.

## V. API design depth
- **Idempotency-Key** on create-side POSTs (analyze, game-plan); **cursor pagination** + consistent `limit`/`after`; standard `filter`/`sort` params.
- Correct **HTTP semantics** (`201` create, `204` no-content, `409` conflict); consistent error body `{code,message}`; the **reliability envelope** on measured values.

## W. Database conventions
- **Every table:** UUID pk, `created_at` (+ `updated_at` where mutable), all times **UTC / `timestamptz`**.
- Explicit **FK on-delete** (`CASCADE`/`SET NULL`); index every FK + hot filter; **soft-delete** (status/archived) for user data, hard-delete only via RTBF.
- Keep business logic in the app, not the DB; **short transactions**; migrations expand-contract (Part 34.N).

## X. Background jobs, resilience & caching
- Jobs are **idempotent** (safe to retry), with **retries + backoff**, a **dead-letter** path, and a visible status.
- External calls get **timeouts + retries-with-backoff + circuit breakers**; never block the request thread on them.
- **Caching:** explicit keys + invalidation; never cache authz decisions or PII.

## Y. Dev workflow
- **Definition of Ready** (clear scope + acceptance + test plan) before work; **Definition of Done** (Part 34.H) before merge.
- **Review checklist:** correctness · tests · reliability/RBAC · migration safety · no secrets/PII · docs/glossary.
- **Onboarding:** one-command setup (`make dev` / devcontainer); **comments explain *why*** not *what*; `TODO(owner: …)` with a ticket. **Feature flags** for risky/gradual rollout.

## Z. Test conventions
- **Fixtures/factories** for test data (no copy-paste); **mock external services**; **contract tests** for the API (provider/consumer).
- Deterministic (fixed seeds); fast unit tests; integration tests on in-memory SQLite; the **golden set** is the accuracy gate (Part 29).

## AA. Frontend & client conventions (Part 32)
- **TypeScript strict**; components small & typed; **design tokens** (Part 32.R), never hard-coded colors/spacing. **No business logic in the UI** — it calls the API and renders the **reliability envelope**; it never recomputes confidence client-side.
- **i18n in code:** every string via the glossary `canonical_id` (Part 28) — no literals in JSX; **true RTL** for Arabic (logical CSS props `inline-start/-end`, not `left/right`).
- **Accessibility in code:** semantic HTML, keyboard focus order, ARIA labels, colour-blind-safe chart palettes — **WCAG 2.1 AA** asserted in component tests (Part 32.L).

## AB. Containerization & environment parity
- **Multi-stage Dockerfiles**; **digest-pinned** base images; run as **non-root**; only the venv + app in the final layer; `HEALTHCHECK` hits `/health`.
- **Dev/prod parity** (12-factor): the *same* image dev→staging→prod, config via env only; **devcontainer / `make dev`** for one-command onboarding (Part 34.Y).
- GPU images (Part 26 deep models) pin **CUDA/cuDNN**; the **CPU fallback** path stays runnable — the classical detector means the stack boots and serves without a GPU.

## AC. Time, dates & units
- **All timestamps UTC, ISO-8601, tz-aware** — never naive `datetime.now()`; localize only at the UI edge (Part 32.L). Durations in **seconds**; video positions as **frame index + fps**, never assume 30 fps.
- **Physical units explicit & canonical:** SI internally (m, m/s, **rad/s** for spin), convert at the boundary; the **unit travels with the value** in the envelope — km/h vs m/s, rpm vs rad/s can never be confused (Part 10/29).

## AD. Numerical & scientific computing (CV/physics)
- **Determinism:** seed every RNG (`numpy`, models); the pipeline is reproducible (Part 13.4); pin BLAS threads where results must be bit-stable.
- **Float discipline:** never `==` on floats — use tolerances; **guard NaN/inf** (occlusion, divide-by-zero in spin/curvature) and **abstain** instead of emitting garbage (Part 10).
- **Vectorize** with numpy over Python loops on hot paths; **name physical constants** — gravity, ball mass/radius, drag/Magnus coefficients live in one constants module (no magic numbers, Part 19).

## AE. Third-party adapters & SLOs
- **Anti-corruption layer:** wrap every vendor (TTNet/YOLO weights, OCR, future LLM, S3, email/push) behind *our* interface — vendor types never leak across layers (Part 34.U); swapping a provider touches **one adapter**.
- **SLOs + error budgets** per service (API latency, analysis turnaround, accuracy gate); **graceful degradation** — a down dependency drops to a lower **capture tier** / **abstain**, it never 500s the whole analysis (Part 10/13).

## AF. Secrets & key management (runbook)
- **No secrets in repo, CI logs, or images** (enforced by trufflehog, Part 31); secrets come from a vault/KMS, injected as env at runtime only.
- **Rotation:** scheduled rotation for the JWT signing key, DB creds, and vendor API keys; **short-lived tokens**; support **two valid keys during rotation** (zero downtime); documented **break-glass + revoke** path (Part 31 incident response).

## AG. Data migrations & backfills
- **Schema vs data:** schema = Alembic (Part 34.D); **data backfills are separate, idempotent, resumable, batched** scripts (no giant single transaction) with a **dry-run** and a row-count reconciliation.
- **Expand → migrate → contract** for breaking changes (add new · dual-write/backfill · switch reads · drop old) so deploys stay **zero-downtime and reversible**; every backfill is **logged + audited** (Part 31).

## AH. Input validation & boundary contracts
- **Parse, don't validate:** every external input (body, query, upload, webhook, vendor response) is parsed into a **Pydantic** model at the edge; the inside of the app trusts only typed objects.
- **Never trust the client for trust decisions:** tenant `org_id` and role come from the **token**, never the body (Part 31 AD); **reject unknown fields** (`extra="forbid"`) to kill mass-assignment.
- **Validate at the boundary, fail with `422`**; bound every list/string/number (lengths, ranges, enums = `canonical_id`s) — no unbounded input reaches an engine or the DB.

## AI. Media & upload handling (the video pipeline)
- **Sniff content, don't trust extensions/filenames;** enforce **size + duration + codec** limits; **quarantine + malware-scan** before processing; **strip metadata** (EXIF/GPS) on ingest.
- **Storage behind an interface** (local dir → S3) — callers never see paths; serve via **short-lived signed URLs**, never a raw user-controlled path (no path traversal, no SSRF on `source=url`, Part 31).
- **Transcode/analyze in the worker, not the request;** persist the **input-quality report** (light/occlusion/fps) so the **reliability envelope** can down-weight bad footage (Part 10/32.K).

## AJ. PII & privacy in code (Part 31)
- **Field-level access in the serializer, not the UI:** medical/injury data is omitted server-side for coaches — RBAC decides shape, hiding is **hidden, not disabled**.
- **Consent is a code gate:** no analysis of a **minor** without a valid guardian-consent record; processing checks consent + purpose, and **retention TTL jobs** delete/anonymize on expiry (RTBF cascades).
- **Pseudonymize in logs & datasets:** IDs not names; training/eval data is de-identified; **no real player PII in the repo, fixtures, or CI** — synthetic only.

## AK. Audit & provenance in code
- **Every analysis run is reproducible:** persist **code SHA + model versions + params + seeds + capture tier** with the result (Part 10 provenance; "everything is a Model").
- **Append-only audit trail** for sensitive actions — officiating override, consent change, role/RBAC change, data export/DSAR — recording **actor · org · timestamp · before/after**; audit logs are **immutable** and never carry secrets/PII payloads (Part 31).

## AL. Reliability as a first-class return type
- Estimators return the **envelope `{value, confidence, ci, tier, source, status}` or `abstain`** — never a bare float or a silent `None`; "preliminary" and "needs review" are **real states**, not nulls.
- **Uncertainty propagates** through aggregation — don't average it away; a profile built from thin/low-confidence inputs stays low-confidence. **Thresholds are config**, not magic numbers (Part 29 gates).

## AM. Error-handling philosophy
- **No bare `except`**; catch narrow, **chain** (`raise NewError(...) from err`); never swallow an error into a default silently.
- **Fail loud for programmer/contract errors** (bug → `500` + alert); **fail soft for data/vendor errors** — degrade a tier or **abstain**, don't crash the run (Part 34.AE).
- **User-safe messages only** (`{code,message}`); full detail and stack live in **structured logs** with a correlation ID, never in the API response (Part 34.L).

## AN. Equations & scientific provenance
- **Every physics/stat formula cites its spec section + source** (Part 19 trajectory/Magnus · Part 20 biomechanics · Part 21 tactics) in the docstring, with **units stated**.
- **No undocumented coefficient** (drag, Magnus, restitution, anthropometric ratios) — named, sourced, in one constants module; each model is **validated against a known/analytic case** in tests (Part 34.AD).

## AO. Rate limiting, quotas & abuse
- **Per-org / per-key token-bucket** limits; **expensive endpoints** (`analyze`, `game-plan`) cost more budget; over limit → **`429 + Retry-After`**.
- **Protect auth:** progressive backoff / lockout on failed logins (Part 31 AC); **fair-use across tenants** — one org can't starve others (no noisy-neighbor on the worker queue).

## AP. Contract & schema-drift (CI-enforced)
- **ORM == migrations:** CI runs `alembic upgrade head` then an autogenerate **diff that must be empty** — `models.py` can never silently drift from the migrations.
- **OpenAPI == routes:** `api/openapi.yaml` is checked against the live FastAPI schema; **glossary completeness** is asserted (no missing EN/AR `canonical_id`). Drift **fails the build** (Part 27/28).

## AQ. Concurrency, transactions & lost updates
- **Session-per-request, short transactions;** retry on deadlock/serialization with backoff.
- **Optimistic locking** (a `version` column / `If-Match`+ETag) so two coaches editing the same profile don't clobber each other — last-write-wins is **rejected**, not silent.
- **Single-flight per video:** an advisory lock / dedup key means a video is **analyzed once**, never twice concurrently (Part 34.X idempotency).

## AR. Outbound webhooks & integrations
- **Signed** (HMAC + timestamp), **replay-protected**, retried with backoff + **dead-letter**; **at-least-once → receivers must be idempotent**.
- **No PII in payloads** — send IDs + a **short-lived signed fetch URL**, not the data; destinations are **allow-listed** (no SSRF, Part 31).

## AS. Graceful lifecycle & resource governance
- **Graceful shutdown:** drain in-flight requests and **checkpoint/requeue jobs on `SIGTERM`** (k8s-safe) — never lose or half-finish an analysis.
- **Probes split:** *liveness* (am I up) vs *readiness* (deps OK — DB/queue/storage) vs *startup*; only readiness gates traffic.
- **Compute/cost governance:** **batch GPU inference**, autoscale workers off **queue depth**, cost caps + **backpressure** instead of unbounded spend (Part 26).

## AT. Licensing, SBOM & model provenance
- **License compliance:** track third-party licenses; **no copyleft contamination** in distributed code; generate an **SBOM** per release (Part 31 supply chain).
- **Pretrained weights carry license + source + checksum** and are pinned — **no weights of unknown provenance** ship (defends the poisoned-weights threat, Part 26/31).

## AU. Config governance & feature flags
- **Every env var documented + validated at boot** (fail-fast, like the JWT-secret guard) with safe defaults; config is typed (`pydantic-settings`), never read ad-hoc.
- **Feature flags** for risky/gradual rollout and **kill-switches** (deep models, LLM, officiating); flags are typed, **default-off**, and **removed after rollout** — no permanent flags rotting in the code (Part 34.Y).

## AV. Mobile & offline-first (player app)
- **Offline capture → local queue → later sync** (Part 32.P); sync is **idempotent** with explicit **conflict resolution** — the **server is authority** for scores/profiles, the client never wins a merge silently.
- **Budgets:** battery, storage, and data-usage caps for self-recording; **OTA-updatable**; deep links + a managed **push-token lifecycle**.
- The **same reliability envelope** renders on mobile — a thin-data number is "preliminary" on the phone too, never a bare value.

## AW. On-device / edge inference
- On-device models (Part 35 capture) are **quantized + size-budgeted**, with a **graceful fallback to the server** when the device can't run them.
- On-device results are **tagged a lower capture tier** and **re-verified server-side** before they harden a profile; **no PII leaves the device** without consent (Part 34.AJ).

## AX. Multi-tenancy depth & isolation testing
- Beyond org-scoping: a **mandatory cross-tenant test per resource** — org A must get **`404`** on org B's data; an unscoped query **fails review** (the non-negotiable from `CLAUDE.md`).
- **Per-tenant limits/config**; **tenant lifecycle is first-class** — create · suspend · **export** · delete-with-cascade (RTBF) — none of it leaks across orgs (Part 31).

## AY. Data pipeline & lineage (the ML data plane)
- Staged **raw → curated → features → train/eval**, each stage **immutable + versioned** (DVC, Part 34.S); **lineage tracked** — which clips/labels produced which model (Part 34.AK).
- **No split leakage:** train/test are **player-disjoint**; **PII is de-identified before it enters the plane** (Part 34.AJ); a dataset ships with a **datasheet** (Part 29/30).

## AZ. Resilience & chaos testing
- **Test the degrade/abstain paths, not just the happy path:** inject vendor / DB / GPU failures and assert the system **drops a tier or abstains** — never `500`s the run or fabricates a number (Part 10/34.AE).
- **Load / soak / stress** before any scale claim; **restore-from-backup is tested**, not assumed (Part 31 BCDR).

## BA. On-call, runbooks & postmortems
- Each service ships a **runbook** (symptoms → checks → fixes) and an **owner** (CODEOWNERS, Part 34.P); alerts are **actionable + tied to SLOs** — no alert spam.
- Incidents get a **blameless postmortem** with tracked action items (Part 31 incident response); recurring toil becomes a backlog item, not a habit.

## BB. LLM & agent engineering
- **Grounded only:** an LLM feature may state **only numbers the engines produced** (with the envelope) — **no hallucinated stats**; every claim is **cited** to evidence (Part 10/21).
- **A prompt is a model:** prompts are **versioned + eval'd** with a model card (Part 29); **structured JSON output validated against a schema**; **temperature pinned** for reproducibility.
- **Prompt-injection defense:** untrusted video text / opponent notes are **data, never instructions** (Part 31); **token/cost budgets** + **graceful fallback to rule-based** when the LLM is down or over budget.

## BC. Real-time & streaming
- Live officiating / courtside / streamed partial results (Part 13.6/14) use **authenticated WebSockets** with the **same RBAC + org-scope** as REST.
- **Heartbeat + reconnect + resume**; **backpressure** (coalesce/drop, never OOM); events are **ordered + idempotent** (sequence numbers).
- The live path still carries **confidence** and can **abstain** — no fake real-time call (Part 10).

## BD. Court coordinate frame & calibration
- **One canonical court coordinate system** (defined origin, axes, **metres**) shared by all CV/physics; pixels → court via a **calibrated homography**.
- Every spatial value states its **frame + units**; **calibration quality feeds the reliability envelope** (poor calibration → lower tier).
- Multi-cam (T3) is **time-synced + extrinsically calibrated** before fusion; un-calibrated geometry **abstains** rather than guesses (Part 19/35).

## BE. Derived data & materialization
- Profiles, dossiers, matchups are **derived artifacts** — recomputed by **versioned, deterministic, idempotent** jobs, **never hand-edited**.
- **Invalidate on input change** (new video → profile stale → rebuild); each artifact is stamped with the **inputs + model versions** it was built from (Part 34.AK). **Staleness is visible**, not silent.

## BF. Fairness & bias engineering (in code)
- Models/thresholds are **tested across subgroups** — para classes, junior vs senior, sex, **left- vs right-handed**, skin tone for detection — so no group is silently underserved (Part 29 fairness).
- **No able-bodied assumption** baked into para analysis (Part 24); a **subgroup regression fails the gate** exactly like an accuracy regression.

## BG. Stable error catalog
- A **registry of error codes** (stable string codes, not raw prose) returned as `{code, message}`; codes are **documented + localized** (glossary) and **never renumbered** — clients depend on them.
- Each code **maps deterministically to an HTTP status** (Part 34.AM/V); adding a code is a reviewed, versioned change.

## BH. Rules-as-code (ITTF)
- The **laws of the game** — scoring to **11 / 2-clear**, **service legality**, let, edge/net, **expedite**, racket-covering legality — live in **one versioned rules engine**, a single source of truth; **never magic numbers scattered in code**.
- Each rule **cites its ITTF handbook clause**, is **tested against known cases**, and every **officiating call is derived from the engine** (explainable + reproducible), not hand-coded per feature (Part 21/25).

## BI. Domain-knowledge versioning
- Domain data that changes over time — **ITTF rules by year**, the **approved-equipment (LARC) list**, the ontology/glossary (Part 28) — is **versioned with effective dates**, never hardcoded.
- An analysis records **which rule-year + equipment version** it used, so a past match stays **reproducible under the rules that applied then** (Part 34.AK/BE).

## BJ. Synthetic & simulation data
- Synthetic footage / sim data is **explicitly labeled and segregated** — it may train or smoke-test, but **never enters a real eval / golden set** (Part 29).
- **Domain randomization** for robustness; the **sim-to-real gap is measured + tracked**, not assumed away (the repo's synthetic-video generator is dev/test-only).

## BK. Match-event modeling (append-only)
- Rallies, shots, bounces, and calls are an **immutable, append-only event log** with stable IDs + timestamps; **corrections are new events, never overwrites**.
- The log is **replayable** to rebuild any derived artifact (Part 34.BE) and underpins **audit + officiating integrity** (Part 34.AK / Part 31).

## BL. Product analytics & experimentation
- Product events use a **typed taxonomy** — **no PII, consent-gated** (Part 34.AJ); analytics never become a backdoor around privacy.
- Experiments / A-B are **pre-registered** (hypothesis + **guardrail metrics**), read with **statistical rigor** (no peeking); **never ship a change that quietly lowers accuracy or confidence-honesty** (Part 16/32.AC).

## BM. Data retention & archival tiers
- Match/video data moves **hot → warm → cold** with documented **retention + archival** (Part 31); archived data stays **restorable + tenant-scoped**.
- **Legal-hold and RTBF override tiering**; storage growth is **governed, not unbounded** (Part 34.AS).

---

➡️ **NEXT FILE: `35_HARDWARE_AND_CAPTURE_SOP.md`**
