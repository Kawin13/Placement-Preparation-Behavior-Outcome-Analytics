from datetime import date, datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class DomainAccuracyBreakdown(BaseModel):
    domain: str
    domain_name: str
    total_attempts: int
    correct_attempts: int
    accuracy_percentage: Optional[float] = None


class ActivityCategoryBreakdown(BaseModel):
    category: str
    category_name: str
    hours_spent: float
    activity_count: int


class TierDistributionItem(BaseModel):
    tier: str
    tier_label: str
    count: int
    mean_ctc: Optional[float] = None


class EngagementPillar(BaseModel):
    total_enrolled_students: int
    active_students_count: int
    total_preparation_hours: float
    total_activities_count: int
    goal_completion_rate: Optional[float] = None
    activity_breakdown: List[ActivityCategoryBreakdown] = Field(default_factory=list)


class AssessmentPillar(BaseModel):
    total_evaluations: int
    overall_accuracy_percentage: Optional[float] = None
    domain_breakdown: List[DomainAccuracyBreakdown] = Field(default_factory=list)


class TrainingPillar(BaseModel):
    total_programs_count: int
    total_sessions_delivered: int
    total_attendance_records: int
    overall_attendance_rate: Optional[float] = None
    mean_paired_score_delta: Optional[float] = None


class PlacementPillar(BaseModel):
    total_reported_offers: int
    verified_offers_count: int
    pending_review_count: int
    rejected_count: int
    verified_placed_students_count: int
    verified_placement_rate: Optional[float] = None
    mean_verified_ctc_lpa: Optional[float] = None
    max_verified_ctc_lpa: Optional[float] = None
    tier_distribution: List[TierDistributionItem] = Field(default_factory=list)


class CollegeIntelligenceOverview(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
    generated_at: datetime
    is_suppressed: bool = False
    suppression_reason: Optional[str] = None
    cohort_sample_size: int
    department_filter: Optional[str] = None
    cohort_filter: Optional[str] = None
    date_window_start: Optional[date] = None
    date_window_end: Optional[date] = None
    engagement: Optional[EngagementPillar] = None
    assessments: Optional[AssessmentPillar] = None
    training: Optional[TrainingPillar] = None
    placement: Optional[PlacementPillar] = None
    non_causal_notice: str
    audit_traceability_notice: str


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(STUDENT|TRAINER|PLACEMENT_OFFICER|ADMIN)$")


class ContentBankDomainItem(BaseModel):
    domain: str
    question_count: int
    assessment_count: int
    total_attempts: int


class ContentBankSummary(BaseModel):
    total_assessments: int
    published_assessments: int
    total_questions: int
    domains: List[ContentBankDomainItem] = Field(default_factory=list)


class StudentCohortAssignmentRequest(BaseModel):
    user_ids: List[uuid.UUID]
    cohort_id: uuid.UUID


class StudentCohortAssignmentResponse(BaseModel):
    assigned_count: int
    cohort_id: uuid.UUID
    errors: List[str] = Field(default_factory=list)
