from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..analytics.profile import aggregate_profile
from ..db import get_db
from ..deps import get_current_org, require_roles
from ..models import Organization, Player, PlayerProfile
from ..schemas import ProfileRead

router = APIRouter(tags=["profiles"])


def _owned_player(pid, db, org):
    p = db.query(Player).filter(Player.id == pid, Player.org_id == org.id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="player not found")
    return p


@router.post(
    "/players/{pid}/profile/rebuild",
    response_model=ProfileRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin", "coach"))],
)
def rebuild_profile(
    pid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    _owned_player(pid, db, org)
    agg = aggregate_profile(db, org.id, pid)
    next_version = (
        db.query(func.coalesce(func.max(PlayerProfile.version), 0))
        .filter(PlayerProfile.player_id == pid)
        .scalar()
        + 1
    )
    profile = PlayerProfile(
        player_id=pid, version=next_version, style_class=agg["style_class"],
        aggregated_stats=agg["aggregated_stats"], strengths=agg["strengths"],
        weaknesses=agg["weaknesses"], source_video_ids=agg["source_video_ids"],
        confidence=agg["confidence"],
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    out = ProfileRead.model_validate(profile)
    out.data_note = agg["data_note"]
    return out


@router.get("/players/{pid}/profile", response_model=ProfileRead)
def get_profile(
    pid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    _owned_player(pid, db, org)
    profile = (
        db.query(PlayerProfile)
        .filter(PlayerProfile.player_id == pid)
        .order_by(PlayerProfile.version.desc())
        .first()
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="no profile yet — rebuild first")
    return profile
