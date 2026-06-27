from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_org
from ..models import Event, Match, Organization, Rally, Shot, Video
from ..schemas import EventRead, MatchRead, RallyRead, ShotRead

router = APIRouter(tags=["matches"])


@router.get("/matches/{mid}", response_model=MatchRead)
def get_match(
    mid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    match = (
        db.query(Match)
        .join(Video, Match.video_id == Video.id)
        .filter(Match.id == mid, Video.org_id == org.id)
        .first()
    )
    if match is None:
        raise HTTPException(status_code=404, detail="match not found")

    out = MatchRead.model_validate(match)
    rallies = []
    for r in db.query(Rally).filter(Rally.match_id == mid).order_by(Rally.idx).all():
        rd = RallyRead.model_validate(r)
        rd.shots = [
            ShotRead.model_validate(s)
            for s in db.query(Shot).filter(Shot.rally_id == r.id).order_by(Shot.idx).all()
        ]
        rd.events = [
            EventRead.model_validate(e)
            for e in db.query(Event).filter(Event.rally_id == r.id).all()
        ]
        rallies.append(rd)
    out.rallies = rallies
    return out
