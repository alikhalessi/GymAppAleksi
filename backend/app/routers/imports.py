from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.ai_import import analyze_workout_plan_with_ai

router = APIRouter(prefix="/imports/workout-plan", tags=["workout plan imports"])


@router.post("/analyze", response_model=schemas.WorkoutPlanImportAnalysis)
def analyze_workout_plan(
    request: schemas.WorkoutPlanImportRequest,
) -> schemas.WorkoutPlanImportAnalysis:
    return analyze_workout_plan_with_ai(request.raw_text)


@router.post(
    "/save",
    response_model=schemas.WorkoutPlanCommitResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_workout_plan_import(
    request: schemas.WorkoutPlanCommitRequest,
    db: Session = Depends(get_db),
) -> schemas.WorkoutPlanCommitResponse:
    parsed_plan = request.parsed_plan

    program = models.Program(
        name=parsed_plan.program.name,
        goal=parsed_plan.program.goal,
        duration_weeks=parsed_plan.program.duration_weeks,
    )
    db.add(program)
    db.flush()

    created_days: list[models.WorkoutDay] = []
    created_exercises: list[models.WorkoutExercise] = []

    for day in parsed_plan.workout_days:
        workout_day = models.WorkoutDay(
            program_id=program.id,
            name=day.name,
            day_order=day.day_order,
        )
        db.add(workout_day)
        db.flush()
        created_days.append(workout_day)

        for exercise in day.exercises:
            workout_exercise = models.WorkoutExercise(
                workout_day_id=workout_day.id,
                movement_name=exercise.movement_name,
                sets=exercise.sets,
                reps=exercise.reps,
                rest_seconds=exercise.rest_seconds,
                notes=exercise.notes,
                exercise_order=exercise.exercise_order,
            )
            db.add(workout_exercise)
            created_exercises.append(workout_exercise)

    db.commit()
    db.refresh(program)

    for workout_day in created_days:
        db.refresh(workout_day)
    for exercise in created_exercises:
        db.refresh(exercise)

    return schemas.WorkoutPlanCommitResponse(
        program=program,
        workout_days=created_days,
        exercises=created_exercises,
        approval_status=request.approval_status,
    )
