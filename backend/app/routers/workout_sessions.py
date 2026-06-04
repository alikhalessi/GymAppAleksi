from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db
from app.models import utc_now
from app.services import ai_session_reflection
from app.services.progression import generate_progression_suggestions

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


@router.get("/dashboard-summary", response_model=schemas.DashboardSummaryRead)
def get_dashboard_summary(db: Session = Depends(get_db)) -> schemas.DashboardSummaryRead:
    sessions = list(
        db.scalars(
            select(models.WorkoutSession)
            .options(
                selectinload(models.WorkoutSession.program),
                selectinload(models.WorkoutSession.workout_day),
                selectinload(models.WorkoutSession.session_sets),
            )
            .order_by(models.WorkoutSession.started_at.desc(), models.WorkoutSession.id.desc())
        )
    )
    completed_sessions = [session for session in sessions if session.status == "completed"]
    active_sessions = [session for session in sessions if session.status == "active"]
    session_sets = [session_set for session in sessions for session_set in session.session_sets]
    completed_sets = [session_set for session_set in session_sets if session_set.completed]
    ratings = [
        session_set.difficulty_rating
        for session_set in completed_sets
        if session_set.difficulty_rating is not None
    ]
    latest_session = completed_sessions[0] if completed_sessions else None
    latest_reflection_summary: str | None = None
    latest_progression_suggestions: list[str] = []
    latest_exercise_names: list[str] = []

    if latest_session is not None:
        seen_exercise_names: set[str] = set()
        for session_set in sorted(
            latest_session.session_sets,
            key=lambda item: (item.created_at, item.id),
        ):
            exercise_name = session_set.exercise_name_snapshot.strip() or f"Exercise #{session_set.workout_exercise_id}"
            if exercise_name not in seen_exercise_names:
                latest_exercise_names.append(exercise_name)
                seen_exercise_names.add(exercise_name)

        latest_reflection = db.scalar(
            select(models.SessionReflection)
            .where(models.SessionReflection.workout_session_id == latest_session.id)
            .order_by(models.SessionReflection.created_at.desc(), models.SessionReflection.id.desc())
        )
        if latest_reflection is not None:
            latest_reflection_summary = latest_reflection.summary

        suggestions = list(
            db.scalars(
                select(models.ProgressionSuggestion)
                .where(models.ProgressionSuggestion.workout_session_id == latest_session.id)
                .order_by(models.ProgressionSuggestion.id.asc())
            )
        )
        latest_progression_suggestions = [
            " - ".join(
                item
                for item in [
                    suggestion.exercise_name_snapshot.strip() or "Exercise",
                    suggestion.suggestion_type.replace("_", " "),
                    suggestion.rationale,
                ]
                if item
            )
            for suggestion in suggestions
        ]

    return schemas.DashboardSummaryRead(
        total_sessions=len(sessions),
        completed_sessions=len(completed_sessions),
        active_sessions=len(active_sessions),
        total_logged_sets=len(session_sets),
        completed_sets=len(completed_sets),
        average_difficulty=(sum(ratings) / len(ratings)) if ratings else None,
        latest_completed_session_id=latest_session.id if latest_session else None,
        latest_completed_session_started_at=latest_session.started_at if latest_session else None,
        latest_completed_session_finished_at=latest_session.finished_at if latest_session else None,
        latest_program_name=latest_session.program.name if latest_session and latest_session.program else None,
        latest_workout_day_name=latest_session.workout_day.name if latest_session and latest_session.workout_day else None,
        latest_exercise_names=latest_exercise_names,
        latest_reflection_summary=latest_reflection_summary,
        latest_progression_suggestions=latest_progression_suggestions,
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
    session.finished_at = utc_now()

    if finish_in.readiness_score is not None:
        session.readiness_score = finish_in.readiness_score
    if finish_in.notes is not None:
        session.notes = finish_in.notes

    db.add(session)
    db.commit()
    return get_session_or_404(session_id, db)


@router.post("/{session_id}/reflection", response_model=schemas.SessionReflectionRead)
def generate_session_reflection(
    session_id: int,
    db: Session = Depends(get_db),
) -> models.SessionReflection:
    session = get_session_or_404(session_id, db)
    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI reflection is available only after finishing the session.",
        )

    reflection_data, model_used = ai_session_reflection.generate_session_reflection_with_ai(session)
    reflection = models.SessionReflection(
        workout_session_id=session.id,
        model_used=model_used,
        **reflection_data,
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)
    return reflection


@router.get("/{session_id}/reflection", response_model=schemas.SessionReflectionRead)
def get_session_reflection(
    session_id: int,
    db: Session = Depends(get_db),
) -> models.SessionReflection:
    session = get_session_or_404(session_id, db)
    reflection = db.scalar(
        select(models.SessionReflection)
        .where(models.SessionReflection.workout_session_id == session.id)
        .order_by(models.SessionReflection.created_at.desc(), models.SessionReflection.id.desc())
    )
    if reflection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reflection found for this session.",
        )
    return reflection


@router.post(
    "/{session_id}/progression-suggestions",
    response_model=list[schemas.ProgressionSuggestionRead],
)
def generate_session_progression_suggestions(
    session_id: int,
    db: Session = Depends(get_db),
) -> list[models.ProgressionSuggestion]:
    session = get_session_or_404(session_id, db)
    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progression suggestions are available only after finishing the session.",
        )

    db.execute(
        delete(models.ProgressionSuggestion).where(
            models.ProgressionSuggestion.workout_session_id == session.id,
        )
    )
    suggestions = [
        models.ProgressionSuggestion(**suggestion)
        for suggestion in generate_progression_suggestions(session)
    ]
    db.add_all(suggestions)
    db.commit()
    for suggestion in suggestions:
        db.refresh(suggestion)
    return suggestions


@router.get(
    "/{session_id}/progression-suggestions",
    response_model=list[schemas.ProgressionSuggestionRead],
)
def get_session_progression_suggestions(
    session_id: int,
    db: Session = Depends(get_db),
) -> list[models.ProgressionSuggestion]:
    session = get_session_or_404(session_id, db)
    return list(
        db.scalars(
            select(models.ProgressionSuggestion)
            .where(models.ProgressionSuggestion.workout_session_id == session.id)
            .order_by(models.ProgressionSuggestion.id.asc())
        )
    )
