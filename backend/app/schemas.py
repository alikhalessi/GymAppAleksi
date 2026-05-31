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
