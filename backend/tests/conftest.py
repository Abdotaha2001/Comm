import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.db import Base, get_db


@pytest.fixture()
def client():
    # Shared in-memory SQLite across all sessions in the test (StaticPool).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


def _register_login(client, email, password, role):
    client.post(
        "/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    tok = client.post(
        "/v1/auth/login", json={"email": email, "password": password}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture()
def coach_headers(client):
    return _register_login(client, "coach@x.com", "pw", "coach")


@pytest.fixture()
def player_headers(client):
    return _register_login(client, "player@x.com", "pw", "player")
