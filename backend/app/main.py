from fastapi import FastAPI

from .config import settings
from .routers import (
    auth,
    health,
    matches,
    matchups,
    players,
    profiles,
    videos,
)


def create_app() -> FastAPI:
    # Schema is owned by Alembic migrations — run `alembic upgrade head` before serving.
    # (Tests create tables on an isolated in-memory engine in conftest.)
    app = FastAPI(title="TT-OS API", version="0.1.0")
    app.include_router(health.router)  # /healthz (unprefixed)
    for r in (auth, players, videos, matches, profiles, matchups):
        app.include_router(r.router, prefix=settings.api_prefix)
    return app


app = create_app()
