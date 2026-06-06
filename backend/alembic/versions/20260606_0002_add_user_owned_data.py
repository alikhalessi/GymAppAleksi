"""add_user_owned_data

Revision ID: 20260606_0002
Revises: 20260606_0001
Create Date: 2026-06-06 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260606_0002"
down_revision: str | None = "20260606_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


USER_OWNED_TABLES = [
    "programs",
    "workout_days",
    "workout_exercises",
    "planned_sets",
    "workout_sessions",
    "session_sets",
    "session_reflections",
    "progression_suggestions",
    "trainee_profiles",
    "readiness_checks",
    "program_versions",
    "youtube_videos",
]


def upgrade() -> None:
    for table_name in USER_OWNED_TABLES:
        op.add_column(table_name, sa.Column("user_id", sa.String(length=120), nullable=True))
        op.create_index(op.f(f"ix_{table_name}_user_id"), table_name, ["user_id"], unique=False)


def downgrade() -> None:
    for table_name in reversed(USER_OWNED_TABLES):
        op.drop_index(op.f(f"ix_{table_name}_user_id"), table_name=table_name)
        op.drop_column(table_name, "user_id")
