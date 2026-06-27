# PART 31 — SECURITY, PRIVACY & THREAT MODEL

> Read `00_INDEX.md` first. The platform holds athletes' **video, biometric, and health** data — much of it for **minors**. This is the security/privacy contract. It extends Part 13 (auth/RBAC/tenancy) and Part 15 (consent/safeguarding), and maps to what the backend already enforces.

## A. Data classification
| Class | Examples | Handling |
|-------|----------|----------|
| **Biometric (highest)** | face/body/style embeddings, gait | explicit consent, separate store, deletable |
| **Sensitive personal** | health/injury, medical, minors' data | consent + purpose-limited + retention limits |
| **Personal** | name, DOB, nationality, video | tenant-scoped, access-controlled |
| **Operational** | match stats, models, logs | internal; audit-logged |

## B. AuthN / AuthZ (what's implemented + required)
- **AuthN:** JWT bearer (✅ `backend/app/security.py`) + hashed API keys (schema). Rotate `JWT_SECRET`; short token TTL; refresh-token rotation (deferred).
- **AuthZ / RBAC:** roles `admin/coach/player/umpire/medical/scout` (✅ `require_roles`); **least privilege** (e.g. players read-only on rosters; medical sees health, not tactics by default).
- **Object-level checks:** every query is **org-scoped** (✅) and ownership-checked; never trust client IDs.

## C. Multi-tenancy isolation
- `org_id` on every row (✅) + **Postgres Row-Level Security** policies (deferred — enforce at DB, not just app).
- Per-tenant storage prefixes; no cross-tenant joins; tenant id derived from the token, never the request body.

## D. Data protection
- **In transit:** TLS everywhere. **At rest:** encrypted DB + object storage; encrypted backups.
- **Secrets:** a secrets manager (not env files in prod); key rotation; no secrets in logs/repo.
- **Video/artifacts:** signed, expiring URLs; private buckets.

## E. Privacy & consent (minors / GDPR)
- **Consent records** (✅ `consents` table) incl. **guardian consent** for minors; purpose limitation.
- **Retention** policy per tenant (`organizations.settings`); scheduled deletion.
- **Right to be forgotten:** cascading delete + embedding/artifact purge.
- **Data minimisation:** keep only what a feature needs.
- **Bystander privacy:** blur spectator/minor faces in background (Part 15).
- **Edge-private mode:** option where video never leaves the venue (Part 15).

## F. Biometric data — special handling
Face/body/style/gait embeddings are **biometric identifiers** → explicit, separate consent; stored apart (vector DB) with their own access policy and deletion path; never shared cross-tenant.

## G. Threat model (STRIDE + ML/sport-specific)
| Threat | Vector | Mitigation |
|--------|--------|-----------|
| **Spoofing** | stolen token | short TTL, rotation, key-hashed API keys, MFA for admins |
| **Tampering** | altered results/scores | audit_log (✅), integrity checks, signed artifacts |
| **Repudiation** | "I didn't make that call" | append-only `audit_log` + evidence packages (Part 09) |
| **Info disclosure** | cross-tenant leak | RBAC + RLS + tenant-scoped queries + encryption |
| **DoS** | upload flood, heavy jobs | rate limiting (`429`), quotas, job queue backpressure |
| **Elevation** | role bypass | server-side RBAC (✅), deny-by-default |
| **Untrusted uploads** | malicious video file | process in a **sandboxed worker**, resource limits, validate/transcode |
| **Model extraction / poisoning** | scraping outputs / bad labels | rate limits, watermarking; annotation IAA gate (Part 30) |
| **Match-fixing / integrity** | manipulated officiating | anomaly detection (Part 15), tamper-evident logs |
| **Prompt injection** | malicious text into the LLM layer | the grounded-LLM Q&A (Part 11) treats retrieved/user text as untrusted; tool/output allow-lists |

## H. Officiating defensibility
Every decisive call is **reproducible** (Part 13.4), carries a **model card** + **evidence package** (Part 09/10), and is written to a tamper-evident audit trail — so a contested call can be independently reviewed.

## I. Operational security
Dependency + secret scanning and SAST in CI · centralised logging/monitoring/alerting · incident-response runbook · least-privilege infra (IAM) · backups + tested disaster recovery.

## J. Compliance
GDPR (EU athletes) · child-safeguarding policy (academies) · anti-doping data handling · regional **data residency** for federations · documented DPIA for biometric processing.

## K. Status vs backend today
- ✅ JWT, RBAC, org-scoping, `consents`, `audit_log`, archive/soft-delete, `429` schema.
- ⬜ Deferred (pre-production): RLS policies, encryption-at-rest config, secrets manager, rate-limit enforcement, refresh-token rotation, upload sandboxing, face blurring.

---

➡️ **NEXT FILE: `32_PRODUCT_UX_AND_USER_JOURNEYS.md`**
