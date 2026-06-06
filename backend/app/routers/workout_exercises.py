from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.auth import AuthUser, get_current_user, get_effective_user_id
from app.services.ownership import ownership_filter, require_owned

router = APIRouter(
    prefix="/programs/{program_id}/workout-days/{workout_day_id}/exercises",
    tags=["workout exercises"],
)


def get_program_or_404(program_id: int, db: Session, current_user: AuthUser) -> models.Program:
    program = db.get(models.Program, program_id)
    return require_owned(program, current_user, "Program not found")


def get_workout_day_or_404(
    program_id: int,
    workout_day_id: int,
    db: Session,
    current_user: AuthUser,
) -> models.WorkoutDay:
    workout_day = db.get(models.WorkoutDay, workout_day_id)
    if workout_day is None or workout_day.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout day not found",
        )
    return require_owned(workout_day, current_user, "Workout day not found")


def get_workout_exercise_or_404(
    workout_day_id: int,
    exercise_id: int,
    db: Session,
    current_user: AuthUser,
) -> models.WorkoutExercise:
    exercise = db.get(models.WorkoutExercise, exercise_id)
    if exercise is None or exercise.workout_day_id != workout_day_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found",
        )
    return require_owned(exercise, current_user, "Workout exercise not found")


@router.post("", response_model=schemas.WorkoutExerciseRead, status_code=status.HTTP_201_CREATED)
def create_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_in: schemas.WorkoutExerciseCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db, current_user)
    get_workout_day_or_404(program_id, workout_day_id, db, current_user)

    exercise = models.WorkoutExercise(
        workout_day_id=workout_day_id,
        user_id=get_effective_user_id(current_user),
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
    current_user: AuthUser = Depends(get_current_user),
) -> list[models.WorkoutExercise]:
    get_program_or_404(program_id, db, current_user)
    get_workout_day_or_404(program_id, workout_day_id, db, current_user)

    return list(
        db.scalars(
            select(models.WorkoutExercise)
            .where(models.WorkoutExercise.workout_day_id == workout_day_id)
            .where(ownership_filter(models.WorkoutExercise, current_user))
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
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db, current_user)
    get_workout_day_or_404(program_id, workout_day_id, db, current_user)
    return get_workout_exercise_or_404(workout_day_id, exercise_id, db, current_user)


@router.put("/{exercise_id}", response_model=schemas.WorkoutExerciseRead)
def update_workout_exercise(
    program_id: int,
    workout_day_id: int,
    exercise_id: int,
    exercise_in: schemas.WorkoutExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutExercise:
    get_program_or_404(program_id, db, current_user)
    get_workout_day_or_404(program_id, workout_day_id, db, current_user)
    exercise = get_workout_exercise_or_404(workout_day_id, exercise_id, db, current_user)

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
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    get_program_or_404(program_id, db, current_user)
    get_workout_day_or_404(program_id, workout_day_id, db, current_user)
    exercise = get_workout_exercise_or_404(workout_day_id, exercise_id, db, current_user)
    db.delete(exercise)
    db.commit()
