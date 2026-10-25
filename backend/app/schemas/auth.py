import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    institution_id: uuid.UUID


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserSummary


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters with upper, lower, number, special char")
    full_name: str = Field(..., min_length=2, max_length=150)
    institution_id: uuid.UUID
    # Optional roll number & cohort ID if student registers directly
    roll_number: Optional[str] = None
    cohort_id: Optional[uuid.UUID] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class StaffCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    role: str = Field(..., description="Must be TRAINER, PLACEMENT_OFFICER, or ADMIN")


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class StudentProfileData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    roll_number: str
    cohort_id: uuid.UUID
    cgpa: Optional[float] = None
    placement_status: str


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    institution_id: uuid.UUID
    is_active: bool
    student_profile: Optional[StudentProfileData] = None
