"""shared entity fields (Part 37 §I): updated_at, deleted_at, version, provenance_hash, schema_version

Adds the standard shared fields to the first-class entity tables. Append-only
children (rallies, shots, events) are intentionally exempt (Part 37 §I/§F).

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

_FULL = ["updated_at", "deleted_at", "version", "provenance_hash", "schema_version"]

# Per-table additions (some tables already have updated_at or version).
SHARED = {
    "organizations": _FULL,
    "users": _FULL,
    "players": ["deleted_at", "version", "provenance_hash", "schema_version"],  # has updated_at
    "videos": _FULL,
    "analysis_runs": _FULL,
    "matches": _FULL,
    "player_profiles": ["updated_at", "deleted_at", "provenance_hash", "schema_version"],  # has version
    "opponent_dossiers": _FULL,
    "matchups": _FULL,
    "game_plans": _FULL,
}


def _column(name: str) -> sa.Column:
    if name == "version":
        return sa.Column("version", sa.Integer(), nullable=False, server_default="1")
    if name in ("updated_at", "deleted_at"):
        return sa.Column(name, sa.DateTime())
    return sa.Column(name, sa.String())


def upgrade() -> None:
    for table, names in SHARED.items():
        with op.batch_alter_table(table) as batch:
            for name in names:
                batch.add_column(_column(name))


def downgrade() -> None:
    for table, names in SHARED.items():
        with op.batch_alter_table(table) as batch:
            for name in reversed(names):
                batch.drop_column(name)
