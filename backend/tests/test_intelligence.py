from app.models import AnalysisRun, Match, Rally, Shot, Video


def _seed_shots(db, org_id, player_id, n=12, all_fh=False, speed=50.0):
    v = Video(org_id=org_id, player_id=player_id, source="upload",
              storage_key="x", status="done")
    db.add(v)
    db.flush()
    run = AnalysisRun(video_id=v.id, status="done")
    db.add(run)
    db.flush()
    m = Match(analysis_run_id=run.id, video_id=v.id, player1_id=player_id)
    db.add(m)
    db.flush()
    r = Rally(match_id=m.id, idx=0, duration_sec=5.0)
    db.add(r)
    db.flush()
    for i in range(n):
        wing = "fh" if all_fh else ("fh" if i % 2 == 0 else "bh")
        db.add(Shot(rally_id=r.id, idx=i, stroke_type="drive", wing=wing,
                    speed_kmh=speed, confidence=0.8))
    db.commit()


def test_full_flagship_loop(client, db, coach_headers):
    a = client.post("/v1/players", headers=coach_headers, json={"full_name": "MyPlayer"}).json()
    b = client.post("/v1/players", headers=coach_headers, json={"full_name": "Opponent"}).json()
    org_id = a["org_id"]

    _seed_shots(db, org_id, a["id"], n=12, speed=55.0)         # fast attacker
    _seed_shots(db, org_id, b["id"], n=12, all_fh=True, speed=30.0)  # FH-over-reliant

    # 1) rebuild my profile
    prof = client.post(f"/v1/players/{a['id']}/profile/rebuild", headers=coach_headers)
    assert prof.status_code == 201, prof.text
    assert prof.json()["style_class"]
    assert prof.json()["strengths"]
    assert client.get(f"/v1/players/{a['id']}/profile", headers=coach_headers).status_code == 200

    # 2) opponent dossier (from in-system player B)
    dossier = client.post("/v1/opponents", headers=coach_headers,
                          json={"subject_player_id": a["id"], "opponent_player_id": b["id"]})
    assert dossier.status_code == 201, dossier.text
    dj = dossier.json()
    assert dj["footage_count"] == 1
    assert dj["style_class"]

    # 3) matchup
    mu = client.post("/v1/matchups", headers=coach_headers,
                     json={"my_player_id": a["id"], "opponent_dossier_id": dj["id"]})
    assert mu.status_code == 201, mu.text
    wp = mu.json()["predicted_winprob"]
    assert 0.15 <= wp <= 0.85

    # 4) game plan
    gp = client.post(f"/v1/matchups/{mu.json()['id']}/game-plan", headers=coach_headers)
    assert gp.status_code == 201, gp.text
    plan = gp.json()["plan"]
    assert "serve" in plan and "receive" in plan and "placement" in plan
    assert gp.json()["training_block"]
    # B is FH-over-reliant -> exploit should mention it
    assert any("Forehand" in e.get("text", "") for e in plan["exploit"])
    assert gp.json()["data_note"]


def test_gameplan_requires_coach(client, player_headers):
    r = client.post("/v1/matchups/none/game-plan", headers=player_headers)
    assert r.status_code == 403
