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
