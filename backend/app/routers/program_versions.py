from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/programs/{program_id}/versions", tags=["program versions"])


def _get_program_or_404(db: Session, program_id: int) -> models.Program:
    program = db.get(models.Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    return program


def _get_version_or_404(db: Session, program_id: int, version_id: int) -> models.ProgramVersion:
    _get_program_or_404(db, program_id)
    version = db.get(models.ProgramVersion, version_id)
    if version is None or version.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program version not found",
        )
    return version


@router.get("", response_model=list[schemas.ProgramVersionRead])
def list_program_versions(program_id: int, db: Session = Depends(get_db)) -> list[models.ProgramVersion]:
    _get_program_or_404(db, program_id)
    return list(
        db.scalars(
            select(models.ProgramVersion)
            .where(models.ProgramVersion.program_id == program_id)
            .order_by(models.ProgramVersion.created_at.desc(), models.ProgramVersion.id.desc())
        )
    )


@router.post("", response_model=schemas.ProgramVersionRead, status_code=status.HTTP_201_CREATED)
def create_program_version(
    program_id: int,
    version_in: schemas.ProgramVersionCreate,
    db: Session = Depends(get_db),
) -> models.ProgramVersion:
    _get_program_or_404(db, program_id)

    if version_in.is_active:
        db.execute(
            update(models.ProgramVersion)
            .where(models.ProgramVersion.program_id == program_id)
            .values(is_active=False)
        )

    version = models.ProgramVersion(
        program_id=program_id,
        **version_in.model_dump()
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.put("/{version_id}", response_model=schemas.ProgramVersionRead)
def update_program_version(
    program_id: int,
    version_id: int,
    version_in: schemas.ProgramVersionUpdate,
    db: Session = Depends(get_db),
) -> models.ProgramVersion:
    version = _get_version_or_404(db, program_id, version_id)

    updates = version_in.model_dump(exclude_unset=True)

    if updates.get("is_active") is True:
        db.execute(
            update(models.ProgramVersion)
            .where(models.ProgramVersion.program_id == program_id)
            .where(models.ProgramVersion.id != version_id)
            .values(is_active=False)
        )

    for field, value in updates.items():
        setattr(version, field, value)

    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.post("/{version_id}/activate", response_model=schemas.ProgramVersionRead)
def activate_program_version(
    program_id: int,
    version_id: int,
    db: Session = Depends(get_db),
) -> models.ProgramVersion:
    version = _get_version_or_404(db, program_id, version_id)

    db.execute(
        update(models.ProgramVersion)
        .where(models.ProgramVersion.program_id == program_id)
        .where(models.ProgramVersion.id != version_id)
        .values(is_active=False)
    )

    version.is_active = True
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
