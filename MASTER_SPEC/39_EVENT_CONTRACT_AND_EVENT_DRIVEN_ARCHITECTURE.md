# PART 39 — EVENT CONTRACT & EVENT-DRIVEN ARCHITECTURE (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative event contract** for the platform — the third pillar of the build triad after the data model (Part 37) and the ontology (Part 38). It defines every domain/integration/audit event, the canonical envelope, delivery semantics, the transactional outbox, consumers, webhooks, versioning, governance, and acceptance.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`, where it is the build target. RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` · 🟡 `PARTIAL` · ⬜ `SPECIFIED` (build target). The MVP executes analysis **inline** (Part 37 §B.4); the event layer is largely ⬜ and **MUST** be built to this contract so a broker drops in without contract change.

---

## A. Scope & Objectives

### A.1 Purpose
Define a single, versioned contract for everything the system **announces**: state changes (domain events), outbound integrations, audit/officiating records, and reliability/capture signals — so producers and consumers evolve independently without breakage.

### A.2 Goals
- **G1.** Every cross-context state change **MUST** be expressible as an event under this contract.
- **G2.** Events **MUST** be reliable (at-least-once), **ordered per aggregate**, and **idempotent** for consumers.
- **G3.** Events **MUST** carry tenant scope, provenance, and confidence where they assert measured facts (Parts 10/31/34.AK).
- **G4.** The event type registry **MUST** be the SSoT; producers **MUST NOT** emit an uncatalogued type (§R).
- **G5.** Event payloads **MUST** use Part 38 `canonical_id`s and **MUST NOT** carry PII beyond identifiers (§O).

### A.3 Non-goals
- This document **MUST NOT** select a specific broker (Kafka/NATS/SQS/Redis Streams) — Part 13 owns infrastructure; this is the contract the broker serves.
- It **MUST NOT** redefine entities (Part 37) or vocabulary (Part 38); it references them.

### A.4 Relationship to Parts 01–38
Realizes Part 37 §R (event architecture) + §S (webhooks) + §H (`domain_events`, `idempotency_keys`); names events with Part 38 taxonomy; carries the Part 10 reliability envelope and Part 34.AK provenance; feeds Part 32 notifications and Part 35 capture signals.

---

## B. Architectural Principles

- **B.1 Event-driven, not event-sourced (by default).** The system of record is the relational store (Part 37); events are **derived announcements** emitted via an **outbox**, not the primary truth. Event-sourced aggregates **MAY** be introduced later for the append-only analysis log (Part 34.BK) without changing this contract.
- **B.2 Transactional outbox.** An event **MUST** be written in the **same database transaction** as the state change it describes (`domain_events` table, §I); a relay publishes asynchronously. This guarantees no lost or phantom events.
- **B.3 At-least-once + idempotent consumers.** Delivery is at-least-once; every consumer **MUST** dedupe on `idempotency_key`/`event_id` (§H).
- **B.4 Per-aggregate ordering.** Events for one `aggregate_id` **MUST** carry a monotonic `sequence` and be processed in order; global ordering is **NOT** guaranteed.
- **B.5 Immutability.** A published event is immutable; corrections are **new** events (Part 34.BK). Audit/officiating events are append-only + tamper-evident (§L).
- **B.6 Provenance-first.** Events asserting a measured/evidentiary fact **MUST** carry `provenance_hash` (Part 34.AK).
- **B.7 Backward compatibility.** Schemas evolve additively; breaking change → new `event_version` (§P).
- **B.8 Privacy by design.** Payloads carry **ids + canonical_ids + signed fetch URLs**, never raw PII or media (§O, Part 34.AR).

---

## C. Canonical Event Envelope

Every event **MUST** be a JSON object with exactly these top-level fields. Unknown extra top-level fields **MUST** be rejected by validators (closed envelope); forward-compatible growth happens inside `data`.

| Field | Type | Req | Meaning |
|-------|------|-----|---------|
| `event_id` | uuid | MUST | Globally unique id of this event instance |
| `type` | string | MUST | `tt.<context>.<aggregate>.<verb>` (§D) |
| `spec_version` | string | MUST | Envelope contract version (`"1.0"`) |
| `event_version` | int | MUST | Per-`type` payload schema version (starts at 1) |
| `occurred_at` | string | MUST | ISO-8601 UTC, tz-aware (Part 34.AC) |
| `org_id` | uuid | MUST¹ | Tenant scope (Part 37 §N) |
| `aggregate_type` | string | MUST | Entity table name (Part 37 §E), e.g. `analysis_run` |
| `aggregate_id` | uuid | MUST | The aggregate instance |
| `sequence` | int | MUST | Monotonic per `aggregate_id` (≥ 1) |
| `actor` | object\|null | MUST | `{type: user\|system\|service, id}` |
| `correlation_id` | uuid | MUST | Ties events to one request/trace (Part 34.L) |
| `causation_id` | uuid\|null | MUST | The event/command that caused this one |
| `idempotency_key` | string | MUST | Dedupe key (unique per logical event) |
| `data` | object | MUST | Typed payload (§G); ids + `canonical_id`s only |
| `data_schema` | string | SHOULD | Pointer to the payload schema/version |
| `provenance_hash` | string\|null | MUST² | sha256 over evidentiary payload (Part 34.AK) |

¹ Platform-level events with no tenant (`tt.org.created`) **MAY** set `org_id` to the created org's id. ² `null` for non-evidentiary events; **MUST** be present for audit/officiating/reliability/capture events.

**Canonical example (`tt.analysis.run.completed`, v1):**
```json
{
  "event_id": "9f2c…", "type": "tt.analysis.run.completed",
  "spec_version": "1.0", "event_version": 1,
  "occurred_at": "2026-06-28T12:00:00Z",
  "org_id": "org-1", "aggregate_type": "analysis_run", "aggregate_id": "run-1",
  "sequence": 3, "actor": {"type": "system", "id": "worker"},
  "correlation_id": "req-1", "causation_id": "evt-run-started",
  "idempotency_key": "analysis_run.completed:run-1",
  "data": {
    "video_id": "vid-1", "match_id": "match-1",
    "reliability_index": 0.81, "capture_certification": "gold",
    "model_versions": {"ball_detector": "opencv-baseline@0.1"}
  },
  "data_schema": "#/events/tt.analysis.run.completed/v1",
  "provenance_hash": "sha256:…"
}
```

---

## D. Event Naming & Taxonomy

- **D.1** Type format **MUST** be `tt.<context>.<aggregate>.<verb>`, all lowercase `snake_case` segments.
- **D.2** `<context>` **MUST** be a bounded context (Part 37 §C). `<aggregate>` **MUST** be a Part 37 entity. `<verb>` **MUST** be a past-tense state change (`created`, `completed`, `failed`, `certified`, `recorded`, `revoked`, `detected`, `requested`).
- **D.3** Domain values inside payloads **MUST** be Part 38 `canonical_id`s (e.g. `capture_certification ∈ {bronze…platinum}`, stroke/spin ids).
- **D.4** Type strings are **immutable** once published; a rename = deprecate + add (§P). The set of valid types is the **registry** (§Q).

---

## E. Event Categories

| Category | Purpose | Delivery | Retention |
|----------|---------|----------|-----------|
| **domain** | a business state change | outbox → broker → consumers | warm |
| **integration** | outbound to third parties (webhooks) | outbox → webhook relay (signed) | warm |
| **audit** | sensitive action record | outbox → append-only audit store | long (immutable) |
| **reliability** | confidence/abstain/drift signal | outbox → broker | warm |
| **capture** | capture-session/certification signal | outbox → broker | warm |
| **analysis** | pipeline lifecycle | outbox → broker | warm |
| **notification** | user-facing message request | outbox → notification service | short |

A single event **MAY** carry more than one category tag, but **MUST** have exactly one primary category recorded in the registry.

---

## F. Complete Event Catalog

Every event the platform emits. `Ver` = current `event_version`. All ⬜ unless noted (the emit points exist as code paths today but do not yet publish — Part 37 §B.4).

