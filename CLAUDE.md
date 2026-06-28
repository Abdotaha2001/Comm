# CLAUDE.md — codebase guide

TT-OS: an AI table tennis platform. This file orients any contributor (human or AI)
fast. Full design lives in `MASTER_SPEC/` (read `MASTER_SPEC/00_INDEX.md` first);
detailed conventions in `MASTER_SPEC/34_ENGINEERING_CONVENTIONS.md`.

## Repo map
| Path | What |
|------|------|
| `MASTER_SPEC/` | The spec (00–34, chained). The "what & why". |
| `PROJECT_PLAN.md` · `BUILD_ORDER.md` | Phased plan + execution order. |
| `i18n/` | Controlled glossary (`glossary.json` → `en.json`/`ar.json` via `build.py`). |
| `schema/schema.sql` · `api/openapi.yaml` | Data model + API contract (Part 27). |
| `backend/` | Running FastAPI service (the built MVP). |

## Backend quick start
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head            # schema (SQLite dev by default; Postgres in prod)
uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs
pytest                          # all tests
python -m app.benchmark         # accuracy harness (golden-set gate)
```

## Backend at a glance
- **Auth:** JWT + RBAC (`app/security.py`, `app/deps.py`). Writes need `admin|coach`.
- **Flow:** register → player → upload video → analyze (real OpenCV CV) → profile → opponent → matchup → game plan.
- **CV:** pluggable `BallDetector` (`app/cv/`); deep models (TTNet/YOLO — Part 26) drop in. Scoreboard OCR + spin estimation included.
- **Intelligence:** `app/analytics/` (rule-based, grounded in Part 21; LLM later).
- **Capture acceptance:** `app/capture_quality.py` — schema-driven CQS + certification gates (min, no averaging), reliability envelope + provenance (Part 35; SoT in `MASTER_SPEC/35_CAPTURE_ACCEPTANCE_SCHEMA.json`).
- **DB:** Alembic owns the schema (`migrations/`); ORM in `app/models.py` mirrors it.

## How to add things (the common cases)
- **New API endpoint:** router in `app/routers/` + Pydantic schema in `app/schemas.py` + a test. Org-scope the query; add RBAC dep for writes.
- **New DB table/column:** edit `app/models.py` **and** add an Alembic migration (`alembic revision -m "..."`). Never rely on `create_all` in prod.
- **New CV detector/model:** implement the `BallDetector` interface (`app/cv/detector.py`); register it; add a benchmark.
- **New term:** add to `i18n/glossary.json` (a `canonical_id`), run `python i18n/build.py`. Never hard-code display strings.

## Non-negotiables
- Every measured value carries **confidence + provenance**; honest "preliminary"/abstain when thin (Part 10).
- Every query is **org-scoped**; RBAC is **deny-by-default**.
- Accuracy changes must keep the **golden-set gate** green (`tests/test_benchmark.py`).
- Conventions in `MASTER_SPEC/34_ENGINEERING_CONVENTIONS.md` — follow them.
