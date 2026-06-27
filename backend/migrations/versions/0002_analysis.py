"""analysis: videos, analysis_runs, matches, rallies, shots, events

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "videos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("storage_key", sa.String()),
        sa.Column("status", sa.String(), nullable=False, server_default="uploaded"),
        sa.Column("capture_tier", sa.String(), nullable=False, server_default="t1"),
        sa.Column("fps", sa.Float()),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("duration_sec", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_videos_org", "videos", ["org_id"])
    op.create_index("idx_videos_player", "videos", ["player_id"])

    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("video_id", sa.String(36), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("model_versions", sa.JSON()),
        sa.Column("input_quality", sa.JSON()),
        sa.Column("reliability_index", sa.Float()),
        sa.Column("error", sa.Text()),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_runs_video", "analysis_runs", ["video_id"])

    op.create_table(
        "matches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("analysis_run_id", sa.String(36), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("video_id", sa.String(36), sa.ForeignKey("videos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player1_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("player2_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("score", sa.JSON()),
        sa.Column("format", sa.String()),
        sa.Column("is_doubles", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("idx_matches_run", "matches", ["analysis_run_id"])

    op.create_table(
        "rallies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("match_id", sa.String(36), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("idx", sa.Integer(), nullable=False),
        sa.Column("start_frame", sa.Integer()),
        sa.Column("end_frame", sa.Integer()),
        sa.Column("start_ms", sa.Integer()),
        sa.Column("end_ms", sa.Integer()),
        sa.Column("server_player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("winner_player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("reason", sa.String()),
        sa.Column("duration_sec", sa.Float()),
        sa.Column("quality", sa.Float()),
        sa.Column("confidence", sa.Float()),
    )
    op.create_index("idx_rallies_match", "rallies", ["match_id"])

    op.create_table(
        "shots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rally_id", sa.String(36), sa.ForeignKey("rallies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("idx", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.String(36), sa.ForeignKey("players.id", ondelete="SET NULL")),
        sa.Column("frame", sa.Integer()),
        sa.Column("ts_ms", sa.Integer()),
        sa.Column("stroke_type", sa.String()),
        sa.Column("spin_type", sa.String()),
        sa.Column("wing", sa.String()),
        sa.Column("speed_kmh", sa.Float()),
        sa.Column("speed_ci", sa.Float()),
        sa.Column("quality", sa.Float()),
        sa.Column("confidence", sa.Float()),
        sa.Column("provenance", sa.JSON()),
    )
    op.create_index("idx_shots_rally", "shots", ["rally_id"])

    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rally_id", sa.String(36), sa.ForeignKey("rallies.id", ondelete="CASCADE")),
        sa.Column("match_id", sa.String(36), sa.ForeignKey("matches.id", ondelete="CASCADE")),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("frame", sa.Integer()),
        sa.Column("ts_ms", sa.Integer()),
        sa.Column("side", sa.String()),
        sa.Column("position", sa.JSON()),
        sa.Column("confidence", sa.Float()),
        sa.Column("provenance", sa.JSON()),
    )
    op.create_index("idx_events_rally", "events", ["rally_id"])
    op.create_index("idx_events_match", "events", ["match_id"])


def downgrade() -> None:
    for t in ("events", "shots", "rallies", "matches", "analysis_runs", "videos"):
        op.drop_table(t)