| Type | Category | Trigger | Aggregate | Key payload | Consumers |
|------|----------|---------|-----------|-------------|-----------|
| `tt.org.created` | domain | org registered | organization | `name` | provisioning, billing |
| `tt.identity.user.registered` | domain | user created | user | `role` | notification, audit |
| `tt.identity.user.disabled` | audit | user disabled | user | `reason` | audit, sessions |
| `tt.admin.role.changed` | audit | RBAC change | user | `from_role,to_role` | audit |
| `tt.consent.recorded` | audit | consent captured | player | `consent_type,guardian` | audit, analysis-gate |
| `tt.consent.revoked` | audit | consent withdrawn | player | `consent_type` | audit, retention |
| `tt.player.created` | domain | player added | player | `player_type,para_class?` | profile |
| `tt.player.archived` | domain | player archived | player | — | retention |
| `tt.video.uploaded` | domain | media stored | video | `source,capture_tier` | analysis |
| `tt.video.ingest_failed` | domain | ingest error | video | `reason` | notification |
| `tt.capture.session.started` | capture | session opened | capture_session | `venue_id,tier` | monitoring |
| `tt.capture.session.ended` | capture | session closed | capture_session | — | monitoring |
| `tt.capture.certified` | capture | capture certified | analysis_run | `certification,effective_score,provenance_hash` | analysis, dashboard |
| `tt.capture.failed` | capture | capture fault | capture_session | `kpi,reason` | operator, notification |
| `tt.analysis.run.queued` | analysis | run enqueued | analysis_run | `video_id` | monitoring |
| `tt.analysis.run.started` | analysis | run began | analysis_run | `video_id` | monitoring |
| `tt.analysis.run.completed` | analysis | run done | analysis_run | `match_id,reliability_index,capture_certification` | profile, notification |
| `tt.analysis.run.failed` | analysis | run failed | analysis_run | `error` | notification, on-call |
| `tt.analysis.run.abstained` | reliability | output below threshold | analysis_run | `reason,confidence` | dashboard |
| `tt.profile.rebuilt` | domain | profile recomputed | player_profile | `version,confidence` | matchup, notification |
| `tt.opponent.dossier.created` | domain | dossier built | opponent_dossier | `subject_player_id,confidence` | matchup |
| `tt.matchup.created` | domain | matchup created | matchup | `my_player_id,opponent_dossier_id` | gameplan |
| `tt.matchup.gameplan.ready` | domain | plan generated | game_plan | `matchup_id,confidence` | notification |
| `tt.gameplan.outcome.recorded` | domain | efficacy logged | game_plan | `match_id,effectiveness` | analytics (Part 16) |
| `tt.officiating.call.logged` | audit | automated/assisted call | match | `call_type,confidence,provenance_hash` | evidence, audit |
| `tt.officiating.call.overridden` | audit | human override | match | `from,to,umpire_id` | evidence, audit |
| `tt.reliability.model.drift_detected` | reliability | drift monitor alarm | model | `metric,delta` | on-call, MLOps |
| `tt.security.login.failed` | audit | failed auth | user | `attempt_count` | rate-limit, audit |
| `tt.security.token.revoked` | audit | token/session revoked | user | `reason` | sessions, audit |
| `tt.security.access.denied` | audit | RBAC denial | user | `resource` | audit |
| `tt.data.export.requested` | audit | DSAR start | player | `request_id` | DSAR worker |
| `tt.data.export.completed` | audit | DSAR done | player | `request_id,signed_url` | notification |
| `tt.data.deletion.requested` | audit | RTBF start | player | `request_id` | retention worker |
| `tt.data.deletion.completed` | audit | RTBF done | player | `request_id` | audit |
| `tt.dataset.version.published` | domain | dataset versioned | dataset | `version` | MLOps (Part 12) |
| `tt.model.deployed` | domain | model released | model | `model_version` | inference, audit |
| `tt.inference.job.completed` | domain | inference done | inference_job | `model_version,run_id` | analysis |
| `tt.notification.requested` | notification | user-facing notice | notification | `channel,template,recipient_id` | notification service |
| `tt.webhook.delivery.failed` | integration | webhook DLQ | webhook_endpoint | `endpoint_id,attempts` | on-call |

New events **MUST** be added to this catalog **and** the registry (§Q) in the same PR.

---

## G. Payload Schemas

Payloads are closed objects of the fields below (+ envelope §C). Types reference Part 37 columns and Part 38 enums. Representative authoritative schemas:

- **`tt.analysis.run.completed` v1** — `{ video_id: uuid, match_id: uuid|null, reliability_index: number[0..1]|null, capture_certification: enum|null, model_versions: object }`.
- **`tt.capture.certified` v1** — `{ certification: enum(bronze..platinum), effective_score: number[0..1], capture_tier: enum(T1,T2,T3,T3_OFFICIATING), reliability_envelope: object, failed_gates: array }` (Part 35); `provenance_hash` **MUST** be set.
- **`tt.matchup.gameplan.ready` v1** — `{ matchup_id: uuid, game_plan_id: uuid, confidence: number[0..1], preliminary: boolean }`.
- **`tt.officiating.call.logged` v1** — `{ call_type: canonical_id(event), rally_id: uuid|null, decision: string, confidence: number[0..1], evidence_package_id: uuid|null }`; `provenance_hash` **MUST** be set; event is **audit** + append-only.
- **`tt.consent.recorded` v1** — `{ player_id: uuid, consent_type: string, guardian: boolean, lawful_basis: string }`; **MUST NOT** include the guardian's PII (id only).
- **`tt.notification.requested` v1** — `{ channel: enum(in_app,email,push,sms), template: string, recipient_id: uuid, params: object }`; `params` **MUST NOT** contain PII beyond ids/`canonical_id`s.

Every measured numeric in a payload **MUST** be accompanied by a confidence (inline or via the reliability envelope) and **MAY** be `null` to express `abstain` (Part 10).

---

## H. Delivery Semantics & Ordering

- **H.1 At-least-once.** Consumers **MUST** be idempotent; processing the same `event_id`/`idempotency_key` twice **MUST** have no additional effect.
- **H.2 Ordering.** Within one `aggregate_id`, consumers **MUST** honor `sequence`; an out-of-order event **MUST** be buffered or rejected, never applied out of order. Cross-aggregate ordering is **NOT** guaranteed.
- **H.3 Idempotency store.** Consumers **MUST** persist processed keys (`idempotency_keys`, Part 37 §H) with a TTL ≥ the maximum redelivery window.
- **H.4 Exactly-once *effect*.** Achieved by at-least-once delivery + idempotent consumers; the system **MUST NOT** claim exactly-once *delivery*.

---

## I. Transactional Outbox & Persistence

- **I.1** Producers **MUST** insert the event row into `domain_events` (Part 37 §H) **inside the same transaction** as the aggregate write. No event without its state change; no state change silently without its event.
- **I.2 `domain_events`** (⬜, Part 37 §H): `(id, org_id, type, event_version, aggregate_type, aggregate_id, sequence, payload jsonb, occurred_at, published_at null, idempotency_key unique, provenance_hash)`. A partial index on `published_at IS NULL` drives the relay poll (Part 37 §K.4).
- **I.3 Relay.** A separate, idempotent **publisher** polls unpublished rows, publishes to the broker/webhook relay, and stamps `published_at`. The relay **MUST** retry with backoff and **MUST NOT** block request threads (Part 34.X).
- **I.4 Sequence allocation.** `sequence` **MUST** be allocated per `aggregate_id` transactionally (e.g. `MAX(sequence)+1` under the aggregate lock, Part 34.AQ).

---

## J. Consumers & Subscriptions

- **J.1** A consumer **MUST** declare the `type`s (and min `event_version`) it handles and **MUST** tolerate unknown fields/types (forward-compat).
- **J.2** Handlers **MUST** be idempotent, bounded in time, and **MUST** move poison messages to a **dead-letter** queue after N retries (§N).
- **J.3** A consumer **MUST NOT** assume it is the only subscriber; side effects **MUST** be scoped to its own context (Part 37 §C).
- **J.4 Internal consumers (MVP):** profile-rebuild on `tt.analysis.run.completed`; notification on `*.ready`/`*.failed`; audit-writer on every `audit` event; retention-worker on `tt.consent.revoked`/`tt.data.deletion.requested`.

---

## K. Webhooks Mapping (outbound integration)

Integration events are delivered to tenant-registered endpoints (Part 37 §S, Part 34.AR).

- **K.1** Payload = the canonical envelope with `data` reduced to **ids + a short-lived signed fetch URL** — never the data itself.
- **K.2** Each delivery **MUST** be **HMAC-SHA256 signed** (`X-TTOS-Signature`) over the raw body + timestamp; receivers **MUST** verify and reject stale/replayed deliveries.
- **K.3** Delivery is at-least-once with backoff + dead-letter; receivers **MUST** be idempotent on `event_id`.
- **K.4** Destinations **MUST** be allow-listed (no SSRF); secrets live in the vault (Part 31).
- **K.5** Supported outbound: `analysis.run.completed`, `capture.certified`, `matchup.gameplan.ready`, `data.export.completed`.

---

## L. Audit & Officiating Integrity Events

- **L.1** Every **audit** event **MUST** be written to an **append-only** store; updates/deletes **MUST** be rejected (Part 37 §F).
- **L.2** Audit/officiating events **MUST** carry `actor`, `occurred_at`, `provenance_hash`, and (for officiating) the `evidence_package_id` (Part 35.T).
- **L.3** Officiating events **MUST** be **tamper-evident**: the `provenance_hash` covers the decision payload; a chain hash (prev-hash) **SHOULD** link consecutive officiating events for an aggregate (Part 31).
- **L.4** Audit payloads **MUST NOT** contain secrets or PII beyond ids (Part 34.AK).

---

## M. Reliability & Capture Events

- **M.1** `tt.analysis.run.abstained` **MUST** be emitted whenever the pipeline declines to assert (Part 10); `data.confidence` **MUST** be present and `reason` set.
- **M.2** `tt.capture.certified` **MUST** carry the certification level, effective score, and reliability envelope (Part 35); a `fail` certification **MUST** also surface via the run's reliability cap (Part 35.AK).
- **M.3** `tt.reliability.model.drift_detected` **MUST** be emitted when a drift monitor breaches its gate (Part 29) and routed to on-call (Part 34.BA).

