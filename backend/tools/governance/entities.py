"""Entity catalog validator (Part 37 §E, §X.11, §Z.4/§Z.7/§Z.8).

Parses the §E entity catalog from Part 37 and reconciles it with the ORM:
- every implemented (ORM) table MUST appear in the catalog (no orphan tables),
- every catalog entity marked IMPLEMENTED (✅) MUST exist in the ORM,
- catalog rows MUST be well-formed (unique table, status, PK, traceable Parts),
- duplicate table definitions are forbidden.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .common import Check, PART37_PATH, orm_metadata

IMPLEMENTED = "✅"
PARTIAL = "🟡"
SPECIFIED = "⬜"


@dataclass
class CatalogRow:
    table: str
    pk: str
    status: str
    parts: str
    line: int


def parse_catalog(text: str | None = None) -> list[CatalogRow]:
    """Parse the §E catalog table. Columns:
    | # | Entity | Tbl | Context | PK | relationships | Delete | Status | Parts |"""
    if text is None:
        text = PART37_PATH.read_text(encoding="utf-8")
    # Isolate the §E section.
    start = text.find("## E.")
    end = text.find("## F.", start)
    section = text[start:end] if start != -1 else text
    rows: list[CatalogRow] = []
    for i, line in enumerate(section.splitlines()):
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.split("|")]
        # cells[0]='' , [1]=#, [2]=Entity, [3]=Tbl, [4]=Context, [5]=PK,
        # [6]=rel, [7]=Delete, [8]=Status, [9]=Parts
        if len(cells) < 10:
            continue
        table = cells[3].strip("` ")
        rows.append(CatalogRow(table=table, pk=cells[5], status=cells[8],
                               parts=cells[9], line=i))
    return rows


def validate_catalog(rows: list[CatalogRow], orm_tables: set[str]) -> list[str]:
    """Pure validation of catalog rows against the set of ORM tables."""
    errors: list[str] = []
    valid_status = {IMPLEMENTED, PARTIAL, SPECIFIED}
    seen: set[str] = set()
    for r in rows:
        if r.table in seen:
            errors.append(f"duplicate catalog entity for table '{r.table}'")
        seen.add(r.table)
        if not any(s in r.status for s in valid_status):
            errors.append(f"entity '{r.table}' has no/invalid status (got '{r.status}')")
        if not r.pk:
            errors.append(f"entity '{r.table}' has no primary identifier")
        if not r.parts or r.parts == "—":
            errors.append(f"entity '{r.table}' has no traceable Parts (requirement)")
    catalog_tables = {r.table for r in rows}
    for t in sorted(orm_tables - catalog_tables):
        errors.append(f"ORM table '{t}' is not in the §E entity catalog (orphan table)")
    for r in rows:
        if IMPLEMENTED in r.status and r.table not in orm_tables:
            errors.append(f"entity '{r.table}' is marked IMPLEMENTED but no ORM table exists")
    return errors


def check_entities() -> Check:
    chk = Check("entities")
    if not PART37_PATH.exists():
        chk.fail(f"Part 37 spec missing: {PART37_PATH}")
        return chk

    rows = parse_catalog()
    if not rows:
        chk.fail("could not parse the §E entity catalog (no rows found)")
        return chk

    orm_tables = set(orm_metadata().tables)
    for err in validate_catalog(rows, orm_tables):
        chk.fail(err)

    chk.info["catalog_entities"] = len(rows)
    chk.info["orm_tables"] = len(orm_tables)
    chk.info["implemented"] = sum(1 for r in rows if IMPLEMENTED in r.status)
    return chk
