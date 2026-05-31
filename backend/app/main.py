from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models
from app.database import engine
from app.routers import (
    health,
    imports,
    planned_sets,
    programs,
    settings,
    workout_days,
    workout_exercises,
    workout_sessions,
    youtube_videos,
)

app = FastAPI(title="SetPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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


models.Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(settings.router)
app.include_router(programs.router)
app.include_router(workout_days.router)
app.include_router(workout_exercises.router)
app.include_router(planned_sets.router)
app.include_router(youtube_videos.router)
app.include_router(imports.router)
app.include_router(workout_sessions.router)
