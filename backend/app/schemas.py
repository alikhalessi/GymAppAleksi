from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    goal: str = Field(..., min_length=1, max_length=255)
    duration_weeks: int = Field(..., ge=1, le=104)


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    goal: str | None = Field(default=None, min_length=1, max_length=255)
    duration_weeks: int | None = Field(default=None, ge=1, le=104)


class ProgramRead(ProgramBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutDayBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    day_order: int = Field(..., ge=1, le=14)


class WorkoutDayCreate(WorkoutDayBase):
    pass


class WorkoutDayUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    day_order: int | None = Field(default=None, ge=1, le=14)


class WorkoutDayRead(WorkoutDayBase):
    id: int
    program_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutExerciseBase(BaseModel):
    movement_name: str = Field(..., min_length=1, max_length=160)
    sets: int = Field(..., ge=1, le=20)
    reps: str = Field(..., min_length=1, max_length=40)
    rest_seconds: int = Field(..., ge=0, le=900)
    notes: str = Field(default="", max_length=1000)
    exercise_order: int = Field(..., ge=1, le=100)


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseUpdate(BaseModel):
    movement_name: str | None = Field(default=None, min_length=1, max_length=160)
    sets: int | None = Field(default=None, ge=1, le=20)
    reps: str | None = Field(default=None, min_length=1, max_length=40)
    rest_seconds: int | None = Field(default=None, ge=0, le=900)
    notes: str | None = Field(default=None, max_length=1000)
    exercise_order: int | None = Field(default=None, ge=1, le=100)


class WorkoutExerciseRead(WorkoutExerciseBase):
    id: int
    workout_day_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OpenAIKeySetRequest(BaseModel):
    api_key: str = Field(..., min_length=10, max_length=300)


class OpenAIKeyStatus(BaseModel):
    configured: bool
    source: str | None = None
    masked_key: str | None = None


class WorkoutPlanImportRequest(BaseModel):
    raw_text: str = Field(..., min_length=10, max_length=12000)


class AIParsedExercise(WorkoutExerciseBase):
    confidence: float = Field(..., ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)


class AIParsedWorkoutDay(WorkoutDayBase):
    exercises: list[AIParsedExercise] = Field(default_factory=list)


class AIParsedProgram(ProgramBase):
    pass


class AIParsedWorkoutPlan(BaseModel):
    program: AIParsedProgram
    workout_days: list[AIParsedWorkoutDay]


class WorkoutPlanImportAnalysis(BaseModel):
    parsed_plan: AIParsedWorkoutPlan
    overall_confidence: float = Field(..., ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
    questions_for_user: list[str] = Field(default_factory=list)
    trainer_review_required: bool


class WorkoutPlanCommitRequest(BaseModel):
    parsed_plan: AIParsedWorkoutPlan
    approval_status: str = Field(default="approved_by_user", max_length=60)


class WorkoutPlanCommitResponse(BaseModel):
    program: ProgramRead
    workout_days: list[WorkoutDayRead]
    exercises: list[WorkoutExerciseRead]
    approval_status: str


class TraineeReadinessProfile(BaseModel):
    training_experience: str = Field(..., max_length=80)
    primary_goal: str = Field(..., max_length=120)
    energy_level: int = Field(..., ge=1, le=10)
    sleep_quality: int = Field(..., ge=1, le=10)
    soreness_level: int = Field(..., ge=1, le=10)
    stress_level: int = Field(..., ge=1, le=10)
    pain_or_limitations: str = Field(default="", max_length=1200)
    available_equipment: str = Field(default="", max_length=1200)
    session_time_limit_minutes: int | None = Field(default=None, ge=10, le=240)
    difficulty_preference: str = Field(default="moderate", max_length=80)
    extra_notes: str = Field(default="", max_length=1600)


class WorkoutPlanEnhanceRequest(BaseModel):
    parsed_plan: AIParsedWorkoutPlan
    readiness: TraineeReadinessProfile


class WorkoutPlanChange(BaseModel):
    day_name: str
    exercise_name: str | None = None
    change_type: str = Field(..., max_length=80)
    original: str = Field(..., max_length=1000)
    adjusted: str = Field(..., max_length=1000)
    reason: str = Field(..., max_length=1200)


class WorkoutPlanEnhancementResponse(BaseModel):
    adjusted_plan: AIParsedWorkoutPlan
    changes: list[WorkoutPlanChange] = Field(default_factory=list)
    summary: str = Field(..., max_length=2000)
    warnings: list[str] = Field(default_factory=list)
    questions_for_user: list[str] = Field(default_factory=list)
    trainer_review_required: bool
