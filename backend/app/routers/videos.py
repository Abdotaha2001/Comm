import os
import shutil
import uuid
from typing import List

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..deps import get_current_org, require_roles
from ..models import AnalysisRun, Match, Organization, Player, Video
from ..schemas import AnalysisRunRead, VideoRead
from ..worker import analyze_run

router = APIRouter(tags=["videos"])
WRITE = (Depends(require_roles("admin", "coach")),)


@router.post(
    "/players/{pid}/videos", response_model=VideoRead, status_code=201, dependencies=list(WRITE)
)
def upload_video(
    pid: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    player = db.query(Player).filter(Player.id == pid, Player.org_id == org.id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="player not found")

    os.makedirs(settings.media_dir, exist_ok=True)
    vid_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    key = os.path.join(settings.media_dir, f"{vid_id}{ext}")
    with open(key, "wb") as out:
        shutil.copyfileobj(file.file, out)

    fps = width = height = duration = None
    cap = cv2.VideoCapture(key)
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS) or None
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None
        n = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration = (n / fps) if fps else None
    cap.release()

    video = Video(
        id=vid_id, org_id=org.id, player_id=pid, source="upload", storage_key=key,
        status="uploaded", fps=fps, width=width, height=height, duration_sec=duration,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.get("/players/{pid}/videos", response_model=List[VideoRead])
def list_videos(
    pid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    return db.query(Video).filter(Video.org_id == org.id, Video.player_id == pid).all()


@router.post("/videos/{vid}/analyze", response_model=AnalysisRunRead, dependencies=list(WRITE))
def analyze_video_endpoint(
    vid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    video = db.query(Video).filter(Video.id == vid, Video.org_id == org.id).first()
    if video is None:
        raise HTTPException(status_code=404, detail="video not found")

    run = AnalysisRun(video_id=video.id, status="queued")
    db.add(run)
    db.commit()
    db.refresh(run)

    # Scaffold runs the worker inline (synthetic clips are fast). Production: queue + GPU worker.
    match_id = None
    try:
        match_id = analyze_run(run.id, db)
    except Exception:
        pass  # worker recorded status=failed + error
    db.refresh(run)
    return AnalysisRunRead(
        id=run.id, video_id=run.video_id, status=run.status,
        reliability_index=run.reliability_index, input_quality=run.input_quality,
        model_versions=run.model_versions, error=run.error, match_id=match_id,
    )


@router.get("/analysis-runs/{rid}", response_model=AnalysisRunRead)
def get_run(
    rid: str,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
):
    run = (
        db.query(AnalysisRun)
        .join(Video, AnalysisRun.video_id == Video.id)
        .filter(AnalysisRun.id == rid, Video.org_id == org.id)
        .first()
    )
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    match = db.query(Match).filter(Match.analysis_run_id == run.id).first()
    return AnalysisRunRead(
        id=run.id, video_id=run.video_id, status=run.status,
        reliability_index=run.reliability_index, input_quality=run.input_quality,
        model_versions=run.model_versions, error=run.error,
        match_id=match.id if match else None,
    )
