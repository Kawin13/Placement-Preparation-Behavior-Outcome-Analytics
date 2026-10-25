import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class DomainWeightRequirement(BaseModel):
    domain: str
    domain_name: str
    weight: float
    min_attempts: int
    target_accuracy: float


class RoleDefinition(BaseModel):
    role_id: str
    role_name: str
    description: str
    target_industry_tier: str
    domain_requirements: List[DomainWeightRequirement]


class DomainEvidenceItem(BaseModel):
    domain: str
    domain_name: str
    weight: float
    attempts_count: int
    correct_count: int
    raw_accuracy_percentage: Optional[float] = None
    weighted_domain_score: Optional[float] = None
    meets_threshold: bool
    attempts_needed: int
    recency_days_ago: Optional[int] = None
    recency_label: str
    status: str  # 'PROFICIENT', 'MODERATE', 'NEEDS_ATTENTION', 'INSUFFICIENT_EVIDENCE'
    evidence_note: str


class PracticeRecommendation(BaseModel):
    assessment_id: uuid.UUID
    assessment_title: str
    domain: str
    category: str
    duration_minutes: int
    priority: str  # 'CRITICAL_DEFICIT', 'HIGH_PRIORITY', 'REINFORCEMENT'
    rationale: str


class RoleReadinessResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    roll_number: Optional[str] = None
    role_id: str
    role_name: str
    role_description: str
    target_industry_tier: str
    readiness_score: Optional[float] = None  # Suppressed when evidence is insufficient
    readiness_tier: str  # 'ROLE_READY', 'DEVELOPING', 'FOUNDATION_NEEDED', 'INSUFFICIENT_EVIDENCE'
    has_sufficient_evidence: bool
    total_role_attempts: int
    domain_evidence: List[DomainEvidenceItem]
    missing_evidence_summary: List[str]
    recommendations: List[PracticeRecommendation]
    non_predictive_disclaimer: str
    formula_documentation: str
    last_evaluated_at: datetime
