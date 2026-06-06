"""initial_schema

Revision ID: 20260606_0001
Revises:
Create Date: 2026-06-06 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260606_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "programs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("goal", sa.String(length=255), nullable=False),
        sa.Column("duration_weeks", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_programs_id"), "programs", ["id"], unique=False)
    op.create_index(op.f("ix_programs_name"), "programs", ["name"], unique=False)

    op.create_table(
        "readiness_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("energy_level", sa.Integer(), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), nullable=True),
        sa.Column("soreness_level", sa.Integer(), nullable=True),
        sa.Column("stress_level", sa.Integer(), nullable=True),
        sa.Column("pain_or_limitations_today", sa.Text(), nullable=False),
        sa.Column("available_time_minutes", sa.Integer(), nullable=True),
        sa.Column("readiness_score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_readiness_checks_id"), "readiness_checks", ["id"], unique=False)

    op.create_table(
        "trainee_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sex", sa.String(length=40), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("training_experience", sa.String(length=80), nullable=False),
        sa.Column("primary_goal", sa.String(length=200), nullable=False),
        sa.Column("limitations", sa.Text(), nullable=False),
        sa.Column("available_equipment", sa.Text(), nullable=False),
        sa.Column("preferred_session_minutes", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trainee_profiles_id"), "trainee_profiles", ["id"], unique=False)

    op.create_table(
        "program_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("version_label", sa.String(length=120), nullable=False),
        sa.Column("version_type", sa.String(length=80), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("parent_version_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["parent_version_id"], ["program_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_program_versions_id"), "program_versions", ["id"], unique=False)
    op.create_index(op.f("ix_program_versions_program_id"), "program_versions", ["program_id"], unique=False)

    op.create_table(
        "workout_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("day_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_days_id"), "workout_days", ["id"], unique=False)
    op.create_index(op.f("ix_workout_days_program_id"), "workout_days", ["program_id"], unique=False)

    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("workout_day_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("readiness_score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_day_id"], ["workout_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_sessions_id"), "workout_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_workout_sessions_program_id"), "workout_sessions", ["program_id"], unique=False)
    op.create_index(op.f("ix_workout_sessions_workout_day_id"), "workout_sessions", ["workout_day_id"], unique=False)

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_day_id", sa.Integer(), nullable=False),
        sa.Column("movement_name", sa.String(length=160), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("reps", sa.String(length=40), nullable=False),
        sa.Column("rest_seconds", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("exercise_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_day_id"], ["workout_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_exercises_id"), "workout_exercises", ["id"], unique=False)
    op.create_index(op.f("ix_workout_exercises_movement_name"), "workout_exercises", ["movement_name"], unique=False)
    op.create_index(op.f("ix_workout_exercises_workout_day_id"), "workout_exercises", ["workout_day_id"], unique=False)

    op.create_table(
        "planned_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("target_reps", sa.String(length=40), nullable=False),
        sa.Column("suggested_weight", sa.Float(), nullable=True),
        sa.Column("weight_unit", sa.String(length=10), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_planned_sets_id"), "planned_sets", ["id"], unique=False)
    op.create_index(op.f("ix_planned_sets_workout_exercise_id"), "planned_sets", ["workout_exercise_id"], unique=False)

    op.create_table(
        "session_reflections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_session_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("what_went_well", sa.Text(), nullable=False),
        sa.Column("what_was_difficult", sa.Text(), nullable=False),
        sa.Column("next_session_suggestion", sa.Text(), nullable=False),
        sa.Column("caution_flags", sa.Text(), nullable=False),
        sa.Column("trainer_review_recommended", sa.Boolean(), nullable=False),
        sa.Column("model_used", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_session_id"], ["workout_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_session_reflections_id"), "session_reflections", ["id"], unique=False)
    op.create_index(op.f("ix_session_reflections_workout_session_id"), "session_reflections", ["workout_session_id"], unique=False)

    op.create_table(
        "session_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_session_id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("planned_reps", sa.String(length=40), nullable=False),
        sa.Column("planned_weight", sa.Float(), nullable=True),
        sa.Column("exercise_name_snapshot", sa.String(length=160), nullable=False),
        sa.Column("workout_day_name_snapshot", sa.String(length=120), nullable=False),
        sa.Column("program_name_snapshot", sa.String(length=120), nullable=False),
        sa.Column("planned_rest_seconds_snapshot", sa.Integer(), nullable=True),
        sa.Column("actual_reps", sa.Integer(), nullable=True),
        sa.Column("actual_weight", sa.Float(), nullable=True),
        sa.Column("weight_unit", sa.String(length=10), nullable=False),
        sa.Column("difficulty_rating", sa.Integer(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("rest_seconds_used", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_session_id"], ["workout_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_session_sets_id"), "session_sets", ["id"], unique=False)
    op.create_index(op.f("ix_session_sets_workout_exercise_id"), "session_sets", ["workout_exercise_id"], unique=False)
    op.create_index(op.f("ix_session_sets_workout_session_id"), "session_sets", ["workout_session_id"], unique=False)

    op.create_table(
        "youtube_videos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("youtube_video_id", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("channel_name", sa.String(length=160), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("approved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_youtube_videos_id"), "youtube_videos", ["id"], unique=False)
    op.create_index(op.f("ix_youtube_videos_workout_exercise_id"), "youtube_videos", ["workout_exercise_id"], unique=False)
    op.create_index(op.f("ix_youtube_videos_youtube_video_id"), "youtube_videos", ["youtube_video_id"], unique=False)

    op.create_table(
        "progression_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_session_id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=True),
        sa.Column("exercise_name_snapshot", sa.String(length=160), nullable=False),
        sa.Column("suggestion_type", sa.String(length=80), nullable=False),
        sa.Column("suggested_weight", sa.Float(), nullable=True),
        sa.Column("weight_unit", sa.String(length=10), nullable=False),
        sa.Column("suggested_reps", sa.String(length=80), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workout_session_id"], ["workout_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_progression_suggestions_id"), "progression_suggestions", ["id"], unique=False)
    op.create_index(op.f("ix_progression_suggestions_workout_exercise_id"), "progression_suggestions", ["workout_exercise_id"], unique=False)
    op.create_index(op.f("ix_progression_suggestions_workout_session_id"), "progression_suggestions", ["workout_session_id"], unique=False)


def downgrade() -> None:
    op.drop_table("progression_suggestions")
    op.drop_table("youtube_videos")
    op.drop_table("session_sets")
    op.drop_table("session_reflections")
    op.drop_table("planned_sets")
    op.drop_table("workout_exercises")
    op.drop_table("workout_sessions")
    op.drop_table("workout_days")
    op.drop_table("program_versions")
    op.drop_table("trainee_profiles")
    op.drop_table("readiness_checks")
    op.drop_table("programs")
