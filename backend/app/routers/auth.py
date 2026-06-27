from fastapi import APIRouter, Depends

from ..deps import get_current_org
from ..models import Organization
from ..schemas import AuthLogin, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse)
def login(body: AuthLogin):
    # Stub: issue a static dev token. Replace with real JWT in Phase 1.
    return TokenResponse(access_token="dev-token")


@router.get("/auth/me")
def me(org: Organization = Depends(get_current_org)):
    return {"org_id": org.id, "email": "dev@tt-os.local", "role": "coach"}
