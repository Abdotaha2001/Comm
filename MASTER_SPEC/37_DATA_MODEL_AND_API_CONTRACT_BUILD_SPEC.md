# PART 37 — DATA MODEL & API CONTRACT (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative, implementation-ready build specification** for the backend. It consolidates the data model and API contract of Part 27 and the architecture of Parts 01–36 into an executable contract. **If implementation conflicts with this document, this document wins** — except where this document is explicitly marked `SPECIFIED` (not yet built), in which case it is the build target.
>
> **RFC-2119 keywords** (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are used normatively.
>
> **Status legend:** ✅ `IMPLEMENTED` (present in `backend/`) · 🟡 `PARTIAL` (present, incomplete vs this spec) · ⬜ `SPECIFIED` (build target, not yet present). Status reflects the repository at the schema revision `0004`.

---

## A. Scope & Objectives

### A.1 Purpose
This document defines the canonical domain model, persistence schema, API contract, and event contract for TT-OS. It is the **Single Source of Truth (SSoT)** for backend structure. Any generated artifact (`models.py`, `schemas.py`, `openapi.yaml`, migrations) MUST conform to it.

### A.2 Goals
- G1. The backend MUST be reconstructible from this document plus the machine-readable artifacts it governs (§Y).
- G2. Every persisted value that is *measured* MUST carry a reliability envelope (§D, Part 10).
- G3. Every record MUST be **org-scoped** and access-controlled deny-by-default (§N, Part 31).
- G4. Documentation and implementation MUST NOT diverge; CI MUST fail on divergence (§Z).
- G5. The contract MUST be backward-compatible and versioned (§V).

### A.3 Non-goals
- N1. This document MUST NOT define UI/UX (Part 32 owns that).
- N2. This document MUST NOT define model architectures or training (Parts 12/18/26 own those).
- N3. This document MUST NOT define infrastructure/deployment topology (Part 13 owns that); it defines only the contract the infrastructure serves.

### A.4 Relationship to Parts 01–36
This document is the persistence/contract projection of the capabilities specified in Parts 01–36. The traceability matrix (§W) maps each Part to its entities, endpoints, events, and modules. Part 27 remains the human-readable data-model narrative; **Part 37 is authoritative for build**.

### A.5 Implementation ownership
- The backend team owns `backend/`.
- Schema changes MUST go through Alembic (§H, §V). `create_all` MUST NOT be used outside tests.
- Changes to this document MUST be reviewed by a CODEOWNER for `MASTER_SPEC/` and accompanied by the corresponding artifact changes in the same PR (§Z).

---

## B. Architectural Principles

- **B.1 API-first.** The OpenAPI contract (§Y) is authoritative for the HTTP surface; clients MUST be generated from it, not hand-written.
- **B.2 Domain-driven design.** Code MUST be organised by bounded context (§C); cross-context access MUST go through defined contracts, not shared tables.
- **B.3 Reliability-first.** Every measured output MUST carry `{value, confidence, ci, tier, source, status}` and MUST be able to `abstain` (Part 10 / 34.AL).
- **B.4 Event-driven.** State transitions that other contexts care about MUST emit a domain event (§R). The MVP MAY process inline but MUST emit the event contract so a bus drops in without contract change (Part 13).
- **B.5 Provenance-first.** Every analysis/officiating artifact MUST persist code + model + schema versions, inputs, and a hash (§I, Part 34.AK).
- **B.6 Immutable evidence.** Officiating evidence and audit logs MUST be append-only and tamper-evident (§F, Part 31).
- **B.7 Backward compatibility.** Breaking changes MUST follow expand→migrate→contract (§V, Part 34.AG/N).
- **B.8 Extensibility.** Flexible/nested data MUST use typed `JSON` columns with a documented shape; new KPIs/levels/enums MUST be addable without a breaking migration (the capture schema is the reference pattern, Part 35).
- **B.9 Machine-readable specifications.** Thresholds, KPIs, glossary, and the API live as machine-readable SSoT files, not prose (§Y).
- **B.10 Single Source of Truth.** Exactly one authoritative definition per concern; duplicates MUST be rejected in review (§Z).

---

## C. Bounded Contexts

Each context owns its tables and exposes a contract. A context MUST NOT write another context's tables directly.

| Context | Owns (core entities) | Status | Origin |
|---------|----------------------|--------|--------|
| **Identity** | `users`, sessions, API keys, refresh tokens | 🟡 | 31 |
| **Organizations** | `organizations`, settings, feature flags | 🟡 | 13/31 |
| **Academies** | academies, teams, rosters | ⬜ | 15/32 |
| **Players** | `players`, equipment, passports | 🟡 | 04/17/20 |
| **Coaches** | coach profiles, assignments | ⬜ | 08/32 |
| **Officials** | official profiles, assignments | ⬜ | 09 |
| **Competitions** | competitions, `matches`, `games`, brackets | 🟡 | 09/15 |
| **Capture** | capture sessions, cameras, calibrations, capture certifications | 🟡 | 02/35 |
| **Video** | `videos`, media storage refs | ✅ | 02/12 |
| **Analysis** | `analysis_runs`, `rallies`, `shots`, `events`, ball/pose tracks, spin events | 🟡 | 01–06 |
| **AI Models** | models, model cards, inference jobs | ⬜ | 12/18/29 |
| **Datasets** | datasets, splits, datasheets | ⬜ | 12/30 |
| **Annotation** | annotations, label tasks, IAA | ⬜ | 30 |
| **Reports** | reports, exports | ⬜ | 16/32 |
| **Evidence** | evidence packages | ⬜ | 09/35 |
| **Reliability** | reliability envelopes (embedded), abstentions | 🟡 | 10 |
| **Officiating** | calls, overrides, decision log | ⬜ | 09 |
| **Intelligence** | `player_profiles`, `opponent_dossiers`, `matchups`, `game_plans` | ✅ | 07/08/17/21 |
| **Training** | training sessions, drills, plans | ⬜ | 08/22/23 |
| **Administration** | roles, permissions, consents | 🟡 | 31 |
| **Monitoring** | audit logs, metrics, drift records | ⬜ | 13/29/31 |
| **Notification** | notifications, channels, preferences | ⬜ | 32 |

---

## D. Canonical Domain Model

Each entity MUST be specified with the attributes below. The full attribute set is given here for the **IMPLEMENTED core**; every other entity in §E MUST follow the same template and the shared rules in §F/§I/§J.

**Specification template (normative):** `Purpose · Owner(context) · Lifecycle · Relationships · Responsibilities · Constraints · Primary identifier · Immutable fields · Mutable fields · Deletion policy · Versioning policy`.

### D.1 Organization ✅ (Part 13/31)
- **Purpose:** tenant boundary; root of all org-scoped data. **Owner:** Organizations.
- **Lifecycle:** `active → suspended → archived`. **PK:** `id` (UUID).
- **Relationships:** 1→N users, players, videos, dossiers, matchups.
- **Constraints:** `name` non-empty; tenant of every child row MUST equal the authenticated org.
- **Immutable:** `id`, `created_at`. **Mutable:** `name`, settings.
- **Deletion:** soft-delete (`archived`); hard-delete only via RTBF cascade (§F, Part 31).
- **Versioning:** row-level `version` (optimistic lock, §V).

### D.2 User ✅ (Part 31)
- **Purpose:** an authenticating principal in an org. **Owner:** Identity.
- **Lifecycle:** `invited → active → disabled`. **PK:** `id`.
- **Relationships:** N→1 organization; N↔M roles (via role assignment; MVP stores a single `role`).
- **Constraints:** `email` UNIQUE **per org**; `password_hash` MUST be PBKDF2+salt (Part 31); plaintext passwords MUST NOT be stored or logged.
- **Immutable:** `id`, `org_id`, `created_at`. **Mutable:** `email`, `password_hash`, `role`, `status`.
- **Deletion:** soft-delete; PII erasure on RTBF.
- **Versioning:** `version`.

### D.3 Player ✅ (Part 04/17/24)
- **Purpose:** an athlete (pro/junior/para) tracked over time. **Owner:** Players.
- **Lifecycle:** `active → archived`. **PK:** `id`.
- **Relationships:** N→1 org; 1→N videos, profiles; subject/opponent of dossiers/matchups.
- **Constraints:** `handedness`, `grip`, `player_type`, `sex`, `para_class` MUST use Part 28 `canonical_id` enums. Minors MUST have a guardian-consent record before analysis (§F, Part 31/34.AJ).
- **Immutable:** `id`, `org_id`, `created_at`. **Mutable:** profile attributes.
- **Deletion:** soft-delete; RTBF cascade to videos/derived artifacts.
- **Versioning:** `version`.

### D.4 Video ✅ (Part 02/12)
- **Purpose:** an ingested media asset for a player. **Owner:** Video.
- **Lifecycle:** `uploaded → analyzing → done | failed → archived`. **PK:** `id`.
- **Relationships:** N→1 org, N→1 player; 1→N analysis_runs.
- **Constraints:** `source ∈ {upload, url}`; `storage_key` MUST reference storage via the storage interface, never a client path (Part 34.AI). Uploads MUST be content-sniffed + size/codec-bounded before processing.
- **Immutable:** `id`, `org_id`, `player_id`, `source`, `storage_key`, `created_at`. **Mutable:** `status`, probe metadata (`fps/width/height/duration_sec`).
- **Deletion:** soft-delete → cold archive → RTBF hard-delete (Part 34.BM).
- **Versioning:** `version`.

### D.5 AnalysisRun ✅ (Part 01–06/10/35)
- **Purpose:** one execution of the analysis pipeline over a video. **Owner:** Analysis.
- **Lifecycle:** `queued → processing → done | failed`. **PK:** `id`.
- **Relationships:** N→1 video; 1→0..1 match; embeds capture certification + reliability.
- **Responsibilities:** persist `model_versions`, `input_quality`, `reliability_index`, and (when a capture report is supplied) `capture_certification` + `capture_acceptance` (Part 35). The capture grade MUST cap `reliability_index` by a min, never an average (Part 10).
- **Immutable after `done`:** all result fields (a re-analysis MUST create a new run, never mutate). **Mutable while running:** `status`, `error`.
- **Deletion:** soft-delete with the video.
- **Versioning:** the run *is* the version (immutable result); `schema_version` of the capture framework MUST be recorded.

### D.6 Match / Rally / Shot / Event ✅ (Part 01/03/05/09)
- **Purpose:** the structured analysis output — an append-only hierarchy. **Owner:** Analysis.
- **Lifecycle:** created with a run; immutable thereafter (corrections = new events, Part 34.BK). **PK:** `id` each.
- **Relationships:** match 1→N rallies 1→N shots; rally/shot 1→N events; match N→1 analysis_run.
- **Constraints:** measured fields (`speed`, `spin`, placement) MUST carry confidence; below threshold MUST `abstain`. Timestamps MUST be frame-index + fps (Part 34.AC).
- **Immutable:** all. **Deletion:** with the match/run.

### D.7 PlayerProfile / OpponentDossier / Matchup / GamePlan ✅ (Part 07/08/17/21)
- **Purpose:** derived intelligence artifacts. **Owner:** Intelligence.
- **Lifecycle:** versioned snapshots; recomputed by deterministic jobs, never hand-edited (Part 34.BE). **PK:** `id` each.
- **Relationships:** profile N→1 player (`version` increments); dossier N→1 org + subject/opponent player; matchup N→1 org + my-player + dossier; game_plan N→1 matchup.
- **Constraints:** each MUST carry `confidence` and `source_video_ids`/inputs; thin data MUST render "preliminary".
- **Immutable:** `version`, inputs, `created_at`. **Mutable:** `status` (game_plan: `draft → final`).
- **Deletion:** soft-delete; rebuilt on input change.
- **Versioning:** explicit integer `version` (profiles); new row per rebuild.

### D.8 CaptureCertification + ReliabilityEnvelope ✅ (embedded) / 🟡 (standalone) (Part 10/35)
- **Purpose:** the capture acceptance result + the reliability descriptor. **Owner:** Capture/Reliability.
- **Current form:** embedded in `analysis_runs.capture_acceptance` (JSON) + `capture_certification` (string). The reliability envelope is embedded per measured value.
- **Specified form (⬜):** a first-class `capture_sessions` table with cameras/calibrations, referenced by videos and runs.
- **Constraints:** governed by `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json`; certification MUST use min-gate logic (no averaging); a `fail` capture MUST force `abstain`.
- **Immutable:** the certification snapshot + `provenance_hash`.

The remaining entities (§E, status ⬜/🟡) are SPECIFIED to the same template; their build MUST instantiate the shared fields (§I), lifecycle (§F), and naming (§J).

---

## E. Complete Entity Catalog

Every entity the platform requires. `Tbl` = canonical table name. Implementation MUST NOT introduce a table not listed here without adding it to this catalog in the same PR (§Z).

| # | Entity | Tbl | Context | PK | Key relationships | Delete | Status | Parts |
|---|--------|-----|---------|----|--------------------|--------|--------|-------|
| 1 | Organization | `organizations` | Organizations | uuid | →users,players | soft/RTBF | ✅ | 13/31 |
| 2 | User | `users` | Identity | uuid | →org; ↔roles | soft/RTBF | ✅ | 31 |
| 3 | Role | `roles` | Administration | uuid | ↔permissions | soft | ⬜ | 31 |
| 4 | Permission | `permissions` | Administration | uuid | ↔roles | soft | ⬜ | 31 |
| 5 | RoleAssignment | `role_assignments` | Administration | uuid | user×role×org | soft | ⬜ | 31 |
| 6 | Consent | `consents` | Administration | uuid | →player/user | retain→RTBF | ⬜ | 31 |
| 7 | Player | `players` | Players | uuid | →org;→videos | soft/RTBF | ✅ | 04/17/24 |
| 8 | Coach | `coaches` | Coaches | uuid | →org;↔players | soft | ⬜ | 08 |
| 9 | Official | `officials` | Officials | uuid | →org;→matches | soft | ⬜ | 09 |
| 10 | Academy | `academies` | Academies | uuid | →org;→teams | soft | ⬜ | 15 |
| 11 | Team | `teams` | Academies | uuid | →academy;↔players | soft | ⬜ | 15 |
| 12 | Venue | `venues` | Capture | uuid | →org;→tables | soft | ⬜ | 35 |
| 13 | Table | `tables` | Capture | uuid | →venue | soft | ⬜ | 35 |
| 14 | CaptureSession | `capture_sessions` | Capture | uuid | →venue,table;→cameras,videos | soft/archive | ⬜ | 35 |
| 15 | Camera | `cameras` | Capture | uuid | →session;→calibrations | soft | ⬜ | 35 |
| 16 | Calibration | `calibrations` | Capture | uuid | →camera (versioned) | retain | ⬜ | 02/35 |
| 17 | CaptureCertification | `capture_certifications` | Capture | uuid | →session/run | immutable | 🟡 | 35 |
| 18 | Video | `videos` | Video | uuid | →player;→runs | soft/RTBF | ✅ | 02/12 |
| 19 | AnalysisRun | `analysis_runs` | Analysis | uuid | →video;→match | soft | ✅ | 01–06 |
| 20 | Match | `matches` | Competitions | uuid | →run;→rallies | soft | ✅ | 09 |
| 21 | Game | `games` | Competitions | uuid | →match;→points | soft | ⬜ | 09 |
| 22 | Rally | `rallies` | Analysis | uuid | →match;→shots,events | soft | ✅ | 01 |
| 23 | Point | `points` | Competitions | uuid | →game;→rally | soft | ⬜ | 09 |
| 24 | Shot/Stroke | `shots` | Analysis | uuid | →rally;→events | soft | ✅ | 05 |
| 25 | Event | `events` | Analysis | uuid | →rally/shot | soft | ✅ | 01/09 |
| 26 | SpinEvent | `spin_events` | Analysis | uuid | →shot | soft | ⬜ | 03 |
| 27 | BallTrack | `ball_tracks` | Analysis | uuid | →rally | soft | ⬜ | 01/03 |
| 28 | PoseTrack | `pose_tracks` | Analysis | uuid | →rally;→player | soft | ⬜ | 04/06 |
| 29 | Equipment | `equipment` | Players | uuid | →player | soft | ⬜ | 20 |
| 30 | TrainingSession | `training_sessions` | Training | uuid | →player;→drills | soft | ⬜ | 08/22 |
| 31 | Drill | `drills` | Training | uuid | (library) | soft | ⬜ | 22 |
| 32 | TrainingPlan | `training_plans` | Training | uuid | →player;→sessions | soft | ⬜ | 08/23 |
| 33 | Annotation | `annotations` | Annotation | uuid | →video/frame | soft | ⬜ | 30 |
| 34 | LabelTask | `label_tasks` | Annotation | uuid | →annotations | soft | ⬜ | 30 |
| 35 | Dataset | `datasets` | Datasets | uuid | →splits | retain/version | ⬜ | 12/30 |
| 36 | Benchmark | `benchmarks` | Datasets | uuid | →model | retain | ⬜ | 29 |
| 37 | Model | `models` | AI Models | uuid | →inference_jobs | retain/version | ⬜ | 12/18 |
| 38 | InferenceJob | `inference_jobs` | AI Models | uuid | →model;→run | soft | ⬜ | 12 |
| 39 | PlayerProfile | `player_profiles` | Intelligence | uuid | →player (versioned) | soft | ✅ | 17 |
| 40 | OpponentDossier | `opponent_dossiers` | Intelligence | uuid | →org;→players | soft | ✅ | 07 |
| 41 | Matchup | `matchups` | Intelligence | uuid | →org;→dossier | soft | ✅ | 17/21 |
| 42 | GamePlan | `game_plans` | Intelligence | uuid | →matchup | soft | ✅ | 17/21 |
| 43 | Report | `reports` | Reports | uuid | →match/player/matchup | soft | ⬜ | 16/32 |
| 44 | EvidencePackage | `evidence_packages` | Evidence | uuid | →match;→run | immutable | ⬜ | 09/35 |
| 45 | Competition | `competitions` | Competitions | uuid | →org;→matches | soft | ⬜ | 15 |
| 46 | AuditLog | `audit_logs` | Monitoring | uuid | →actor/org | append-only | ⬜ | 31/34.AK |
| 47 | DomainEvent | `domain_events` | Monitoring | uuid | (outbox) | retain | ⬜ | 13/34.R |
| 48 | Notification | `notifications` | Notification | uuid | →user | soft | ⬜ | 32 |
| 49 | NotificationPref | `notification_prefs` | Notification | uuid | →user | soft | ⬜ | 32 |
| 50 | Setting | `settings` | Administration | uuid | →org/user | soft | ⬜ | 13 |
| 51 | FeatureFlag | `feature_flags` | Administration | uuid | →org | soft | ⬜ | 34.AU |
| 52 | ProvenanceRecord | `provenance_records` | Monitoring | uuid | →artifact | immutable | 🟡 | 34.AK |
| 53 | DriftRecord | `drift_records` | Monitoring | uuid | →model | retain | ⬜ | 29 |
| 54 | DSARRequest | `dsar_requests` | Administration | uuid | →player/user | retain | ⬜ | 31 |
| 55 | WebhookEndpoint | `webhook_endpoints` | Integration | uuid | →org | soft | ⬜ | 34.AR |
| 56 | IdempotencyKey | `idempotency_keys` | Identity | string | →org | TTL | ⬜ | 34.V |

---

## F. Entity Lifecycle

All entities MUST implement these states via status fields + timestamps; transitions MUST be explicit and auditable.

| State | Rule |
|-------|------|
| **Creation** | set `id` (UUID v4), `created_at` (UTC), `created_by`, `version=1`, `schema_version`. |
| **Processing** | long-running entities (`videos`, `analysis_runs`, jobs) MUST expose a `status` enum and update `updated_at`. |
| **Locked** | officiating evidence, audit logs, completed analysis results MUST become immutable (append-only); writes MUST be rejected (`409`). |
| **Archived** | user data MUST soft-delete first (`deleted_at` set / `status=archived`); reads MUST exclude archived by default. |
| **Deleted** | hard-delete MUST occur only via RTBF/retention jobs (Part 34.AJ/BM), cascading per §G. |
| **Retention** | each entity MUST declare a retention tier (hot/warm/cold) and TTL; expiry MUST anonymize or delete. |
| **Recovery** | soft-deleted records MUST be recoverable within the retention window; recovery MUST be audited. |

Transition matrix (normative for the implemented entities):
- `videos`: `uploaded → analyzing → (done|failed) → archived → deleted`.
- `analysis_runs`: `queued → processing → (done|failed)`; terminal states immutable.
- `game_plans`: `draft → final → archived`.
- `organizations`/`players`/`users`: `active → (suspended|disabled) → archived → deleted`.

---

## G. Entity Relationship Model

### G.1 Cardinality (core, IMPLEMENTED)
```
organizations 1───N users
organizations 1───N players
players       1───N videos
videos        1───N analysis_runs
analysis_runs 1───0..1 matches
matches       1───N rallies 1───N shots
rallies       1───N events        shots 1───N events
players       1───N player_profiles      (version increments)
organizations 1───N opponent_dossiers ───N players (subject, opponent)
organizations 1───N matchups ── N─1 opponent_dossiers ── N─1 players (my_player)
matchups      1───N game_plans
```

### G.2 Relationship classes
- **One-to-one:** `analysis_run ↔ match` (0..1). `matchup ↔ latest game_plan` (logical).
- **One-to-many:** all parent/child rows above.
- **Many-to-many:** `users ↔ roles` (via `role_assignments`, ⬜); `teams ↔ players` (via membership, ⬜); `roles ↔ permissions` (⬜).
- **Ownership/Composition (cascade delete):** match→rallies→shots→events; matchup→game_plans; player→profiles. Child rows MUST NOT exist without their parent.
- **Aggregation (no cascade, SET NULL):** dossier→opponent_player; matchup→dossier.

### G.3 Referential integrity (normative)
- Every FK MUST be declared with an explicit `ON DELETE` rule: `CASCADE` for composition, `SET NULL` for aggregation (Part 34.W).
- Every FK column MUST be indexed (§K).
- Cross-org references MUST NOT exist; a FK MUST resolve within the same `org_id`. CI MUST include a cross-tenant isolation test (§X, Part 34.AX).

---

## H. Database Schema

Alembic owns the schema; `app/models.py` MUST mirror migrations exactly (CI-enforced, §Z). Below: the IMPLEMENTED tables at column granularity (authoritative), then the SPECIFIED tables at design granularity (build target). All times are `DateTime` UTC; all ids are `String(36)` UUID in SQLite dev / `uuid`/`timestamptz` in Postgres prod.

### H.1 `organizations` ✅
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | uuid | no | PK |
| name | text | no | |
| created_at | timestamptz | no | default now |

### H.2 `users` ✅
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | uuid | no | PK |
| org_id | uuid | no | FK→organizations, CASCADE, indexed |
| email | text | no | UNIQUE(org_id, email) |
| password_hash | text | no | PBKDF2; never logged |
| role | text | no | `admin\|coach\|player\|official\|viewer` |
| created_at | timestamptz | no | |

### H.3 `players` ✅
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | uuid | no | PK |
| org_id | uuid | no | FK→organizations, CASCADE, indexed |
| full_name | text | no | |
| handedness | text | yes | enum (Part 28) |
| grip | text | yes | enum |
| player_type | text | yes | `pro\|junior` |
| sex | text | yes | `m\|f\|x` |
| para_class | smallint | yes | 1..11 (Part 24) |
| dob | date | yes | drives minor-consent gate |
| created_at | timestamptz | no | |

### H.4 `videos` ✅
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | uuid | no | PK |
| org_id | uuid | no | FK→organizations, CASCADE, indexed |
| player_id | uuid | no | FK→players, CASCADE, indexed |
| source | text | no | `upload\|url` |
| storage_key | text | no | storage-interface ref |
| status | text | no | lifecycle (§F) |
| fps | float | yes | probe |
| width | int | yes | probe |
| height | int | yes | probe |
| duration_sec | float | yes | probe |
| created_at | timestamptz | no | |

### H.5 `analysis_runs` ✅ (revision 0002 + 0004)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | uuid | no | PK |
| video_id | uuid | no | FK→videos, indexed |
| status | text | no | `queued\|processing\|done\|failed` |
| model_versions | json | yes | provenance |
| input_quality | json | yes | footage signals + capture link |
| reliability_index | float | yes | capped by capture grade (Part 10) |
| capture_certification | text | yes | `fail\|bronze\|silver\|gold\|platinum` (0004) |
| capture_acceptance | json | yes | compact CQS result + envelope + provenance hash (0004) |
| error | text | yes | |
| started_at / finished_at / created_at | timestamptz | yes/yes/yes | |

### H.6 `matches` ✅ / `rallies` ✅ / `shots` ✅ / `events` ✅
- `matches(id pk, analysis_run_id fk→analysis_runs indexed, score_summary json, reliability_index float, created_at)`.
- `rallies(id pk, match_id fk→matches CASCADE indexed, idx int, start_frame int, end_frame int, winner text, created_at)`.
- `shots(id pk, rally_id fk→rallies CASCADE indexed, idx int, stroke_class text[enum], hand text, speed_kmh float, spin_rpm float, confidence float, created_at)`.
- `events(id pk, rally_id fk→rallies CASCADE indexed, shot_id fk→shots SET NULL, type text[enum], frame int, payload json, confidence float, created_at)`.
- Measured numeric columns (`speed_kmh`, `spin_rpm`, placement) MUST be paired with a `confidence` and MUST be nullable to allow `abstain`.

### H.7 `player_profiles` ✅ / `opponent_dossiers` ✅ / `matchups` ✅ / `game_plans` ✅
Schemas per migration 0003 (authoritative): see `backend/migrations/versions/0003_intelligence.py`. Each carries `confidence`, JSON payloads, source ids, `created_at`; FKs CASCADE to org/player, SET NULL to optional refs; indexed on the primary parent.

### H.8 SPECIFIED tables (build target)
Each ⬜ entity in §E MUST be created with: `id uuid PK`, the shared fields (§I), its FKs (with ON DELETE per §G), its enums (Part 28), and the indexes in §K. Notable specified schemas:
- **`capture_sessions`** `(id, org_id FK, venue_id FK, table_id FK, tier text, started_at, ended_at, certification_id FK, provenance_hash, schema_version)`.
- **`cameras`** `(id, session_id FK CASCADE, persistent_camera_uid text, model text, firmware text, global_shutter bool)`; UNIQUE(session_id, persistent_camera_uid).
- **`calibrations`** `(id, camera_id FK CASCADE, version int, intrinsics json, distortion json, extrinsics json, reproj_rms_px float, valid_until, provenance_hash)`; immutable.
- **`audit_logs`** `(id, org_id FK, actor_user_id FK SET NULL, action text, target_type text, target_id uuid, before json, after json, created_at)`; append-only, no PII payloads.
- **`domain_events`** (transactional outbox) `(id, org_id, type text, version int, aggregate_type text, aggregate_id uuid, payload json, occurred_at, published_at null, idempotency_key text UNIQUE)`.
- **`idempotency_keys`** `(key string PK, org_id, request_fingerprint text, response_hash text, created_at, expires_at)`.
- **`provenance_records`** `(id, org_id, artifact_type text, artifact_id uuid, code_sha text, model_versions json, schema_version text, inputs json, hash text, created_at)`; immutable.

### H.9 Partition / retention / archival (normative)
- High-volume tables (`shots`, `events`, `ball_tracks`, `pose_tracks`, `audit_logs`, `domain_events`) SHOULD be **range-partitioned by month** in Postgres prod.
- Media (`videos`) MUST follow hot→warm→cold tiering (Part 34.BM). Archived rows MUST remain tenant-scoped and restorable.
- `domain_events`/`idempotency_keys` MUST have a TTL purge job; legal-hold MUST override purge.

---

## I. Shared Fields

Every table (except pure link tables and append-only logs where noted) MUST include:

| Field | Type | Rule |
|-------|------|------|
| `id` | uuid | PK; UUID v4; client MUST NOT set it on create. |
| `created_at` | timestamptz | UTC; set on insert; immutable. |
| `updated_at` | timestamptz | UTC; set on every update (🟡 — MUST be backfilled where missing). |
| `deleted_at` | timestamptz | soft-delete marker; null = live. |
| `created_by` | uuid | actor user id (nullable for system). |
| `updated_by` | uuid | actor of last mutation. |
| `version` | int | optimistic-lock counter; bumped per update (§V). |
| `provenance_hash` | text | for measured/evidentiary artifacts (Part 34.AK). |
| `schema_version` | text | the contract version the row was written under. |
| `org_id` | uuid | tenant scope on every org-owned table; FK→organizations. |

`updated_at`, `created_by`, `updated_by`, `version`, `provenance_hash`, `schema_version` are currently 🟡 (partially present). Implementation MUST add them via an expand migration; §X gates this.

---

## J. Naming Conventions

- **Database:** tables `snake_case` plural (`analysis_runs`); columns `snake_case`; FKs `<entity>_id`; indexes `idx_<table>_<cols>`; uniques `uq_<table>_<cols>`; checks `ck_<table>_<rule>`.
- **API paths:** `/v1/<plural-noun>` resource-oriented (`/v1/players/{id}/videos`).
- **JSON fields:** `snake_case`; reliability envelope keys fixed as `{value, confidence, ci, tier, source, status}`.
- **Enums:** values are Part 28 `canonical_id`s; MUST NOT be free-text.
- **Files:** `snake_case.py`; SSoT artifacts keep their `Part` prefix (`35_CAPTURE_ACCEPTANCE_SCHEMA.json`).
- **IDs:** UUID v4 string; URL path params named `id`/`pid`/`vid`/`rid` consistently.
- **Events:** `tt.<context>.<aggregate>.<verb>` (e.g. `tt.analysis.run.completed`), `snake_case` payload keys, integer `version`.

---

## K. Index Strategy

- **K.1 Primary:** every table on `id`.
- **K.2 Secondary:** every FK column (`org_id`, `video_id`, `match_id`, …) MUST be indexed.
- **K.3 Composite:** hot filters — `(org_id, created_at)`, `(player_id, version)` on profiles, `(match_id, idx)` on rallies, `(rally_id, idx)` on shots.
- **K.4 Partial:** `WHERE deleted_at IS NULL` indexes for live-row queries; `WHERE published_at IS NULL` on `domain_events` (outbox poll).
- **K.5 Unique:** `uq_users_org_email(org_id,email)`; `uq_cameras_session_uid`; `uq_idempotency_key`.
- **K.6 GIN (Postgres):** on heavily-queried `JSONB` (`input_quality`, `capture_acceptance`, dossier `summary`).
- **K.7 Vector:** embedding columns for similarity (opponent/style search) MUST use `pgvector` `ivfflat`/`hnsw` (⬜, Part 11).
- **K.8 Spatial:** court/placement geometry queries SHOULD use a spatial or numeric-range index (⬜, Part 19).
- **K.9 Search:** global search (Part 32.S) MUST use a tenant-scoped full-text index, never a cross-tenant scan.
- **Rationale:** indexes MUST be justified by a query path; unused indexes MUST be removed (Part 34.M).

---

## L. API Design Principles

- **L.1 REST**, resource-oriented, plural nouns, under `/v1`.
- **L.2 Stateless:** every request MUST carry its own auth; server MUST hold no session affinity.
- **L.3 Consistent:** uniform envelope for measured values, uniform error body (§Q), uniform pagination (§U).
- **L.4 Versioned:** path-versioned (`/v1`); breaking change → `/v2` (§V).
- **L.5 Reliable:** measured responses MUST carry confidence + status and MAY `abstain`.
- **L.6 Idempotent:** `GET/PUT/DELETE` idempotent; create-side `POST` (`analyze`, `game-plan`) MUST honour `Idempotency-Key` (§U, Part 34.V) (🟡 — header accepted, dedup store ⬜).
- **L.7 Discoverable:** the OpenAPI document MUST describe every endpoint, schema, and error.

---

## M. Authentication

- **M.1 JWT (HS256)** bearer tokens are the primary mechanism ✅ (`app/security.py`). Tokens MUST carry `sub` (user id), `org` (tenant), `role`, `exp`. The signing secret MUST come from config and MUST NOT be the dev default in prod (✅ guard).
- **M.2 Refresh tokens** ⬜ MUST be supported for session continuity; short-lived access + longer refresh; rotation on use (Part 34.AF).
- **M.3 API keys / service accounts** ⬜ for machine clients (capture rigs, CI); scoped, revocable, rate-limited.
- **M.4 OAuth/OIDC** MAY be added for federation SSO; MUST map external identity to a `users` row.
- **M.5** All tokens/keys MUST be revocable; revocation MUST take effect within the access-token TTL.

## N. Authorization

- **N.1 RBAC** deny-by-default ✅ (`require_roles`): writes require `admin|coach`; reads org-scoped. 
- **N.2 ABAC/field-level** 🟡: medical/injury fields MUST be omitted server-side for non-medical roles (Part 31/34.AJ).
- **N.3 Object ownership:** every query MUST filter by `org_id` derived from the **token**, never the body (Part 31/34.AH).
- **N.4 Organization boundaries / multi-tenant isolation:** cross-org access MUST return `404` (not `403`, to avoid existence disclosure). A cross-tenant isolation test per resource is MANDATORY (§X).

---

## O. REST Resource Catalog

`Auth` column: `public` | `bearer`; `RBAC` = required roles for the operation. ✅ = live.

| Method & Path | Purpose | Auth | RBAC | Status |
|---------------|---------|------|------|--------|
| `GET /v1/health` | liveness | public | — | ✅ |
| `POST /v1/auth/register` | create org+user | public | — | ✅ |
| `POST /v1/auth/login` | obtain JWT | public | — | ✅ |
| `POST /v1/auth/refresh` | rotate token | bearer | — | ⬜ |
| `GET/POST /v1/players` | list/create player | bearer | r:any / w:admin,coach | ✅ |
| `GET /v1/players/{id}` | read player | bearer | any | ✅ |
| `POST /v1/players/{id}/videos` | upload video | bearer | admin,coach | ✅ |
| `GET /v1/players/{id}/videos` | list videos | bearer | any | ✅ |
| `POST /v1/videos/{id}/analyze` | run analysis (+ capture report) | bearer | admin,coach | ✅ |
| `GET /v1/analysis-runs/{id}` | run status + reliability | bearer | any | ✅ |
| `GET /v1/analysis-runs/{id}/capture` | dashboard envelope + KPI states | bearer | any | ⬜ |
| `GET /v1/matches/{id}` | match tree | bearer | any | ✅ |
| `GET/POST /v1/players/{id}/profile[/rebuild]` | profile read/rebuild | bearer | r:any / w:admin,coach | ✅ |
| `POST /v1/opponents` | create dossier | bearer | admin,coach | ✅ |
| `POST /v1/matchups` | create matchup | bearer | admin,coach | ✅ |
| `POST /v1/matchups/{id}/game-plan` | generate plan | bearer | admin,coach | ✅ |
| `GET /v1/matchups/{id}` | read matchup+plan | bearer | any | ✅ |
| `/v1/training-plans`, `/v1/drills` | training | bearer | mixed | ⬜ |
| `/v1/reports/*`, `/v1/evidence/*` | reports/evidence | bearer | mixed | ⬜ |
| `/v1/webhooks`, `/v1/notifications` | integration | bearer | admin | ⬜ |
| `/v1/admin/*` (roles, consents, flags, DSAR) | administration | bearer | admin | ⬜ |

The live surface is 20 paths / 31 schemas (`api/openapi.yaml`). New endpoints MUST be added to both the OpenAPI document and this catalog in the same PR (§Z).

---

## P. Request & Response Contracts

- **P.1** Every request body MUST be a Pydantic model in `app/schemas.py` with `extra="forbid"` (reject unknown fields, Part 34.AH).
- **P.2** Every response MUST be a declared `response_model`; measured values MUST embed the reliability envelope.
- **P.3 Validation:** bounded strings/numbers/enums; violations → `422` with field detail.
- **P.4 Status codes:** `200` read, `201` create, `202` accepted (async), `204` no-content, `400/401/403/404/409/422/429/5xx` per §Q.
- **P.5 Headers:** requests MAY send `Idempotency-Key`, `If-Match` (ETag); responses MUST send `ETag` on mutable resources and `Retry-After` on `429`.
- **P.6 Examples (normative):**
  - `POST /v1/videos/{id}/analyze` request: `{ "capture_measurements": { "<kpi_id>": <value> }, "capture_context": { "operator_id": "...", "camera_ids": ["..."], "calibration_version": "...", "capture_tier": "T3" } }` (all optional).
  - response (`AnalysisRun`): `{ id, video_id, status, reliability_index, input_quality, model_versions, capture_certification, capture_acceptance{ reliability_envelope, provenance_hash, failed_gates[] }, error, match_id }`.
- **P.7 Error response body (uniform):** `{ "code": "<stable_code>", "message": "<human>", "details": {...}? }`.

---

## Q. Error Model

Stable string `code`s (Part 34.BG); each maps deterministically to a status. The catalog is authoritative; codes MUST NOT be renumbered.

| Category | code (example) | HTTP |
|----------|----------------|------|
| Validation | `validation_error` | 422 |
| Authentication | `unauthenticated`, `token_expired` | 401 |
| Authorization | `forbidden` | 403 |
| Not found / cross-tenant | `not_found` | 404 |
| Business rule | `rule_violation` (e.g. `minor_consent_required`) | 409/422 |
| Conflict | `conflict`, `version_conflict` | 409 |
| Rate limit | `rate_limited` | 429 (+`Retry-After`) |
| Internal | `internal_error` | 500 |
| Reliability abstention | `abstained` | 200 with `status="abstain"` (NOT an HTTP error) |

`abstained` MUST be represented as a successful response whose envelope `status` is `abstain` — abstention is a first-class result, not a failure (Part 10).

---

## R. Event Architecture

The MVP MAY execute inline but MUST emit the following contract via a **transactional outbox** (`domain_events`) so a broker drops in without contract change.

| Event | Type | Emitted when | Status |
|-------|------|--------------|--------|
| `tt.video.uploaded` | domain | video stored | ⬜ |
| `tt.analysis.run.started` / `.completed` / `.failed` | domain | run transitions | ⬜ |
| `tt.capture.certified` | reliability | capture certified | ⬜ |
| `tt.profile.rebuilt` | domain | profile recomputed | ⬜ |
| `tt.matchup.gameplan.ready` | domain | plan generated | ⬜ |
| `tt.officiating.call.logged` / `.overridden` | audit | call/override | ⬜ |
| `tt.security.*`, `tt.consent.*` | audit | sensitive action | ⬜ |
| `tt.notification.requested` | integration | user-facing notice | ⬜ |

Rules: events MUST be **versioned** (integer `version`); **ordered per aggregate** (sequence within `aggregate_id`); **idempotent** (consumers dedupe on `idempotency_key`); **at-least-once** delivery; payloads MUST NOT contain PII beyond ids (Part 34.AR).

---

## S. Webhooks

- **S.1 Supported:** `analysis.completed`, `gameplan.ready`, `capture.certified`, `report.ready` (⬜).
- **S.2 Payload:** `{ id, type, version, occurred_at, org_id, data:{ ids + signed fetch URL } }` — data by reference, not value (Part 34.AR).
- **S.3 Retries:** exponential backoff + dead-letter; at-least-once → receivers MUST be idempotent.
- **S.4 Signature:** `X-TTOS-Signature` = HMAC-SHA256 over the raw body with the endpoint secret + a timestamp; receivers MUST verify and reject stale/replayed deliveries.
- **S.5 Verification:** a `GET` challenge or signed ping MUST confirm endpoint ownership on registration.
- **S.6 Ordering:** consumers MUST NOT assume order; use `occurred_at` + per-aggregate sequence.
- **S.7 Security:** destinations MUST be allow-listed (no SSRF); secrets stored in the vault (Part 31).

---

## T. Import / Export

- **T.1 CSV:** roster import; the capture **acceptance checklist** export (`35_CAPTURE_ACCEPTANCE_CHECKLIST.csv`) ✅.
- **T.2 JSON:** full entity export for DSAR/portability (Part 32.Z) ⬜; the analysis result is JSON-native.
- **T.3 Video:** signed-URL upload/download via the storage interface; raw paths MUST NOT be exposed (Part 34.AI).
- **T.4 Reports:** PDF (coach + simplified player) ⬜ (Part 32.M).
- **T.5 Evidence packages:** immutable, hashed bundle (frames + 3D + envelope) for officiating ⬜ (Part 09/35).
- **T.6 Annotations / datasets:** versioned export with a datasheet; PII de-identified before export (Part 34.AJ/BJ) ⬜.
- All imports MUST be validated at the boundary; all exports MUST be org-scoped and audited.

---

## U. Performance Targets

| Concern | Target (normative) |
|---------|--------------------|
| API read p95 | < 300 ms (cached/simple), < 800 ms (aggregations) |
| API write p95 | < 500 ms (excluding analysis) |
| Analysis enqueue | `202` in < 300 ms; processing async |
| Live officiating latency | < 100 ms; coaching < 200 ms (Part 35.AG) |
| Payload limit | request body ≤ 1 MB (excl. uploads); uploads bounded by size/codec |
| Pagination | cursor-based; default `limit=50`, max `limit=200` |
| DB | no N+1; every list paginated; FK-indexed |
| Concurrency | optimistic locking on mutable rows; single-flight per video (Part 34.AQ) |
| Caching | explicit keys + invalidation; MUST NOT cache authz decisions or PII (Part 34.X) |

## V. Versioning Strategy

- **Database:** Alembic linear history; one migration per change; `upgrade head` MUST run clean on SQLite **and** Postgres; downgrades MUST be provided. Current head: `0004`.
- **API:** path-versioned `/v1`; additive changes are non-breaking; breaking changes require `/v2` + deprecation window.
- **Events/Schemas:** integer `version`; consumers MUST tolerate unknown fields (forward-compat).
- **Backward compatibility:** expand→migrate→contract (Part 34.AG); no destructive change without backup.
- **Deprecation:** announce → grace period → remove; `Deprecation`/`Sunset` headers SHOULD be sent.
- **Migration:** data backfills are separate, idempotent, resumable, dry-runnable scripts (Part 34.AG).

---

## W. Traceability Matrix

Each Part MUST map to entities/endpoints/events/modules. (Representative, complete by context.)

| Part | Entity(s) | Endpoint(s) | Event(s) | Module(s) |
|------|-----------|-------------|----------|-----------|
| 01 CV | analysis_runs, ball_tracks | analyze | run.* | `cv/` |
| 02 Capture/3D | capture_sessions, cameras, calibrations | analyze, …/capture | capture.certified | `capture_quality`, `cv/` |
| 03 Ball intel | shots, spin_events, ball_tracks | matches | run.completed | `cv/spin` |
| 04 ReID | players, pose_tracks | players | — | `cv/` (⬜) |
| 05 Stroke | shots | matches | — | `cv/` |
| 06 Biomech | pose_tracks | reports | — | `analytics/` (⬜) |
| 07 Tactical | opponent_dossiers | opponents | — | `analytics/opponent` |
| 08 Coaching | training_plans, drills | training-plans | gameplan.ready | `analytics/gameplan` |
| 09 Rules/Umpire | matches, games, points, evidence_packages, officiating | matches, evidence | officiating.* | `analytics/` (⬜) |
| 10 Reliability | (envelope embedded), provenance_records | all measured | reliability.* | `capture_quality`, schemas |
| 11 Knowledge | (embeddings) | (q&a) | — | (⬜) |
| 12 Data/ML | datasets, models, inference_jobs | (admin) | — | `benchmark`, (⬜) |
| 13 Platform | domain_events, settings | all | all | `main`, `db`, routers |
| 14 Integrations | webhook_endpoints | webhooks | notification.* | (⬜) |
| 15 Federation | academies, teams, competitions, venues | admin | — | (⬜) |
| 16 Validation | benchmarks, reports | reports | — | `benchmark` |
| 17 Flagship | player_profiles, matchups, game_plans | profile, matchups | profile.rebuilt | `analytics/` |
| 18 Model catalog | models | (admin) | — | `cv/` registry |
| 19 Domain math | (in shots/spin) | — | — | `cv/spin`, constants |
| 20 Equipment | equipment | players | — | `analytics/` |
| 21 Tactics | game_plans | game-plan | — | `analytics/playbook` |
| 22 Drills | drills, training_sessions | drills | — | (⬜) |
| 23 Development | training_plans | training-plans | — | (⬜) |
| 24 Para | players (para_class) | players | — | schemas |
| 25 Anatomy | pose_tracks | — | — | (⬜) |
| 26 Assets | models | — | — | `cv/` |
| 27 Data model | all | all | all | this doc |
| 28 Ontology | (enums everywhere) | — | — | `i18n/`, schemas |
| 29 Eval | benchmarks, drift_records | — | — | `benchmark` |
| 30 Annotation | annotations, label_tasks, datasets | — | — | (⬜) |
| 31 Security | users, roles, permissions, consents, audit_logs, dsar_requests | auth, admin | security.*, consent.* | `security`, `deps` |
| 32 Product/UX | reports, notifications, settings | reports, notifications | notification.* | (⬜) |
| 33 Competitive | — | — | — | — |
| 34 Conventions | idempotency_keys, feature_flags | (cross-cutting) | (cross-cutting) | all |
| 35 Hardware/Capture | capture_sessions, capture_certifications | …/capture | capture.certified | `capture_quality` |
| 36 Risk | — | — | — | — |

Every row with a ⬜ module is a build target; CI MUST NOT mark Part 37 "complete" until §X gates pass for that row.

---

## X. Acceptance Criteria

Objective gates. Implementation conforms to Part 37 **iff** all MUST gates pass.

- **X.1** `alembic upgrade head` MUST succeed on SQLite and Postgres; `alembic downgrade` to base MUST succeed.
- **X.2** `app/models.py` MUST equal the migration state — Alembic autogenerate diff MUST be empty (no drift, Part 34.AP).
- **X.3** The live FastAPI schema MUST equal `api/openapi.yaml` — every route present in both, identical request/response refs.
- **X.4** Every endpoint MUST have a happy-path test, an auth/RBAC test, and a validation test (Part 34.E).
- **X.5** Every org-owned resource MUST have a **cross-tenant isolation** test returning `404` (Part 34.AX).
- **X.6** Every measured response field MUST carry a reliability envelope; a unit test MUST assert the envelope shape.
- **X.7** The capture framework MUST satisfy its tests, incl. the min-gate property and the committed-checklist drift gate (Part 35).
- **X.8** The golden-set accuracy gate MUST stay green (`tests/test_benchmark.py`, Part 29).
- **X.9** Secret scan MUST pass; no secret/PII in code, logs, or fixtures (Part 31/34.AF).
- **X.10** Every table MUST carry the shared fields (§I); a schema test MUST assert their presence.
- **X.11** No table/endpoint/schema may exist that is absent from §E/§O; a manifest test MUST assert catalog↔implementation equality.

## Y. Machine-Readable Build Artifacts

Authoritative artifacts and their ownership/sync rules. The **left side defines**, the **right side conforms**.

| Artifact | Canonical path | Owns | Synchronised with |
|----------|----------------|------|-------------------|
| ORM models | `backend/app/models.py` | runtime tables | MUST mirror migrations (X.2) |
| Migrations | `backend/migrations/versions/` | the schema (SSoT for DB) | this doc §H |
| Pydantic schemas | `backend/app/schemas.py` | request/response shapes | OpenAPI (X.3) |
| API contract | `api/openapi.yaml` | HTTP surface (SSoT for API) | routers (X.3), §O/§P |
| DB engine/session | `backend/app/db.py` | connection/session | §H |
| Event contracts | `backend/app/events.py` | event shapes (SSoT for events) | §R (⬜ — MUST be created) |
| Capture acceptance | `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json` | KPIs/levels/thresholds | `app/capture_quality.py` (Part 35) |
| Ontology | `i18n/glossary.json` | enums/canonical_ids | `en.json`/`ar.json` (Part 28) |
| Eval gate | `backend/app/benchmark.py` | accuracy gate | `tests/test_benchmark.py` (Part 29) |
| Docs | `backend/docs/` (⬜), `CLAUDE.md` | human entrypoints | this doc |

Sync rules: a change to any **SSoT** artifact MUST update its conforming artifact(s) in the **same PR**; CI (§Z) MUST fail otherwise. Note: the user-suggested names `database.py`, `backend/openapi.yaml`, `backend/alembic/` map to the canonical paths above (`app/db.py`, `api/openapi.yaml`, `backend/migrations/`); `events.py` is a new SSoT artifact to be created.

## Z. Consistency & Governance

The following governance rules are **mandatory** and MUST be enforced by CI; a failure MUST block merge.

- **Z.1 No divergence:** docs↔code consistency is CI-gated (X.2, X.3, X.7, X.10, X.11).
- **Z.2 OpenAPI sync:** the committed `api/openapi.yaml` MUST equal the app's generated schema (X.3).
- **Z.3 Traceable migrations:** every schema change MUST be a reviewed Alembic migration with up+down; linear history; no `create_all` in prod.
- **Z.4 Unique entity definitions:** each entity MUST be defined exactly once (§D/§E); duplicate table or schema names MUST fail CI.
- **Z.5 No duplicate schemas:** Pydantic/JSON schema names MUST be unique; a lint MUST enforce it.
- **Z.6 API→persistence:** every endpoint MUST read/write a defined entity (no orphan endpoints).
- **Z.7 Persistence→entity:** every table MUST correspond to a §E entity (no orphan tables — X.11).
- **Z.8 Entity→requirement:** every entity MUST trace to a Part via §W (no orphan entities).
- **Z.9 CI gates:** the pipeline MUST run — lint + type + migrations(up/down) + pytest + golden-set + secret-scan + drift(ORM/OpenAPI/checklist) + catalog-manifest. Any failure MUST block merge.
- **Z.10 Ownership:** changes to this document MUST be co-reviewed by a `MASTER_SPEC/` CODEOWNER and carry the conforming artifact changes.

This document, together with the artifacts in §Y, is the authoritative backend build specification for TT-OS.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
