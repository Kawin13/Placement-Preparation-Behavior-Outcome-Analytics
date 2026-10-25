import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ExampleCase(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class VisibleTestCase(BaseModel):
    case_index: int
    input_data: str
    expected_output: str


# -------------------------------------------------------------
# Topic Schemas
# -------------------------------------------------------------

class DSATopicItem(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    order_index: int
    summary: Optional[str] = None
    problem_count: int = 0
    solved_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Problem List & Details
# -------------------------------------------------------------

class DSAProblemListItem(BaseModel):
    id: uuid.UUID
    problem_number: int
    slug: str
    title: str
    difficulty: str
    topic_name: Optional[str] = None
    topic_slug: Optional[str] = None
    sheet_tags: List[str] = Field(default_factory=list)
    is_problem_of_the_day: bool = False
    status: str = "PUBLISHED"
    user_status: str = "UNSOLVED"  # UNSOLVED | ATTEMPTED | SOLVED
    acceptance_rate: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class DSAProblemDetail(BaseModel):
    id: uuid.UUID
    problem_number: int
    slug: str
    title: str
    difficulty: str
    topic_id: Optional[uuid.UUID] = None
    topic_name: Optional[str] = None
    topic_slug: Optional[str] = None
    description: str
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    examples: List[ExampleCase] = Field(default_factory=list)
    starter_code: Dict[str, str] = Field(default_factory=dict)
    expected_time_complexity: Optional[str] = None
    expected_space_complexity: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    sample_test_cases: List[VisibleTestCase] = Field(default_factory=list)
    sheet_tags: List[str] = Field(default_factory=list)
    is_problem_of_the_day: bool = False
    user_status: str = "UNSOLVED"

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# Execution & Submission Schemas
# -------------------------------------------------------------

class DSARunCodeRequest(BaseModel):
    language: str = Field(..., pattern="^(python|java)$")
    code: str = Field(..., min_length=1, max_length=50000)
    custom_input: Optional[str] = Field(None, max_length=10000)


class DSARunCaseResult(BaseModel):
    case_index: int
    input_data: str
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    passed: bool
    execution_time_ms: int = 0
    error: Optional[str] = None


class DSARunCodeResponse(BaseModel):
    status: str  # SUCCESS | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SECURITY_VIOLATION
    results: List[DSARunCaseResult] = Field(default_factory=list)
    custom_result: Optional[DSARunCaseResult] = None
    stdout: Optional[str] = None
    compilation_error: Optional[str] = None


class DSASubmitRequest(BaseModel):
    language: str = Field(..., pattern="^(python|java)$")
    code: str = Field(..., min_length=1, max_length=50000)
    hints_viewed: int = 0


class DSASubmitResponse(BaseModel):
    submission_id: uuid.UUID
    verdict: str  # ACCEPTED | WRONG_ANSWER | COMPILATION_ERROR | RUNTIME_ERROR | TIME_LIMIT_EXCEEDED | SECURITY_VIOLATION
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    test_cases_passed: int = 0
    total_test_cases: int = 0
    failed_test_case_index: Optional[int] = None
    error_message: Optional[str] = None
    is_first_solve: bool = False
    accuracy_percentage: float = 0.0


class DSASubmissionHistoryItem(BaseModel):
    id: uuid.UUID
    submitted_at: datetime
    language: str
    verdict: str
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    test_cases_passed: int = 0
    total_test_cases: int = 0

    model_config = ConfigDict(from_attributes=True)


class DSAEditorialResponse(BaseModel):
    problem_id: uuid.UUID
    problem_number: int
    title: str
    editorial: Optional[str] = None
    expected_time_complexity: Optional[str] = None
    expected_space_complexity: Optional[str] = None
    reference_solutions: Dict[str, str] = Field(default_factory=dict)


# -------------------------------------------------------------
# Authoring Schemas (Trainer / Admin)
# -------------------------------------------------------------

class DSATestCaseCreate(BaseModel):
    input_data: str
    expected_output: str
    is_hidden: bool = False
    order_index: int = 0


class DSAProblemCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    slug: Optional[str] = None
    difficulty: str = Field("MEDIUM", pattern="^(EASY|MEDIUM|HARD)$")
    topic_slug: str
    description: str = Field(..., min_length=10)
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    examples: List[ExampleCase] = Field(default_factory=list)
    starter_code: Dict[str, str] = Field(default_factory=dict)
    expected_time_complexity: Optional[str] = None
    expected_space_complexity: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    editorial: Optional[str] = None
    sheet_tags: List[str] = Field(default_factory=list)
    is_problem_of_the_day: bool = False
    test_cases: List[DSATestCaseCreate] = Field(default_factory=list)


# -------------------------------------------------------------
# Student Analytics Schemas
# -------------------------------------------------------------

class DSATopicStat(BaseModel):
    topic_name: str
    topic_slug: str
    total_problems: int
    solved_problems: int
    accuracy_percentage: float


class DSAStudentAnalyticsResponse(BaseModel):
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    total_problems: int
    total_submissions: int
    acceptance_rate: float
    topic_stats: List[DSATopicStat] = Field(default_factory=list)
    recommended_problem_slug: Optional[str] = None
    recommended_problem_title: Optional[str] = None
    recommended_reason: Optional[str] = None
