from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)



class Program(Base):
    """Workout program created by a user for the MVP."""

    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_days: Mapped[list["WorkoutDay"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )
    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )
    versions: Mapped[list["ProgramVersion"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )


class ProgramVersion(Base):
    """Metadata layer tracking the provenance and version history of a workout program."""

    __tablename__ = "program_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_label: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    version_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    parent_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("program_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    program: Mapped[Program] = relationship(back_populates="versions")


class TraineeProfile(Base):
    """Single-user trainee profile context for the local MVP."""

    __tablename__ = "trainee_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_experience: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    primary_goal: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    limitations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    available_equipment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    preferred_session_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class ReadinessCheck(Base):
    """Pre-session training context captured by the user."""

    __tablename__ = "readiness_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    energy_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sleep_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    soreness_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pain_or_limitations_today: Mapped[str] = mapped_column(Text, nullable=False, default="")
    available_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class WorkoutDay(Base):
    """A named training day inside a workout program."""

    __tablename__ = "workout_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    day_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    program: Mapped[Program] = relationship(back_populates="workout_days")
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan",
    )
    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan",
    )


class WorkoutExercise(Base):
    """Exercise prescription inside a workout day."""

    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_day_id: Mapped[int] = mapped_column(
        ForeignKey("workout_days.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movement_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[str] = mapped_column(String(40), nullable=False)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    exercise_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_day: Mapped[WorkoutDay] = relationship(back_populates="exercises")
    planned_sets: Mapped[list["PlannedSet"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
    )
    youtube_videos: Mapped[list["YouTubeVideo"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
    )
    session_sets: Mapped[list["SessionSet"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
    )


class PlannedSet(Base):
    """Set-level prescription for a workout exercise."""

    __tablename__ = "planned_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    target_reps: Mapped[str] = mapped_column(String(40), nullable=False)
    suggested_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str] = mapped_column(String(10), nullable=False, default="kg")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_exercise: Mapped[WorkoutExercise] = relationship(back_populates="planned_sets")


class YouTubeVideo(Base):
    """Stored YouTube example video for a workout exercise."""

    __tablename__ = "youtube_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    youtube_video_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    thumbnail_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_exercise: Mapped[WorkoutExercise] = relationship(back_populates="youtube_videos")


class WorkoutSession(Base):
    """An executed workout session for a selected workout day."""

    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workout_day_id: Mapped[int] = mapped_column(
        ForeignKey("workout_days.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")

    program: Mapped[Program] = relationship(back_populates="workout_sessions")
    workout_day: Mapped[WorkoutDay] = relationship(back_populates="workout_sessions")
    session_sets: Mapped[list["SessionSet"]] = relationship(
        back_populates="workout_session",
        cascade="all, delete-orphan",
    )
    reflections: Mapped[list["SessionReflection"]] = relationship(
        back_populates="workout_session",
        cascade="all, delete-orphan",
    )
    progression_suggestions: Mapped[list["ProgressionSuggestion"]] = relationship(
        back_populates="workout_session",
        cascade="all, delete-orphan",
    )


class SessionSet(Base):
    """Actual set performance recorded during a workout session."""

    __tablename__ = "session_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_reps: Mapped[str] = mapped_column(String(40), nullable=False)
    planned_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    workout_day_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    program_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    planned_rest_seconds_snapshot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str] = mapped_column(String(10), nullable=False, default="kg")
    difficulty_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rest_seconds_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_session: Mapped[WorkoutSession] = relationship(back_populates="session_sets")
    workout_exercise: Mapped[WorkoutExercise] = relationship(back_populates="session_sets")


class SessionReflection(Base):
    """AI-generated advisory reflection for a completed workout session."""

    __tablename__ = "session_reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    what_went_well: Mapped[str] = mapped_column(Text, nullable=False)
    what_was_difficult: Mapped[str] = mapped_column(Text, nullable=False)
    next_session_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    caution_flags: Mapped[str] = mapped_column(Text, nullable=False)
    trainer_review_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    model_used: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_session: Mapped[WorkoutSession] = relationship(back_populates="reflections")


class ProgressionSuggestion(Base):
    """Rule-based advisory suggestion for the next time an exercise is trained."""

    __tablename__ = "progression_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workout_session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workout_exercise_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    suggestion_type: Mapped[str] = mapped_column(String(80), nullable=False)
    suggested_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str] = mapped_column(String(10), nullable=False, default="kg")
    suggested_reps: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")
    confidence: Mapped[str] = mapped_column(String(40), nullable=False, default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workout_session: Mapped[WorkoutSession] = relationship(back_populates="progression_suggestions")


__all__ = [
    "Base",
    "TraineeProfile",
    "ReadinessCheck",
    "Program",
    "WorkoutDay",
    "WorkoutExercise",
    "PlannedSet",
    "YouTubeVideo",
    "WorkoutSession",
    "SessionSet",
    "SessionReflection",
    "ProgressionSuggestion",
    "ProgramVersion",
]
