from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routers import health, imports, programs, settings, workout_days, workout_exercises

app = FastAPI(
    title="SetPilot API",
    description="Backend API scaffold for the SetPilot workout execution app.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(settings.router)
app.include_router(programs.router)
app.include_router(workout_days.router)
app.include_router(workout_exercises.router)
app.include_router(imports.router)
