from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..analytics.gameplan import generate_plan
from ..analytics.matchup import build_matchup
from ..analytics.opponent import build_dossier
from ..analytics.profile import aggregate_profile
from ..db import get_db
from ..deps import get_current_org, require_roles
from ..models import GamePlan, Matchup, OpponentDossier, Organization, Player
from ..schemas import (
    GamePlanRead,
    MatchupCreate,
    MatchupRead,
    OpponentCreate,
    OpponentRead,
)

router = APIRouter(tags=["matchups"])
WRITE = [Depends(require_roles("admin", "coach"))]


def _check_player(pid, db, org):
    if pid and not db.query(Player).filter(Player.id == pid, Player.org_id == org.id).first():
        raise HTTPException(status_code=404, detail=f"player {pid} not found")


@router.post("/opponents", response_model=OpponentRead, status_code=201, dependencies=WRITE)
def create_opponent(
    body: OpponentCreate,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    _check_player(body.subject_player_id, db, org)
    _check_player(body.opponent_player_id, db, org)
    d = build_dossier(
        db, org.id, body.subject_player_id,
        opponent_player_id=body.opponent_player_id,
        opponent_ref=body.opponent_ref, video_ids=body.video_ids,
    )
    dossier = OpponentDossier(
        org_id=org.id, subject_player_id=body.subject_player_id,
        opponent_player_id=body.opponent_player_id, opponent_ref=body.opponent_ref,
        footage_count=d["footage_count"], style_class=d["style_class"],
        summary=d["summary"], confidence=d["confidence"],
    )
    db.add(dossier)
    db.commit()
    db.refresh(dossier)
    return dossier


@router.get("/opponents/{did}", response_model=OpponentRead)
def get_opponent(did: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_org)):
    d = db.query(OpponentDossier).filter(OpponentDossier.id == did, OpponentDossier.org_id == org.id).first()
    if d is None:
        raise HTTPException(status_code=404, detail="dossier not found")
    return d


@router.post("/matchups", response_model=MatchupRead, status_code=201, dependencies=WRITE)
def create_matchup(
    body: MatchupCreate,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    _check_player(body.my_player_id, db, org)
    dossier = db.query(OpponentDossier).filter(
        OpponentDossier.id == body.opponent_dossier_id, OpponentDossier.org_id == org.id
    ).first()
    if dossier is None:
        raise HTTPException(status_code=404, detail="opponent dossier not found")

    d = {"style_class": dossier.style_class, "summary": dossier.summary, "confidence": dossier.confidence}
    m = build_matchup(db, org.id, body.my_player_id, d)
    matchup = Matchup(
        org_id=org.id, my_player_id=body.my_player_id, opponent_dossier_id=dossier.id,
        h2h=m["h2h"], predicted_winprob=m["predicted_winprob"], confidence=m["confidence"],
    )
    db.add(matchup)
    db.commit()
    db.refresh(matchup)
    return matchup


@router.get("/matchups/{mid}", response_model=MatchupRead)
def get_matchup(mid: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_org)):
    m = db.query(Matchup).filter(Matchup.id == mid, Matchup.org_id == org.id).first()
    if m is None:
        raise HTTPException(status_code=404, detail="matchup not found")
    return m


@router.post("/matchups/{mid}/game-plan", response_model=GamePlanRead, status_code=201, dependencies=WRITE)
def create_game_plan(
    mid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    matchup = db.query(Matchup).filter(Matchup.id == mid, Matchup.org_id == org.id).first()
    if matchup is None:
        raise HTTPException(status_code=404, detail="matchup not found")
    dossier = db.query(OpponentDossier).filter(OpponentDossier.id == matchup.opponent_dossier_id).first()
    d = {
        "style_class": dossier.style_class if dossier else None,
        "summary": dossier.summary if dossier else {},
        "confidence": dossier.confidence if dossier else 0.0,
    }
    my_profile = aggregate_profile(db, org.id, matchup.my_player_id)
    gp = generate_plan(my_profile, d, {"confidence": matchup.confidence})

    plan = GamePlan(
        matchup_id=matchup.id, plan=gp["plan"], training_block=gp["training_block"],
        status="draft", confidence=gp["confidence"],
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    out = GamePlanRead.model_validate(plan)
    out.data_note = gp["data_note"]
    return out


@router.get("/game-plans/{gid}", response_model=GamePlanRead)
def get_game_plan(gid: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_org)):
    plan = (
        db.query(GamePlan)
        .join(Matchup, GamePlan.matchup_id == Matchup.id)
        .filter(GamePlan.id == gid, Matchup.org_id == org.id)
        .first()
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="game plan not found")
    return plan
