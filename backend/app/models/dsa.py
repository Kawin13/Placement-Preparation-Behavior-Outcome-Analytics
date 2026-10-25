import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DSATopic(Base):
    __tablename__ = "dsa_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    problems = relationship("DSAProblem", back_populates="topic", cascade="all, delete-orphan")


class DSAProblem(Base):
    __tablename__ = "dsa_problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_number = Column(Integer, unique=True, nullable=False, index=True)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False, default="MEDIUM")
    topic_id = Column(UUID(as_uuid=True), ForeignKey("dsa_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    constraints = Column(Text, nullable=True)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    examples = Column(JSON, nullable=False, default=list)  # list of {input, output, explanation}
    starter_code = Column(JSON, nullable=False, default=dict)  # {"python": "...", "java": "..."}
    expected_time_complexity = Column(String(50), nullable=True)
    expected_space_complexity = Column(String(50), nullable=True)
    hints = Column(JSON, nullable=False, default=list)  # list of progressive hint strings
    editorial = Column(Text, nullable=True)
    status = Column(String(30), default="PUBLISHED", nullable=False)
    is_problem_of_the_day = Column(Boolean, default=False, nullable=False)
    sheet_tags = Column(JSON, nullable=False, default=list)  # e.g. ["Core 75", "Blind 50"]
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    topic = relationship("DSATopic", back_populates="problems")
    author = relationship("User")
    test_cases = relationship("DSATestCase", back_populates="problem", cascade="all, delete-orphan", order_by="DSATestCase.order_index")
    submissions = relationship("DSASubmission", back_populates="problem", cascade="all, delete-orphan")
    progress_records = relationship("DSAUserProgress", back_populates="problem", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("difficulty IN ('EASY', 'MEDIUM', 'HARD')", name="chk_dsa_problem_difficulty"),
        CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name="chk_dsa_problem_status"),
    )


class DSATestCase(Base):
    __tablename__ = "dsa_test_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("dsa_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    time_limit_ms = Column(Integer, default=2000, nullable=False)
    memory_limit_mb = Column(Integer, default=256, nullable=False)

    problem = relationship("DSAProblem", back_populates="test_cases")


class DSASubmission(Base):
    __tablename__ = "dsa_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("dsa_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    verdict = Column(String(30), nullable=False)
    runtime_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    test_cases_passed = Column(Integer, default=0, nullable=False)
    total_test_cases = Column(Integer, default=0, nullable=False)
    failed_test_case_index = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    stdout_sample = Column(Text, nullable=True)
    hints_viewed = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user = relationship("User")
    problem = relationship("DSAProblem", back_populates="submissions")

    __table_args__ = (
        CheckConstraint(
            "verdict IN ('ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 'COMPILATION_ERROR', 'RUNTIME_ERROR')",
            name="chk_dsa_submission_verdict",
        ),
        CheckConstraint("language IN ('python', 'java')", name="chk_dsa_submission_language"),
    )


class DSAUserProgress(Base):
    __tablename__ = "dsa_user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("dsa_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="UNSOLVED", nullable=False)
    attempts_count = Column(Integer, default=0, nullable=False)
    best_runtime_ms = Column(Integer, nullable=True)
    solved_at = Column(DateTime(timezone=True), nullable=True)
    last_attempted_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    problem = relationship("DSAProblem", back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_dsa_user_problem_progress"),
        CheckConstraint("status IN ('UNSOLVED', 'ATTEMPTED', 'SOLVED')", name="chk_dsa_progress_status"),
    )
