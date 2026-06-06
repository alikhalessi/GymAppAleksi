import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from app import models
from app.database import engine
from app.routers import (
    auth,
    health,
    imports,
    planned_sets,
    program_versions,
    programs,
    readiness_checks,
    settings,
    trainee_profile,
    workout_days,
    workout_exercises,
    workout_sessions,
    youtube_videos,
)

app = FastAPI(title="SetPilot API", version="0.1.0")

DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
    if not raw_origins:
        return DEFAULT_ALLOWED_ORIGINS

    cleaned = raw_origins
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1]

    origins = [origin.strip() for origin in cleaned.split(",") if origin.strip()]
    return origins or DEFAULT_ALLOWED_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validation_errors_to_text(errors: list[dict]) -> str:
    lines: list[str] = []
    for item in errors:
        location = ".".join(str(part) for part in item.get("loc", [])) or "unknown"
        message = item.get("msg", "Invalid value")
        error_type = item.get("type", "validation")
        lines.append(f"{location}: {message} ({error_type})")
    return "\n".join(lines)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": validation_errors_to_text(exc.errors())},
    )


def ensure_local_sqlite_snapshot_columns() -> None:
    """Keep existing local SQLite databases usable without adding Alembic yet."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "session_sets" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("session_sets")}
    columns_to_add = {
        "exercise_name_snapshot": "VARCHAR(160) NOT NULL DEFAULT ''",
        "workout_day_name_snapshot": "VARCHAR(120) NOT NULL DEFAULT ''",
        "program_name_snapshot": "VARCHAR(120) NOT NULL DEFAULT ''",
        "planned_rest_seconds_snapshot": "INTEGER",
    }

    with engine.begin() as connection:
        for column_name, column_definition in columns_to_add.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE session_sets ADD COLUMN {column_name} {column_definition}"),
                )


models.Base.metadata.create_all(bind=engine)
ensure_local_sqlite_snapshot_columns()

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(settings.router)
app.include_router(trainee_profile.router)
app.include_router(readiness_checks.router)
app.include_router(programs.router)
app.include_router(program_versions.router)
app.include_router(workout_days.router)
app.include_router(workout_exercises.router)
app.include_router(planned_sets.router)
app.include_router(youtube_videos.router)
app.include_router(imports.router)
app.include_router(workout_sessions.router)
