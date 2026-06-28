"""capture acceptance: certification + acceptance record on analysis_runs

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("analysis_runs") as batch:
        batch.add_column(sa.Column("capture_certification", sa.String()))
        batch.add_column(sa.Column("capture_acceptance", sa.JSON()))


def downgrade() -> None:
    with op.batch_alter_table("analysis_runs") as batch:
        batch.drop_column("capture_acceptance")
        batch.drop_column("capture_certification")
