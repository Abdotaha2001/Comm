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

This document is the authoritative event contract for TT-OS; the data model (Part 37), ontology (Part 38), and this event contract together form the platform's build foundation.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
