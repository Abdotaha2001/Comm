from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .db import get_db
from .models import Organization, User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="missing bearer token")
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if user is None or user.status != "active":
        raise HTTPException(status_code=401, detail="user not found or inactive")
    return user


def get_current_org(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Organization:
    org = db.query(Organization).filter(Organization.id == user.org_id).first()
    if org is None:
        raise HTTPException(status_code=401, detail="organization not found")
    return org


def require_roles(*roles: str):
    """Dependency factory: require the current user to hold one of `roles`."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=403, detail="insufficient role")
        return user

    return checker
