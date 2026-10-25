import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.readiness import RoleDefinition, RoleReadinessResponse
from app.services.readiness import list_approved_roles, calculate_role_readiness

router = APIRouter()


@router.get("/roles", response_model=List[RoleDefinition])
def get_approved_roles(
    current_user: User = Depends(get_current_user),
):
    """
    Returns all approved job roles, their target industry tiers,
    and associated skill framework requirements.
    """
    return list_approved_roles()


@router.get("/evaluate", response_model=RoleReadinessResponse)
def evaluate_student_role_readiness(
    role_id: str = Query("SDE", description="Role identifier (e.g. SDE, DATA_ANALYST, CORE_TECH)"),
    student_id: Optional[uuid.UUID] = Query(None, description="Optional target student ID for staff inspection"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculates role-specific readiness using verified attempt records and difficulty weighting.
    Enforces minimum sample thresholds (N >= 5 per domain).
    Suppresses readiness scores where evidence is insufficient.
    Strictly forbids peer-to-peer student inspection.
    """
    target_id = current_user.id
    if student_id:
        if current_user.role == "STUDENT" and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students are restricted from inspecting peer readiness records",
            )
        target_id = student_id

    try:
        readiness = calculate_role_readiness(db=db, user_id=target_id, role_id=role_id)
        return readiness
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
