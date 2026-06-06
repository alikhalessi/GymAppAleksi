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


class ProgramVersionBase(BaseModel):
    version_label: str = Field(default="", max_length=120)
    version_type: str = Field(..., max_length=80)
    source: str = Field(default="", max_length=80)
    parent_version_id: int | None = None
    is_active: bool = False
    notes: str = Field(default="", max_length=10000)


class ProgramVersionCreate(ProgramVersionBase):
    pass


class ProgramVersionUpdate(BaseModel):
    version_label: str | None = Field(default=None, max_length=120)
    version_type: str | None = Field(default=None, max_length=80)
    source: str | None = Field(default=None, max_length=80)
    parent_version_id: int | None = None
    is_active: bool | None = None
    notes: str | None = Field(default=None, max_length=10000)


class ProgramVersionRead(ProgramVersionBase):
    id: int
    program_id: int
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


class PlannedSetBase(BaseModel):
    set_number: int = Field(..., ge=1, le=30)
    target_reps: str = Field(..., min_length=1, max_length=40)
    suggested_weight: float | None = Field(default=None, ge=0, le=1000)
    weight_unit: str = Field(default="kg", min_length=1, max_length=10)
    note: str = Field(default="", max_length=1000)


class PlannedSetCreate(PlannedSetBase):
    pass


class PlannedSetUpdate(BaseModel):
    set_number: int | None = Field(default=None, ge=1, le=30)
    target_reps: str | None = Field(default=None, min_length=1, max_length=40)
    suggested_weight: float | None = Field(default=None, ge=0, le=1000)
    weight_unit: str | None = Field(default=None, min_length=1, max_length=10)
    note: str | None = Field(default=None, max_length=1000)


class PlannedSetRead(PlannedSetBase):
    id: int
    workout_exercise_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class YouTubeVideoBase(BaseModel):
    youtube_video_id: str = Field(..., min_length=5, max_length=40)
    title: str = Field(..., min_length=1, max_length=255)
    channel_name: str = Field(default="", max_length=160)
    thumbnail_url: str = Field(default="", max_length=500)
    display_order: int = Field(default=1, ge=1, le=20)
    approved: bool = True


class YouTubeVideoCreate(YouTubeVideoBase):
    pass


class YouTubeVideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    channel_name: str | None = Field(default=None, max_length=160)
    thumbnail_url: str | None = Field(default=None, max_length=500)
    display_order: int | None = Field(default=None, ge=1, le=20)
    approved: bool | None = None


class YouTubeVideoRead(YouTubeVideoBase):
    id: int
    workout_exercise_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OpenAIKeySetRequest(BaseModel):
    api_key: str = Field(..., min_length=10, max_length=300)


class OpenAIKeyStatus(BaseModel):
    configured: bool
    source: str | None = None
    masked_key: str | None = None


class AuthStatus(BaseModel):
    auth_required: bool
    supabase_url_configured: bool
    jwt_secret_configured: bool
    jwks_url_configured: bool
    verification_configured: bool
    verification_mode: str


class AuthUserRead(BaseModel):
    user_id: str
    email: str | None = None
    raw_claims: dict


class AuthMeResponse(BaseModel):
    authenticated: bool
    auth_required: bool
    verification_configured: bool
    user: AuthUserRead | None = None
    message: str


class TraineeProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=10, le=100)
    sex: str | None = Field(default=None, max_length=40)
    height_cm: float | None = Field(default=None, ge=80, le=250)
    weight_kg: float | None = Field(default=None, ge=20, le=350)
    training_experience: str | None = Field(default=None, max_length=80)
    primary_goal: str | None = Field(default=None, max_length=200)
    limitations: str | None = Field(default=None, max_length=6000)
    available_equipment: str | None = Field(default=None, max_length=4000)
    preferred_session_minutes: int | None = Field(default=None, ge=10, le=240)
    notes: str | None = Field(default=None, max_length=12000)


class TraineeProfileRead(BaseModel):
    id: int
    display_name: str
    age: int | None
    sex: str
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    training_experience: str
    primary_goal: str
    limitations: str
    available_equipment: str
    preferred_session_minutes: int | None
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReadinessCheckCreate(BaseModel):
    energy_level: int | None = Field(default=None, ge=1, le=10)
    sleep_quality: int | None = Field(default=None, ge=1, le=10)
    soreness_level: int | None = Field(default=None, ge=1, le=10)
    stress_level: int | None = Field(default=None, ge=1, le=10)
    pain_or_limitations_today: str = Field(default="", max_length=6000)
    available_time_minutes: int | None = Field(default=None, ge=1, le=240)
    notes: str = Field(default="", max_length=2000)


