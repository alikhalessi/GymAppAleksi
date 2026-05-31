from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Program(Base):
    """Workout program created by a user for the MVP.

    Authentication is intentionally out of scope for Sprint 1, so this model
    does not yet include a user_id. That will be added when auth is introduced.
    """

    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    goal: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

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
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    program: Mapped[Program] = relationship(back_populates="workout_days")
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan",
    )


class WorkoutExercise(Base):
    """Exercise prescription inside a workout day.

    This is the MVP program-entry version of an exercise. A richer exercise
    library with YouTube video examples can be introduced later without blocking
    program building now.
    """

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
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    workout_day: Mapped[WorkoutDay] = relationship(back_populates="exercises")


__all__ = ["Base", "Program", "WorkoutDay", "WorkoutExercise"]
