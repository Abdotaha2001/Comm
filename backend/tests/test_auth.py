def test_register_login_me(client):
    r = client.post(
        "/v1/auth/register",
        json={"email": "a@x.com", "password": "secret", "role": "coach"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "a@x.com"

    tok = client.post(
        "/v1/auth/login", json={"email": "a@x.com", "password": "secret"}
    ).json()["access_token"]
    me = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert me.status_code == 200
    assert me.json()["role"] == "coach"


def test_login_wrong_password(client):
    client.post("/v1/auth/register", json={"email": "b@x.com", "password": "pw"})
    r = client.post("/v1/auth/login", json={"email": "b@x.com", "password": "nope"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/v1/auth/me").status_code == 401


def test_invalid_token_rejected(client):
    r = client.get("/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401
