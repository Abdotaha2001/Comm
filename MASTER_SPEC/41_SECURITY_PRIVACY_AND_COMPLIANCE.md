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

### A.3 Non-goals
- Not the data model (Part 37) — it **classifies** Part 37's fields and constrains their access.
- Not the event contract (Part 39) — it **consumes** Part 39's audit/outbox machinery for tamper-evident logging.
- Not the reliability law (Part 40) — it **binds** Part 40's officiating reproducibility + abstention to non-repudiation.
- Not federation organizational governance (Part 15) — it is the **technical** security/privacy contract.

### A.4 Relationship to Parts
Formalizes Part 31; extends Part 13 (auth/RBAC/tenancy) and Part 15 (consent/safeguarding); classifies Part 37 fields; uses Part 39 §L (immutable audit events) + the transactional outbox; binds Part 40 §BO (reliability-incident response) + officiating reproducibility; consumes Part 35 provenance/tamper-evidence (capture chain-of-custody); tags data classes as canonical ids in Part 38; ties risks to Part 36.

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
- **H.8 Published aggregates** (leaderboards, research stats) **MUST** apply **differential privacy** / k-anonymity so individuals can't be re-identified.

---

## I. Data-Subject Rights (DSR) & Data Lifecycle

- **I.1 Rights with SLAs.** Support **access, rectification, portability (export), erasure, objection, restriction** with documented SLAs and an authenticated, audited workflow.
- **I.2 Right to be forgotten** = cascading delete of source + **all** derived data (profiles, dossiers, embeddings, cached artifacts, search indexes) + **crypto-erase** of encrypted copies where deletion is impractical.
- **I.3 No orphan derivatives.** Erasure/withdrawal **MUST** purge derivatives; a derivative that outlives its source consent is a breach (§H.5).
- **I.4 Retention.** Per-tenant retention policy with **scheduled deletion**; `operational` events tier to cold/cheap storage then expire (Part 39 §AI). Soft-delete (`deleted_at`, Part 37) is **not** erasure — a hard-delete + crypto-erase path **MUST** back RTBF.
- **I.5 Records.** Maintain a **ROPA** (records of processing) and a **DPIA** for biometric processing (mandatory, §W).
- **I.6 Export format** for portability **MUST** be machine-readable (JSON) and exclude other subjects' data.

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

---

## L. Officiating Integrity (cryptographic, high-stakes)

- **L.1 Reproducibility.** Every decisive call **MUST** be reproducible from provenance (model + code_sha + inputs + seed, Part 40 §J/§BP) and carry a **model card** + **evidence package** (Part 09/40).
- **L.2 Signature + trusted timestamp.** Each decisive decision **MUST** be **signed with an HSM key** (§G.4) and bound to a **trusted timestamp** → non-repudiation + tamper-evidence.
- **L.3 Chain-of-custody.** Evidence packages (clips, frames, tracks) carry an unbroken custody chain from capture (Part 35 provenance hash) to decision.
- **L.4 Clock integrity.** **NTP/clock integrity** is a security control — a manipulated clock breaks timing-based calls and timestamps; drift is monitored.
- **L.5 Human oversight.** Decisive calls are **advisory until validated** (Part 40 §K) and surface an **abstain → escalate-to-umpire** path; the system never silently forces a call it cannot defend.
- **L.6 EU AI Act alignment.** Officiating/selection are likely **high-risk AI** (§W): risk management, logging, human oversight, transparency, and accuracy/robustness evidence are **mandatory** before such features ship.

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
| **EU AI Act** | officiating / talent selection = likely **high-risk** | risk mgmt, logging, **human oversight** (§L.5), transparency, accuracy/robustness evidence (§Q) |
| **Anti-doping data** | federation integrations | restricted handling + residency |
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

This table is the **truth** of where security stands today: a sound auth/RBAC/tenant/secret-scan core (✅), with the privacy-record, tamper-evidence, encryption-config, and abuse-protection layers **specified and tracked** (⬜) — production-blocking, not optional.

---

## AB. Acceptance & Assurance

- **AB.1** Target **OWASP ASVS** level (L2 for app, L3 for officiating/medical paths); map controls to ASVS + Top-10.
- **AB.2 Penetration test + bug-bounty** before any federation rollout; findings tracked to closure.
- **AB.3** Pursue **SOC 2 / ISO 27001**; continuous compliance monitoring; staff/coach **security-awareness training**.
- **AB.4** Public **vulnerability-disclosure policy** (`security.txt`) + responsible-disclosure process.
- **AB.5** A release that regresses a §Z invariant or a ✅ in §AA is **blocked**.

---

## AC. Open Problems & Roadmap (honest)

- **Biometric anonymization is impossible** (§B.9) — manage via consent + minimization + DP aggregates, not de-identification.
- **Adversarial robustness of officiating** (§Q.1) is unsolved in general — abstain + human oversight (§L.5) until robustness evidence exists.
- **Cross-border residency** for global federations is operationally hard — region-pinned storage + processing is the roadmap.
- **Minors at scale** — guardian-consent verification and age-appropriate design across academies need product + legal investment.
- **Privacy vs accuracy** (edge-private mode reduces central training data) — on-device/federated learning is the long-term answer.

---

## AD. Security Glossary & Notation

Canonical via Part 38 where applicable: **RBAC** (role-based) / **ABAC** (attribute-based) access control · **IDOR** (insecure direct object reference) · **SSRF** (server-side request forgery) · **RLS** (row-level security) · **MFA / WebAuthn / passkeys / FIDO2** · **KDF / Argon2id / PBKDF2** · **KMS / HSM / envelope encryption** · **DPIA** (data-protection impact assessment) · **DSR / DSAR** (data-subject (access) request) · **ROPA** (records of processing) · **RTBF** (right to be forgotten) · **DP** (differential privacy) · **BIPA** (Illinois biometric law) · **ASVS** (OWASP app-sec verification standard) · **SBOM** (software bill of materials) · **ATO** (account takeover) · **break-glass** (audited emergency access) · **class:`biometric|special|minor|personal|operational|secret`** (data classes, §C). Data classes **SHOULD** be added to `i18n/glossary.json` (Part 38) as canonical ids.

This document is the authoritative security, privacy & compliance law for TT-OS; with the data model (37), ontology (38), event contract (39), and reliability law (40), it completes the platform's build foundation — **structure, meaning, communication, honesty, and trust.**

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
