import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------
# Question & Option Schemas
# ---------------------------------------------------------

class OptionCreate(BaseModel):
    option_text: str = Field(..., min_length=1, max_length=1000)
    is_correct: bool = False
    feedback: Optional[str] = Field(None, max_length=1000)


class OptionCandidateResponse(BaseModel):
    """Sanitized option response for active candidates (answers stripped)."""
    id: uuid.UUID
    option_text: str

    model_config = ConfigDict(from_attributes=True)


class OptionReviewResponse(BaseModel):
    """Full option response for post-submission review."""
    id: uuid.UUID
    option_text: str
    is_correct: bool
    feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    skill_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=5)
    question_type: str = Field("MCQ_SINGLE", pattern="^(MCQ_SINGLE|MCQ_MULTI|NUMERICAL|CODE|SQL|SUBJECTIVE)$")
    difficulty: str = Field("MEDIUM", pattern="^(EASY|MEDIUM|HARD)$")
    default_points: int = Field(1, ge=1, le=100)
    explanation: Optional[str] = None
    options: List[OptionCreate] = Field(default_factory=list)


class CandidateQuestionResponse(BaseModel):
    """Question payload for active assessment session (no correct answers or explanations)."""
    id: uuid.UUID
    title: str
    content: str
    question_type: str
    difficulty: str
    points: int
    order_index: int
    options: List[OptionCandidateResponse]
    saved_answer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewQuestionResponse(BaseModel):
    """Question payload for post-submission review with solution proofs."""
    id: uuid.UUID
    title: str
    content: str
    question_type: str
    difficulty: str
    points: int
    order_index: int
    explanation: Optional[str]
    options: List[OptionReviewResponse]
    submitted_answer: Optional[str]
    is_correct: bool
    score_awarded: Decimal
    time_spent_ms: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Assessment Schemas
# ---------------------------------------------------------

class AssessmentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    instructions: Optional[str] = Field(None, max_length=1000)
    category: str = Field("QUANTITATIVE_APTITUDE", max_length=50)
    duration_minutes: int = Field(30, ge=1, le=300)
    passing_score: Optional[Decimal] = Field(None, ge=0)
    is_published: bool = False


class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    instructions: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    passing_score: Optional[Decimal] = Field(None, ge=0)
    is_published: Optional[bool] = None


class AssessmentListItem(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: int
    passing_score: Optional[Decimal] = None
    version: int
    is_published: bool
    question_count: int = 0
    total_points: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetailResponse(AssessmentListItem):
    instructions: Optional[str] = None


class LinkQuestionsRequest(BaseModel):
    question_ids: List[uuid.UUID]
    points_per_question: int = Field(1, ge=1, le=50)


# ---------------------------------------------------------
# Practice Session Schemas
# ---------------------------------------------------------

class StartSessionRequest(BaseModel):
    assessment_id: uuid.UUID
    session_type: str = Field("PRACTICE", pattern="^(PRACTICE|TIMED_MOCK)$")


class ActiveSessionResponse(BaseModel):
    session_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    assessment_category: Optional[str]
    session_type: str
    status: str
    duration_minutes: int
    time_spent_seconds: int
    started_at: datetime
    questions: List[CandidateQuestionResponse]


class SaveAnswerRequest(BaseModel):
    question_id: uuid.UUID
    submitted_answer: str = Field(..., max_length=5000)
    time_spent_ms: int = Field(0, ge=0)


class SubmitSessionResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    total_score: Decimal
    max_score: Decimal
    percentage: float
    is_passed: Optional[bool]
    questions_count: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    time_spent_seconds: int
    completed_at: datetime


class SessionReviewResponse(BaseModel):
    session_id: uuid.UUID
    assessment_title: str
    assessment_category: Optional[str]
    status: str
    total_score: Decimal
    max_score: Decimal
    percentage: float
    time_spent_seconds: int
    started_at: datetime
    completed_at: Optional[datetime]
    questions: List[ReviewQuestionResponse]


# ---------------------------------------------------------
# Mistake Notebook Schemas
# ---------------------------------------------------------

class MistakeEntryResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    question_title: str
    question_content: str
    question_type: str
    skill_domain: Optional[str]
    student_notes: Optional[str]
    error_tag: Optional[str]
    mastery_status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class UpdateMistakeStatusRequest(BaseModel):
    mastery_status: str = Field(..., pattern="^(UNRESOLVED|REVIEWED|MASTERED)$")
    student_notes: Optional[str] = Field(None, max_length=2000)
    error_tag: Optional[str] = Field(None, max_length=50)
