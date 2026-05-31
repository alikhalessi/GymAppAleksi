from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str


class ProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    goal: str = Field(..., min_length=1, max_length=240)
    duration_weeks: int = Field(..., ge=1, le=104)

    @field_validator("name", "goal")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    goal: str | None = Field(default=None, min_length=1, max_length=240)
    duration_weeks: int | None = Field(default=None, ge=1, le=104)

    @field_validator("name", "goal")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped


class ProgramRead(ProgramBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
