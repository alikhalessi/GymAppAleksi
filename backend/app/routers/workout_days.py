from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.auth import AuthUser, get_current_user, get_effective_user_id
from app.services.ownership import ownership_filter, require_owned

router = APIRouter(prefix="/programs/{program_id}/workout-days", tags=["workout days"])


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


@router.post("", response_model=schemas.WorkoutDayRead, status_code=status.HTTP_201_CREATED)
def create_workout_day(
    program_id: int,
    workout_day_in: schemas.WorkoutDayCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db, current_user)
    workout_day = models.WorkoutDay(
        program_id=program_id,
        user_id=get_effective_user_id(current_user),
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
    current_user: AuthUser = Depends(get_current_user),
) -> list[models.WorkoutDay]:
    get_program_or_404(program_id, db, current_user)
    return list(
        db.scalars(
            select(models.WorkoutDay)
            .where(models.WorkoutDay.program_id == program_id)
            .where(ownership_filter(models.WorkoutDay, current_user))
            .order_by(models.WorkoutDay.day_order.asc(), models.WorkoutDay.created_at.asc())
        )
    )


@router.get("/{workout_day_id}", response_model=schemas.WorkoutDayRead)
def get_workout_day(
    program_id: int,
    workout_day_id: int,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db, current_user)
    return get_workout_day_or_404(program_id, workout_day_id, db, current_user)


@router.put("/{workout_day_id}", response_model=schemas.WorkoutDayRead)
def update_workout_day(
    program_id: int,
    workout_day_id: int,
    workout_day_in: schemas.WorkoutDayUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.WorkoutDay:
    get_program_or_404(program_id, db, current_user)
    workout_day = get_workout_day_or_404(program_id, workout_day_id, db, current_user)

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
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    get_program_or_404(program_id, db, current_user)
    workout_day = get_workout_day_or_404(program_id, workout_day_id, db, current_user)
    db.delete(workout_day)
    db.commit()
