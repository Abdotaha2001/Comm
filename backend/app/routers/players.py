from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..deps import get_current_org, require_roles
from ..db import get_db
from ..models import Organization, Player
from ..schemas import PlayerCreate, PlayerRead, PlayerUpdate

router = APIRouter(prefix="/players", tags=["players"])

# Roles allowed to modify players (read is open to any authenticated user).
WRITE_ROLES = ("admin", "coach")


def _get_owned(pid: str, db: Session, org: Organization) -> Player:
    p = db.query(Player).filter(Player.id == pid, Player.org_id == org.id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="player not found")
    return p


@router.post(
    "",
    response_model=PlayerRead,
    status_code=201,
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
def create_player(
    body: PlayerCreate,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    player = Player(org_id=org.id, **body.model_dump())
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.get("", response_model=List[PlayerRead])
def list_players(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    q = db.query(Player).filter(Player.org_id == org.id, Player.status == "active")
    if type:
        q = q.filter(Player.type == type)
    return q.limit(200).all()


@router.get("/{pid}", response_model=PlayerRead)
def get_player(
    pid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return _get_owned(pid, db, org)


@router.patch(
    "/{pid}",
    response_model=PlayerRead,
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
def update_player(
    pid: str,
    body: PlayerUpdate,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    player = _get_owned(pid, db, org)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(player, k, v)
    db.commit()
    db.refresh(player)
    return player


@router.delete(
    "/{pid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
def archive_player(
    pid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    player = _get_owned(pid, db, org)
    player.status = "archived"
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
