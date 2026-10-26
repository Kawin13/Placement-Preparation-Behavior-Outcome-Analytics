import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CareerPathResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    title: str
    description: Optional[str] = None
    target_role: str
    is_active: bool
    display_order: int
    created_at: datetime


class SelectCareerGoalRequest(BaseModel):
    career_path_id: uuid.UUID
    target_date: Optional[datetime] = None


class StudentCareerGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    career_path_id: uuid.UUID
    career_path_code: str
    career_path_title: str
    target_role: str
    status: str
    target_date: Optional[datetime] = None
    created_at: datetime


class LearningResourceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    subtopic_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    resource_type: str
    external_url: Optional[str] = None
    difficulty: str
    estimated_duration_min: int
    status: str
    is_completed: bool = False


class LearningResourceDetail(LearningResourceSummary):
    content: Optional[str] = None
    updated_at: datetime


class RoadmapTopicSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    slug: str
    name: str
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    display_order: int
    resources_count: int = 0
    practice_questions_count: int = 0
    dsa_problems_count: int = 0
    completion_percentage: int = 0
    status: str = "NOT_STARTED"
    assessment_id: Optional[uuid.UUID] = None


class RoadmapSubjectTree(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: Optional[str] = None
    icon: str
    display_order: int
    topics: List[RoadmapTopicSummary]


class RoadmapTreeResponse(BaseModel):
    career_path: CareerPathResponse
    subjects: List[RoadmapSubjectTree]
    overall_progress_percentage: int
    completed_topics_count: int
    total_topics_count: int


class TopicPracticeQuestionItem(BaseModel):
    id: uuid.UUID
    title: str
    content: Optional[str] = None
    difficulty: str
    question_type: str = "MCQ_SINGLE"
    points: int = 2
    attempts_count: int = 0
    user_accuracy: Optional[float] = None
    is_solved: bool = False


class TopicDSAProblemItem(BaseModel):
    id: uuid.UUID
    problem_number: int
    slug: str
    title: str
    difficulty: str
    status: str = "UNSOLVED"  # UNSOLVED, ATTEMPTED, SOLVED


class TopicAssessmentInfo(BaseModel):
    id: uuid.UUID
    title: str
    duration_minutes: int
    passing_score: Optional[float] = None
    questions_count: int
    category: Optional[str] = None


class TopicDetailResponse(BaseModel):
    id: uuid.UUID
    subject_id: uuid.UUID
    subject_name: str
    slug: str
    name: str
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    resources: List[LearningResourceSummary]
    practice_questions: List[TopicPracticeQuestionItem]
    dsa_problems: List[TopicDSAProblemItem]
    assessment: Optional[TopicAssessmentInfo] = None
    completion_percentage: int
    status: str
    questions_attempted: int
    questions_correct: int
    coding_problems_solved: int
    resources_completed: int
    accuracy_rate: int = 0
    evidence_confidence: str = "INSUFFICIENT"
    recommended_next_step: Optional[str] = None


class TrackEventRequest(BaseModel):
    event_type: str = Field(..., description="SESSION_START, SESSION_COMPLETE, SESSION_ABANDONED, RESOURCE_OPENED, RESOURCE_COMPLETED, TOPIC_SWITCH")
    category: Optional[str] = None
    entity_id: Optional[str] = None
    duration_seconds: int = 0
    metadata_json: Optional[Dict[str, Any]] = None


class RecommendedActionResponse(BaseModel):
    action_type: str  # STUDY_RESOURCE, SOLVE_PRACTICE, SOLVE_DSA, REVIEW_MISTAKES
    title: str
    reason: str
    target_id: Optional[str] = None
    target_slug: Optional[str] = None
    target_topic_id: Optional[str] = None
    target_url: str
    estimated_minutes: int
