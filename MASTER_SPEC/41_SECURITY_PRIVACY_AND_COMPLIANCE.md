# PART 41 — SECURITY, PRIVACY & COMPLIANCE (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative security, privacy & compliance law** of the platform — the build-ready formalization of Part 31, and the **fifth build pillar** after the data model (37), ontology (38), event contract (39), and reliability law (40). Where 37–40 give the platform *structure, meaning, communication, and honesty*, this part gives it **trust & safety**: the contract that protects athletes' video, biometric, health, and minors' data, and keeps officiating defensible.
>
> The platform holds **special-category biometric and health data, much of it for minors**, and makes **decisions about people** (officiating, talent selection). That makes security and privacy a **safety** property, not a feature.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`, where it is the build target. It **supersedes Part 31 for build**; Part 31 remains the readable concept overview. RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` (grounded in `backend/`) · 🟡 `PARTIAL` · ⬜ `SPECIFIED` (build target). Honesty rule (§B.5): a control is ✅ **only** if it is actually in code; aspirational controls are ⬜ — even where Part 31 optimistically marked them ✅ (corrected in §AA).

---

## A. Scope & Objectives

### A.1 Purpose
Guarantee that the platform **protects the people in its data** and **cannot be made to lie about who did what**. Confidentiality, integrity, and availability of athlete data; lawful, consented, minimal processing; and tamper-evident, non-repudiable records for any decision that affects a person.

### A.2 Goals
- **G1.** Every request is **authenticated**, **authorized** (deny-by-default), and **tenant-scoped** — no implicit trust (§D/§E/§F).
- **G2.** Every datum carries a **classification** (§C) that determines its storage, encryption, consent basis, retention, access, and erasure path.
- **G3.** **Privacy by design & default** (§H): lawful basis, consent (guardian consent for minors), minimization, and consent-withdrawal that propagates to **derived** artifacts.
- **G4.** Every **decisive call** (officiating, medical, talent) is **reproducible, signed, and tamper-evidently logged** (§K/§L) — non-repudiation.
- **G5.** **No secret, token, PII, or full media URL** is ever written to a log, repo, or CI output (§K/§Y).
- **G6.** Security invariants are **CI-enforced** (§Z), not left to reviewer vigilance — drift fails the build.
- **G7.** The system is **honest about its gaps** (§AA): production-blocking controls are tracked, not hidden behind a green checkmark.
- **G8.** Compliance (GDPR / biometric / children / EU AI Act) is an **auditable, evidenced claim** (§W/§AB), never a marketing label.
- **G9.** Decisions about people (officiating, selection, profiling) are **contestable** — human review, explanation, and a signed appeal path (§AC/§L).
- **G10.** Where the platform touches the **physical world** (robots, wearables), security **is safety**: authenticated commands + fail-safe defaults (§AH).

### A.3 Non-goals
- Not the data model (Part 37) — it **classifies** Part 37's fields and constrains their access.
- Not the event contract (Part 39) — it **consumes** Part 39's audit/outbox machinery for tamper-evident logging.
- Not the reliability law (Part 40) — it **binds** Part 40's officiating reproducibility + abstention to non-repudiation.
- Not federation organizational governance (Part 15) — it is the **technical** security/privacy contract.

### A.4 Relationship to Parts
Formalizes Part 31; extends Part 13 (auth/RBAC/tenancy) and Part 15 (consent/safeguarding/residency); classifies Part 37 fields; uses Part 39 §L (immutable audit events) + the transactional outbox; binds Part 40 §BO (reliability-incident response) + officiating reproducibility; consumes Part 35 provenance/tamper-evidence (capture chain-of-custody); governs the automated decisions of Parts 08/09/17 (§AC); secures the cyber-physical/IoT surface of Part 14 (§AH); guards the pretrained-weights supply chain of Part 26 (§AF/§Q); tags data classes as canonical ids in Part 38; ties risks to Part 36.

---

## B. Principles

- **B.1 Deny-by-default.** Access is denied unless a server-side rule explicitly grants it (§E). The UI is **never** the access-control boundary.
- **B.2 Least privilege.** Every identity (user, service, CI job, model) gets the **minimum** scope for its purpose, time-boxed where possible (§E/§S).
- **B.3 Defense in depth.** No single control is load-bearing: app RBAC **and** DB row-level security; validation **and** sandboxing; consent **and** encryption (§F/§N).
- **B.4 Privacy by design & default.** The most private setting is the default; data is **minimized** at collection, not cleaned up later (§H).
- **B.5 Honesty about gaps.** A control is ✅ only if it is in code (verified against `backend/`). Overstating a control is a **security defect** — it creates false assurance (cf. Part 40 §B.1: honesty over completeness).
- **B.6 Assume breach.** Design so that a single compromised credential, token, or dependency has **bounded blast radius** (short TTL, tenant isolation, segmented secrets, immutable backups) (§D/§U).
- **B.7 Tenant isolation is sacrosanct.** Cross-tenant data exposure is the **worst-case** failure (§F); the tenant id is derived from the **token**, never the request body.
- **B.8 Tamper-evidence for decisions.** Anything that affects a person (call, score, selection, injury flag) **MUST** be reproducible and written to an append-only, hash-chained trail (§K/§L).
- **B.9 Biometric is forever.** Gait/style/face embeddings **re-identify** and cannot be truly anonymized; "anonymized" biometrics are still personal data (§H.6).

---

## C. Data Classification & Handling (the SoT)

Every persisted field and artifact **MUST** carry exactly one **class**; the class dictates handling. Classes are canonical ids (Part 38): `class:biometric` · `class:special` · `class:minor` · `class:personal` · `class:operational` · `class:secret`.

| Class | Examples (this platform) | Encryption | Lawful basis / consent | Retention | Access | Erasure |
|-------|--------------------------|------------|------------------------|-----------|--------|---------|
| **`biometric`** (highest) | face/body/style/gait embeddings (Part 04 ReID), pose vectors | at-rest **+ separate store** (vector DB), own key | **explicit, separate** consent (GDPR Art 9) | shortest viable; per-tenant | biometric-scoped policy only; never cross-tenant | dedicated purge path (§I) |
| **`special`** | health/injury/medical (Part 06), para-classification (Part 24) | at-rest, field-level | explicit consent + purpose limit | purpose-bound | **medical role only** (§E field-level) | cascade + derived |
| **`minor`** (overlay) | any data where `subject.age < 18` (academies) | as base class, **stricter** | **guardian** consent (GDPR Art 8) | minimized; age-appropriate | no ad-profiling; restricted | guardian-initiated DSR |
| **`personal`** | name, DOB, nationality, raw video, scoreboard identity | at-rest + TLS | consent or legitimate interest | tenant policy | tenant-scoped + RBAC | RTBF (§I) |
| **`operational`** | match stats, model outputs, telemetry, audit | at-rest | contract/legitimate interest | tiered (Part 39 §AI) | internal, audit-logged | per retention |
| **`secret`** | JWT secret, API keys, KMS keys, webhook HMAC | **KMS / secrets manager** | n/a | rotation schedule | service-only, JIT | rotate + revoke |

- **C.1** Class **MUST** be derivable at query time (column-level tag or table-level policy) so access checks and exports can filter by it.
- **C.2** A field **MUST NOT** be down-classified silently; reclassification is an audited change (§K).
- **C.3** `minor` is an **overlay** that ratchets every other rule **stricter** (consent, retention, profiling, access).
- **C.4** Derived data **inherits the strictest class** of its inputs (a stat computed from biometric input is at least `special`) — the no-dilution rule, mirroring Part 40 §H.

---

## D. Authentication (AuthN)

