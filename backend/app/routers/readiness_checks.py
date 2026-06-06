from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.auth import AuthUser, get_current_user, get_effective_user_id
from app.services.ownership import ownership_filter

router = APIRouter(prefix="/readiness-checks", tags=["readiness checks"])


def calculate_readiness_score(check: schemas.ReadinessCheckCreate) -> int | None:
    components: list[int] = []
    if check.energy_level is not None:
        components.append(check.energy_level)
    if check.sleep_quality is not None:
        components.append(check.sleep_quality)
    if check.soreness_level is not None:
        components.append(11 - check.soreness_level)
    if check.stress_level is not None:
        components.append(11 - check.stress_level)

    if not components:
        return None

    score = round(sum(components) / len(components))
    return max(1, min(10, score))


@router.post("", response_model=schemas.ReadinessCheckRead, status_code=status.HTTP_201_CREATED)
def create_readiness_check(
    check_in: schemas.ReadinessCheckCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.ReadinessCheck:
    check = models.ReadinessCheck(
        user_id=get_effective_user_id(current_user),
        **check_in.model_dump(),
        readiness_score=calculate_readiness_score(check_in),
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.get("/latest", response_model=schemas.ReadinessCheckRead)
def get_latest_readiness_check(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> models.ReadinessCheck:
    check = db.scalar(
        select(models.ReadinessCheck)
        .where(ownership_filter(models.ReadinessCheck, current_user))
        .order_by(
            models.ReadinessCheck.created_at.desc(),
            models.ReadinessCheck.id.desc(),
        )
    )
    if check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readiness check found.",
        )
    return check


@router.get("", response_model=list[schemas.ReadinessCheckRead])
def list_readiness_checks(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> list[models.ReadinessCheck]:
    return list(
        db.scalars(
            select(models.ReadinessCheck)
            .where(ownership_filter(models.ReadinessCheck, current_user))
            .order_by(models.ReadinessCheck.created_at.desc(), models.ReadinessCheck.id.desc())
            .limit(limit)
        )
    )