---

## N. Error Handling, Retries & Dead-Letter

- **N.1** Transient consumer failures **MUST** retry with exponential backoff + jitter; after N attempts the event **MUST** go to a **dead-letter** queue with the failure reason (Part 34.X).
- **N.2** A DLQ entry **MUST** be alertable and replayable after a fix; replay **MUST** be idempotent.
- **N.3** Producer/outbox failures **MUST NOT** lose events (the outbox row persists until `published_at` is set).
- **N.4** Poison/unschema'd events **MUST** be quarantined, never silently dropped (Part 34.AM).

---

## O. Security & Privacy

- **O.1** Payloads **MUST NOT** contain PII beyond identifiers, raw media, tokens, or secrets (Part 31/34.AR).
- **O.2** Every event **MUST** be tenant-scoped (`org_id`); consumers **MUST** enforce org isolation (Part 37 §N).
- **O.3** Officiating/decisive systems **MUST** run on an isolated segment (Part 35.AG); their events **MUST NOT** egress to the internet except via signed, allow-listed webhooks.
- **O.4** Event logs **MUST** redact per Part 34.L; correlation ids are pseudonymous.

---

## P. Versioning & Compatibility

- **P.1** `spec_version` governs the **envelope**; `event_version` governs a **type's payload**.
- **P.2** **Additive** payload changes (new optional field) **MUST NOT** bump `event_version`; consumers tolerate unknown fields.
- **P.3** **Breaking** changes (rename/remove/retype a field, change meaning) **MUST** introduce a new `event_version`; both versions **MAY** be emitted during a deprecation window.
- **P.4** Type strings are immutable; deprecate + add for renames; deprecated types remain valid for one major cycle (Part 38 §B.8 parity).
- **P.5** Consumers **MUST** declare the minimum `event_version` they support and **MUST** ignore higher minor revisions gracefully.

---

## Q. Build Artifacts

| Artifact | Canonical path | Owns | Status |
|----------|----------------|------|--------|
| Event registry + envelope + `emit()` | `backend/app/events.py` | the SSoT for types/schemas + outbox write | ⬜ |
| Outbox table | `domain_events` (migration) | persisted events (Part 37 §H) | ⬜ |
| Idempotency store | `idempotency_keys` (migration) | consumer dedupe (Part 37 §H) | ⬜ |
| Relay/publisher | `backend/app/events_relay.py` | poll outbox → broker/webhooks | ⬜ |
| Webhook signer | (in relay) | HMAC signing (Part 34.AR) | ⬜ |
| Event catalog (machine-readable) | `backend/app/events_catalog.json` | type → category → schema ref | ⬜ |

`events.py` **MUST** expose: the canonical envelope, a typed registry of `type → (category, event_version, payload schema)`, and `emit(type, aggregate, data, *, actor, correlation_id, causation_id)` that performs the **transactional outbox write**. Producers **MUST** call `emit()`; they **MUST NOT** publish to a broker directly.

---

## R. Governance & CI Enforcement

CI **MUST** (ties Part 37 §Z) fail the build if:
- **R.1** an emitted `type` is **not** in the registry/catalog (no uncatalogued events);
- **R.2** a registry type is **never** emitted and **never** documented as external-only (no dead types);
- **R.3** a payload fails its declared schema (closed envelope + typed `data`);
- **R.4** a payload field is **PII** by a denylist heuristic (name/email/phone/raw media) (§O);
- **R.5** a domain value in a payload is **not** a Part 38 `canonical_id` for its enum;
- **R.6** the committed `events_catalog.json` is **stale** vs `events.py` (drift gate, Part 34.AP);
- **R.7** an `audit`/`officiating`/`reliability`/`capture` event lacks `provenance_hash`.
Reviews of event changes **MUST** be co-approved by a `MASTER_SPEC/` + backend CODEOWNER and include the registry + catalog update.

---

## S. Traceability Matrix

| Event | Aggregate (Part 37) | Ontology (Part 38) | Consumers | Parts |
|-------|---------------------|--------------------|-----------|-------|
| analysis.run.* | analysis_run | `analysis_run`,`reliability` | profile, notify | 01–06/10/37 |
| capture.certified | analysis_run/capture_session | `capture_certification` | analysis, dashboard | 35/10 |
| profile.rebuilt | player_profile | `player_profile` | matchup | 17/37 |
| matchup.gameplan.ready | game_plan | `game_plan` | notify | 17/21 |
| officiating.call.* | match | `violation`,`let`,`winner` | evidence, audit | 09/31/35 |
| consent.* | player | `impairment`,consent | audit, retention | 31/24 |
| reliability.model.drift_detected | model | `model`,`benchmark` | on-call | 29/34 |
| data.export/deletion.* | player | DSAR/RTBF | DSAR/retention | 31 |
| notification.requested | notification | — | notification svc | 32 |

Every event **MUST** trace to an aggregate (37), ≥1 ontology term (38), ≥1 consumer, and ≥1 Part.

---

## T. Acceptance Criteria

The event layer conforms **iff**:
- **T.1** Every emitted event validates against the canonical envelope (§C) and its payload schema (§G).
- **T.2** Every event type is in the registry/catalog; no uncatalogued or dead types (§R.1/R.2).
- **T.3** Producers write events via the **transactional outbox**; a crash between state change and publish loses neither (§I).
- **T.4** Consumers are idempotent and order-respecting; a duplicate/redelivery has no extra effect (§H).
- **T.5** No payload contains PII beyond ids; audit/officiating/reliability/capture events carry `provenance_hash` (§O/§R).
- **T.6** Webhook deliveries are HMAC-signed, retried, dead-lettered, and allow-listed (§K).
- **T.7** Versioning is additive-by-default; a breaking change introduces a new `event_version` with a deprecation window (§P).
- **T.8** Every event traces end-to-end (aggregate → ontology → consumer → Part) (§S).

---

## U. Commands, Events & Queries (CQRS boundary)
- **Commands** are imperative requests that **MAY be rejected** (validation/authz/business rule); they map to the write API (Part 37 §O). A command is **NOT** an event.
- An accepted command **MUST** produce a state change **and** emit one or more **events** (past-tense facts, immutable) via the outbox (§I).
- **Queries** read **projections / read models** built by consumers (e.g. a denormalized match view); read models are **eventually consistent** and **MUST** expose their staleness (Part 34.BE).
- Write side (commands→events) and read side (projections) **MAY** scale independently (CQRS); the relational store remains the system of record (§B.1).

## V. Sagas & process managers (distributed workflows)
- Cross-context workflows **MUST** be modeled as **sagas** (a chain of local transactions, each emitting an event that triggers the next), never a distributed two-phase commit.
- **Flagship saga:** `video.uploaded → analysis.run.completed → profile.rebuilt → matchup.created → matchup.gameplan.ready → notification.requested`. Each step is idempotent and independently retryable.
- **Choreography** (events trigger steps) is the default; **orchestration** (a process manager) **SHOULD** be used where a step needs cross-context coordination or a timeout.
- **Compensation:** a failed step **MUST** trigger forward **compensating events** (mark failed, notify, release locks) — there is no cross-service rollback, only compensation.
- Each saga **MUST** have a **timeout** and a **terminal state**; a stalled saga **MUST** alert (Part 34.BA).

## W. Aggregate event state machines
- Each aggregate has a **legal state machine**; an event **MUST** correspond to a legal transition, and an illegal transition **MUST** be rejected (Part 37 §F).
- `video`: `uploaded → analyzing` (run.started) `→ done` (run.completed) `| failed` (run.failed) `→ archived`.
- `analysis_run`: `queued → processing → done | failed`; `done`/`failed` are **terminal** (re-analysis = a new run, never a mutation).
- `capture_session`: `started → ended`; `capture.certified` emitted against the run.
- `game_plan`: `draft → final → archived`; `gameplan.outcome.recorded` is a post-terminal annotation.
- A consumer applying an event **MUST** verify the source state (optimistic, Part 34.AQ) and **MUST** ignore or quarantine an event whose `sequence` does not match the expected next state.

## X. Schema registry & contract compatibility
- The **registry** (`events.py` + `events_catalog.json`, §Q) is the SSoT for every `type → event_version → payload schema`. A producer **MUST NOT** emit a type/version absent from it.
- **Default compatibility = BACKWARD** (new consumers read old events). Safe without a version bump: add an **optional** field; add an enum value (consumers tolerate unknown, §P.2). Breaking → **new `event_version`** (§P.3).
- **Consumer-driven contracts:** each consumer **MUST** declare the fields it depends on; CI **MUST** fail a producer change that breaks a registered consumer contract (§R; Part 34.AP).

| Change to a payload | Compatible? |
|---|---|
| add optional field · add enum value · loosen validation | ✅ (no bump) |
| remove field · rename field · change type · add required field · tighten validation · change meaning | ❌ (new `event_version`) |

## Y. Partitioning, consumer groups & scaling
- **Partition key MUST be `aggregate_id`** so per-aggregate ordering (§H.2) is preserved within a partition; cross-partition order is **not** guaranteed.
- **Tenant isolation:** `org_id` **SHOULD** be a routing dimension so one tenant cannot starve others (Part 34.AO).
- **Consumer groups** scale horizontally; a partition is handled by at most one consumer per group (ordering); parallelism is bounded by partition count.
- **Hot partitions** (a busy aggregate/tenant) **MUST** be detectable and mitigated via backpressure (§N) — never by breaking ordering.

