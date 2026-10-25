import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TrainingProgramCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    domain: str = Field(..., description="QUANT, LOGICAL, VERBAL, PROGRAMMING, SQL, FULL_STACK")
    start_date: date
    end_date: date
    total_planned_hours: int = Field(default=20, gt=0, le=500)
    trainer_id: Optional[uuid.UUID] = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on or after start_date")
        return v


class TrainingProgramResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    title: str
    description: Optional[str] = None
    domain: str
    start_date: date
    end_date: date
    total_planned_hours: int
    trainer_id: Optional[uuid.UUID] = None
    trainer_name: Optional[str] = None
    total_sessions_count: int
    total_enrolled_students: int
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingSessionCreate(BaseModel):
    program_id: uuid.UUID
    session_date: date
    start_time: Optional[str] = Field(None, max_length=10)
    duration_minutes: int = Field(default=60, gt=0, le=480)
    topic_covered: str = Field(..., min_length=2, max_length=255)
    trainer_notes: Optional[str] = None


class TrainingSessionResponse(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    session_date: date
    start_time: Optional[str] = None
    duration_minutes: int
    topic_covered: str
    trainer_notes: Optional[str] = None
    attendance_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceMarkItem(BaseModel):
    user_id: uuid.UUID
    attendance_status: str = Field(..., description="PRESENT, ABSENT, EXCUSED")

    @field_validator("attendance_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"PRESENT", "ABSENT", "EXCUSED"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


class BatchAttendanceRequest(BaseModel):
    session_id: uuid.UUID
    attendance_list: List[AttendanceMarkItem]


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    student_name: str
    student_roll: Optional[str] = None
    attendance_status: str
    marked_by_name: Optional[str] = None
    marked_at: datetime

    class Config:
        from_attributes = True


class StudentAttendanceSummary(BaseModel):
    user_id: uuid.UUID
    student_name: str
    student_roll: Optional[str] = None
    sessions_attended: int
    total_sessions: int
    attendance_percentage: float
    total_hours_attended: float


class PrePostStudentScore(BaseModel):
    user_id: uuid.UUID
    student_name: str
    student_roll: Optional[str] = None
    department_name: Optional[str] = None
    sessions_attended: int
    attendance_percentage: float
    pre_training_score: Optional[float] = None
    post_training_score: Optional[float] = None
    score_delta: Optional[float] = None
    is_matched_pair: bool


class TrainingEffectivenessReport(BaseModel):
    program_id: uuid.UUID
    program_title: str
    domain: str
    total_sessions_completed: int
    total_enrolled: int
    matched_pairs_count: int
    missing_pre_count: int
    missing_post_count: int
    mean_attendance_percentage: float
    mean_pre_score: Optional[float] = None
    mean_post_score: Optional[float] = None
    mean_score_delta: Optional[float] = None
    correlation_attendance_and_gain: Optional[float] = None
    student_breakdown: List[PrePostStudentScore]
    non_causal_disclaimer: str
    data_limitations: str
