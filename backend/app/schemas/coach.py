import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class MistakeExplanationRequest(BaseModel):
    question_id: uuid.UUID
    selected_answer: Optional[str] = None
    student_notes: Optional[str] = None
    error_tag: Optional[str] = None


class MistakeExplanationResponse(BaseModel):
    question_id: uuid.UUID
    question_title: str
    concept_summary: str
    detailed_proof_or_explanation: str
    why_answer_was_incorrect: Optional[str] = None
    remedial_takeaway: str
    recommended_topic: str
    provider_used: str  # 'GEMINI_EXTERNAL' | 'OFFLINE_GROUNDED_MENTOR'
    is_grounded_in_syllabus: bool
    privacy_notice: str


class StudyPlanRequest(BaseModel):
    target_role_id: str = "SDE"
    weekly_hours_available: int = Field(default=10, ge=2, le=40)


class StudyPlanItem(BaseModel):
    day_number: int
    domain: str
    topic_focus: str
    action_type: str  # 'PRACTICE_DRILL', 'MISTAKE_REVIEW', 'CONCEPT_STUDY'
    suggested_duration_minutes: int
    suggested_assessment_id: Optional[uuid.UUID] = None
    suggested_assessment_title: Optional[str] = None
    pedagogical_objective: str


class StudyPlanResponse(BaseModel):
    student_id: uuid.UUID
    target_role_id: str
    target_role_name: str
    plan_overview: str
    schedule: List[StudyPlanItem]
    provider_used: str
    evidence_grounding_note: str
    privacy_notice: str
