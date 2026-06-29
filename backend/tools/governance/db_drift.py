"""ORM <-> migration <-> database synchronization (Part 37 §X.1/§X.2, §Z.3).

Runs the migration round-trip (upgrade head -> downgrade base -> upgrade head)
and verifies the resulting database schema equals the SQLAlchemy models exactly
(tables + columns). Catches: missing migration, extra migration, a model column
without a migration, broken upgrade/downgrade.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, inspect

from .common import BACKEND_ROOT, Check, orm_metadata


def diff_schema(expected: dict[str, set], actual: dict[str, set]) -> list[str]:
    """Pure schema diff between model tables/columns (expected) and DB (actual)."""
    errors: list[str] = []
    for t in sorted(set(expected) - set(actual)):
        errors.append(f"table '{t}' is in models but missing from migrations")
    for t in sorted(set(actual) - set(expected)):
        errors.append(f"table '{t}' is in migrations but missing from models")
    for t in sorted(set(expected) & set(actual)):
        for c in sorted(expected[t] - actual[t]):
            errors.append(f"{t}.{c}: column in model but not migrated (missing migration)")
        for c in sorted(actual[t] - expected[t]):
            errors.append(f"{t}.{c}: column migrated but not in model (extra migration)")
    return errors


def _alembic(args: list[str], db_url: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, DATABASE_URL=db_url)
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=str(BACKEND_ROOT), env=env, capture_output=True, text=True,
    )


def check_migrations() -> Check:
    chk = Check("migrations")
    tmp = Path(tempfile.mkdtemp()) / "gov.db"
    db_url = f"sqlite:///{tmp}"
    try:
        for step in (["upgrade", "head"], ["downgrade", "base"], ["upgrade", "head"]):
            res = _alembic(step, db_url)
            if res.returncode != 0:
                chk.fail(f"alembic {' '.join(step)} failed: {res.stderr.strip()[-500:]}")
                return chk
        chk.info["round_trip"] = "upgrade->downgrade->upgrade ok"

        meta = orm_metadata()
        insp = inspect(create_engine(db_url))
        db_tables = set(insp.get_table_names()) - {"alembic_version"}
        expected = {t: set(meta.tables[t].columns.keys()) for t in meta.tables}
        actual = {t: {c["name"] for c in insp.get_columns(t)} for t in db_tables}
        for err in diff_schema(expected, actual):
            chk.fail(err)
        chk.info["tables"] = len(expected)
    finally:
        try:
            tmp.unlink(missing_ok=True)
            tmp.parent.rmdir()
        except OSError:
            pass
    return chk