class ReadinessCheckRead(BaseModel):
    id: int
    energy_level: int | None
    sleep_quality: int | None
    soreness_level: int | None
    stress_level: int | None
    pain_or_limitations_today: str
    available_time_minutes: int | None
    readiness_score: int | None
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}


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
    age: int | None = Field(default=None, ge=10, le=100)
    sex: str = Field(default="", max_length=40)
    height_cm: float | None = Field(default=None, ge=80, le=250)
    weight_kg: float | None = Field(default=None, ge=20, le=350)
    bmi: float | None = Field(default=None, ge=10, le=80)
    training_experience: str = Field(..., max_length=80)
    primary_goal: str = Field(..., max_length=120)
    energy_level: int = Field(..., ge=1, le=10)
    sleep_quality: int = Field(..., ge=1, le=10)
    soreness_level: int = Field(..., ge=1, le=10)
    stress_level: int = Field(..., ge=1, le=10)
    pain_or_limitations: str = Field(default="", max_length=6000)
    available_equipment: str = Field(default="", max_length=4000)
    session_time_limit_minutes: int | None = Field(default=None, ge=10, le=240)
    difficulty_preference: str = Field(default="moderate", max_length=80)
    extra_notes: str = Field(default="", max_length=12000)


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


class WorkoutSessionCreate(BaseModel):
    program_id: int = Field(..., ge=1)
    workout_day_id: int = Field(..., ge=1)
    readiness_score: int | None = Field(default=None, ge=1, le=10)
    notes: str = Field(default="", max_length=2000)


class WorkoutSessionFinishRequest(BaseModel):
    readiness_score: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = Field(default=None, max_length=2000)


class SessionSetCreate(BaseModel):
    workout_exercise_id: int = Field(..., ge=1)
    set_number: int = Field(..., ge=1, le=30)
    planned_reps: str = Field(..., min_length=1, max_length=40)
    planned_weight: float | None = Field(default=None, ge=0, le=1000)
    actual_reps: int | None = Field(default=None, ge=0, le=200)
    actual_weight: float | None = Field(default=None, ge=0, le=1000)
    weight_unit: str = Field(default="kg", min_length=1, max_length=10)
    difficulty_rating: int | None = Field(default=None, ge=1, le=10)
    completed: bool = False
    rest_seconds_used: int | None = Field(default=None, ge=0, le=3600)
    notes: str = Field(default="", max_length=2000)


class SessionSetUpdate(BaseModel):
    set_number: int | None = Field(default=None, ge=1, le=30)
    planned_reps: str | None = Field(default=None, min_length=1, max_length=40)
    planned_weight: float | None = Field(default=None, ge=0, le=1000)
    actual_reps: int | None = Field(default=None, ge=0, le=200)
    actual_weight: float | None = Field(default=None, ge=0, le=1000)
    weight_unit: str | None = Field(default=None, min_length=1, max_length=10)
    difficulty_rating: int | None = Field(default=None, ge=1, le=10)
    completed: bool | None = None
    rest_seconds_used: int | None = Field(default=None, ge=0, le=3600)
    notes: str | None = Field(default=None, max_length=2000)


class SessionSetRead(BaseModel):
    id: int
    workout_session_id: int
    workout_exercise_id: int
    set_number: int
    planned_reps: str
    planned_weight: float | None
    exercise_name_snapshot: str
    workout_day_name_snapshot: str
    program_name_snapshot: str
    planned_rest_seconds_snapshot: int | None
    actual_reps: int | None
    actual_weight: float | None
    weight_unit: str
    difficulty_rating: int | None
    completed: bool
    rest_seconds_used: int | None
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSessionRead(BaseModel):
    id: int
    program_id: int
    workout_day_id: int
    started_at: datetime
    finished_at: datetime | None
    readiness_score: int | None
    notes: str
    status: str
    session_sets: list[SessionSetRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SessionReflectionRead(BaseModel):
    id: int
    workout_session_id: int
    summary: str
    what_went_well: str
    what_was_difficult: str
    next_session_suggestion: str
    caution_flags: str
    trainer_review_recommended: bool
    model_used: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionReflectionGenerateResponse(SessionReflectionRead):
    pass


class ProgressionSuggestionRead(BaseModel):
    id: int
    workout_session_id: int
    workout_exercise_id: int | None
    exercise_name_snapshot: str
    suggestion_type: str
    suggested_weight: float | None
    weight_unit: str
    suggested_reps: str
    rationale: str
    confidence: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgressionSuggestionGenerateResponse(BaseModel):
    suggestions: list[ProgressionSuggestionRead] = Field(default_factory=list)


class DashboardSummaryRead(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    total_logged_sets: int
    completed_sets: int
    average_difficulty: float | None
    latest_completed_session_id: int | None
    latest_completed_session_started_at: datetime | None
    latest_completed_session_finished_at: datetime | None
    latest_program_name: str | None
    latest_workout_day_name: str | None
    latest_exercise_names: list[str] = Field(default_factory=list)
    latest_reflection_summary: str | None
    latest_progression_suggestions: list[str] = Field(default_factory=list)
