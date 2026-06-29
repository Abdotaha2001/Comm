def test_player_role_cannot_write_but_can_read(client, player_headers):
    # role=player → forbidden to create
    r = client.post("/v1/players", headers=player_headers, json={"full_name": "X"})
    assert r.status_code == 403
    # but reading is allowed for any authenticated user
    assert client.get("/v1/players", headers=player_headers).status_code == 200


def test_coach_role_can_write(client, coach_headers):
    r = client.post("/v1/players", headers=coach_headers, json={"full_name": "Y"})
    assert r.status_code == 201
