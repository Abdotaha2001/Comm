from datetime import date, datetime
from typing import Literal, Optional

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
