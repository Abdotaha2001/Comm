from fastapi import FastAPI

from .config import settings
from .db import Base, engine
from .routers import auth, health, players


def create_app() -> FastAPI:
    # Skeleton: create tables directly. Production uses schema/schema.sql + Alembic.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="TT-OS API", version="0.1.0")
    app.include_router(health.router)  # /healthz (unprefixed)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(players.router, prefix=settings.api_prefix)
    return app


app = create_app()
