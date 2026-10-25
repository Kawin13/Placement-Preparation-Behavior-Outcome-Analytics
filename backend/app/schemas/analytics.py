import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Skill Gap & Topic Schemas
# --------------------------------------------------------------------------

class TopicPerformanceItem(BaseModel):
    topic_name: str
    domain: str
    attempts_count: int
    correct_count: int
    accuracy_percentage: Optional[float] = None
    difficulty_factor: float
    status: str  # 'PROFICIENT', 'MODERATE', 'NEEDS_ATTENTION', 'INSUFFICIENT_DATA'
    evidence_note: str


class SkillGapItem(BaseModel):
    domain: str
    domain_name: str
    attempts_count: int
    correct_count: int
    accuracy_percentage: Optional[float] = None
    skill_gap_index: Optional[float] = None
    status: str  # 'PROFICIENT', 'MODERATE', 'NEEDS_ATTENTION', 'INSUFFICIENT_DATA'
    evidence_note: str


class DailyTrendPoint(BaseModel):
    date: str
    active_minutes: int
    measured_minutes: int
    self_logged_minutes: int
    attempts_count: int
    accuracy_percentage: Optional[float] = None


# --------------------------------------------------------------------------
# Student Analytics Schemas
# --------------------------------------------------------------------------

class PreparationTimeBreakdown(BaseModel):
    total_hours: float
    measured_platform_hours: float
    self_logged_hours: float
    measured_sessions_count: int
    self_logged_activities_count: int
    provenance_note: str


class StudentAnalyticsResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    roll_number: Optional[str] = None
    cohort_name: Optional[str] = None
    time_window: str
    prep_time: PreparationTimeBreakdown
    total_evaluated_attempts: int
    overall_accuracy_percentage: Optional[float] = None
    mistake_remediation_rate: Optional[float] = None
    total_mistakes_logged: int
    mastered_mistakes_count: int
    skill_gaps: List[SkillGapItem]
    topic_breakdown: List[TopicPerformanceItem]
    daily_trends: List[DailyTrendPoint]
    data_limitation_notice: str


# --------------------------------------------------------------------------
# Cohort Analytics Schemas
# --------------------------------------------------------------------------

class CohortTopicFrictionPoint(BaseModel):
    topic_name: str
    domain: str
    cohort_attempts: int
    cohort_accuracy_percentage: float
    severity: str  # 'HIGH_FRICTION', 'MODERATE_FRICTION', 'STABLE'


class PlacementCorrelationDiagnostic(BaseModel):
    sample_size: int
    is_statistically_valid: bool
    spearman_rho: Optional[float] = None
    significance_note: str
    non_causal_disclaimer: str


class CohortAnalyticsResponse(BaseModel):
    cohort_id: uuid.UUID
    cohort_name: str
    department_name: str
    graduation_year: int
    section: Optional[str] = None
    total_enrolled_students: int
    active_participating_students: int
    participation_rate_percentage: float
    total_cohort_active_hours: float
    cohort_average_accuracy: Optional[float] = None
    skill_gap_distribution: Dict[str, Dict[str, int]]  # domain -> { 'PROFICIENT': X, 'MODERATE': Y, ... }
    topic_friction_points: List[CohortTopicFrictionPoint]
    placement_correlation: PlacementCorrelationDiagnostic
    data_freshness_timestamp: datetime
