"""intelligence: player_profiles, opponent_dossiers, matchups, game_plans

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "player_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("style_class", sa.String()),
        sa.Column("aggregated_stats", sa.JSON()),
        sa.Column("strengths", sa.JSON()),
        sa.Column("weaknesses", sa.JSON()),
        sa.Column("source_video_ids", sa.JSON()),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_profiles_player", "player_profiles", ["player_id"])

    op.create_table(
        "opponent_dossiers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opponent_player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("opponent_ref", sa.String()),
        sa.Column("footage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("style_class", sa.String()),
        sa.Column("summary", sa.JSON()),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_dossiers_subject", "opponent_dossiers", ["subject_player_id"])

    op.create_table(
        "matchups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("my_player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opponent_dossier_id", sa.String(36), sa.ForeignKey("opponent_dossiers.id", ondelete="SET NULL")),
        sa.Column("h2h", sa.JSON()),
        sa.Column("predicted_winprob", sa.Float()),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_matchups_player", "matchups", ["my_player_id"])

    op.create_table(
        "game_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("matchup_id", sa.String(36), sa.ForeignKey("matchups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", sa.JSON()),
        sa.Column("training_block", sa.JSON()),
        sa.Column("report_key", sa.String()),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_plans_matchup", "game_plans", ["matchup_id"])


def downgrade() -> None:
    for t in ("game_plans", "matchups", "opponent_dossiers", "player_profiles"):
        op.drop_table(t)