## Z. Event observability & SLOs
- The platform **MUST** expose per type/consumer: **publish lag** (state-change→published), **consumer lag** (published→processed), **end-to-end latency**, **throughput**, **DLQ depth**, **redelivery rate** (Part 13/34.L).
- **Tracing:** `correlation_id` + `causation_id` (§C) **MUST** let an operator reconstruct an event chain / saga end-to-end.
- **SLO defaults (normative):** outbox publish-lag p95 < 5 s; consumer-lag p95 < 30 s; steady-state DLQ depth = 0 (any entry alerts). Breaches **MUST** page on-call (Part 34.BA).

## AA. Replay, reprocessing & snapshots
- The outbox/event log **MUST** be **replayable** to rebuild a derived artifact / read model (profiles, dossiers, projections — Part 34.BE) and to **backfill a new consumer**.
- Replay **MUST** be **idempotent** (consumers dedupe, §H), tenant-scopable, and time-bounded.
- **Snapshots** of expensive read models **SHOULD** bound replay cost (replay from the last snapshot, not genesis).
- A replay **MUST NOT** re-fire external side effects (webhooks/notifications) unless in an explicit, gated, audited "side-effecting replay" mode (§O).

## AB. Event testing strategy
- **Unit:** every event validates against the envelope (§C) + payload schema (§G); negative tests for closed-envelope rejection and the PII denylist (§R.4).
- **Contract:** consumer-driven contract tests (§X) run in CI per producer/consumer pair.
- **Integration:** outbox → relay → consumer, asserting the transactional outbox (a crash between state write and publish loses nothing, §I) and idempotent re-delivery.
- **Chaos:** inject duplicate / out-of-order / delayed / poison events and broker-down; assert ordering, dedupe, DLQ, and zero data loss (Part 34.AZ).

## AC. Subscription authorization & payload encryption
- **Subscription authz:** a consumer/webhook **MUST** be authorized for the `org_id` and the event types it receives; cross-tenant subscription **MUST** be denied (Part 37 §N).
- **By reference for sensitive data:** events touching medical/minor data **MUST** keep it by reference (ids + signed URL); if a sensitive value must travel, it **MUST** be field-encrypted with a rotating key (Part 34.AF/AJ).
- **Integrity:** evidentiary events carry `provenance_hash`; broker transport **MUST** be TLS; webhooks are HMAC-signed (§K, Part 31).
- **Key rotation:** webhook + encryption keys **MUST** support two valid keys during rotation (Part 34.AF).

## AD. Event granularity (fat vs thin)
- **Default: thin events** — ids + the minimal facts a consumer needs + a signed fetch URL for bulk/sensitive data (§K). Thin events keep the relational store authoritative and avoid PII sprawl (§O).
- **Event-carried state transfer (fat events)** **MAY** be used where a consumer needs **autonomy** (no callback) for decoupling/performance — but **MUST NOT** duplicate the system of record nor carry PII, and the carried state **MUST** be versioned (§P).
- The granularity choice per type **MUST** be recorded in the registry (§Q).

## AE. Time semantics & late events
- Every event carries **event-time** (`occurred_at`); consumers **MUST** distinguish it from **processing-time** (Part 34.AC).
- Clocks **MUST** be NTP/PTP-synced (Part 35.L); the system **MUST** tolerate bounded **clock skew** and **MUST NOT** assume `occurred_at` is globally monotonic across producers — use `sequence` for per-aggregate order (§H).
- **Late / out-of-order** events within an aggregate **MUST** be reordered by `sequence` or quarantined; windowed aggregations **MUST** define an allowed lateness + watermark.

---

## AF. Event Taxonomy

This is the **authoritative classification**; it refines the working categories of §E. Every event **MUST** belong to **exactly one primary taxonomy** (recorded in the registry, §AU). The §E categories map in as: domain→Domain, integration→Integration, audit→Audit, reliability→AI/ML, capture→Capture, analysis→System (pipeline lifecycle) + AI/ML (outputs), notification→Notification.

| Taxonomy | Purpose | Owner | Lifetime | Examples | Allowed publishers | Allowed subscribers |
|----------|---------|-------|----------|----------|--------------------|---------------------|
| **Domain** | a business fact/state change | owning bounded context | warm | `player.created`, `matchup.gameplan.ready` | the owning service only (§AG) | any authorized context |
| **Integration** | outbound to third parties | Integration ctx | warm | webhook deliveries (§K) | webhook relay | external endpoints (allow-listed) |
| **System** | platform process lifecycle | Platform ctx | warm | `analysis.run.*`, `inference.job.*` | the executing service | monitoring, dependent steps |
| **Infrastructure** | broker/relay/storage/deploy health | Platform/SRE | short | `webhook.delivery.failed`, DLQ, relay lag | relay/infra components | on-call, monitoring |
| **Audit** | sensitive action record | Compliance ctx | long (immutable) | `officiating.call.*`, `admin.role.changed` | any context (write-through) | audit store only |
| **Security** | authn/authz signal | Identity/Security | long | `security.login.failed`, `access.denied` | Identity ctx | SIEM, rate-limit, audit |
| **AI/ML** | model/training/inference/reliability | AI Models ctx | warm | §AP catalog | AI Models / Analysis | dashboard, MLOps, analysis |
| **Capture** | capture session + hardware | Capture ctx | warm | §AR catalog, `capture.certified` | Capture service / edge | analysis, operator dashboard |
| **Analytics** | efficacy/usage/product metrics | Analytics ctx | warm | `gameplan.outcome.recorded` | Analytics/Intelligence | analytics store (no PII, §AO) |
| **Notification** | user-facing message request | Notification ctx | short | `notification.requested` | any context | notification service |
| **Compliance** | consent/DSAR/RTBF/legal | Compliance ctx | long | `consent.*`, `data.export/deletion.*` | Compliance ctx | DSAR/retention workers, audit |

A publisher **MUST NOT** emit into a taxonomy it does not own (§AG); a subscriber **MUST** be authorized for the taxonomy + tenant (§AC).

## AG. Aggregate Ownership & Publishing Authority

**No service may publish events owned by another bounded context.** For each aggregate (Part 37 §E):

| Aggregate | Owner (authoritative service) | Allowed publishers | Allowed consumers | Forbidden publishers | Source of Truth | Conflict resolution |
|-----------|-------------------------------|--------------------|-------------------|----------------------|-----------------|---------------------|
| `organization`,`user` | Identity | Identity | all | anyone else | `users`/`organizations` | last-writer rejected (optimistic, Part 34.AQ) |
| `player` | Players | Players | Intelligence, Analysis | Analysis, CV | `players` | owner wins; others request via command |
| `video` | Video | Video ingest | Analysis | Analysis worker | `videos` | immutable after upload |
| `analysis_run`,`match`,`rally`,`shot` | Analysis | Analysis worker | Intelligence, Reports | Players, Capture | `analysis_runs`+children | append-only; new run, never mutate |
| `capture_session`,`capture_certification` | Capture | Capture service/edge | Analysis | Analysis | capture tables / Part 35 schema | certification immutable |
| `player_profile`,`opponent_dossier`,`matchup`,`game_plan` | Intelligence | Intelligence jobs | Notification, Reports | Analysis, CV | derived (Part 34.BE) | recompute, never hand-edit |
| `model`,`dataset`,`inference_job` | AI Models | MLOps/registry | Analysis | Analysis | registry (Part 12) | registry is authoritative |
| `audit_log` | Compliance | all (write-through API) | audit store | direct DB writers | append-only log | immutable |

A cross-context need **MUST** be satisfied by issuing a **command** to the owner (§U), which then publishes the owned event — never by a foreign service emitting the event directly. CI **SHOULD** enforce ownership via the producer registry (§AU/§R).

## AH. Event Lifecycle

An event instance progresses through these states; transitions are one-way (no regression) except documented retries.

| State | Meaning | Allowed operations | Next |
|-------|---------|--------------------|------|
| **Draft** | constructed in memory, pre-validation | populate envelope (§C) | Validated / (discard) |
| **Validated** | envelope + payload schema pass (§C/§G) | — | Persisted |
| **Persisted** | written to the outbox in the state-change txn (§I) | read by relay | Published / Expired |
| **Published** | emitted to broker/webhook; `published_at` set | deliver | Delivered |
| **Delivered** | received by ≥1 consumer | process | Consumed / (retry) |
| **Consumed** | a consumer applied it idempotently (§H) | ack | Acknowledged |
| **Acknowledged** | all required consumers acked | — | Archived |
| **Archived** | moved to cold storage per §AI | restore (read-only) | Expired |
| **Expired** | past retention; eligible for deletion | purge | Purged |
| **Purged** | removed (or anonymized) per §AI; tombstone kept for audit | — | (terminal) |

Invalid transitions (e.g. Persisted→Acknowledged without Published) **MUST** be rejected. A failed delivery loops Delivered→retry→(Delivered|DLQ) per §AJ. Legal hold (§AI) **MUST** block Expired→Purged.

