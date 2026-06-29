"""Shared helpers for the Part 37 governance validators."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
OPENAPI_PATH = REPO_ROOT / "api" / "openapi.yaml"
PART37_PATH = REPO_ROOT / "MASTER_SPEC" / "37_DATA_MODEL_AND_API_CONTRACT_BUILD_SPEC.md"
CAPTURE_SCHEMA_PATH = REPO_ROOT / "MASTER_SPEC" / "35_CAPTURE_ACCEPTANCE_SCHEMA.json"

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
API_PREFIX = "/v1"

# Tables that are append-only analysis children — exempt from the full shared-field
# set per Part 37 §I / §F. They still carry a primary key.
APPEND_ONLY_TABLES = {"rallies", "shots", "events"}

# Mandatory shared fields for first-class entity tables (Part 37 §I).
REQUIRED_SHARED_FIELDS = {
    "id", "created_at", "updated_at", "version", "provenance_hash", "schema_version",
}


@dataclass
class Check:
    """Outcome of one governance validator."""
    name: str
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    info: dict[str, Any] = field(default_factory=dict)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "errors": self.errors, "info": self.info}


def normalize_path(path: str) -> str:
    """Normalize an HTTP path for comparison: drop the /v1 prefix and collapse
    every `{param}` to `{}` so parameter naming differences don't cause drift."""
    if path.startswith(API_PREFIX + "/") or path == API_PREFIX:
        path = path[len(API_PREFIX):] or "/"
    path = re.sub(r"\{[^}]+\}", "{}", path)
    return path


def operation_set(paths: dict) -> set[tuple[str, str]]:
    """Build the set of (METHOD, normalized_path) operations from an OpenAPI
    `paths` mapping."""
    ops: set[tuple[str, str]] = set()
    for raw_path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method in item:
            if method.lower() in HTTP_METHODS:
                ops.add((method.upper(), normalize_path(raw_path)))
    return ops


def orm_metadata():
    """Import the ORM and return SQLAlchemy MetaData (tables populated)."""
    import app.models  # noqa: F401  (registers tables on Base.metadata)
    from app.db import Base

    return Base.metadata
