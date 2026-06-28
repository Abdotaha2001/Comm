"""Part 37 governance validators — automated spec-vs-implementation enforcement.

Each `check_*` returns a `Check`. `run_all()` runs them and returns (ok, checks).
CLI: `python -m tools.governance` (see `__main__`).
"""
from __future__ import annotations

from .common import Check
from .db_drift import check_migrations
from .entities import check_entities
from .openapi_drift import check_openapi
from .shared_fields import check_shared_fields
from .traceability import check_traceability

ALL_CHECKS = (
    check_migrations,
    check_openapi,
    check_entities,
    check_shared_fields,
    check_traceability,
)


def run_all() -> tuple[bool, list[Check]]:
    results = [c() for c in ALL_CHECKS]
    return all(r.ok for r in results), results


__all__ = [
    "Check", "run_all", "ALL_CHECKS",
    "check_migrations", "check_openapi", "check_entities",
    "check_shared_fields", "check_traceability",
]