## AI. Event Retention & Archival Policy

Retention is per **family** (the AF taxonomy + family below). Times are minimums; legal hold overrides all.

| Family | Hot (queryable) | Warm | Cold/archive | Immutable | Deletion |
|--------|-----------------|------|--------------|-----------|----------|
| Audit | 90 d | 1 y | **7 y** WORM | yes | only after legal retention; tombstone kept |
| Security | 90 d | 1 y | 2 y | yes | per policy |
| Compliance (consent/DSAR/RTBF) | 1 y | 3 y | **life of relationship + legal** | yes | RTBF anonymizes subject, keeps the compliance record |
| Capture (+ hardware §AR) | 30 d | 90 d | 1 y | no | TTL purge |
| Analysis / System | 30 d | 90 d | 1 y | no | TTL purge |
| AI/ML (§AP) | 90 d | 1 y | 2 y (lineage) | model/eval records yes | dataset/model lineage retained for reproducibility |
| Training/lineage | 1 y | 3 y | per model life | yes | bound to dataset/model version |
| Notification | 7 d | 30 d | — | no | purge |

**Archive strategy:** events move hot→warm→cold by age (Part 34.BM); cold = object storage, tenant-scoped, restorable. **Cold storage MUST** remain encrypted and access-audited. **Legal hold MUST** freeze any matching events from purge. **Immutable** families use append-only/WORM storage. **Deletion** for user-linked events follows RTBF (anonymize, keep the minimal compliance tombstone, Part 31/34.AJ).

## AJ. Dead-Letter Queue (DLQ) & Retry Policy

Operationalizes §N.

- **Retry strategy:** exponential backoff with full jitter — `delay = min(cap, base · 2^attempt) ± jitter`; `base = 1 s`, `cap = 5 min`.
- **Maximum retries:** Critical = 10, Normal = 6, Background/Bulk = 3 (priority per §AM); on exhaustion the event moves to the **DLQ** with the full failure context (Part 34.AM/X).
- **Poison events** (repeated deterministic failure / schema mismatch) **MUST** skip remaining retries and go straight to **quarantine** with the offending payload + validator error.
- **Replay:** **manual replay** (operator-initiated, default) and **automatic replay** (only for transient infra failures, rate-limited) **MUST** be idempotent (§H) and **MUST NOT** re-fire external side effects unless in side-effecting mode (§AA).
- **Permanent failure:** after exhausted retries + failed manual replay, the event is marked `permanently_failed` and an incident is opened.
- **Alert thresholds:** any DLQ entry for an Audit/Security/Compliance/Officiating event → **page immediately**; DLQ depth > 0 steady-state for other families → alert (§Z).
- **Escalation & ownership:** the **aggregate owner** (§AG) owns its DLQ; unresolved > SLA (§AL) escalates to on-call (Part 34.BA).

## AK. Failure Scenarios & Recovery Matrix

| Failure | Detection | Impact | Recovery | Escalation | Monitoring | Acceptance |
|---------|-----------|--------|----------|-----------|-----------|-----------|
| Broker unavailable | publish errors / health probe | events stuck in outbox (not lost) | relay retries; drain on recovery (§I) | SRE on-call | publish-lag, broker up | no event lost; lag recovers < SLA |
| Producer crash | missing heartbeat / run stuck | state change may be mid-flight | outbox txn is atomic → either both or neither (§I/§B.2) | service owner | run-state, outbox depth | no phantom/lost events |
| Consumer crash | consumer-lag spike | processing delayed | restart; resume from last offset; idempotent reprocess (§H) | consumer owner | consumer-lag | no double effect |
| Duplicate delivery | repeated `event_id`/key | potential double effect | consumer dedupe (§H) | — | redelivery-rate | exactly-once *effect* |
| Out-of-order delivery | `sequence` gap | wrong state if applied | reorder by `sequence` / buffer / quarantine (§AE/§W) | consumer owner | out-of-order count | per-aggregate order preserved |
| Network partition | timeouts | partial delivery | at-least-once + idempotency heal post-partition | SRE | error-rate | converges, no loss |
| Clock skew | `occurred_at` anomalies | bad windowing | rely on `sequence`, not wall-clock (§AE) | SRE | NTP/PTP offset | order unaffected by skew |
| Schema mismatch | validation fail (§C/§G) | unprocessable event | quarantine; producer fix + version bump (§P/§X) | producer owner | schema-fail count | no silent drop |
| Poison payload | repeated deterministic fail | blocks partition | quarantine immediately (§AJ) | producer owner | quarantine count | partition unblocked |
| Storage unavailable | outbox write error | command rejected (fail-closed) | command returns 5xx; client retries (§U) | SRE | DB health | no partial commit |
| Partial publish | published but `published_at` unset | possible re-publish | idempotent relay + consumer dedupe | SRE | outbox anomalies | no double effect |
| Replay failure | replay job error | stale read model | fix + re-run idempotent replay (§AA) | data owner | replay status | read model rebuilt |
| Version incompatibility | consumer cannot parse | consumer skips/quarantines | dual-emit during deprecation window (§P) | producer + consumer | version metrics | no break; window honored |

## AL. Event SLA & Operational Objectives

Per **class** (assigned in the registry, §AU; priority §AM). Extends the SLOs in §Z.

| Class | Max publish latency (p95) | Max delivery latency (p95) | Availability | Durability | Monitoring objective |
|-------|---------------------------|----------------------------|--------------|------------|----------------------|
| **Critical** (officiating, security, capture.certified) | < 1 s | < 5 s | 99.95% | 11 nines (outbox+broker) | page on any breach/DLQ |
| **Normal** (domain, analysis lifecycle) | < 5 s | < 30 s | 99.9% | durable | alert on sustained breach |
| **Background** (profile rebuild, dossier) | < 30 s | < 5 min | 99.5% | durable | dashboard |
| **Analytics** (efficacy/usage) | < 1 min | < 15 min | 99% | durable | dashboard |
| **Batch/ML** (training, dataset, benchmark) | minutes | minutes–hours | best-effort | durable | job tracker |
| **Archive** | n/a | n/a | n/a | cold-durable | integrity check |

Durability target for the outbox is **no event lost on a single-node failure** (§B.2). Breaches **MUST** be measured against §Z metrics.

## AM. Event Priority & Scheduling

| Priority | Used by | Scheduling rule |
|----------|---------|-----------------|
| **Critical** | officiating, security, `capture.certified`, `run.failed` | preempt; dedicated lane; never starved |
| **High** | domain facts needed by a saga step (§V) | ahead of Normal |
| **Normal** | most domain/system events | FIFO per partition |
| **Low** | non-urgent notifications | after Normal |
| **Background** | profile/dossier rebuild | idle capacity |
| **Bulk** | replay/backfill (§AA), batch ML | lowest; throttled |

- **Starvation prevention:** lower priorities **MUST** receive a guaranteed minimum share (aging) so they are not indefinitely deferred.
- **Ordering implications:** priority **MUST NOT** reorder events **within** an aggregate partition (per-aggregate order, §H.2) — priority lanes apply **across** aggregates only.
- **QoS:** Critical lanes **MUST** have reserved capacity; Bulk **MUST** be rate-limited to protect Critical/Normal (Part 34.AO).

## AN. Payload Size & Serialization Rules

- **Format:** UTF-8 **JSON** is the canonical wire format; field keys are `snake_case` (Part 38 §C). A binary format (e.g. Avro/Protobuf) **MAY** be used on the broker provided it is schema-registry-backed (§X) and lossless to the JSON contract.
- **Maximum payload size:** `data` **MUST** be ≤ **256 KB**. Anything larger **MUST** be passed **by reference** (object id + short-lived signed URL, §K/§AD) — events **MUST NOT** embed media, frames, or large arrays.
- **Compression:** transport-level compression **SHOULD** be applied for payloads > 8 KB; it **MUST** be transparent to consumers.
- **Binary attachments:** **forbidden** inline; referenced via the storage interface only (Part 34.AI).
- **Chunking:** a logical fact **MUST NOT** be split across events; high-volume streams (e.g. §AQ physics) **MUST** be aggregated/summarized, not chunked.
- **Encoding / validation:** every event **MUST** validate against its registered schema (§X) before Persisted (§AH); invalid → rejected (producer) or quarantined (consumer).
- **Schema evolution:** additive-only without a version bump (§P/§X).

## AO. Data Classification Within Events

Every payload field **MUST** carry a sensitivity class (declared in the schema, §G/§X). Handling is mandatory:

| Class | Examples | Logging | Encryption | Masking | Retention | Transport |
|-------|----------|---------|------------|---------|-----------|-----------|
| **PUBLIC** | counts, enums (`canonical_id`) | ok | standard TLS | none | family default | TLS |
| **INTERNAL** | ids, versions, scores | ok | TLS | none | family default | TLS |
| **CONFIDENTIAL** | dossiers, game plans | redact in app logs | TLS; at-rest encryption | partial | family default | TLS |
| **RESTRICTED** | officiating decisions | audit-only | at-rest + integrity hash | n/a | long (§AI) | TLS + signed |
| **PII** | names, emails (by reference only) | **never log** | field-encrypt if it must travel | full mask in logs | RTBF-bound | TLS |
| **MINOR** | any minor's data | **never log**; consent-gated | field-encrypt; by reference | full | strict RTBF | TLS + restricted |
| **BIOMETRIC** | pose/face-derived identifiers | **never log** | field-encrypt; by reference | full | strict | TLS + restricted |
| **SECURITY** | tokens, secrets | **never** in events at all | n/a (forbidden in payloads) | n/a | n/a | n/a |

