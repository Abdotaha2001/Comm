import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
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
