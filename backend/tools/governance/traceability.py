"""Traceability validator (Part 37 §W, §X.11, §Z.6/§Z.8).

Verifies the requirement -> entity -> API -> persistence -> documentation chain:
- every ORM table maps to a catalogued entity with a non-empty Parts cell
  (persistence -> entity -> requirement),
- every router module maps to at least one documented API path
  (module -> API -> documentation),
- modules referenced as present by the traceability matrix actually exist.
Produces a traceability report in `info`.
"""
from __future__ import annotations

import yaml

from .common import BACKEND_ROOT, Check, OPENAPI_PATH, orm_metadata
from .entities import parse_catalog

# router module -> a path fragment that MUST appear in the committed contract.
ROUTER_API_FRAGMENTS = {
    "auth": "/auth",
    "health": "/healthz",
    "players": "/players",
    "videos": "/videos",
    "matches": "/matches",
    "profiles": "/profile",
    "matchups": "/matchups",
}

# modules the matrix marks as present (Part 37 §W / §Y).
REQUIRED_MODULES = [
    "app/security.py", "app/deps.py", "app/db.py", "app/benchmark.py",
    "app/capture_quality.py", "app/cv", "app/analytics",
]


def trace_errors(rows, orm_tables) -> tuple[list[str], dict]:
    """Pure: persistence -> entity -> requirement. Returns (errors, report)."""
    by_table = {r.table: r for r in rows}
    errors: list[str] = []
    report: dict[str, str] = {}
    for table in sorted(orm_tables):
        row = by_table.get(table)
        if row is None:
            errors.append(f"table '{table}' has no entity in the catalog (no requirement trace)")
        elif not row.parts or row.parts == "—":
            errors.append(f"table '{table}' traces to no Part (requirement)")
        else:
            report[f"entity:{table}"] = f"Parts {row.parts}"
    return errors, report


def check_traceability() -> Check:
    chk = Check("traceability")

    # persistence -> entity -> requirement
    errors, report = trace_errors(parse_catalog(), set(orm_metadata().tables))
    for e in errors:
        chk.fail(e)

    # module -> API -> documentation
    committed_paths = []
    if OPENAPI_PATH.exists():
        committed_paths = list(yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8")).get("paths", {}))
    routers_dir = BACKEND_ROOT / "app" / "routers"
    for module, fragment in ROUTER_API_FRAGMENTS.items():
        if not (routers_dir / f"{module}.py").exists():
            chk.fail(f"router module '{module}.py' referenced by traceability is missing")
            continue
        if not any(fragment in p for p in committed_paths):
            chk.fail(f"router '{module}' maps to no documented path containing '{fragment}'")
        else:
            report[f"router:{module}"] = fragment

    # referenced modules exist
    for rel in REQUIRED_MODULES:
        if not (BACKEND_ROOT / rel).exists():
            chk.fail(f"module referenced by the traceability matrix is missing: {rel}")
        else:
            report[f"module:{rel}"] = "present"

    chk.info["report"] = report
    return chk
