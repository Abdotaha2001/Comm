# TT-OS backend (P0 scaffold)

A minimal FastAPI service implementing the start of `api/openapi.yaml` against the
data model in `schema/schema.sql` (MASTER_SPEC Part 27). Ships a working
`/healthz`, stub auth, and `players` CRUD — enough to prove the contract runs.

> Dev/test uses **SQLite** (zero setup). Production uses **Postgres** (`schema/schema.sql`).

## Run
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/healthz   and   /docs (Swagger UI)
```

## Test
```bash
cd backend
pytest -q
```

## What's here vs next
- ✅ `/healthz`, `/v1/auth/login` (stub), `/v1/auth/me`, `/v1/players` CRUD (+ archive), enum validation.
- ⬜ Next: Alembic migrations from `schema/schema.sql`, real JWT auth + RBAC, videos/analysis worker,
  profiles, opponents, matchups, game-plan (BUILD_ORDER Phase 1).

## Layout
```
app/
  config.py      settings (DATABASE_URL, api prefix)
  db.py          SQLAlchemy engine/session + Base
  models.py      ORM (organizations, users, players)
  schemas.py     Pydantic I/O (enums grounded in Part 28)
  deps.py        DB session + current-org (stub auth)
  main.py        app factory + router wiring
  routers/       health, auth, players
tests/           pytest (SQLite in-memory)
```
