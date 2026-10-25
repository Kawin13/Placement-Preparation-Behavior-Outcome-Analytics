import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.training import (
    TrainingProgramCreate,
    TrainingProgramResponse,
    TrainingSessionCreate,
    TrainingSessionResponse,
    BatchAttendanceRequest,
    AttendanceRecordResponse,
    TrainingEffectivenessReport,
)
from app.services.training import (
    create_training_program,
    list_training_programs,
    get_training_program_by_id,
    create_training_session,
    list_training_sessions,
    mark_batch_attendance,
    get_session_attendance,
    calculate_program_effectiveness,
)

router = APIRouter()


@router.post("/programs", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
def record_training_program(
    req: TrainingProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates an approved institutional training programme.
    Authorized for Trainers, Placement Officers, and Administrators.
    """
    return create_training_program(db=db, actor=current_user, req=req)


@router.get("/programs", response_model=List[TrainingProgramResponse])
def get_training_programs(
    domain: Optional[str] = Query(None, description="Optional domain filter (QUANT, LOGICAL, etc.)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists approved training programmes for the user's institution.
    """
    return list_training_programs(db=db, actor=current_user, domain_filter=domain)


@router.get("/programs/{program_id}", response_model=TrainingProgramResponse)
def get_training_program_detail(
    program_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves metadata for a specific training programme.
    """
    return get_training_program_by_id(db=db, actor=current_user, program_id=program_id)


@router.post("/sessions", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def record_training_session(
    req: TrainingSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates an individual training session under an existing programme.
    """
    return create_training_session(db=db, actor=current_user, req=req)


@router.get("/programs/{program_id}/sessions", response_model=List[TrainingSessionResponse])
def get_program_sessions(
    program_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists scheduled and completed sessions for a training programme.
    """
    return list_training_sessions(db=db, actor=current_user, program_id=program_id)


@router.post("/attendance", response_model=List[AttendanceRecordResponse])
def record_attendance(
    req: BatchAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Records session attendance (PRESENT, ABSENT, EXCUSED) from authorized trainer or officer sources.
    """
    return mark_batch_attendance(db=db, actor=current_user, req=req)


@router.get("/sessions/{session_id}/attendance", response_model=List[AttendanceRecordResponse])
def get_attendance_list(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the attendance roll for a specific session.
    Students are restricted to viewing only their own record.
    """
    return get_session_attendance(db=db, actor=current_user, session_id=session_id)


@router.get("/programs/{program_id}/effectiveness", response_model=TrainingEffectivenessReport)
def get_program_effectiveness(
    program_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluates training programme effectiveness using paired pre/post assessment comparison windows.
    Surfaces matched sample sizes, missing data/attrition, and non-causal association notices.
    """
    return calculate_program_effectiveness(db=db, actor=current_user, program_id=program_id)
