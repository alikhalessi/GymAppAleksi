from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/programs/{program_id}/workout-days/{workout_day_id}/exercises",
    tags=["workout exercises"],
)


def get_program_or_404(program_id: int, db: Session) -> models.Program:
    program = db.get(models.Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    return program


def get_workout_day_or_404(
    program_id: int,
    workout_day_id: int,
    db: Session,
) -> models.WorkoutDay:
    workout_day = db.get(models.WorkoutDay, workout_day_id)
    if workout_day is None or workout_day.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout day not found",
        )
    return workout_day


def get_workout_exercise_or_404(
    workout_day_id: int,
    exercise_id: int,
    db: Session,
) -> models.WorkoutExercise:
    exercise = db.get(models.WorkoutExercise, exercise_id)
    if exercise is None or exercise.workout_day_id != workout_day_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found",
        )
    return exercise


@router.post("", response_model=schemas.WorkoutExerciseRead, status_code=status.HTTP_201_CREATED)
def create_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_in: schemas.WorkoutExerciseCreate,
    db: Session = Depends(get_db),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db)
    get_workout_day_or_404(program_id, workout_day_id, db)

    exercise = models.WorkoutExercise(
        workout_day_id=workout_day_id,
        **exercise_in.model_dump(),
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("", response_model=list[schemas.WorkoutExerciseRead])
def list_workout_exercises(
    program_id: int,
    workout_day_id: int,
    db: Session = Depends(get_db),
) -> list[models.WorkoutExercise]:
    get_program_or_404(program_id, db)
    get_workout_day_or_404(program_id, workout_day_id, db)

    return list(
        db.scalars(
            select(models.WorkoutExercise)
            .where(models.WorkoutExercise.workout_day_id == workout_day_id)
            .order_by(
                models.WorkoutExercise.exercise_order.asc(),
                models.WorkoutExercise.created_at.asc(),
            )
        )
    )


@router.get("/{exercise_id}", response_model=schemas.WorkoutExerciseRead)
def get_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_id: int,
    db: Session = Depends(get_db),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db)
    get_workout_day_or_404(program_id, workout_day_id, db)
    return get_workout_exercise_or_404(workout_day_id, exercise_id, db)


@router.put("/{exercise_id}", response_model=schemas.WorkoutExerciseRead)
def update_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_id: int,
    exercise_in: schemas.WorkoutExerciseUpdate,
    db: Session = Depends(get_db),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db)
    get_workout_day_or_404(program_id, workout_day_id, db)
    exercise = get_workout_exercise_or_404(workout_day_id, exercise_id, db)

    updates = exercise_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(exercise, field, value)

    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_id: int,
    db: Session = Depends(get_db),
) -> None:
    get_program_or_404(program_id, db)
    get_workout_day_or_404(program_id, workout_day_id, db)
    exercise = get_workout_exercise_or_404(workout_day_id, exercise_id, db)
    db.delete(exercise)
    db.commit()
