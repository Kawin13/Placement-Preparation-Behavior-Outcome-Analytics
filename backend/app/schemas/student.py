import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


VALID_CATEGORIES = {
    "QUANTITATIVE_APTITUDE",
    "LOGICAL_REASONING",
    "VERBAL_ABILITY",
    "PROGRAMMING",
    "SQL",
    "CORE_TECHNICAL",
    "HR_BEHAVIORAL",
    "GENERAL",
}

VALID_ACTIVITY_TYPES = {
    "PRACTICE_SESSION",
    "MOCK_TEST",
    "CONCEPT_REVISION",
    "MISTAKE_REVIEW",
    "SELF_STUDY",
}

VALID_COMPLETION_STATES = {"COMPLETED", "IN_PROGRESS", "ABANDONED"}

VALID_TARGET_TYPES = {"QUESTIONS_COUNT", "MINUTES_PRACTICED", "ACCURACY_PERCENT"}

VALID_GOAL_STATUSES = {"IN_PROGRESS", "COMPLETED", "ARCHIVED"}

VALID_PLACEMENT_STATUSES = {"NOT_PLACED", "IN_PROCESS", "PLACED", "OPTED_OUT"}


class StudentProfileDetailed(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    roll_number: str
    cgpa: Optional[float] = None
    placement_status: str
    user_full_name: str
    user_email: EmailStr
    institution_id: uuid.UUID
    institution_name: str
    department_id: Optional[uuid.UUID] = None
    department_name: Optional[str] = None
    department_code: Optional[str] = None
    cohort_id: uuid.UUID
    cohort_graduation_year: Optional[int] = None
    cohort_section: Optional[str] = None


class StudentProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    roll_number: Optional[str] = Field(None, min_length=2, max_length=50)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    placement_status: Optional[str] = None

    @field_validator("placement_status")
    @classmethod
    def validate_placement_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PLACEMENT_STATUSES:
            raise ValueError(f"placement_status must be one of: {', '.join(sorted(VALID_PLACEMENT_STATUSES))}")
        return v


class PreparationActivityCreate(BaseModel):
    activity_type: str = Field(..., description="PRACTICE_SESSION, MOCK_TEST, CONCEPT_REVISION, MISTAKE_REVIEW, SELF_STUDY")
    category: str = Field(..., description="QUANTITATIVE_APTITUDE, LOGICAL_REASONING, VERBAL_ABILITY, PROGRAMMING, SQL, CORE_TECHNICAL, HR_BEHAVIORAL, GENERAL")
    topic: str = Field(..., min_length=2, max_length=150)
    duration_minutes: int = Field(..., ge=1, le=720, description="Active study duration in minutes (1 to 720)")
    completion_state: str = Field("COMPLETED", description="COMPLETED, IN_PROGRESS, ABANDONED")
    notes: Optional[str] = Field(None, max_length=2000)
    activity_date: Optional[datetime] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, v: str) -> str:
        if v not in VALID_ACTIVITY_TYPES:
            raise ValueError(f"activity_type must be one of: {', '.join(sorted(VALID_ACTIVITY_TYPES))}")
        return v

    @field_validator("completion_state")
    @classmethod
    def validate_completion_state(cls, v: str) -> str:
        if v not in VALID_COMPLETION_STATES:
            raise ValueError(f"completion_state must be one of: {', '.join(sorted(VALID_COMPLETION_STATES))}")
        return v


class PreparationActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    category: Optional[str] = None
    topic: Optional[str] = Field(None, min_length=2, max_length=150)
    duration_minutes: Optional[int] = Field(None, ge=1, le=720)
    completion_state: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    activity_date: Optional[datetime] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ACTIVITY_TYPES:
            raise ValueError(f"activity_type must be one of: {', '.join(sorted(VALID_ACTIVITY_TYPES))}")
        return v

    @field_validator("completion_state")
    @classmethod
    def validate_completion_state(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_COMPLETION_STATES:
            raise ValueError(f"completion_state must be one of: {', '.join(sorted(VALID_COMPLETION_STATES))}")
        return v


class PreparationActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    category: str
    topic: str
    duration_minutes: int
    completion_state: str
    provenance: str
    notes: Optional[str] = None
    activity_date: datetime
    created_at: datetime
    updated_at: datetime


class PreparationActivityListResponse(BaseModel):
    items: List[PreparationActivityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LearningGoalCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    category: str = Field(..., description="Category being targeted")
    target_type: str = Field(..., description="QUESTIONS_COUNT, MINUTES_PRACTICED, ACCURACY_PERCENT")
    target_value: float = Field(..., gt=0.0)
    deadline: Optional[datetime] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: str) -> str:
        if v not in VALID_TARGET_TYPES:
            raise ValueError(f"target_type must be one of: {', '.join(sorted(VALID_TARGET_TYPES))}")
        return v


class LearningGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    category: Optional[str] = None
    target_type: Optional[str] = None
    target_value: Optional[float] = Field(None, gt=0.0)
    current_value: Optional[float] = Field(None, ge=0.0)
    deadline: Optional[datetime] = None
    status: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}")
        return v

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TARGET_TYPES:
            raise ValueError(f"target_type must be one of: {', '.join(sorted(VALID_TARGET_TYPES))}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_GOAL_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_GOAL_STATUSES))}")
        return v


class LearningGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    category: str
    target_type: str
    target_value: float
    current_value: float
    deadline: Optional[datetime] = None
    status: str
    progress_percentage: float
    created_at: datetime
    updated_at: datetime


class StudentWorkspaceSummary(BaseModel):
    total_activities: int
    total_duration_minutes: int
    completed_activities: int
    unique_topics_count: int
    active_goals_count: int
    completed_goals_count: int
    category_minutes: Dict[str, int]
    recent_activities: List[PreparationActivityResponse]


class BatchStudentImportRow(BaseModel):
    row_number: int
    roll_number: str
    full_name: str
    email: str
    department_code: str
    graduation_year: int
    section: Optional[str] = None
    cgpa: Optional[float] = None
    status: str  # VALID or REJECTED
    error_reason: Optional[str] = None


class BatchStudentImportPreviewRequest(BaseModel):
    csv_content: str = Field(..., description="Raw CSV string with header: roll_number,full_name,email,department_code,graduation_year,section,cgpa")


class BatchStudentImportPreviewResponse(BaseModel):
    total_rows: int
    valid_rows_count: int
    rejected_rows_count: int
    valid_rows: List[BatchStudentImportRow]
    rejected_rows: List[BatchStudentImportRow]


class BatchStudentImportCommitRequest(BaseModel):
    rows: List[BatchStudentImportRow]


class BatchStudentImportCommitResponse(BaseModel):
    created_count: int
    skipped_count: int
    status: str
