# TT-OS backend (P0 scaffold)

A minimal FastAPI service implementing the start of `api/openapi.yaml` against the
data model in `schema/schema.sql` (MASTER_SPEC Part 27). Ships a working
`/healthz`, stub auth, and `players` CRUD — enough to prove the contract runs.

> Dev/test uses **SQLite** (zero setup). Production uses **Postgres** (`schema/schema.sql`).

## Run
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head          # create/upgrade the schema (DATABASE_URL)
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/healthz   and   /docs (Swagger UI)
```

## Migrations (Alembic)
```bash
alembic upgrade head                      # apply
alembic revision -m "add videos"          # new migration (then edit it)
alembic downgrade -1                       # roll back one
```
Migrations are the source of truth for the schema; the ORM models in `app/models.py`
mirror them and will grow to match `schema/schema.sql` as features land.

## Test
```bash
cd backend
pytest -q
```

## Auth (JWT + RBAC)
```bash
# register (creates an org + user), then login for a bearer token:
curl -X POST localhost:8000/v1/auth/register -d '{"email":"c@x.com","password":"pw","role":"coach"}' -H 'content-type: application/json'
TOKEN=$(curl -s -X POST localhost:8000/v1/auth/login -d '{"email":"c@x.com","password":"pw"}' -H 'content-type: application/json' | jq -r .access_token)
curl localhost:8000/v1/players -H "Authorization: Bearer $TOKEN"
```
Writes to `/v1/players` require role `admin` or `coach` (others get 403); reads need any valid token (else 401).

## What's here vs next
**Phase 1 (done):** Alembic migrations · JWT auth + RBAC · players CRUD · video upload +
analysis worker (real OpenCV ball detection → rallies/shots/events) · player profiles →
opponent dossiers → matchups → game plans (rule-based, Part 21).
**Phase 2 (in progress):** scoreboard OCR (7-segment, free ground truth) · markerless
spin estimation (Magnus/curvature) · benchmark harness + golden-set gate (`python -m app.benchmark`).
**Next:** swap the OpenCV baseline for a deep detector (TTNet/TrackNet/YOLO — Part 26) behind
the same `BallDetector`; move the worker to a GPU queue; real spin via SpinDOE; 3D (multi-cam).

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
