from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/exercises/{exercise_id}/planned-sets",
    tags=["planned sets"],
)


def get_exercise_or_404(exercise_id: int, db: Session) -> models.WorkoutExercise:
    exercise = db.get(models.WorkoutExercise, exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found",
        )
    return exercise


def get_planned_set_or_404(
    exercise_id: int,
    planned_set_id: int,
    db: Session,
) -> models.PlannedSet:
    planned_set = db.get(models.PlannedSet, planned_set_id)
    if planned_set is None or planned_set.workout_exercise_id != exercise_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned set not found",
        )
    return planned_set


@router.post("", response_model=schemas.PlannedSetRead, status_code=status.HTTP_201_CREATED)
def create_planned_set(
    exercise_id: int,
    planned_set_in: schemas.PlannedSetCreate,
    db: Session = Depends(get_db),
) -> models.PlannedSet:
    get_exercise_or_404(exercise_id, db)
    planned_set = models.PlannedSet(
        workout_exercise_id=exercise_id,
        **planned_set_in.model_dump(),
    )
    db.add(planned_set)
    db.commit()
    db.refresh(planned_set)
    return planned_set


@router.get("", response_model=list[schemas.PlannedSetRead])
def list_planned_sets(
    exercise_id: int,
    db: Session = Depends(get_db),
) -> list[models.PlannedSet]:
    get_exercise_or_404(exercise_id, db)
    return list(
        db.scalars(
            select(models.PlannedSet)
            .where(models.PlannedSet.workout_exercise_id == exercise_id)
            .order_by(models.PlannedSet.set_number.asc(), models.PlannedSet.created_at.asc())
        )
    )


@router.put("/{planned_set_id}", response_model=schemas.PlannedSetRead)
def update_planned_set(
    exercise_id: int,
    planned_set_id: int,
    planned_set_in: schemas.PlannedSetUpdate,
    db: Session = Depends(get_db),
) -> models.PlannedSet:
    get_exercise_or_404(exercise_id, db)
    planned_set = get_planned_set_or_404(exercise_id, planned_set_id, db)

    updates = planned_set_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(planned_set, field, value)

    db.add(planned_set)
    db.commit()
    db.refresh(planned_set)
    return planned_set


@router.delete("/{planned_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planned_set(
    exercise_id: int,
    planned_set_id: int,
    db: Session = Depends(get_db),
) -> None:
    get_exercise_or_404(exercise_id, db)
    planned_set = get_planned_set_or_404(exercise_id, planned_set_id, db)
    db.delete(planned_set)
    db.commit()
