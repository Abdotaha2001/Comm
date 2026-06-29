"""per-shot reliability envelope (Part 40 §C): shots.reliability

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("shots") as batch:
        batch.add_column(sa.Column("reliability", sa.JSON()))


def downgrade() -> None:
    with op.batch_alter_table("shots") as batch:
        batch.drop_column("reliability")
