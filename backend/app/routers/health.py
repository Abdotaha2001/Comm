from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/healthz")
def healthz():
    return {"status": "ok"}
