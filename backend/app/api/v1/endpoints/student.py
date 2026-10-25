import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_roles, verify_student_record_ownership
from app.models.user import User, StudentProfile
from app.schemas.auth import StudentProfileData

router = APIRouter()


class StudentProfileUpdateRequest(BaseModel):
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    roll_number: Optional[str] = Field(None, min_length=2, max_length=50)


@router.get(
    "/profile",
    response_model=StudentProfileData,
    status_code=status.HTTP_200_OK,
    summary="Get Own Student Academic Profile",
    description="Enforces student record ownership."
)
def get_own_profile(
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> StudentProfileData:
    verify_student_record_ownership(current_student.id, current_student)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_student.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile has not been initialized yet.",
        )
    return StudentProfileData.model_validate(profile)


@router.put(
    "/profile",
    response_model=StudentProfileData,
    status_code=status.HTTP_200_OK,
    summary="Update Own Academic Profile Details",
    description="Allows students to update their verified academic details."
)
def update_own_profile(
    payload: StudentProfileUpdateRequest,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> StudentProfileData:
    verify_student_record_ownership(current_student.id, current_student)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_student.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile does not exist.",
        )

    if payload.cgpa is not None:
        profile.cgpa = payload.cgpa
    if payload.roll_number is not None:
        profile.roll_number = payload.roll_number.strip()

    db.commit()
    db.refresh(profile)
    return StudentProfileData.model_validate(profile)
