"""Shared-fields validator (Part 37 §I, §X.10).

Every first-class entity table MUST carry the mandatory shared fields. Append-only
analysis children (rallies, shots, events) are exempt by spec but MUST keep a
primary key.
"""
from __future__ import annotations

from .common import APPEND_ONLY_TABLES, Check, REQUIRED_SHARED_FIELDS, orm_metadata


def missing_shared(table_columns: dict[str, set], append_only: set | None = None,
                   required: set | None = None) -> dict[str, list]:
    """Pure: per-table missing shared fields. Append-only tables need only 'id'."""
    append_only = APPEND_ONLY_TABLES if append_only is None else append_only
    required = REQUIRED_SHARED_FIELDS if required is None else required
    result: dict[str, list] = {}
    for table, cols in table_columns.items():
        need = {"id"} if table in append_only else required
        miss = sorted(need - set(cols))
        if miss:
            result[table] = miss
    return result


def check_shared_fields() -> Check:
    chk = Check("shared_fields")
    meta = orm_metadata()
    table_columns = {t: set(meta.tables[t].columns.keys()) for t in meta.tables}
    miss = missing_shared(table_columns)
    for table, fields in sorted(miss.items()):
        if table in APPEND_ONLY_TABLES:
            chk.fail(f"append-only table '{table}' has no primary key 'id'")
        else:
            chk.fail(f"table '{table}' is missing shared fields: {fields}")
    chk.info["required"] = sorted(REQUIRED_SHARED_FIELDS)
    chk.info["tables_checked"] = len(table_columns)
    chk.info["non_compliant"] = sorted(miss)
    return chk