PII/MINOR/BIOMETRIC values **MUST** travel **by reference** (ids + signed URL) by default (§AD/§AC); if a value must be carried, it **MUST** be field-encrypted with a rotating key (Part 34.AF). SECURITY-class material **MUST NOT** appear in any event (§O).

## AP. AI / Machine Learning Event Ontology

`taxonomy = AI/ML`; producers in AI Models / Analysis; consumers in MLOps, analysis, dashboard. Extends the operational subset in §F.

| Type | Trigger | Producer | Consumers | Key payload |
|------|---------|----------|-----------|-------------|
| `tt.ml.model.registered` | new model in registry | registry | MLOps | `model_version` |
| `tt.ml.model.approved` | passes release gate | MLOps | inference | `model_version` |
| `tt.ml.model.deprecated` | retired | MLOps | inference | `model_version,replaced_by` |
| `tt.ml.training.started`/`.completed` | training job | trainer | MLOps | `dataset_version,run_id` |
| `tt.ml.validation.passed` | held-out eval ok | eval | MLOps | `metrics` |
| `tt.benchmark.passed`/`tt.benchmark.failed` | golden-set gate (Part 29) | eval | release gate, on-call | `metric,target,actual` |
| `tt.ml.golden_set.failed` | golden gate breach | eval | on-call | `metric,delta` |
| `tt.ml.calibration.updated` | confidence recalibrated | calibration | reliability | `method,ece` |
| `tt.reliability.reduced` | confidence lowered | reliability | dashboard | `from,to,reason` |
| `tt.reliability.capped` | capture cap applied (Part 35.AK) | analysis | dashboard | `cap,certification` |
| `tt.analysis.run.abstained` | abstain (§F/§M) | analysis | dashboard | `reason,confidence` |
| `tt.ml.ground_truth.added` | label captured | annotation | datasets | `dataset_version` |
| `tt.dataset.approved`/`tt.dataset.rejected` | dataset review | data steward | MLOps | `dataset_version,reason` |
| `tt.dataset.version.published` | dataset versioned | datasets | MLOps | `version` |
| `tt.ml.retraining.requested` | drift/coverage trigger | MLOps | trainer | `reason` |
| `tt.reliability.model.drift_detected` | drift monitor (Part 29) | monitor | on-call, MLOps | `metric,delta` |
| `tt.inference.job.started`/`.completed` | inference unit | inference | analysis | `model_version,run_id` |
| `tt.model.deployed` | model live | MLOps | inference, audit | `model_version` |

Lifecycle: `registered → approved → deployed → (drift_detected → retraining_requested → training → validation/benchmark → registered) → deprecated`. ML events asserting quality **MUST** carry `provenance_hash` (model+dataset+code versions, Part 34.AK).

## AQ. Physics Engine Event Catalog

`taxonomy = AI/ML` (physics sub-domain); producers in CV/physics; **high-volume + internal** — these **MUST** be sampled/aggregated, not all published externally (§AN), and default to short retention (§AI).

| Type | Meaning | Key payload |
|------|---------|-------------|
| `tt.physics.trajectory.estimated` | a ball flight estimated | `rally_id,points,confidence` |
| `tt.physics.velocity.estimated` | speed estimated | `speed_kmh,confidence` |
| `tt.physics.acceleration.estimated` | acceleration estimated | `value,confidence` |
| `tt.physics.spin.estimated` | spin vector estimated | `spin_axis,rpm,confidence` |
| `tt.physics.magnus.applied` | Magnus model applied (Part 19) | `coefficients` |
| `tt.physics.bounce.classified` | bounce type identified | `bounce_type,confidence` |
| `tt.physics.collision.corrected` | racket/table collision corrected | `correction` |
| `tt.physics.validation.failed` | physics sanity check failed | `check,reason` |
| `tt.physics.simulation.completed` | forward simulation done | `result,confidence` |
| `tt.physics.confidence.reduced` | estimate down-weighted | `from,to,reason` |

Every physics estimate **MUST** carry `confidence` and a unit (Part 34.AC); below threshold it **MUST** `abstain` (§M, Part 10).

## AR. Capture Hardware Event Catalog

`taxonomy = Capture` (+ Infrastructure for failures); producers at the edge/capture service; consumers = operator dashboard + analysis. Each maps to a Part 35 KPI/fail-action.

| Type | Meaning | Maps to (Part 35) |
|------|---------|-------------------|
| `tt.capture.camera.connected` | camera online | AF (health) |
| `tt.capture.camera.lost` | camera offline | AF / AS |
| `tt.capture.frames.dropped` | dropped-frame threshold | AF (dropped_frames) |
| `tt.capture.calibration.drifted` | calibration residual breach | AH (drift) |
| `tt.capture.sync.lost` | inter-camera sync breach | AA (sync) |
| `tt.capture.light.low` | illuminance below floor | AC (lux) |
| `tt.capture.temperature.high` | sensor over-temp | AF (thermal) |
| `tt.capture.rolling_shutter.warned` | RS risk on non-GS camera | Z (RS) |
| `tt.capture.storage.full` | media nearly full | M / AF (storage) |
| `tt.capture.network.lost` | uplink down → offline buffer | AG (network) |
| `tt.capture.battery.low` | battery headroom low | AF (battery) |
| `tt.capture.lens.dirty` | lens occlusion/dirt | R / AD |
| `tt.capture.occlusion.detected` | play-volume occlusion | AD (occlusion) |
| `tt.capture.frame.corrupted` | corrupt frame detected | AF |
| `tt.capture.hardware.failed` | rig fault | T (officiating impact) |

A Critical-impact capture event (sync.lost, hardware.failed during officiating) **MUST** force the affected outputs to a lower tier or **abstain** (Part 35.AK / §M).

## AS. Event Dependency Graph

The canonical chain (a DAG; cf. the saga §V) — **mandatory** (→) vs **optional** (⇢):

```
video.uploaded → capture.certified → analysis.run.completed → (AI/ML + physics outputs)
   → profile.rebuilt ⇢ matchup.created → matchup.gameplan.ready → notification.requested
   → audit (parallel, on every step) → archive (terminal, §AH/§AI)
```

- **Mandatory dependencies:** `analysis.run.completed` **MUST** be preceded by `video.uploaded`; `matchup.gameplan.ready` **MUST** be preceded by `matchup.created` + a current `profile.rebuilt`.
- **Optional dependencies:** `capture.certified` is optional (a bare upload skips it, Part 35); profile rebuild **MAY** be triggered by batch rather than each run.
- **Forbidden cycles:** the graph **MUST** be acyclic; a consumer **MUST NOT** emit an event that (transitively) re-triggers its own trigger for the same `aggregate_id` (infinite loops). The registry (§AU) `related_events` + CI **MUST** detect cycles.
- **Audit** is a fan-out from every step (parallel), never a dependency for progress.

## AT. Aggregate State Machine Appendix

Expands §W. Each: states · transitions (triggering event) · terminal · invalid · failure handling.

**`video`** — states: `uploaded, analyzing, done, failed, archived`.
- `uploaded →(run.started) analyzing →(run.completed) done | →(run.failed) failed`; `done|failed →(retention) archived`.
- Terminal: `archived`. Invalid: `uploaded→done` (no run). Failure: ingest error keeps `uploaded` + emits `video.ingest_failed`.

**`analysis_run`** — states: `queued, processing, done, failed`.
- `queued →(run.started) processing →(run.completed) done | →(run.failed) failed`.
- Terminal: `done`, `failed` (immutable; re-analysis = new run). Invalid: any transition out of a terminal state. Failure: worker crash → run stays `processing` until a reaper times it out → `failed`.

**`capture_session`** — states: `started, ended, certified?`.
- `started →(session.ended) ended`; `capture.certified` annotates the associated run (not a session state). Terminal: `ended`. Failure: `capture.failed`/hardware events (§AR) may end a session early.

**`player_profile`** — states: `building, current, superseded`.
- `building →(profile.rebuilt) current`; a new rebuild makes the prior `superseded` (versioned, Part 34.BE). Terminal: `superseded`. Invalid: editing a `current` profile by hand. Failure: rebuild error leaves the prior `current` intact.

**`match`** — states: `provisional, confirmed, archived`.
- created `provisional` with a run; `→(officiating/confirm) confirmed`; `→ archived`. Terminal: `archived`. Officiating events append immutably (§L); an override produces a new immutable record, never a mutation.

**`game_plan`** — states: `draft, final, archived`.
- `draft →(gameplan.ready) final →(retention) archived`; `gameplan.outcome.recorded` is a post-terminal annotation (Analytics). Terminal: `archived`. Invalid: `archived→final`.

Every consumer applying a transition **MUST** verify the current state (optimistic, Part 34.AQ) and reject/quarantine an out-of-state event (§AK).

