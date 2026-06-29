from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import Organization, User
from ..schemas import AuthLogin, RegisterRequest, TokenResponse, UserRead
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserRead, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="email already registered")
    org = Organization(name=body.org_name or body.email, type="individual")
    db.add(org)
    db.flush()
    user = User(
        org_id=org.id,
        email=body.email,
        full_name=body.full_name,
        role=body.role,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login(body: AuthLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or not user.password_hash or not verify_password(
        body.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(sub=user.id, org_id=user.org_id, role=user.role)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
