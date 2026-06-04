from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("", response_model=schemas.ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program(
    program_in: schemas.ProgramCreate,
    db: Session = Depends(get_db),
) -> models.Program:
    program = models.Program(**program_in.model_dump())
    db.add(program)
    db.commit()
    db.refresh(program)

    version = models.ProgramVersion(
        program_id=program.id,
        version_label="Manual program",
        version_type="manual",
        source="manual",
        is_active=True,
    )
    db.add(version)
    db.commit()

    return program


@router.get("", response_model=list[schemas.ProgramRead])
def list_programs(db: Session = Depends(get_db)) -> list[models.Program]:
    return list(db.scalars(select(models.Program).order_by(models.Program.created_at.desc())))


@router.get("/{program_id}", response_model=schemas.ProgramRead)
def get_program(program_id: int, db: Session = Depends(get_db)) -> models.Program:
    program = db.get(models.Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    return program


@router.put("/{program_id}", response_model=schemas.ProgramRead)
def update_program(
    program_id: int,
    program_in: schemas.ProgramUpdate,
    db: Session = Depends(get_db),
) -> models.Program:
    program = db.get(models.Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    updates = program_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(program, field, value)

    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(program_id: int, db: Session = Depends(get_db)) -> None:
    program = db.get(models.Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    db.delete(program)
    db.commit()
