"""initial: organizations, users, players

Revision ID: 0001
Revises:
Create Date: 2026-06-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("full_name", sa.String()),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String()),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_users_org", "users", ["org_id"])
    op.create_table(
        "players",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(length=36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("handedness", sa.String(), nullable=False),
        sa.Column("grip", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.Date()),
        sa.Column("sex", sa.String()),
        sa.Column("country", sa.String()),
        sa.Column("para_class", sa.SmallInteger()),
        sa.Column("impairment_type", sa.String()),
        sa.Column("mobility_mode", sa.String(), nullable=False),
        sa.Column("disability_notes", sa.Text()),
        sa.Column("maturation_status", sa.String()),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_index("idx_players_org", "players", ["org_id"])


def downgrade() -> None:
    op.drop_table("players")
    op.drop_table("users")
    op.drop_table("organizations")
