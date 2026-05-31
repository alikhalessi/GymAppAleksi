from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/programs/{program_id}/workout-days", tags=["workout days"])


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


@router.post("", response_model=schemas.WorkoutDayRead, status_code=status.HTTP_201_CREATED)
def create_workout_day(
    program_id: int,
    workout_day_in: schemas.WorkoutDayCreate,
    db: Session = Depends(get_db),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db)
    workout_day = models.WorkoutDay(
        program_id=program_id,
        **workout_day_in.model_dump(),
    )
    db.add(workout_day)
    db.commit()
    db.refresh(workout_day)
    return workout_day


@router.get("", response_model=list[schemas.WorkoutDayRead])
def list_workout_days(
    program_id: int,
    db: Session = Depends(get_db),
) -> list[models.WorkoutDay]:
    get_program_or_404(program_id, db)
    return list(
        db.scalars(
            select(models.WorkoutDay)
            .where(models.WorkoutDay.program_id == program_id)
            .order_by(models.WorkoutDay.day_order.asc(), models.WorkoutDay.created_at.asc())
        )
    )


@router.get("/{workout_day_id}", response_model=schemas.WorkoutDayRead)
def get_workout_day(
    program_id: int,
    workout_day_id: int,
    db: Session = Depends(get_db),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db)
    return get_workout_day_or_404(program_id, workout_day_id, db)


@router.put("/{workout_day_id}", response_model=schemas.WorkoutDayRead)
def update_workout_day(
    program_id: int,
    workout_day_id: int,
    workout_day_in: schemas.WorkoutDayUpdate,
    db: Session = Depends(get_db),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db)
    workout_day = get_workout_day_or_404(program_id, workout_day_id, db)

    updates = workout_day_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(workout_day, field, value)

    db.add(workout_day)
    db.commit()
    db.refresh(workout_day)
    return workout_day


@router.delete("/{workout_day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_day(
    program_id: int,
    workout_day_id: int,
    db: Session = Depends(get_db),
) -> None:
    get_program_or_404(program_id, db)
    workout_day = get_workout_day_or_404(program_id, workout_day_id, db)
    db.delete(workout_day)
    db.commit()
