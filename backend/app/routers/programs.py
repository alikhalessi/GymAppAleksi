from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Program
from app.schemas import ProgramCreate, ProgramRead, ProgramUpdate

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program(
    payload: ProgramCreate,
    db: Session = Depends(get_db),
) -> Program:
    program = Program(**payload.model_dump())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("", response_model=list[ProgramRead])
def list_programs(db: Session = Depends(get_db)) -> list[Program]:
    return list(db.scalars(select(Program).order_by(Program.created_at.desc())))


@router.get("/{program_id}", response_model=ProgramRead)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
) -> Program:
    program = db.get(Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    return program


@router.put("/{program_id}", response_model=ProgramRead)
def update_program(
    program_id: int,
    payload: ProgramUpdate,
    db: Session = Depends(get_db),
) -> Program:
    program = db.get(Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(program, field, value)

    db.commit()
    db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
) -> Response:
    program = db.get(Program, program_id)
    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    db.delete(program)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