- **D.1** Bearer auth is a signed **JWT** (✅ `backend/app/security.py`, hand-rolled HS256 over stdlib `hmac`/`hashlib`; verified with `hmac.compare_digest`).
- **D.2 Algorithm pinning.** The verifier **MUST NOT** select the algorithm from the token header (no `alg=none`, no RS/HS confusion). The current implementation is **structurally pinned** — it always recomputes HS256 and never dispatches on `header.alg` (✅ implicit); it **SHOULD** additionally assert `header.alg == "HS256"` for explicit defense-in-depth (🟡).
- **D.3 Secret hygiene.** `JWT_SECRET` **MUST** be a strong, rotated secret from a secrets manager (§Y); the dev default in `config.py` (`_DEFAULT_SECRET`) **MUST NOT** run in production — startup **MUST** refuse to boot in `prod` with the default (⬜, real gap).
- **D.4 Token lifetime.** Access tokens **MUST** be short-lived (current `jwt_expire_seconds=3600` is acceptable for access only) and paired with **refresh-token rotation + a revocation list** (⬜) — HS256 JWTs are otherwise valid until expiry and cannot be revoked.
- **D.5 Passwords.** Hashed with a strong KDF; current is **PBKDF2** (✅ `security.py`) — production **MUST** upgrade to **Argon2id** (or scrypt) (⬜). Enforce a password policy + a **breached-password check** (HIBP k-anonymity) (⬜).
- **D.6 MFA.** **Phishing-resistant MFA** (WebAuthn / passkeys / FIDO2) **MUST** be available and **mandatory for `admin`, `umpire`, `medical`** (⬜); **never** SMS-only (SIM-swap).
- **D.7 Brute-force & ATO.** Per-account + per-IP lockout, anomaly/risk-based step-up auth (new device / impossible travel) (⬜).
- **D.8 Account recovery** (the #1 ATO vector): no account enumeration (§M.5), signed time-limited reset links, recovery codes, session invalidation on reset (⬜).
- **D.9 Security-event notifications:** email on new-device login and on password/MFA/email change (⬜).
- **D.10 CSPRNG.** All tokens, ids, salts, nonces, and reset secrets **MUST** come from a cryptographically secure RNG (`os.urandom`/`secrets`) — **never** `random`; this **MUST** be asserted, not assumed.
- **D.11 API keys** are scoped + hashed + rotatable + revocable + expiring — full lifecycle in §AD.6.
- **D.12 Enterprise SSO.** Hand-rolled JWT is the **scaffold**; federation/academy tenants use **OIDC/SAML SSO + SCIM** (§AD) as the authoritative identity path.

---

## E. Authorization (RBAC + ABAC + Field-Level)

- **E.1 Deny-by-default, server-side.** Every write is gated by an explicit role dependency (✅ `require_roles`, `backend/app/deps.py`); reads are tenant-scoped (✅ `get_current_org`). No authorization decision is made in the client.
- **E.2 Canonical role → capability matrix** (deny unless ✓):

| Capability | admin | coach | player | umpire | medical | scout |
|------------|:-----:|:-----:|:------:|:------:|:-------:|:-----:|
| Manage org / users / roles | ✓ | | | | | |
| Manage roster / players | ✓ | ✓ | | | | |
| Upload / analyze video | ✓ | ✓ | | | | |
| Read analysis / profiles | ✓ | ✓ | own | | | ✓ |
| Build dossiers / matchups / game-plans | ✓ | ✓ | | | | ✓ |
| Officiating decision (decisive) | ✓ | | | ✓ | | |
| Read **medical / injury** (`special`) | ✓* | | own | | ✓ | |
| Manage consents / DSR | ✓ | | own | | ✓ (medical scope) | |

\* `admin` access to `special`/`medical` data **MUST** be break-glass + audited (§E.6), not routine.

- **E.3 Object-level (IDOR) checks.** Every resource access **MUST** verify `org_id` **and** ownership server-side; a client-supplied id is **never** trusted (IDOR is OWASP #1). Each endpoint **MUST** have a test asserting another tenant gets `404/403` (§Z).
- **E.4 Field-level / ABAC.** Access is attribute-based beyond role: `special`/`medical` fields are **hidden from `coach`/`scout`** even on a record they can otherwise read; `medical` sees only **their** athletes; access is **purpose-bound** (§U).
- **E.5 Mass-assignment protection.** Write models **MUST** whitelist editable fields; a create/update can **never** set `org_id`, `role`, `status`, `id`, ownership, or another tenant's keys (✅ today via Pydantic create/update models — keep it that way; add a CI check, §Z).
- **E.6 Privileged-access discipline.** Separation of duties, **just-in-time** elevation, **break-glass** with mandatory audit, periodic **access reviews**, and privileged-user activity monitoring (⬜).
- **E.7 Decision architecture.** At scale, RBAC + ABAC + field-level **SHOULD** be evaluated by a central **PDP/policy-as-code** with **fail-closed** enforcement, and **consent is an authorization input** (deny on absent/withdrawn consent for `biometric`/`special`/`minor`) — see §AE.

---

## F. Multi-Tenancy Isolation

- **F.1** Every tenant-owned row carries `org_id` (✅) and **every** query is org-scoped (✅ via `get_current_org` + router filters).
- **F.2 Tenant from token, not body.** The `org_id` used for scoping **MUST** come from the authenticated principal, **never** from the request payload or a path the client controls (✅).
- **F.3 Defense in depth at the DB.** Postgres **Row-Level Security** policies **MUST** enforce `org_id` isolation at the database, so an app-layer bug cannot leak across tenants (⬜, production-blocking).
- **F.4 No cross-tenant joins**; per-tenant **storage prefixes** for media/artifacts; per-tenant encryption context where feasible.
- **F.5 Tenant quotas.** Per-tenant **compute/volume quotas** (§O) bound a tenant's footprint — expensive analysis jobs are a **financial-DoS** vector (Part 36).
- **F.6 Isolation tests are mandatory** (§Z): a cross-tenant probe per resource family is part of the security regression gate.

---

## G. Cryptography & Key Management

- **G.1 In transit:** **TLS 1.3** everywhere (incl. internal service-to-service and webhooks).
- **G.2 At rest:** **AES-256** for DB, object storage, and **backups**; biometric store encrypted with its **own** key (§C).
- **G.3 Key management:** a **KMS** with **envelope encryption** and a scheduled **key-rotation** policy; application code never holds raw long-term keys (⬜).
- **G.4 Officiating signing key:** an **HSM-backed** signing key for decisive calls (§L); never exportable.
- **G.5 Media access:** all video/artifact access via **signed, expiring URLs** from **private** buckets — no public objects, no long-lived links (⬜).
- **G.6 Hashing:** content/provenance hashing is **SHA-256** (✅ capture provenance, Part 35); password KDF is Argon2id target (§D.5).
- **G.7 Crypto-agility:** algorithms and key ids are recorded in provenance so they can be rotated/deprecated without ambiguity.

---

## H. Privacy by Design & Consent

- **H.1 Lawful basis** **MUST** be recorded per processing purpose and per data class (§C); processing without a basis is forbidden.
- **H.2 Consent records.** A `consents` store (subject, purpose, basis, scope, timestamp, version, **guardian** for minors, withdrawal) **MUST** exist and gate biometric/special processing. **Status: ⬜ — not yet a table** (Part 31 §K marks it ✅; that is inaccurate, corrected here).
- **H.3 Guardian consent (minors).** `minor` data **MUST** require verifiable guardian consent (GDPR Art 8) and **MUST NOT** be used for ad-profiling; age-appropriate design by default.
- **H.4 Purpose limitation & minimization.** Collect and retain only what a feature needs; a new purpose needs a new basis (§H.1).
- **H.5 Withdrawal propagates to derived data.** Consent withdrawal **MUST** stop processing **and delete derived embeddings/artifacts** (not just the source clip) — the no-orphan-derivative rule (§I.3).
- **H.6 Biometric ≠ anonymizable.** Treat "anonymized" gait/style/face data as **still personal** (§B.9); only true aggregates with **differential privacy** may be published (§H.8).
- **H.7 Bystander & edge privacy.** Blur spectator/minor faces in background (Part 15); offer an **edge-private mode** where video never leaves the venue (Part 02/15) (⬜).
- **H.8 Published aggregates** (leaderboards, research stats) **MUST** apply **differential privacy** / k-anonymity so individuals can't be re-identified (ε-budget governance, §AJ.4).
- **H.9 Transparency & notice.** Data subjects **MUST** receive a clear privacy notice (GDPR Art 13/14): what is collected, purpose, lawful basis, retention, recipients, transfers, rights, and **that profiling/automated decisions occur** (§AC).
- **H.10 Erasure has a trained-model limit.** Withdrawal deletes derived embeddings/artifacts (§I.2), but influence already baked into model weights needs an explicit **machine-unlearning** stance (§AJ.5) — the platform **MUST NOT** claim a deletion it cannot perform.
- **H.11 Consent validity.** Consent **MUST** be **freely given, specific, informed, and unambiguous** (GDPR Art 4/7): **granular per purpose** (not bundled), **no pre-ticked boxes, no dark patterns**, and **withdrawal as easy as granting**; processing of non-essential data **MUST NOT** be a precondition of service where consent is the basis.
- **H.12 Consent provenance.** Each consent records **what / when / version / the text shown / lawful basis**, so it is **demonstrable** (Art 7.1 accountability) and auditable (§K).

---

## I. Data-Subject Rights (DSR) & Data Lifecycle

- **I.1 Rights with SLAs.** Support **access, rectification, portability (export), erasure, objection, restriction** with documented SLAs and an authenticated, audited workflow.
- **I.2 Right to be forgotten** = cascading delete of source + **all** derived data (profiles, dossiers, embeddings, cached artifacts, search indexes) + **crypto-erase** of encrypted copies where deletion is impractical.
- **I.3 No orphan derivatives.** Erasure/withdrawal **MUST** purge derivatives; a derivative that outlives its source consent is a breach (§H.5).
- **I.4 Retention.** Per-tenant retention policy with **scheduled deletion**; `operational` events tier to cold/cheap storage then expire (Part 39 §AI). Soft-delete (`deleted_at`, Part 37) is **not** erasure — a hard-delete + crypto-erase path **MUST** back RTBF.
- **I.5 Records.** Maintain a **ROPA** (records of processing) and a **DPIA** for biometric processing (mandatory, §W).
- **I.6 Export format** for portability **MUST** be machine-readable (JSON) and exclude other subjects' data.
- **I.7 Identity-proofing (DSAR-as-attack).** A request **MUST** verify the requester **is** the subject (or authorized guardian) with assurance **proportionate to the data's sensitivity** — an unverified access request is itself an **info-disclosure** vector (social-engineered DSAR). Biometric/`special` exports require stronger proofing.
- **I.8 DSR abuse protection.** DSR endpoints are **rate-limited + audited** (anti-harvesting/DoS); bulk or automated requests are throttled.
- **I.9 Legal hold.** Retention/erasure **MUST** honor a **legal hold** (litigation/anti-doping/investigation): held records are exempt from scheduled deletion and the hold is itself audited (§K).

---

## J. Third-Party / Opponent Data (product-specific)

- **J.1** Scouting **processes a non-consenting opponent's** biometric/personal data. The platform **MUST** record a **lawful basis** (legitimate-interest assessment / public-competition footage) per scouting use.
- **J.2 Minimization & retention** are stricter for non-consenting subjects; honor **objection/erasure** where the basis requires it; respect **regional** rules and data residency (§W).
- **J.3** Opponent dossiers (Part 37 `opponent_dossiers`) **MUST** carry their lawful-basis + retention metadata, and **MUST NOT** be shared cross-tenant.

---

## K. Audit Logging & Tamper-Evidence

- **K.1 Append-only, hash-chained** audit trail: each entry chains the prior entry's hash (tamper-evident), aligned to Part 39 §L immutable audit events. **Status: ⬜ — no `audit_log` table today** (Part 31 §K marks it ✅; inaccurate, corrected here).
- **K.2 What MUST be logged:** authn/authz decisions, access to `biometric`/`special`/`minor` data, decisive officiating/medical/talent actions, consent changes, exports/erasures, privileged/break-glass access, security events.
- **K.3 What MUST NEVER be logged:** passwords, tokens, secrets, full signed media URLs, raw biometric vectors, or PII beyond the minimal id needed (§G/§Y). Logs are **themselves** classified `operational` with access control + retention.
- **K.4 Integrity & availability.** Audit storage is **write-once** for the retention window; alerting fires on anomalous access patterns and on any chain-verification failure.
- **K.5 Officiating linkage.** Each decisive-call audit entry references the signed decision (§L) and its evidence package (Part 09/40) — a contested call is independently replayable.
- **K.6 Log-injection / forging.** Untrusted values **MUST** be sanitized of CR/LF/control characters before logging (prevent log forging); structured (JSON) logging is preferred over string concatenation.
- **K.7 PII leak detection.** A **detective** control (automated scanner) **SHOULD** flag tokens/PII/secret patterns in logs — the "never log PII" rule (§K.3) needs enforcement, not just intent.

---

## L. Officiating Integrity (cryptographic, high-stakes)

- **L.1 Reproducibility.** Every decisive call **MUST** be reproducible from provenance (model + code_sha + inputs + seed, Part 40 §J/§BP) and carry a **model card** + **evidence package** (Part 09/40).
- **L.2 Signature + trusted timestamp.** Each decisive decision **MUST** be **signed with an HSM key** (§G.4) and bound to a **trusted timestamp + a unique nonce** (anti-replay) → non-repudiation + tamper-evidence; a replayed or duplicated signed decision is rejected.
- **L.3 Chain-of-custody.** Evidence packages (clips, frames, tracks) carry an unbroken custody chain from capture (Part 35 provenance hash) to decision.
- **L.4 Clock integrity.** **NTP/clock integrity** is a security control — a manipulated clock breaks timing-based calls and timestamps; drift is monitored.
- **L.5 Human oversight.** Decisive calls are **advisory until validated** (Part 40 §K) and surface an **abstain → escalate-to-umpire** path; the system never silently forces a call it cannot defend.
- **L.6 EU AI Act alignment.** Officiating/selection are likely **high-risk AI** (§W): risk management, logging, human oversight, transparency, and accuracy/robustness evidence are **mandatory** before such features ship.
- **L.7 Contestability.** A decisive call is an automated decision about a person (§AC): the affected party **MUST** have a right to explanation + a signed, tamper-evident **appeal** path (§AC.3/§AC.4, §AI.5).

---

## M. API, Input & Session Hardening

- **M.1 Strict input validation** (Pydantic) + output encoding; reject unknown fields (anti mass-assignment, §E.5).
- **M.2 Request limits:** body-size caps, pagination caps, upload size/duration caps (§N), and timeouts on every external call.
- **M.3 CORS** allow-list (no `*` with credentials); **CSRF** protection for any cookie-based flow.
- **M.4 Security headers** on every response (§X): HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
- **M.5 Account-enumeration fix (real, current gap).** `POST /auth/register` returns **`409 "email already registered"`** (✅ confirmed in `backend/app/routers/auth.py`) and login/reset reveal account existence → **enumeration leak**. Fix: **generic responses** ("if that email is valid, you'll receive…"), constant-time handling, and rate-limited auth endpoints (⬜, tracked).
- **M.6 Webhooks:** outbound webhooks **MUST** be **HMAC-signed** with a per-tenant secret + timestamp and **replay protection**; inbound webhook URLs are SSRF vectors (§N).

---

## N. SSRF & Untrusted-Media Handling (concrete to our API)

- **N.1 SSRF defense.** `source=url` ingest and webhook target URLs **MUST**: allow-list schemes (`https` only), **resolve then validate** the IP, **deny** RFC-1918/link-local/loopback/cloud-metadata (`169.254.169.254`) ranges, and **forbid redirects** into private ranges. (⬜, production-blocking — ingest of remote URLs is a Part 37 capability.)
- **N.2 Sandboxed media processing.** Video is decoded/transcoded by **ffmpeg/OpenCV**, which carry CVEs. Processing **MUST** run in a **network-isolated, resource-limited, ephemeral, non-root** worker; validate + transcode before use; cap size/duration; treat every uploaded file as hostile (⬜).
- **N.3** Never pass untrusted file paths/URLs to a shell; no `eval` of metadata; strip/validate container metadata.

---

## O. Rate Limiting, Quotas & Abuse Protection

- **O.1** Per-tenant, per-account, and per-IP **rate limits** returning `429` with backoff hints. The `429` response is **schema-only today** (Part 31 §K) — **enforcement is ⬜**.
- **O.2 Auth endpoints** (`register`/`login`/reset) **MUST** be strictly rate-limited (anti brute-force + enumeration, §M.5).
- **O.3 Compute/financial-DoS:** per-tenant **job quotas** + queue **backpressure**; one tenant cannot starve others or inflate cost (§F.5).
- **O.4** Bot/scraping protection (model-extraction defense, §Q); **WAF + DDoS** protection at the edge (§U).

---

## P. Threat Model (STRIDE + ML + Sport-Specific)

Authoritative threat catalog; each maps to a concrete surface on **our** API and a mitigation + status.

| Threat | Vector (our surface) | Mitigation | Status |
|--------|----------------------|------------|--------|
| **Spoofing** | stolen JWT / API key | short TTL + refresh rotation + revocation; alg-pinning; key-hashed API keys; MFA for privileged | 🟡 (TTL ✅, rest ⬜) |
| **Tampering** | altered results/scores | hash-chained `audit_log`; signed officiating; integrity checks | ⬜ (audit_log/sign ⬜) |
| **Repudiation** | "I didn't make that call" | append-only audit + signed decisions + evidence package | ⬜ |
| **Info disclosure** | cross-tenant leak (IDOR) | org-scope ✅ + RLS + field-level + encryption | 🟡 (app-scope ✅, RLS ⬜) |
| **DoS** | upload flood / heavy jobs | rate limits (`429`), quotas, backpressure, WAF | ⬜ (enforcement) |
| **Elevation** | role bypass / mass-assignment | server-side RBAC ✅ + deny-by-default ✅ + whitelist writes ✅ | ✅ (add CI guard) |
| **Untrusted upload** | malicious video file | sandboxed, non-root, resource-limited worker; validate/transcode | ⬜ |
| **SSRF** | `source=url` / webhook URL | scheme allow-list + IP validation + no private redirects | ⬜ |
| **Model extraction / poisoning** | scraping outputs / bad labels | rate-limit + watermark; annotation IAA gate (Part 30) | 🟡 (IAA spec) |
| **Adversarial evasion** | patches/lighting vs officiating/ball/scoreboard | robustness testing; abstain on OOD (Part 40 §Y) | 🟡 (OOD ✅) |
| **Match-fixing / integrity** | manipulated officiating/clock | signed calls + clock integrity + anomaly detection (Part 15) | ⬜ |
| **Prompt injection** | malicious text into LLM Q&A (Part 11) | untrusted-text handling + tool/output allow-lists (§R) | ⬜ |
| **Account takeover** | credential stuffing / weak recovery | breached-password check, lockout, phishing-resistant MFA, hardened recovery | ⬜ |

---

## Q. ML / AI Model Security

- **Q.1 Adversarial robustness.** Officiating/ball/scoreboard models **MUST** be tested against evasion (adversarial patches, lighting/sticker attacks) — a wrong **forced** call is the worst case; under attack/OOD the system **abstains** (Part 40 §Y).
- **Q.2 Model theft / extraction.** Rate-limit + **watermark** outputs; detect bulk-scraping query patterns (§O).
- **Q.3 Membership inference.** Don't leak who is in the training set; prefer DP training for sensitive aggregates.
- **Q.4 Data poisoning.** The annotation **IAA gate** (Part 30) + label provenance defend the training set; reject unverified third-party labels.
- **Q.5 Pretrained-model supply chain.** Reused weights (Part 26: TTNet/TrackNet/…) **MUST** be checksum/signature-verified and weight-scanned — a backdoored model is a supply-chain compromise (§S).

---

## R. LLM-Layer Security (Part 11 grounded Q&A)

- **R.1 Treat all retrieved/user/external text as untrusted** — defend against **prompt injection**; instructions embedded in data **MUST NOT** change tool scope or policy.
- **R.2 Tool-use + output allow-lists**; the model cannot call tools or reach data outside the requesting principal's RBAC/tenant scope (§E/§F).
- **R.3 PII out of prompts.** Strip secrets/PII before they reach a model context; block exfiltration channels.
- **R.4 Ground every answer.** No ungrounded claims; cite evidence (Part 11/40) — an unsupported answer is an abstention.
- **R.5 Jailbreak + injection testing** is part of the release gate for any LLM-backed feature.

---

## S. Secure SDLC & Supply Chain

- **S.1 Secret scanning** in CI (✅ `secret-scan` job, `trufflehog`, `.github/workflows/ci.yml`); a finding **fails** the build. **SAST** **SHOULD** be added (⬜).
- **S.2 Dependency hygiene:** pinned dependencies + **SBOM** + automated vuln scanning (Dependabot-style); no untrusted packages (⬜).
- **S.3 Signed builds**, least-privilege CI tokens, no long-lived CI secrets; CI **MUST NOT** print secrets (§Y).
- **S.4 Pretrained-model provenance** (§Q.5) is part of the supply chain.
- **S.5 Code review + the governance gate (§Z)** are required to merge; security-relevant changes get a security review (`/security-review`).

---

## T. Detection, Logging & Incident Response

- **T.1 Centralized logging/metrics/tracing** (Part 34) with **anomalous-access alerting** on `biometric`/`special` data and on auth anomalies.
- **T.2 Incident response:** severity levels + on-call runbook; **contain → eradicate → recover → blameless post-mortem → prevent** (gate update). Aligns with Part 40 §BO reliability-incident flow; officiating/medical incidents are **High severity** and page immediately.
- **T.3 Breach notification:** GDPR **72-hour** authority notice; inform affected users and **guardians of minors**; keep a documented decision log.
- **T.4 Kill-switch.** A harmful feature (e.g. a public wrong officiating call) **MUST** be disableable without a redeploy (Part 34 feature flags).

---

## U. Resilience, BCDR & Backups

- **U.1 WAF + DDoS** protection; **circuit breakers** + graceful degradation under load (degrade to abstain, never to a wrong confident answer — Part 40).
- **U.2 RTO/RPO targets** per service tier; **immutable, encrypted backups** (ransomware-resistant) with **tested restores** (an untested backup is not a backup).
- **U.3 Compute quotas** per tenant bound financial-DoS (§O.3).

---

## V. Edge / Courtside Device Security

- **V.1** Courtside boxes (Part 02) **MUST** use **secure boot**, **disk encryption**, and **physical-tamper resistance**; keys are device-bound.
- **V.2 Device identity/attestation** for any device that uploads or signs; revoke compromised devices.
- **V.3 Vendor/third-party risk** review for broadcast feeds, cloud, robots, and any external data source.

---

## W. Compliance Mapping

| Regime | Trigger on this platform | Mandatory controls |
|--------|--------------------------|--------------------|
| **GDPR** | EU athletes/staff | lawful basis (§H), DSR (§I), **DPIA** for biometric, **72-h** breach (§T), DPO, DPAs, **ROPA**, data residency |
| **GDPR Art 9** (special category) | biometric + health | **explicit** consent, separate store, stricter access (§C/§E) |
| **GDPR Art 8 / children** | academies (minors) | **guardian** consent, no ad-profiling, age-appropriate design (§H.3) |
| **COPPA** (US minors) | US academies | verifiable parental consent, minimization |
| **BIPA / US biometric laws** | biometric embeddings | written consent, **public retention/deletion schedule**, no sale, private right of action → high liability |
| **EU AI Act** | officiating / talent selection = likely **high-risk** | risk mgmt, logging, **human oversight** (§L.5), transparency, accuracy/robustness evidence (§Q), automated-decision rights (§AC) |
| **Controller vs Processor (GDPR Art 28)** | controller (own users) **+** processor (federation customers) | declare role per relationship; DPAs; sub-processor register; process on instructions (§AJ.1) |
| **International transfers (GDPR Ch. V)** | EU data → non-EU processing | adequacy / **SCCs** / BCRs + **TIA**; region-pinning (§AJ.2) |
| **Transparency (GDPR Art 13/14)** | any personal-data collection | privacy notice: purpose, basis, retention, rights, **profiling disclosure** (§H.9) |
| **Automated decisions (GDPR Art 22)** | officiating / talent selection / profiling | human review + explanation + **appeal**; no solely-automated on minors (§AC) |
| **Fairness / non-discrimination** | EU AI Act + equality law | subgroup fairness gate; **no proxy discrimination** (§AC.7 / Part 40) |
| **Anti-doping data** | federation integrations | restricted handling + residency (§AI.4) |
| **SOC 2 / ISO 27001 / OWASP ASVS** | enterprise/federation sales | control framework + audit (§AB) |

Compliance claims are **evidenced** (DPIA docs, ROPA, audit exports), never asserted (§A.2 G8).

---

## X. Security Headers & Secure Defaults (build-ready)

| Header / default | Value (baseline) |
|------------------|------------------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` |
| `Content-Security-Policy` | `default-src 'self'; frame-ancestors 'none'; object-src 'none'` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | minimize (deny camera/mic/geolocation unless needed) |
| Cookies (web flows) | `Secure; HttpOnly; SameSite=Strict` |
| CORS | explicit origin allow-list; no `*` with credentials |

Status: ⬜ (middleware to add). These are non-controversial defaults and **MUST** ship before any browser-facing release.

---

## Y. Secrets & Configuration Management

- **Y.1** Production secrets come from a **secrets manager** (not env files / repo); the dev `_DEFAULT_SECRET` is forbidden in prod (§D.3).
- **Y.2 Rotation** on a schedule (JWT secret, API keys, webhook HMAC, KMS keys); rotation is non-disruptive (overlapping validity).
- **Y.3 Never in logs/CI/repo** (enforced by §S.1 secret-scan); per-environment isolation (dev/stage/prod use different secrets).

---

## Z. Governance & CI Enforcement (security invariants)

Security rules **MUST** be machine-checked in CI (the security analogue of Parts 37/39/40 governance), so a regression **fails the build** rather than relying on review. Target home: `backend/tools/governance/` (new `security.py` check, wired into `ALL_CHECKS`).

| Check | Invariant | Status |
|-------|-----------|--------|
| `secret-scan` | no secret/token in the repo (trufflehog) | ✅ enforced (CI) |
| `rbac-deny-by-default` | every write router has a `require_roles` dependency | 🟡 (true in code; add a CI assertion) |
| `org-scope` | data queries filter by `org_id` from the principal | 🟡 (true in code; add a CI assertion) |
| `mass-assignment` | no create/update model exposes `org_id`/`role`/`status`/`id` | 🟡 (true; add CI assertion) |
| `jwt-alg-pin` | verifier never selects algorithm from the token header | ✅ structural (assert explicitly) |
| `no-pii-logs` | lint forbids logging tokens/PII/full media URLs | ⬜ |
| `security-headers` | header middleware present on the app | ⬜ |
| `auth-enumeration` | auth endpoints return generic responses + are rate-limited | ⬜ (current 409 leak, §M.5) |
| `dep-vuln` | no known-critical CVE in pinned deps; SBOM emitted | ⬜ |
| `untrusted-media` | URL ingest validates IP ranges; media worker is sandboxed | ⬜ |
| `safe-model-loading` | weights load via `safetensors` / sandbox — no in-process `pickle`/`torch.load` of untrusted files | ⬜ |
| `path-traversal` | `storage_key`/path inputs validated against an allow-listed prefix (no `..`/absolute) | ⬜ |
| `no-shell-exec` | media tooling invoked with arg arrays — no `shell=True` / string interpolation | ⬜ |
| `csprng` | tokens/ids/salts/nonces use `secrets`/`os.urandom`, never `random` | 🟡 (assert) |
| `consent-gate` | access to `biometric`/`special`/`minor` checks a valid consent | ⬜ |
| `vetted-crypto` | prod uses maintained crypto libs (no hand-rolled JOSE/KDF, §AL.1) | ⬜ |
| `model-signing` | deployed models are signed + checksum-verified before load (§AP.2) | ⬜ |
| `slo-gates` | security SLOs (§AK) wired as gates (patch SLA, rotation age, restore test) | ⬜ |

- **Z.1** Each ✅/🟡 invariant **MUST** have a test; promoting 🟡→✅ means the CI assertion exists, not just the behavior.
- **Z.2** The build manifest (Part 37 governance) **SHOULD** record the security-gate result alongside the other checks.

---

## AA. Build-Artifacts Status (honest, grounded in `backend/`)

| Control | Artifact | Status |
|---------|----------|--------|
| JWT bearer auth (HS256, alg structurally pinned) | `app/security.py`, `app/deps.py` | ✅ |
| Password hashing (PBKDF2; Argon2id target) | `app/security.py` | ✅ (🟡 upgrade) |
| RBAC `require_roles`, deny-by-default writes | `app/deps.py`, routers | ✅ |
| Org-scoping on every query | `app/deps.py` `get_current_org`, routers | ✅ |
| Mass-assignment protection (whitelist writes) | Pydantic create/update models | ✅ |
| Soft-delete / shared lifecycle fields | `app/models.py` (Part 37) | ✅ |
| Secret scanning in CI | `.github/workflows/ci.yml` (trufflehog) | ✅ |
| `429` rate-limit **schema** | `app/schemas.py` | 🟡 (no enforcement) |
| Consent records (`consents` table) | — | ⬜ (Part 31 over-claimed ✅) |
| Tamper-evident `audit_log` (hash-chained) | — | ⬜ (Part 31 over-claimed ✅) |
| Postgres RLS tenant isolation | — | ⬜ |
| Encryption-at-rest config + KMS | — | ⬜ |
| Secrets manager + no prod default secret | `config.py` `_DEFAULT_SECRET` | ⬜ (gap) |
| Refresh-token rotation + revocation | — | ⬜ |
| Phishing-resistant MFA (privileged roles) | — | ⬜ |
| Account-enumeration fix (generic auth responses) | `routers/auth.py` `409` | ⬜ (gap) |
| SSRF guard + sandboxed media worker | — | ⬜ |
| Signed officiating (HSM) + clock integrity | — | ⬜ |
| Security-headers middleware | — | ⬜ |
| Face/bystander blurring; edge-private mode | — | ⬜ |
| SBOM + dependency-vuln gate; SAST | — | ⬜ |
| Enterprise SSO (OIDC/SAML) + SCIM provisioning | — | ⬜ |
| Workload identity (mTLS / SPIFFE) for services | — | ⬜ |
| Safe model loading (safetensors / sandbox; no in-proc pickle) | — | ⬜ |
| Path-traversal guard on `storage_key` | — | ⬜ |
| PEP/PDP policy-as-code + consent-as-authz | `require_roles` (scattered today) | ⬜ |
| Infra/cloud/container hardening (CSPM, PSS, segmentation) | — | ⬜ |
| Cyber-physical safety (command-auth, E-stop) — Part 14 | — | ⬜ |
| Market-integrity barriers (embargo, insider controls) | — | ⬜ |
| Controller/Processor declaration + DPA + sub-processor register | — | ⬜ |
| International-transfer mechanism (SCCs/TIA) | — | ⬜ |
| Art 22 human-review + explanation + appeal | — | ⬜ |
| Machine-unlearning policy / DP ε-budget | — | ⬜ |
| Security SLO gates (patch/rotation/RPO/RTO) | §AK targets | ⬜ |
| Vetted crypto libraries (replace hand-rolled HS256/PBKDF2) | `security.py` (hand-rolled) | ⬜ |
| Named owners (CISO/DPO) + RACI + risk-acceptance log | — | ⬜ |
| Vuln/patch SLA by severity + EOL tracking | dep-scan only | ⬜ |
| DLP / egress monitoring + export watermarking | — | ⬜ |
| Model registry access control + signed dual-control promotion | — | ⬜ |
| DAST + media-pipeline fuzzing + dependency-confusion guard | SAST/secret-scan only | ⬜ |
| Media sanitization (NIST 800-88) · SPF/DKIM/DMARC · a11y security | — | ⬜ |

This table is the **truth** of where security stands today: a sound auth/RBAC/tenant/secret-scan core (✅), with the privacy-record, tamper-evidence, encryption-config, abuse-protection, enterprise-identity, app-sec-hardening, cyber-physical-safety, and deep-compliance layers **specified and tracked** (⬜) — production-blocking, not optional. The breadth of ⬜ is deliberate honesty (§B.5): a green checkmark is earned by code, not by intent.

---

## AB. Acceptance & Assurance

- **AB.1** Target **OWASP ASVS** level (L2 for app, L3 for officiating/medical paths); map controls to ASVS + Top-10.
- **AB.2 Penetration test + bug-bounty** before any federation rollout; findings tracked to closure.
- **AB.3** Pursue **SOC 2 / ISO 27001**; continuous compliance monitoring; staff/coach **security-awareness training**.
- **AB.4** Public **vulnerability-disclosure policy** (`security.txt`) + responsible-disclosure process.
- **AB.5** A release that regresses a §Z invariant or a ✅ in §AA is **blocked**.

---

## AC. Automated Decision-Making, Profiling & Contestability (GDPR Art 22 / EU AI Act)

Talent selection (Part 08), officiating calls (Part 09), and player profiling (Part 17) are **decisions about people with legal or significant effects** — governed beyond accuracy (Part 40).

- **AC.1 No solely-automated significant decisions** about a person **without** a lawful exception (explicit consent / contract / law) **and** safeguards (GDPR Art 22). On `minor` subjects, solely-automated significant decisions are **forbidden** by default.
- **AC.2 Human-in-the-loop.** Such decisions **MUST** route through a qualified human with authority + context to **override** — not a rubber stamp (cf. Part 40 §L abstain→escalate).
- **AC.3 Right to explanation.** The subject **MUST** be able to obtain a **meaningful explanation** of the logic, main factors, and evidence (Part 40 envelope + Part 32 drill-down) in plain language.
- **AC.4 Right to contest & appeal.** A documented **appeal/dispute** path **MUST** exist (human re-review, evidence package, audit trail §K); the outcome + rationale are recorded.
- **AC.5 Profiling transparency.** Subjects **MUST** be informed (Art 13/14, §W) that profiling occurs, its purpose + consequences + how to object; profiling of `minor` subjects is minimized and **never** used for advertising.
- **AC.6 EU AI Act high-risk obligations** (officiating/selection): risk-management system, data governance, technical documentation, logging, human oversight, accuracy/robustness/cybersecurity, and **post-market monitoring** — evidenced (§AB), not asserted.
- **AC.7 No proxy discrimination.** Decisions **MUST NOT** rely on protected-attribute proxies; fairness is a **release gate** (§AJ / Part 40 fairness).

## AD. Federated Identity & Enterprise SSO

Federations and academies are the buyers; they require enterprise identity. The hand-rolled JWT (§D) is the **scaffold**, not the enterprise contract.

- **AD.1 SSO.** The platform **MUST** support **OIDC** and **SAML 2.0** SSO so a federation's IdP owns authentication; local passwords are disabled for SSO-managed tenants.
- **AD.2 Provisioning.** **SCIM 2.0** user/group provisioning **+ de-provisioning** — a revoked staff member **MUST** lose access promptly (automated joiner/mover/leaver), not by manual cleanup.
- **AD.3 Role mapping.** IdP groups map to platform roles (§E) deterministically + audited; no privilege gain via self-asserted claims.
- **AD.4 Delegated / act-as access.** A coach acting for a player, or support acting for a tenant, **MUST** use explicit, time-boxed, **audited impersonation** (§K) — never shared credentials.
- **AD.5 Workload / service identity.** Inter-service calls (Part 13) **MUST** use **mTLS + workload identity** (e.g. SPIFFE/SVID) — no static service tokens; least-privilege per service (§B.2).
- **AD.6 API-key lifecycle.** Programmatic keys are **scoped** (tenant + capability), hashed at rest, **rotatable**, **revocable**, expiring, and listed with last-use; never embedded in distributed clients.

## AE. Authorization Architecture (PEP/PDP & Policy-as-Code)

- **AE.1 Decision point.** Authorization (RBAC + ABAC + field-level, §E) **SHOULD** be evaluated by a central **PDP** (policy decision point) with **PEPs** at each entry, so policy is consistent + testable — not scattered `if role ==` checks.
- **AE.2 Policy-as-code.** Policies **SHOULD** be code (e.g. **OPA/Rego** or **Cedar**), **version-controlled, reviewed, unit-tested**; a policy change is a tracked, audited deploy.
- **AE.3 Consent as an authorization input.** Access to `biometric`/`special`/`minor` data **MUST** be denied at the PDP when a **valid consent (§H) is absent or withdrawn** — consent gates access **programmatically**, not just as a record.
- **AE.4 Fail-closed + decision logging.** Authorization errors **default-deny**; sensitive-data denies **SHOULD** be logged (§K) for anomaly detection.

## AF. Application Security: Injection, Deserialization & File Safety

Concrete, code-level controls for **our** surface (uploads, model weights, media, storage keys).

- **AF.1 Model-weight deserialization is RCE.** Loading pretrained weights (Part 26) via `pickle`/`torch.load` **executes arbitrary code**. The platform **MUST** prefer **`safetensors`** (non-executable), verify **checksum + signature** (§Q.5), and load any unavoidable pickle **only** in a network-isolated sandbox (§N.2). Untrusted weights are **never** loaded in-process. ⬜ (gap — Part 26 reuse path).
- **AF.2 Path traversal.** Storage identifiers (`Video.storage_key`) and any path/key derived from input **MUST** be validated/canonicalized against an allow-listed prefix; `..` and absolute paths are rejected — never `open()` a client-influenced path directly. ⬜ (gap — concrete to the pipeline).
- **AF.3 Command injection.** Media tooling (ffmpeg/OpenCV) **MUST** be invoked with **argument arrays, never a shell string**; no input value reaches a shell; binaries are pinned.
- **AF.4 Decompression / pixel-flood bombs.** Uploads **MUST** cap decoded dimensions, duration, frame count, and output size; reject media that expands beyond limits (zip/video/image bombs) — a resource-exhaustion DoS.
- **AF.5 File validation.** Validate by **magic bytes** (not extension/MIME), reject **polyglots**, **transcode to a known-safe form** before use; strip/validate container metadata.
- **AF.6 SQL/NoSQL injection.** All DB access is **parameterized** (SQLAlchemy ORM ✅); raw SQL with string interpolation is forbidden.
- **AF.7 Log injection.** Untrusted values written to logs are sanitized of CR/LF/control chars to prevent log forging (§K.6).

## AG. Infrastructure, Cloud, Network & Container Security

- **AG.1 Zero-trust network.** Private subnets, **default-deny segmentation**, and **egress filtering** (a compromised worker can't call out freely — also an SSRF backstop, §N); service-to-service via mTLS (§AD.5).
- **AG.2 Containers / K8s.** **Image scanning** in CI, **admission control** (signed images only), **Pod Security Standards** (non-root, read-only FS, no privilege escalation, dropped caps), and **runtime** detection (e.g. Falco).
- **AG.3 Cloud posture (CSPM).** Continuous misconfiguration scanning; **no public buckets/objects**; least-privilege cloud IAM (no wildcard admin); encryption + logging on by default.
- **AG.4 Database hardening.** Per-service least-privilege DB users (no shared superuser), TLS connections, query/audit logging, and RLS (§F.3).
- **AG.5 DNS / TLS lifecycle.** Automated certificate issuance/rotation (ACME), **CAA** records, HSTS preload (§X); monitor for cert/DNS tampering.
- **AG.6 Backups.** **Immutable / object-lock (WORM)** backups with a **separate key/account**, tested restores, ransomware-resilient retention (§U.2).
- **AG.7 Bootstrapping (secret-zero).** The secrets-manager trust root (§Y) **MUST** use platform-native workload identity / instance attestation — no long-lived bootstrap secret in an image or repo.

## AH. Cyber-Physical Safety: Robots, Actuators & Wearables (Part 14)

When the platform drives **robots/actuators** or ingests **wearable** streams, security becomes **physical safety**.

- **AH.1 Actuator command authentication.** Every command to a ball-robot/actuator **MUST** be authenticated, integrity-protected, and **replay-protected** (nonce); an unauthenticated command path is a path to **physical harm**.
- **AH.2 Fail-safe.** Hardware **E-stop**, motion **rate/range/force limits**, watchdogs, and **safe-state on signal loss** are mandatory; software faults degrade to **stop**, never to uncontrolled motion.
- **AH.3 Physical-harm threat model.** Threat-model the cyber-physical path (spoofed command, hijacked session, malicious firmware) with **safety** (not just confidentiality) as the impact axis; humans-in-the-loop near moving equipment.
- **AH.4 Device attestation & firmware.** Robots/edge devices use **secure boot + signed firmware + attestation** (§V); revoke compromised devices.
- **AH.5 Continuous biometric/health streams.** Wearable health/biometric data (heart-rate, IMU, load) is `special`/`biometric` (§C): explicit consent for **continuous** capture, on-device minimization, encrypted transport, athlete control + withdrawal (§H).

## AI. Sport & Market Integrity

- **AI.1 Market-sensitive data.** Live **win-probability**, injury, lineup, and officiating data are **market-moving** (betting). Pre-/in-event predictive data **MUST** have **leak controls + an embargo** until publicly appropriate.
- **AI.2 Information barriers.** **Insider access** to predictive/officiating data is least-privilege + audited; staff trading/leaking on it is prohibited and monitored (§K anomaly).
- **AI.3 Manipulation detection.** Detect **betting-driven manipulation** and officiating anomalies (Part 15), coordinated with tamper-evident calls (§L).
- **AI.4 Anti-doping.** Anti-doping / medical integrations (WADA/ADAMS-style) handle restricted data with strict access, residency, and retention (§C/§W).
- **AI.5 Dispute & appeal integrity.** The officiating **appeal chain** (§AC.4) is itself tamper-evident: who challenged, what evidence, what changed — signed (§L).

## AJ. Privacy Engineering Depth

- **AJ.1 Controller vs Processor.** The platform's **legal role MUST be declared per relationship**: typically **controller** for its own direct users and **processor** for federation/club customers' athlete data. Processor obligations (process only on documented instructions, sub-processor approval + flow-down, assist with DSR/breach) and a **sub-processor register** are mandatory (§W).
- **AJ.2 International transfers.** Cross-border transfers **MUST** use a valid mechanism — **adequacy**, **SCCs**, or BCRs — backed by a **Transfer Impact Assessment**; region-pinned storage/processing where required (Part 15 residency).
- **AJ.3 Pseudonymization rigor.** Separate identifiers from observations where feasible; **pseudonymized ≠ anonymized**, and **biometric is non-anonymizable** (§B.9); **raw video itself re-identifies** (face/gait) and is `personal`/`biometric` even before embeddings.
- **AJ.4 Differential-privacy budget.** Published aggregates (§H.8) **MUST** track a **DP ε-budget** with governance — repeated queries erode privacy; the budget is finite + audited.
- **AJ.5 Machine unlearning (the hard one).** Erasure/withdrawal deletes rows + derived artifacts (§I.2), **but data already trained into model weights persists**. The platform **MUST** state its stance — exclude on a **retrain cadence**, support **approximate unlearning**, or rely on a **lawful basis that doesn't require deletion** — and **MUST NOT** claim an erasure it cannot perform (honesty, §B.5). ⬜ open problem (§AS).
- **AJ.6 Re-identification testing.** Before publishing "anonymized" datasets/aggregates, run a **re-identification / linkage-risk** assessment; biometric-derived data is treated as personal regardless.

## AK. Security SLOs, Metrics & Targets (quantitative)

A build spec is enforceable only if **measurable**. These are **default targets** (config, Part 34.AL; federations may tighten, never silently loosen) and act as gates (§Z/§AB) — the quantitative complement to the qualitative MUSTs above.

| Metric | Default target |
|--------|----------------|
| Vuln remediation — Critical (CVSS ≥ 9.0) | ≤ **24 h** |
| Vuln remediation — High / Medium / Low | ≤ **7 d** / **30 d** / **90 d** |
| Secret / key rotation | ≤ **90 d** (immediate on suspected compromise) |
| Access-token TTL · refresh-token TTL | ≤ **15 min** · ≤ **7–30 d** with rotation |
| Password KDF | **Argon2id** (≥ 19 MiB, t ≥ 2); interim PBKDF2 ≥ 600 k iters |
| MFA coverage — privileged roles (admin/umpire/medical) | **100 %** |
| MTTD · MTTR (contain) — security incident | ≤ **24 h** · ≤ **72 h** |
| Breach notification (regulator) | ≤ **72 h** (legal) |
| Backup **RPO** · **RTO** (officiating/medical tier tighter) | ≤ **24 h** · ≤ **8 h**; restore test **quarterly** |
| Penetration test | ≥ **annual** + on major change; bug-bounty continuous |
| Audit-log retention | ≥ **1 y** (officiating ≥ **7 y** / per rules); integrity verified continuously |
| Dependency + SBOM scan · secret scan | **every build** · **every push** (✅) |
| Access review — standard · privileged | **quarterly** · **monthly** |
| DSR response · acknowledge | ≤ **30 d** · ≤ **72 h** (GDPR) |
| Encryption coverage — `biometric`/`special` at rest | **100 %** (AES-256); transit **TLS 1.3** (min 1.2) |
| End-of-support components in prod | **zero** |

- **AK.1** Each target is a **gate**: a regression past it fails the security gate (§Z) or blocks release (§AB).
- **AK.2** Tightenings by a federation/tenant are config; **loosenings require a documented, owner-approved exception** (§AM.5).

## AL. Cryptographic Implementation Standards

- **AL.1 Don't roll your own crypto.** The scaffold's **hand-rolled HS256** (`backend/app/security.py`) + **PBKDF2** are acceptable for dev only; production **MUST** use **vetted, maintained libraries** — e.g. **PyJWT/Authlib** (JWT/JOSE), **`argon2-cffi`** (hashing), **`cryptography`** (primitives). Hand-rolled JOSE/KDF in prod is a defect. ⬜ (gap).
- **AL.2 Algorithm allow-list.** Approved: **TLS 1.3**, **AES-256-GCM**, **Argon2id**, **SHA-256/512**, **Ed25519 / ECDSA-P256 / RSA-2048+** (signing), **HMAC-SHA256**. Forbidden: MD5, SHA-1, DES/3DES, RC4, ECB, `alg=none` (§D.2).
- **AL.3 Crypto-agility.** Algorithm + key-id are recorded in provenance (§G.7) so primitives can be rotated/deprecated without ambiguity; a **post-quantum** migration is planned (§AS).
- **AL.4 Constant-time + CSPRNG.** Secret/MAC comparisons are constant-time (✅ `hmac.compare_digest`); all randomness is CSPRNG (§D.10).
- **AL.5 Key separation.** Distinct keys per purpose (token-signing ≠ data-encryption ≠ officiating-signing); the officiating key is HSM-isolated (§G.4).
- **AL.6 FIPS.** FIPS-140-validated modules where a federation/government customer requires them.

## AM. Security Governance, Roles & Ownership (RACI)

- **AM.1 Named owners.** A **security owner (CISO function)** and a **DPO** (mandatory for large-scale special-category processing, GDPR Art 37) are accountable, named roles — not "everyone".
- **AM.2 RACI.** Security-significant decisions carry an explicit RACI:

| Decision | R | A | C | I |
|----------|---|---|---|---|
| Vuln remediation / exception | eng owner | security owner | DPO (if data) | team |
| Incident response | on-call | security owner | legal/DPO | execs |
| Model→prod promotion (officiating/medical) | ML eng | security owner **+** domain expert (dual-control, §AP.3) | DPO | federation |
| DPIA sign-off (biometric) | privacy eng | DPO | security owner | legal |
| Access review | team lead | security owner | — | audit |

- **AM.3 Model-promotion is dual-control + signed** (§AP.3) for high-risk models — ties to the Art 22 human-accountability chain (§AC).
- **AM.4 Security champions** per team; **security in definition-of-done**; a **security-review gate** (`/security-review`) on security-relevant changes.
- **AM.5 Risk acceptance.** Any deviation from a MUST is a **documented, time-boxed, owner-approved exception** in the risk register (Part 36) — **never silent** (honesty, §B.5).

## AN. Vulnerability & Patch Management

- **AN.1 Discovery** is continuous: dependency scan (§S.2), image scan (§AG.2), DAST/pen-test (§AQ), bug-bounty (§AB).
- **AN.2 Remediation SLA by severity** (§AK) with a tracked owner per finding; no finding is unowned.
- **AN.3 EOL tracking.** No end-of-support runtime/dependency in prod (§AK); an upgrade roadmap is maintained.
- **AN.4 Exceptions** follow §AM.5 (time-boxed, compensating controls, expiry).
- **AN.5 Zero-day path.** Emergency patch + **virtual patching** (WAF) + feature **kill-switch** (§T.4).
- **AN.6 Supply-chain attacks.** Defend **dependency-confusion + typosquatting**: scoped/private registries, hash-pinned installs, namespace ownership (§AQ.3/§S.2).

## AO. Insider Threat & Data-Loss Prevention (DLP)

- **AO.1** Least privilege + JIT + separation of duties (§E.6) bound the blast radius of a malicious/compromised insider.
- **AO.2 Egress DLP.** Monitor + restrict **bulk export/download** of `biometric`/`special` data; alert on anomalous volume/time (§T.1).
- **AO.3 Attribution.** **Watermark/trace exports** (ties model-extraction §Q.2) so a leak is attributable to a principal.
- **AO.4 Information barriers** for market-sensitive data (§AI.2); privileged-user activity monitoring + non-repudiable audit (§K).
- **AO.5 Offboarding.** Joiner/mover/leaver automation (SCIM §AD.2): a revoked principal **promptly** loses tokens/keys/devices/sessions.
- **AO.6 Detection.** Honeytokens/canaries on sensitive stores to detect exfiltration early.

## AP. MLSecOps: Model Registry, Deployment & Promotion

- **AP.1 Registry access control.** Who can read/write/**promote** models is RBAC-governed + audited; training-data access is least-privilege (§C).
- **AP.2 Signed, provenanced models.** Every deployed model is **signed + checksum-verified**, carries a **model card** (Part 40) + training-data lineage; **unsigned models cannot deploy** (ties §Q.5 pretrained provenance, §AF.1 safetensors).
- **AP.3 Promotion authority.** High-risk models (officiating/medical) promote only via **dual-control, signed** approval (§AM.3) with **staged rollout + canary + instant rollback**.
- **AP.4 Pipeline integrity.** Secure the training/CI pipeline (least-priv runners, isolated data, reproducible builds); poisoning defenses (§Q.4).
- **AP.5 Feature/embedding-store security.** Biometric embeddings are access-controlled + encrypted (§C/§F); **no training on withdrawn-consent data** (§AE.3/§AJ.5).
- **AP.6 Post-deploy monitoring.** Drift/calibration (Part 40 §AJ) + abuse/extraction detection (§Q.2); a failed gate triggers rollback (§AM).

## AQ. Security Testing & Assurance Depth

- **AQ.1 Static + composition.** SAST + secret-scan (✅) + dependency/SBOM scan in CI (§S); **DAST** against running staging.
- **AQ.2 Fuzz the media/CV ingest.** Malformed-video fuzzing of the ffmpeg/OpenCV decode path is the **highest-risk untrusted-input surface** (§N/§AF); fuzz API request parsers too.
- **AQ.3 Malicious-package checks** — dependency-confusion/typosquat (§AN.6).
- **AQ.4 Offensive + drills.** Pen-test ≥ annual + on major change; **red-team** exercises; IR **tabletop** drills (§T); cadence per §AK.
- **AQ.5 ML/LLM adversarial testing.** Evasion testing (§Q.1) + LLM jailbreak/prompt-injection testing (§R.5) are **release gates**.
- **AQ.6 Privacy testing.** Verify DSR flows, **erasure actually deletes** (incl. derivatives), consent-gate enforcement (§AE.3), and re-identification risk (§AJ.6).

## AR. Operational Hardening Miscellany

- **AR.1 Secure decommissioning.** Crypto-shred keys; sanitize/destroy media per **NIST 800-88**; verify before disposal/return.
- **AR.2 Platform email authenticity.** **SPF + DKIM + DMARC (reject)** to stop phishing that impersonates the platform (reset links, notifications).
- **AR.3 Session management.** Idle + absolute timeouts, concurrent-session limits, **"log out everywhere"**, revoke-on-suspicion (§D/§M).
- **AR.4 Accessibility of security.** Auth/MFA/consent flows usable by para-athletes + assistive tech (Part 24) — security **MUST NOT** exclude.
- **AR.5 Forensic readiness.** Centralized, time-synced (§L.4), tamper-evident logs (§K) retained for investigation; incident evidence chain-of-custody.
- **AR.6 Residency mechanics.** Region-pinned tenants + in-region keys/processing where required (§AJ.2 / Part 15); maintain data-flow maps.
- **AR.7 Risk-register linkage.** Each §P threat carries **likelihood × impact + residual risk** in the Part 36 register, reviewed on change.

## AS. Open Problems & Roadmap (honest)

- **Biometric anonymization is impossible** (§B.9) — manage via consent + minimization + DP aggregates, not de-identification.
- **Adversarial robustness of officiating** (§Q.1) is unsolved in general — abstain + human oversight (§L.5) until robustness evidence exists.
- **Cross-border residency** for global federations is operationally hard — region-pinned storage + processing is the roadmap.
- **Minors at scale** — guardian-consent verification and age-appropriate design across academies need product + legal investment.
- **Privacy vs accuracy** (edge-private mode reduces central training data) — on-device/federated learning is the long-term answer.
- **Machine unlearning** (§AJ.5) — removing a withdrawn subject's influence from trained weights is unsolved at low cost; retrain-cadence + approximate unlearning is the roadmap; never claim erasure we can't perform.
- **Post-quantum cryptography** — current TLS/signatures (§G) are not quantum-safe; crypto-agility (§G.7) is the bridge, a PQC migration the destination (long-term).
- **Market-integrity vs utility** (§AI) — coaches want live win-probability; betting markets want it too. Embargo/leak-control trades product value for integrity; the boundary needs federation policy.

---

## AT. Security Glossary & Notation

Canonical via Part 38 where applicable: **RBAC** (role-based) / **ABAC** (attribute-based) access control · **PEP/PDP** (policy enforcement/decision point) · **policy-as-code** (OPA/Rego, Cedar) · **IDOR** (insecure direct object reference) · **SSRF** (server-side request forgery) · **RLS** (row-level security) · **SSO / OIDC / SAML** · **SCIM** (provisioning) · **SPIFFE/SVID · mTLS** (workload identity) · **MFA / WebAuthn / passkeys / FIDO2** · **KDF / Argon2id / PBKDF2** · **KMS / HSM / envelope encryption · CSPRNG** · **safetensors** (non-executable weights) · **CRLF** (log-injection vector) · **DPIA** (data-protection impact assessment) · **DSR / DSAR** (data-subject (access) request) · **ROPA** (records of processing) · **RTBF** (right to be forgotten) · **controller / processor** (GDPR roles) · **SCC / TIA** (transfer clauses / impact assessment) · **Art 22** (automated-decision rights) · **DP / ε-budget** (differential privacy) · **CSPM** (cloud security posture) · **WORM / object-lock** (immutable backups) · **E-stop** (cyber-physical fail-safe) · **BIPA** (Illinois biometric law) · **ASVS** (OWASP app-sec verification standard) · **SBOM** (software bill of materials) · **ATO** (account takeover) · **break-glass** (audited emergency access) · **SLO/SLA** (service-level objective/agreement) · **RPO/RTO** (recovery point/time objective) · **MTTD/MTTR** (mean time to detect/respond) · **RACI** (responsible/accountable/consulted/informed) · **CISO/DPO** (security/data-protection officer) · **SAST/DAST/IAST** (static/dynamic/interactive app-sec testing) · **fuzzing** (malformed-input testing) · **dependency-confusion / typosquatting** (supply-chain attacks) · **DLP** (data-loss prevention) · **MLSecOps** (ML security operations) · **canary/honeytoken** (exfiltration tripwire) · **NIST 800-88** (media sanitization) · **SPF/DKIM/DMARC** (email authentication) · **FIPS-140** (crypto-module validation) · **class:`biometric|special|minor|personal|operational|secret`** (data classes, §C). Data classes **SHOULD** be added to `i18n/glossary.json` (Part 38) as canonical ids.

This document is the authoritative security, privacy & compliance law for TT-OS; with the data model (37), ontology (38), event contract (39), and reliability law (40), it forms the trust core of the platform's build foundation — **structure, meaning, communication, honesty, and trust.** Part 42 adds the sixth pillar — **operability** (observability, SRE & operations).

---

➡️ **NEXT FILE: `42_OBSERVABILITY_SRE_AND_OPERATIONS.md`**
