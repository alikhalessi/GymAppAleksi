import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db
from app.models import utc_now
from app.services import ai_change_proposal

router = APIRouter(prefix="/plan-change-proposals", tags=["plan change proposals"])

ALLOWED_PROPOSAL_STATUSES = {"draft", "accepted", "rejected", "archived"}


def get_proposal_or_404(proposal_id: int, db: Session) -> models.PlanChangeProposal:
    proposal = db.get(models.PlanChangeProposal, proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan change proposal not found",
        )
    return proposal


def validate_status_filter(status_filter: str | None) -> None:
    if status_filter is not None and status_filter not in ALLOWED_PROPOSAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid proposal status.",
        )


def get_program_with_plan_context(db: Session, program_id: int) -> models.Program:
    program = db.scalar(
        select(models.Program)
        .options(
            selectinload(models.Program.versions),
            selectinload(models.Program.workout_days).selectinload(models.WorkoutDay.exercises),
        )
        .where(models.Program.id == program_id)
    )
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program


def validate_and_resolve_context(
    request: schemas.PlanChangeProposalRequest,
    db: Session,
) -> tuple[
    models.Program | None,
    models.ProgramVersion | None,
    models.WorkoutDay | None,
    models.WorkoutSession | None,
]:
    program: models.Program | None = None
    version: models.ProgramVersion | None = None
    workout_day: models.WorkoutDay | None = None
    session: models.WorkoutSession | None = None
    resolved_program_id = request.program_id

    if request.program_version_id is not None:
        version = db.get(models.ProgramVersion, request.program_version_id)
        if version is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program version not found")
        if resolved_program_id is not None and version.program_id != resolved_program_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program version not found")
        resolved_program_id = version.program_id

    if request.workout_day_id is not None:
        workout_day = db.get(models.WorkoutDay, request.workout_day_id)
        if workout_day is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")
        if resolved_program_id is not None and workout_day.program_id != resolved_program_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")
        resolved_program_id = workout_day.program_id

    if request.workout_session_id is not None:
        session = db.scalar(
            select(models.WorkoutSession)
            .options(selectinload(models.WorkoutSession.session_sets))
            .where(models.WorkoutSession.id == request.workout_session_id)
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout session not found")
        if resolved_program_id is not None and session.program_id != resolved_program_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout session not found")
        if workout_day is not None and session.workout_day_id != workout_day.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout session not found")
        resolved_program_id = session.program_id

    if resolved_program_id is not None:
        program = get_program_with_plan_context(db, resolved_program_id)

    if version is None and program is not None:
        version = next((item for item in program.versions if item.is_active), None)

    return program, version, workout_day, session


def build_program_context(program: models.Program | None) -> dict[str, Any] | None:
    if program is None:
        return None

    workout_days = sorted(program.workout_days, key=lambda item: (item.day_order, item.id))
    return {
        "id": program.id,
        "name": program.name,
        "goal": program.goal,
        "duration_weeks": program.duration_weeks,
        "workout_days": [
            {
                "id": day.id,
                "name": day.name,
                "day_order": day.day_order,
                "exercises": [
                    {
                        "id": exercise.id,
                        "movement_name": exercise.movement_name,
                        "sets": exercise.sets,
                        "reps": exercise.reps,
                        "rest_seconds": exercise.rest_seconds,
                        "notes": exercise.notes,
                        "exercise_order": exercise.exercise_order,
                    }
                    for exercise in sorted(day.exercises, key=lambda item: (item.exercise_order, item.id))
                ],
            }
            for day in workout_days
        ],
    }


def build_version_context(version: models.ProgramVersion | None) -> dict[str, Any] | None:
    if version is None:
        return None
    return {
        "id": version.id,
        "program_id": version.program_id,
        "version_label": version.version_label,
        "version_type": version.version_type,
        "source": version.source,
        "is_active": version.is_active,
        "notes": version.notes,
    }


def build_day_context(day: models.WorkoutDay | None) -> dict[str, Any] | None:
    if day is None:
        return None
    return {"id": day.id, "program_id": day.program_id, "name": day.name, "day_order": day.day_order}


def build_session_context(session: models.WorkoutSession | None) -> dict[str, Any] | None:
    if session is None:
        return None
    return {
        "id": session.id,
        "program_id": session.program_id,
        "workout_day_id": session.workout_day_id,
        "status": session.status,
        "readiness_score": session.readiness_score,
        "notes": session.notes,
        "sets": [
            {
                "exercise_name_snapshot": session_set.exercise_name_snapshot,
                "set_number": session_set.set_number,
                "planned_reps": session_set.planned_reps,
                "planned_weight": session_set.planned_weight,
                "actual_reps": session_set.actual_reps,
                "actual_weight": session_set.actual_weight,
                "weight_unit": session_set.weight_unit,
                "difficulty_rating": session_set.difficulty_rating,
                "completed": session_set.completed,
                "notes": session_set.notes,
            }
            for session_set in sorted(
                session.session_sets,
                key=lambda item: (item.exercise_name_snapshot, item.set_number, item.id),
            )
        ],
    }


def build_profile_context(db: Session) -> dict[str, Any] | None:
    profile = db.scalar(select(models.TraineeProfile).order_by(models.TraineeProfile.id.asc()))
    if profile is None:
        return None
    return {
        "age": profile.age,
        "sex": profile.sex,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "bmi": profile.bmi,
        "training_experience": profile.training_experience,
        "primary_goal": profile.primary_goal,
        "limitations": profile.limitations,
        "available_equipment": profile.available_equipment,
        "preferred_session_minutes": profile.preferred_session_minutes,
        "notes": profile.notes,
    }


def build_readiness_context(db: Session) -> dict[str, Any] | None:
    readiness = db.scalar(
        select(models.ReadinessCheck).order_by(
            models.ReadinessCheck.created_at.desc(),
            models.ReadinessCheck.id.desc(),
        )
    )
    if readiness is None:
        return None
    return {
        "energy_level": readiness.energy_level,
        "sleep_quality": readiness.sleep_quality,
        "soreness_level": readiness.soreness_level,
        "stress_level": readiness.stress_level,
        "pain_or_limitations_today": readiness.pain_or_limitations_today,
        "available_time_minutes": readiness.available_time_minutes,
        "readiness_score": readiness.readiness_score,
        "notes": readiness.notes,
        "created_at": readiness.created_at.isoformat(),
    }


def build_change_proposal_payload(
    request: schemas.PlanChangeProposalRequest,
    program: models.Program | None,
    version: models.ProgramVersion | None,
    workout_day: models.WorkoutDay | None,
    session: models.WorkoutSession | None,
    db: Session,
) -> dict[str, Any]:
    return {
        "instruction": "Create advisory proposed changes only. Do not mutate the workout plan.",
        "user_request": request.user_request,
        "context_note": request.context_note,
        "program": build_program_context(program),
        "active_or_selected_program_version": build_version_context(version),
        "selected_workout_day": build_day_context(workout_day),
        "selected_workout_session": build_session_context(session),
        "latest_trainee_profile": build_profile_context(db),
        "latest_readiness_check": build_readiness_context(db),
    }


@router.post("", response_model=schemas.PlanChangeProposalRead, status_code=status.HTTP_201_CREATED)
def create_plan_change_proposal(
    request: schemas.PlanChangeProposalRequest,
    db: Session = Depends(get_db),
) -> models.PlanChangeProposal:
    program, version, workout_day, session = validate_and_resolve_context(request, db)
    payload = build_change_proposal_payload(request, program, version, workout_day, session, db)
    proposal_data, model_used = ai_change_proposal.generate_change_proposal_with_ai(payload)

    proposal = models.PlanChangeProposal(
        program_id=program.id if program else None,
        program_version_id=version.id if version else None,
        workout_day_id=workout_day.id if workout_day else None,
        workout_session_id=session.id if session else None,
        user_request=request.user_request,
        proposal_title=str(proposal_data.get("proposal_title", ""))[:160],
        proposal_summary=str(proposal_data.get("proposal_summary", "")),
        proposed_changes_json=json.dumps(proposal_data.get("proposed_changes", []), ensure_ascii=False),
        caution_notes=str(proposal_data.get("caution_notes", "")),
        trainer_review_recommended=bool(proposal_data.get("trainer_review_recommended", False)),
        status="draft",
        model_used=model_used,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("", response_model=list[schemas.PlanChangeProposalRead])
def list_plan_change_proposals(
    program_id: int | None = Query(default=None, ge=1),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[models.PlanChangeProposal]:
    validate_status_filter(status_filter)
    query = select(models.PlanChangeProposal)
    if program_id is not None:
        query = query.where(models.PlanChangeProposal.program_id == program_id)
    if status_filter is not None:
        query = query.where(models.PlanChangeProposal.status == status_filter)

    return list(
        db.scalars(
            query.order_by(
                models.PlanChangeProposal.created_at.desc(),
                models.PlanChangeProposal.id.desc(),
            ).limit(limit)
        )
    )


@router.get("/{proposal_id}", response_model=schemas.PlanChangeProposalRead)
def get_plan_change_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
) -> models.PlanChangeProposal:
    return get_proposal_or_404(proposal_id, db)


@router.put("/{proposal_id}/status", response_model=schemas.PlanChangeProposalRead)
def update_plan_change_proposal_status(
    proposal_id: int,
    status_update: schemas.PlanChangeProposalStatusUpdate,
    db: Session = Depends(get_db),
) -> models.PlanChangeProposal:
    proposal = get_proposal_or_404(proposal_id, db)
    proposal.status = status_update.status
    proposal.updated_at = utc_now()
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal
