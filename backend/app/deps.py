from fastapi import Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import Organization


def get_current_org(db: Session = Depends(get_db)) -> Organization:
    """Stub tenancy: resolve the caller's organization.

    For the P0 scaffold we auto-create/return a single default org. Replace with
    JWT/api-key resolution + RBAC in Phase 1 (MASTER_SPEC Parts 13, 27).
    """
    org = db.query(Organization).first()
    if org is None:
        org = Organization(name="Default Org", type="individual")
        db.add(org)
        db.commit()
        db.refresh(org)
    return org
