def test_create_get_list_player(client):
    r = client.post(
        "/v1/players",
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

    assert client.get(f"/v1/players/{pid}").status_code == 200
    listing = client.get("/v1/players").json()
    assert len(listing) == 1


def test_assign_disability_then_archive(client):
    pid = client.post("/v1/players", json={"full_name": "Sara"}).json()["id"]

    patched = client.patch(
        f"/v1/players/{pid}",
        json={
            "para_class": 5,
            "mobility_mode": "wheelchair",
            "impairment_type": "limb_deficiency",
        },
    )
    assert patched.status_code == 200
    assert patched.json()["para_class"] == 5
    assert patched.json()["mobility_mode"] == "wheelchair"

    assert client.delete(f"/v1/players/{pid}").status_code == 204
    # archived players drop out of the active listing
    assert client.get("/v1/players").json() == []
    assert client.get(f"/v1/players/{pid}").status_code == 200  # still fetchable by id


def test_invalid_enum_rejected(client):
    r = client.post("/v1/players", json={"full_name": "X", "handedness": "sideways"})
    assert r.status_code == 422


def test_para_class_out_of_range_rejected(client):
    r = client.post("/v1/players", json={"full_name": "X", "para_class": 12})
    assert r.status_code == 422


def test_missing_player_404(client):
    assert client.get("/v1/players/does-not-exist").status_code == 404