## AU. Canonical Event Registry

Every event has a **permanent `EV-####` identifier** (immutable for the platform's lifetime). The registry is the **authoritative source for event identifiers**; `events_catalog.json` (§Q) is its machine-readable projection. Columns: ID · type · taxonomy (§AF) · version · owner (§AG) · producer → consumers · entity (Part 37) · ontology (Part 38) · status. Payload schema refs point to §G/§AP/§AQ/§AR; `related_events` are given by the dependency graph (§AS).

| ID | Type | Taxonomy | V | Owner | Producer → Consumers | Entity (37) | Onto (38) | Status |
|----|------|----------|---|-------|----------------------|-------------|-----------|--------|
| EV-0001 | tt.org.created | Domain | 1 | Identity | Identity → provisioning | organization | `organization` | active |
| EV-0002 | tt.identity.user.registered | Domain | 1 | Identity | Identity → notify,audit | user | `user` | active |
| EV-0003 | tt.identity.user.disabled | Audit | 1 | Identity | Identity → audit,sessions | user | `user` | active |
| EV-0004 | tt.admin.role.changed | Audit | 1 | Compliance | Admin → audit | user | `user` | active |
| EV-0005 | tt.consent.recorded | Compliance | 1 | Compliance | Compliance → audit,analysis-gate | player | `impairment` | active |
| EV-0006 | tt.consent.revoked | Compliance | 1 | Compliance | Compliance → retention,audit | player | `impairment` | active |
| EV-0007 | tt.player.created | Domain | 1 | Players | Players → profile | player | `player` | active |
| EV-0008 | tt.player.archived | Domain | 1 | Players | Players → retention | player | `player` | active |
| EV-0009 | tt.video.uploaded | Domain | 1 | Video | Video → analysis | video | `video` | active |
| EV-0010 | tt.video.ingest_failed | System | 1 | Video | Video → notify | video | `video` | active |
| EV-0011 | tt.capture.session.started | Capture | 1 | Capture | Capture → monitoring | capture_session | `capture_tier` | active |
| EV-0012 | tt.capture.session.ended | Capture | 1 | Capture | Capture → monitoring | capture_session | `capture_tier` | active |
| EV-0013 | tt.capture.certified | Capture | 1 | Capture | Capture → analysis,dashboard | analysis_run | `capture_certification` | active |
| EV-0014 | tt.capture.failed | Capture | 1 | Capture | Capture → operator,notify | capture_session | `capture_failure` | active |
| EV-0015 | tt.analysis.run.queued | System | 1 | Analysis | Analysis → monitoring | analysis_run | `analysis_run` | active |
| EV-0016 | tt.analysis.run.started | System | 1 | Analysis | Analysis → monitoring | analysis_run | `analysis_run` | active |
| EV-0017 | tt.analysis.run.completed | System | 1 | Analysis | Analysis → profile,notify | analysis_run | `reliability` | active |
| EV-0018 | tt.analysis.run.failed | System | 1 | Analysis | Analysis → notify,on-call | analysis_run | `analysis_run` | active |
| EV-0019 | tt.analysis.run.abstained | AI/ML | 1 | Analysis | Analysis → dashboard | analysis_run | `abstain` | active |
| EV-0020 | tt.profile.rebuilt | Domain | 1 | Intelligence | Intelligence → matchup,notify | player_profile | `player_profile` | active |
| EV-0021 | tt.opponent.dossier.created | Domain | 1 | Intelligence | Intelligence → matchup | opponent_dossier | `opponent_dossier` | active |
| EV-0022 | tt.matchup.created | Domain | 1 | Intelligence | Intelligence → gameplan | matchup | `matchup` | active |
| EV-0023 | tt.matchup.gameplan.ready | Domain | 1 | Intelligence | Intelligence → notify | game_plan | `game_plan` | active |
| EV-0024 | tt.gameplan.outcome.recorded | Analytics | 1 | Analytics | Analytics → efficacy | game_plan | `game_plan` | active |
| EV-0025 | tt.officiating.call.logged | Audit | 1 | Compliance | Officiating → evidence,audit | match | `violation` | active |
| EV-0026 | tt.officiating.call.overridden | Audit | 1 | Compliance | Umpire → evidence,audit | match | `let` | active |
| EV-0027 | tt.security.login.failed | Security | 1 | Identity | Identity → rate-limit,audit | user | `user` | active |
| EV-0028 | tt.security.token.revoked | Security | 1 | Identity | Identity → sessions,audit | user | `user` | active |
| EV-0029 | tt.security.access.denied | Security | 1 | Identity | Identity → audit | user | `user` | active |
| EV-0030 | tt.data.export.requested | Compliance | 1 | Compliance | Compliance → DSAR worker | player | `player` | active |
| EV-0031 | tt.data.export.completed | Compliance | 1 | Compliance | Compliance → notify | player | `player` | active |
| EV-0032 | tt.data.deletion.requested | Compliance | 1 | Compliance | Compliance → retention | player | `player` | active |
| EV-0033 | tt.data.deletion.completed | Compliance | 1 | Compliance | Compliance → audit | player | `player` | active |
| EV-0034 | tt.notification.requested | Notification | 1 | Notification | any → notification svc | notification | — | active |
| EV-0035 | tt.webhook.delivery.failed | Infrastructure | 1 | Platform | relay → on-call | webhook_endpoint | — | active |
| EV-0036 | tt.ml.model.registered | AI/ML | 1 | AI Models | registry → MLOps | model | `model` | active |
| EV-0037 | tt.ml.model.approved | AI/ML | 1 | AI Models | MLOps → inference | model | `model` | active |
| EV-0038 | tt.ml.model.deprecated | AI/ML | 1 | AI Models | MLOps → inference | model | `model` | active |
| EV-0039 | tt.ml.training.started | AI/ML | 1 | AI Models | trainer → MLOps | model | `training` | active |
| EV-0040 | tt.ml.training.completed | AI/ML | 1 | AI Models | trainer → MLOps | model | `training` | active |
| EV-0041 | tt.ml.validation.passed | AI/ML | 1 | AI Models | eval → MLOps | model | `validation` | active |
| EV-0042 | tt.benchmark.passed | AI/ML | 1 | AI Models | eval → release gate | benchmark | `benchmark` | active |
| EV-0043 | tt.benchmark.failed | AI/ML | 1 | AI Models | eval → on-call | benchmark | `benchmark` | active |
| EV-0044 | tt.ml.golden_set.failed | AI/ML | 1 | AI Models | eval → on-call | benchmark | `benchmark` | active |
| EV-0045 | tt.ml.calibration.updated | AI/ML | 1 | AI Models | calibration → reliability | model | `calibration` | active |
| EV-0046 | tt.reliability.reduced | AI/ML | 1 | Analysis | reliability → dashboard | analysis_run | `reliability` | active |
| EV-0047 | tt.reliability.capped | AI/ML | 1 | Analysis | analysis → dashboard | analysis_run | `reliability_envelope` | active |
| EV-0048 | tt.ml.ground_truth.added | AI/ML | 1 | Annotation | annotation → datasets | dataset | `ground_truth` | active |
| EV-0049 | tt.dataset.approved | AI/ML | 1 | Datasets | steward → MLOps | dataset | `dataset` | active |
| EV-0050 | tt.dataset.rejected | AI/ML | 1 | Datasets | steward → MLOps | dataset | `dataset` | active |
| EV-0051 | tt.dataset.version.published | AI/ML | 1 | Datasets | datasets → MLOps | dataset | `dataset` | active |
| EV-0052 | tt.ml.retraining.requested | AI/ML | 1 | AI Models | MLOps → trainer | model | `training` | active |
| EV-0053 | tt.reliability.model.drift_detected | AI/ML | 1 | AI Models | monitor → on-call,MLOps | model | `model` | active |
| EV-0054 | tt.inference.job.started | System | 1 | AI Models | inference → analysis | inference_job | `inference_job` | active |
| EV-0055 | tt.inference.job.completed | System | 1 | AI Models | inference → analysis | inference_job | `inference_job` | active |
| EV-0056 | tt.model.deployed | Domain | 1 | AI Models | MLOps → inference,audit | model | `model` | active |
| EV-0057 | tt.physics.trajectory.estimated | AI/ML | 1 | Analysis | physics → analysis | shot | `rpm` | active |
| EV-0058 | tt.physics.velocity.estimated | AI/ML | 1 | Analysis | physics → analysis | shot | `statistic` | active |
| EV-0059 | tt.physics.acceleration.estimated | AI/ML | 1 | Analysis | physics → analysis | shot | `statistic` | active |
| EV-0060 | tt.physics.spin.estimated | AI/ML | 1 | Analysis | physics → analysis | shot | `spin_axis` | active |
| EV-0061 | tt.physics.magnus.applied | AI/ML | 1 | Analysis | physics → analysis | shot | `spin_strength` | active |
| EV-0062 | tt.physics.bounce.classified | AI/ML | 1 | Analysis | physics → analysis | event | `bounce` | active |
| EV-0063 | tt.physics.collision.corrected | AI/ML | 1 | Analysis | physics → analysis | shot | `hit` | active |
| EV-0064 | tt.physics.validation.failed | AI/ML | 1 | Analysis | physics → on-call | analysis_run | `reliability` | active |
| EV-0065 | tt.physics.simulation.completed | AI/ML | 1 | Analysis | physics → analysis | analysis_run | `statistic` | active |
| EV-0066 | tt.physics.confidence.reduced | AI/ML | 1 | Analysis | physics → dashboard | shot | `confidence` | active |
| EV-0067 | tt.capture.camera.connected | Capture | 1 | Capture | edge → dashboard | camera | `camera` | active |
| EV-0068 | tt.capture.camera.lost | Capture | 1 | Capture | edge → operator,analysis | camera | `camera` | active |
| EV-0069 | tt.capture.frames.dropped | Capture | 1 | Capture | edge → dashboard | camera | `capture_failure` | active |
| EV-0070 | tt.capture.calibration.drifted | Capture | 1 | Capture | edge → analysis | calibration | `calibration` | active |
| EV-0071 | tt.capture.sync.lost | Capture | 1 | Capture | edge → analysis | capture_session | `capture_tier` | active |
| EV-0072 | tt.capture.light.low | Capture | 1 | Capture | edge → operator | capture_session | `lighting` | active |
| EV-0073 | tt.capture.temperature.high | Capture | 1 | Capture | edge → operator | camera | `sensor` | active |
| EV-0074 | tt.capture.rolling_shutter.warned | Capture | 1 | Capture | edge → analysis | camera | `camera` | active |
| EV-0075 | tt.capture.storage.full | Infrastructure | 1 | Capture | edge → operator | capture_session | `environment` | active |
| EV-0076 | tt.capture.network.lost | Infrastructure | 1 | Capture | edge → operator | capture_session | `environment` | active |
| EV-0077 | tt.capture.battery.low | Capture | 1 | Capture | edge → operator | camera | `sensor` | active |
| EV-0078 | tt.capture.lens.dirty | Capture | 1 | Capture | edge → operator | camera | `camera` | active |
| EV-0079 | tt.capture.occlusion.detected | Capture | 1 | Capture | edge → analysis | capture_session | `occlusion` | active |
| EV-0080 | tt.capture.frame.corrupted | Capture | 1 | Capture | edge → analysis | video | `capture_failure` | active |
| EV-0081 | tt.capture.hardware.failed | Infrastructure | 1 | Capture | edge → on-call | camera | `capture_failure` | active |

Rules: a new event **MUST** be appended with the next `EV-####` (never reuse a retired id); deprecation sets `status: deprecated` + `replaced_by` (§P); the registry, `events_catalog.json`, and `events.py` **MUST** agree (CI drift gate, §R / Part 34.AP).

---

## AV. Event API Documentation (AsyncAPI)

- The event surface **MUST** be documented as an **AsyncAPI** specification (`api/asyncapi.yaml`) — the event analog of the OpenAPI HTTP contract (Part 37 §Y). It **MUST** be **generated from the canonical registry (§AU) + catalog (§Q)**, never hand-drifted.
- It **MUST** describe every **channel** (topic), **message** (event `type` + headers = the envelope §C), and **payload schema** (§G/§AP/§AQ/§AR), plus operations (who publishes/subscribes, §AG) and `event_version`.
- It is the **discoverability source** for integrators; consumer/producer stubs **SHOULD** be generated from it. CI **MUST** fail if it drifts from the registry (drift gate, §R / Part 34.AP).
- Status: ⬜ `SPECIFIED` (build target alongside `events.py`).

## AW. CloudEvents Conformance & Interoperability

- The envelope (§C) **MUST** be expressible as a **CNCF CloudEvents 1.0** message for external interoperability. Canonical mapping:

| CloudEvents 1.0 | TT-OS envelope (§C) |
|-----------------|---------------------|
| `id` | `event_id` |
| `type` | `type` |
| `source` | the producing service URI + `aggregate_type` |
| `subject` | `aggregate_id` |
| `time` | `occurred_at` |
| `specversion` | `"1.0"` |
| `dataschema` | `data_schema` |
| `data` | `data` |
| extensions `orgid, sequence, correlationid, causationid, idempotencykey, provenancehash` | the remaining envelope fields |

- External/webhook deliveries (§K) **SHOULD** use the CloudEvents **structured JSON** binding; internal transport **MAY** use the native envelope. Conformance keeps the platform interoperable with standard tooling **without** changing the contract.

## AX. Multi-Region, Replication & Data Residency

- Each aggregate has a **home region**; per-aggregate ordering (§H) is guaranteed **within** the home region. The single-writer-per-aggregate rule (§AG) means cross-region write conflicts cannot arise for owned events.
- Events **MAY** be **replicated read-only** to other regions for locality/DR; replicas **MUST** preserve per-aggregate `sequence` and **MUST NOT** accept writes.
- **Data residency (Part 31):** events of a residency-restricted tenant (e.g. EU) **MUST NOT** be replicated outside the permitted geography; residency is a routing constraint on topics/partitions (§Y).
- **Active-active is NOT permitted** for the same aggregate; the model is **active-passive** failover (§AY).

## AY. Disaster Recovery (RPO / RTO)

- The **outbox is the durable source of truth** for events (§I) and **MUST** be backed up with the relational store (Part 34.AZ), so events survive broker loss.
- **Targets (normative):** Critical events **RPO = 0** (outbox written in the state-change txn → no loss) with **RTO < 15 min** (broker/relay failover); Normal **RTO < 1 h**; analytics/batch best-effort.
- **Failover:** a standby broker/relay in the passive region (§AX) takes over; the relay resumes from unpublished outbox rows idempotently (§I).
- DR restores **MUST** be **tested**, not assumed (Part 34.AZ); a drill **MUST** verify zero event loss and order preservation, and **MUST** include legal-hold/immutable families (§AI).

## AZ. Crypto-Shredding & Right-to-Erasure in Immutable Logs

- Immutable/WORM families (Audit, Officiating, Compliance — §AI/§L) cannot be edited or deleted, which tensions with the right-to-erasure (Part 31). Resolution: **crypto-shredding**.
- Any PII/MINOR/BIOMETRIC value that must persist in an immutable event **MUST** be **encrypted with a per-subject data key**; the event stores **ciphertext only** (§AO/§AC).
- **RTBF** (`tt.data.deletion.*`, §F) **MUST** delete the subject's data key, rendering the ciphertext permanently unrecoverable — satisfying erasure **without mutating** the immutable log; the event structure, non-PII facts, and audit tombstone remain.
- Key custody + rotation follow Part 34.AF; a shredded key **MUST NOT** be recoverable from backups.

## BA. Event Versioning: Upcasting & Coexistence

- Beyond §P: when a `type` reaches a new `event_version`, a registered **upcaster** **MUST** transform a persisted older payload into the current shape **at read/replay time**, so consumers handle a single logical schema.
- During a deprecation window producers **MAY dual-emit** old + new versions; consumers **MUST** declare a minimum supported version and **MUST** ignore higher minor revisions gracefully (§P.5).
- Upcasters are pure, versioned, tested functions (§AB) registered with the catalog (§AU); an old `event_version` **MUST NOT** be retired until no stored/queued event of that version remains (or all are upcast).

## BB. Migration & Rollout from the Inline MVP (Strangler)

- Today the pipeline runs **inline** (Part 37 §B.4); the event layer (§Q) is ⬜. Adoption **MUST** be incremental, reversible, and **MUST NOT** change this contract:
  1. **Emit-only (shadow):** add the outbox (§I) + `emit()` (§Q); produce events alongside existing inline behavior — **no consumer acts** yet.
  2. **Consume behind flags:** add idempotent consumers (profile rebuild, notifications) behind feature flags (Part 34.AU); compare against inline results.
  3. **Flip reads:** move read models/projections to event-driven (§U) once validated.
  4. **Decouple:** retire the inline coupling; the broker becomes the integration path.
- Each step is independently shippable and **MUST** be reversible by a flag.

## BC. Cost & Volume Governance

- High-volume families (physics §AQ, hardware telemetry §AR) **MUST** be **sampled/aggregated at the edge**, not published verbatim (§AN), and default to short retention (§AI).
- **Per-tenant volume quotas** **MUST** bound emission so one tenant cannot inflate cost or starve others (§Y / Part 34.AO); a breach throttles Bulk/Background first (§AM).
- Retention tiering (§AI) **MUST** move cold events to cheap storage; broker/storage/egress cost **SHOULD** be monitored with budget alerts (Part 34.AS).

## BD. Consumer Offset & Checkpoint Semantics

- With at-least-once delivery (§H), a consumer **MUST** commit its offset/checkpoint **only after** the event is **successfully and idempotently processed** (process-then-commit) — never before — so a crash redelivers rather than skips.
- Checkpoints are **per (consumer-group, partition)** (§Y); on rebalance, a partition's new owner **MUST** resume from the last committed offset.
- A processing failure **MUST NOT** advance the offset; the event is retried then dead-lettered (§AJ). Offsets/checkpoints **MUST** be durable and survive consumer restarts.

This document is the authoritative event contract for TT-OS; the data model (Part 37), ontology (Part 38), and this event contract together form the platform's build foundation.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
