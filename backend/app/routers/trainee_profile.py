from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.models import utc_now

router = APIRouter(prefix="/trainee-profile", tags=["trainee profile"])


def calculate_bmi(height_cm: float | None, weight_kg: float | None) -> float | None:
    if height_cm is None or weight_kg is None or height_cm <= 0 or weight_kg <= 0:
        return None
    meters = height_cm / 100
    return round(weight_kg / (meters * meters), 1)


def get_or_create_profile(db: Session) -> models.TraineeProfile:
    profile = db.scalar(select(models.TraineeProfile).order_by(models.TraineeProfile.id.asc()))
    if profile is not None:
        return profile

    profile = models.TraineeProfile(id=1)
    profile.bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=schemas.TraineeProfileRead)
def get_trainee_profile(db: Session = Depends(get_db)) -> models.TraineeProfile:
    return get_or_create_profile(db)


@router.put("", response_model=schemas.TraineeProfileRead)
def update_trainee_profile(
    profile_in: schemas.TraineeProfileUpdate,
    db: Session = Depends(get_db),
) -> models.TraineeProfile:
    profile = get_or_create_profile(db)
    updates = profile_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value if value is not None else None)

    for text_field in (
        "display_name",
        "sex",
        "training_experience",
        "primary_goal",
        "limitations",
        "available_equipment",
        "notes",
    ):
        if getattr(profile, text_field) is None:
            setattr(profile, text_field, "")

    profile.bmi = calculate_bmi(profile.height_cm, profile.weight_kg)
    profile.updated_at = utc_now()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
