def test_create_get_list_player(client, coach_headers):
    r = client.post(
        "/v1/players",
        headers=coach_headers,
        json={
            "full_name": "Ahmed",
            "type": "junior",
            "handedness": "left",
            "grip": "penhold_chinese",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    pid = body["id"]
    assert body["full_name"] == "Ahmed"
    assert body["handedness"] == "left"
    assert body["status"] == "active"

    assert client.get(f"/v1/players/{pid}", headers=coach_headers).status_code == 200
    listing = client.get("/v1/players", headers=coach_headers).json()
    assert len(listing) == 1


def test_assign_disability_then_archive(client, coach_headers):
    pid = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "Sara"}
    ).json()["id"]

    patched = client.patch(
        f"/v1/players/{pid}",
        headers=coach_headers,
        json={
            "para_class": 5,
            "mobility_mode": "wheelchair",
            "impairment_type": "limb_deficiency",
        },
    )
    assert patched.status_code == 200
    assert patched.json()["para_class"] == 5
    assert patched.json()["mobility_mode"] == "wheelchair"

    assert client.delete(f"/v1/players/{pid}", headers=coach_headers).status_code == 204
    assert client.get("/v1/players", headers=coach_headers).json() == []
    assert client.get(f"/v1/players/{pid}", headers=coach_headers).status_code == 200


def test_invalid_enum_rejected(client, coach_headers):
    r = client.post(
        "/v1/players",
        headers=coach_headers,
        json={"full_name": "X", "handedness": "sideways"},
    )
    assert r.status_code == 422


def test_para_class_out_of_range_rejected(client, coach_headers):
    r = client.post(
        "/v1/players", headers=coach_headers, json={"full_name": "X", "para_class": 12}
    )
    assert r.status_code == 422


def test_missing_player_404(client, coach_headers):
    assert (
        client.get("/v1/players/does-not-exist", headers=coach_headers).status_code
        == 404
    )


def test_players_require_auth(client):
    # No bearer token → 401
    assert client.get("/v1/players").status_code == 401
    assert client.post("/v1/players", json={"full_name": "X"}).status_code == 401
