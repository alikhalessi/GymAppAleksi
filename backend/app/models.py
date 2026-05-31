from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Program(Base):
    """Workout program created by a user for the MVP."""

    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workout_days: Mapped[list["WorkoutDay"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
    )


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    program: Mapped[Program] = relationship(back_populates="workout_days")
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workout_day: Mapped[WorkoutDay] = relationship(back_populates="exercises")
    planned_sets: Mapped[list["PlannedSet"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
    )
    youtube_videos: Mapped[list["YouTubeVideo"]] = relationship(
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    workout_exercise: Mapped[WorkoutExercise] = relationship(back_populates="youtube_videos")


__all__ = ["Base", "Program", "WorkoutDay", "WorkoutExercise", "PlannedSet", "YouTubeVideo"]
