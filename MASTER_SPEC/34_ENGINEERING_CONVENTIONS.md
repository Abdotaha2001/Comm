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

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
