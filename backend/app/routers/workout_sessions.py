from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/sessions", tags=["workout sessions"])


def get_session_or_404(session_id: int, db: Session) -> models.WorkoutSession:
    session = db.scalar(
        select(models.WorkoutSession)
        .options(
            selectinload(models.WorkoutSession.program),
            selectinload(models.WorkoutSession.workout_day),
            selectinload(models.WorkoutSession.session_sets),
        )
        .where(models.WorkoutSession.id == session_id)
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout session not found",
        )
    return session


def get_exercise_for_session_or_404(
    session: models.WorkoutSession,
    workout_exercise_id: int,
    db: Session,
) -> models.WorkoutExercise:
    exercise = db.get(models.WorkoutExercise, workout_exercise_id)
    if exercise is None or exercise.workout_day_id != session.workout_day_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found for this session",
        )
    return exercise


def get_session_set_or_404(
    session_id: int,
    session_set_id: int,
    db: Session,
) -> models.SessionSet:
    session_set = db.get(models.SessionSet, session_set_id)
    if session_set is None or session_set.workout_session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session set not found",
        )
    return session_set


def session_set_exists(
    session_id: int,
    workout_exercise_id: int,
    set_number: int,
    db: Session,
) -> bool:
    existing_id = db.scalar(
        select(models.SessionSet.id).where(
            models.SessionSet.workout_session_id == session_id,
            models.SessionSet.workout_exercise_id == workout_exercise_id,
            models.SessionSet.set_number == set_number,
        )
    )
    return existing_id is not None


@router.post("/start", response_model=schemas.WorkoutSessionRead, status_code=status.HTTP_201_CREATED)
def start_session(
    session_in: schemas.WorkoutSessionCreate,
    db: Session = Depends(get_db),
) -> models.WorkoutSession:
    program = db.get(models.Program, session_in.program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    workout_day = db.get(models.WorkoutDay, session_in.workout_day_id)
    if workout_day is None or workout_day.program_id != session_in.program_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")

    session = models.WorkoutSession(**session_in.model_dump(), status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    return get_session_or_404(session.id, db)


@router.get("/recent", response_model=list[schemas.WorkoutSessionRead])
def get_recent_sessions(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[models.WorkoutSession]:
    return list(
        db.scalars(
            select(models.WorkoutSession)
            .options(selectinload(models.WorkoutSession.session_sets))
            .order_by(models.WorkoutSession.started_at.desc())
            .limit(limit)
        )
    )


@router.get("/{session_id}", response_model=schemas.WorkoutSessionRead)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
) -> models.WorkoutSession:
    return get_session_or_404(session_id, db)


@router.post(
    "/{session_id}/sets",
    response_model=schemas.SessionSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_session_set(
    session_id: int,
    session_set_in: schemas.SessionSetCreate,
    db: Session = Depends(get_db),
) -> models.SessionSet:
    session = get_session_or_404(session_id, db)
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add sets to a finished session",
        )

    exercise = get_exercise_for_session_or_404(session, session_set_in.workout_exercise_id, db)
    if session_set_exists(
        session_id,
        session_set_in.workout_exercise_id,
        session_set_in.set_number,
        db,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session set already exists. Use update instead.",
        )

    session_set = models.SessionSet(
        workout_session_id=session_id,
        exercise_name_snapshot=exercise.movement_name,
        workout_day_name_snapshot=session.workout_day.name if session.workout_day else "",
        program_name_snapshot=session.program.name if session.program else "",
        planned_rest_seconds_snapshot=exercise.rest_seconds,
        **session_set_in.model_dump(),
    )
    db.add(session_set)
    db.commit()
    db.refresh(session_set)
    return session_set


@router.put("/{session_id}/sets/{session_set_id}", response_model=schemas.SessionSetRead)
def update_session_set(
    session_id: int,
    session_set_id: int,
    session_set_in: schemas.SessionSetUpdate,
    db: Session = Depends(get_db),
) -> models.SessionSet:
    session = get_session_or_404(session_id, db)
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update sets in a finished session",
        )

    session_set = get_session_set_or_404(session_id, session_set_id, db)
    updates = session_set_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(session_set, field, value)

    db.add(session_set)
    db.commit()
    db.refresh(session_set)
    return session_set


@router.post("/{session_id}/finish", response_model=schemas.WorkoutSessionRead)
def finish_session(
    session_id: int,
    finish_in: schemas.WorkoutSessionFinishRequest,
    db: Session = Depends(get_db),
) -> models.WorkoutSession:
    session = get_session_or_404(session_id, db)
    session.status = "completed"
    session.finished_at = datetime.utcnow()

    if finish_in.readiness_score is not None:
        session.readiness_score = finish_in.readiness_score
    if finish_in.notes is not None:
        session.notes = finish_in.notes

    db.add(session)
    db.commit()
    return get_session_or_404(session_id, db)
