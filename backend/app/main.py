from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import health

app = FastAPI(
    title="SetPilot API",
    description="Backend API scaffold for the SetPilot workout execution app.",
    version="0.1.0",
)

models.Base.metadata.create_all(bind=engine)

app.include_router(health.router)
