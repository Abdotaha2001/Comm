import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
)

from .db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="individual")
    created_at = Column(DateTime, default=_now)


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, nullable=False, unique=True)
    full_name = Column(String)
    role = Column(String, nullable=False, default="coach")
    password_hash = Column(String)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=_now)


class Player(Base):
    __tablename__ = "players"
    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    full_name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="pro")
    handedness = Column(String, nullable=False, default="unknown")
    grip = Column(String, nullable=False, default="unknown")
    date_of_birth = Column(Date)
    sex = Column(String)
    country = Column(String)
    # Para (MASTER_SPEC Part 24)
    para_class = Column(SmallInteger)
    impairment_type = Column(String)
    mobility_mode = Column(String, nullable=False, default="na")
    disability_notes = Column(Text)
    maturation_status = Column(String)
    # lifecycle
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class Video(Base):
    __tablename__ = "videos"
    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    player_id = Column(String(36), ForeignKey("players.id"))
    source = Column(String, nullable=False, default="upload")
    storage_key = Column(String)
    status = Column(String, nullable=False, default="uploaded")
    capture_tier = Column(String, nullable=False, default="t1")
    fps = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    duration_sec = Column(Float)
    created_at = Column(DateTime, default=_now)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id = Column(String(36), primary_key=True, default=_uuid)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    status = Column(String, nullable=False, default="queued")
    model_versions = Column(JSON)
    input_quality = Column(JSON)
    reliability_index = Column(Float)
    # Capture Acceptance Framework (Part 35): set when a capture report is supplied.
    capture_certification = Column(String)
    capture_acceptance = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    created_at = Column(DateTime, default=_now)


class Match(Base):
    __tablename__ = "matches"
    id = Column(String(36), primary_key=True, default=_uuid)
    analysis_run_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    player1_id = Column(String(36), ForeignKey("players.id"))
    player2_id = Column(String(36), ForeignKey("players.id"))
    score = Column(JSON)
    format = Column(String)
    is_doubles = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, default=_now)


class Rally(Base):
    __tablename__ = "rallies"
    id = Column(String(36), primary_key=True, default=_uuid)
    match_id = Column(String(36), ForeignKey("matches.id"), nullable=False)
    idx = Column(Integer, nullable=False)
    start_frame = Column(Integer)
    end_frame = Column(Integer)
    start_ms = Column(Integer)
    end_ms = Column(Integer)
    server_player_id = Column(String(36), ForeignKey("players.id"))
    winner_player_id = Column(String(36), ForeignKey("players.id"))
    reason = Column(String)
    duration_sec = Column(Float)
    quality = Column(Float)
    confidence = Column(Float)


class Shot(Base):
    __tablename__ = "shots"
    id = Column(String(36), primary_key=True, default=_uuid)
    rally_id = Column(String(36), ForeignKey("rallies.id"), nullable=False)
    idx = Column(Integer, nullable=False)
    player_id = Column(String(36), ForeignKey("players.id"))
    frame = Column(Integer)
    ts_ms = Column(Integer)
    stroke_type = Column(String)
    spin_type = Column(String)
    wing = Column(String)
    speed_kmh = Column(Float)
    speed_ci = Column(Float)
    quality = Column(Float)
    confidence = Column(Float)
    provenance = Column(JSON)


class Event(Base):
    __tablename__ = "events"
    id = Column(String(36), primary_key=True, default=_uuid)
    rally_id = Column(String(36), ForeignKey("rallies.id"))
    match_id = Column(String(36), ForeignKey("matches.id"))
    type = Column(String, nullable=False)
    frame = Column(Integer)
    ts_ms = Column(Integer)
    side = Column(String)
    position = Column(JSON)
    confidence = Column(Float)
    provenance = Column(JSON)


class PlayerProfile(Base):
    __tablename__ = "player_profiles"
    id = Column(String(36), primary_key=True, default=_uuid)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    version = Column(Integer, nullable=False)
    style_class = Column(String)
    aggregated_stats = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    source_video_ids = Column(JSON)
    confidence = Column(Float)
    created_at = Column(DateTime, default=_now)


class OpponentDossier(Base):
    __tablename__ = "opponent_dossiers"
    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    subject_player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    opponent_player_id = Column(String(36), ForeignKey("players.id"))
    opponent_ref = Column(String)
    footage_count = Column(Integer, nullable=False, default=0)
    style_class = Column(String)
    summary = Column(JSON)
    confidence = Column(Float)
    created_at = Column(DateTime, default=_now)


class Matchup(Base):
    __tablename__ = "matchups"
    id = Column(String(36), primary_key=True, default=_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    my_player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    opponent_dossier_id = Column(String(36), ForeignKey("opponent_dossiers.id"))
    h2h = Column(JSON)
    predicted_winprob = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime, default=_now)


class GamePlan(Base):
    __tablename__ = "game_plans"
    id = Column(String(36), primary_key=True, default=_uuid)
    matchup_id = Column(String(36), ForeignKey("matchups.id"), nullable=False)
    plan = Column(JSON)
    training_block = Column(JSON)
    report_key = Column(String)
    status = Column(String, nullable=False, default="draft")
    confidence = Column(Float)
    created_at = Column(DateTime, default=_now)
