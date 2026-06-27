from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Enums grounded in MASTER_SPEC Part 28 (controlled vocabulary).
Handedness = Literal["left", "right", "unknown"]
Grip = Literal[
    "shakehand", "penhold_chinese", "penhold_japanese", "seemiller", "other", "unknown"
]
PlayerType = Literal["pro", "junior"]
Sex = Literal["m", "f", "x"]
Mobility = Literal["standing", "wheelchair", "na"]
Maturation = Literal["early", "average", "late", "unknown"]
Impairment = Literal[
    "impaired_muscle_power",
    "impaired_passive_rom",
    "limb_deficiency",
    "leg_length_difference",
    "short_stature",
    "hypertonia",
    "ataxia",
    "athetosis",
    "intellectual",
]


class PlayerCreate(BaseModel):
    full_name: str
    type: PlayerType = "pro"
    handedness: Handedness = "unknown"
    grip: Grip = "unknown"
    date_of_birth: Optional[date] = None
    sex: Optional[Sex] = None
    country: Optional[str] = None
    para_class: Optional[int] = Field(default=None, ge=1, le=11)
    impairment_type: Optional[Impairment] = None
    mobility_mode: Mobility = "na"
    disability_notes: Optional[str] = None
    maturation_status: Optional[Maturation] = None


class PlayerUpdate(BaseModel):
    full_name: Optional[str] = None
    type: Optional[PlayerType] = None
    handedness: Optional[Handedness] = None
    grip: Optional[Grip] = None
    date_of_birth: Optional[date] = None
    sex: Optional[Sex] = None
    country: Optional[str] = None
    para_class: Optional[int] = Field(default=None, ge=1, le=11)
    impairment_type: Optional[Impairment] = None
    mobility_mode: Optional[Mobility] = None
    disability_notes: Optional[str] = None
    maturation_status: Optional[Maturation] = None


class PlayerRead(PlayerCreate):
    id: str
    org_id: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


Role = Literal["admin", "coach", "player", "umpire", "medical", "scout"]


class AuthLogin(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    org_name: Optional[str] = None
    role: Role = "admin"


class UserRead(BaseModel):
    id: str
    org_id: str
    email: str
    full_name: Optional[str] = None
    role: str
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


# ── Videos / analysis / results ───────────────────────────────
class VideoRead(BaseModel):
    id: str
    player_id: Optional[str] = None
    source: str
    status: str
    capture_tier: str
    fps: Optional[float] = None
    duration_sec: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class AnalysisRunRead(BaseModel):
    id: str
    video_id: str
    status: str
    reliability_index: Optional[float] = None
    input_quality: Optional[dict] = None
    model_versions: Optional[dict] = None
    error: Optional[str] = None
    match_id: Optional[str] = None


class EventRead(BaseModel):
    type: str
    frame: Optional[int] = None
    ts_ms: Optional[int] = None
    side: Optional[str] = None
    position: Optional[dict] = None
    confidence: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class ShotRead(BaseModel):
    idx: int
    frame: Optional[int] = None
    ts_ms: Optional[int] = None
    stroke_type: Optional[str] = None
    spin_type: Optional[str] = None
    wing: Optional[str] = None
    speed_kmh: Optional[float] = None
    speed_ci: Optional[float] = None
    confidence: Optional[float] = None
    provenance: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


class RallyRead(BaseModel):
    idx: int
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    duration_sec: Optional[float] = None
    quality: Optional[float] = None
    confidence: Optional[float] = None
    shots: List[ShotRead] = []
    events: List[EventRead] = []
    model_config = ConfigDict(from_attributes=True)


class MatchRead(BaseModel):
    id: str
    video_id: str
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    is_doubles: int = 0
    rallies: List[RallyRead] = []
    model_config = ConfigDict(from_attributes=True)


# ── Intelligence: profiles / opponents / matchups / game plans ──
class ProfileRead(BaseModel):
    id: str
    player_id: str
    version: int
    style_class: Optional[str] = None
    aggregated_stats: Optional[dict] = None
    strengths: Optional[list] = None
    weaknesses: Optional[list] = None
    confidence: Optional[float] = None
    data_note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class OpponentCreate(BaseModel):
    subject_player_id: str
    opponent_player_id: Optional[str] = None
    opponent_ref: Optional[str] = None
    video_ids: Optional[List[str]] = None


class OpponentRead(BaseModel):
    id: str
    subject_player_id: str
    opponent_player_id: Optional[str] = None
    opponent_ref: Optional[str] = None
    footage_count: int
    style_class: Optional[str] = None
    summary: Optional[dict] = None
    confidence: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class MatchupCreate(BaseModel):
    my_player_id: str
    opponent_dossier_id: str


class MatchupRead(BaseModel):
    id: str
    my_player_id: str
    opponent_dossier_id: Optional[str] = None
    predicted_winprob: Optional[float] = None
    confidence: Optional[float] = None
    h2h: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)


class GamePlanRead(BaseModel):
    id: str
    matchup_id: str
    status: str
    plan: Optional[dict] = None
    training_block: Optional[list] = None
    confidence: Optional[float] = None
    data_note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
