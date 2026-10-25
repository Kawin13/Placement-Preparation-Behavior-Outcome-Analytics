import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    session_type = Column(String(30), nullable=False, default="PRACTICE")
    status = Column(String(30), default="IN_PROGRESS", nullable=False)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    assessment_version = Column(Integer, default=1, nullable=False)
    total_score = Column(Numeric(6, 2), nullable=True)
    max_score = Column(Numeric(6, 2), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="practice_sessions")
    assessment = relationship("Assessment", back_populates="sessions")
    attempts = relationship("AttemptRecord", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "session_type IN ('PRACTICE', 'TIMED_MOCK', 'REVISE_MISTAKES')",
            name="chk_session_type",
        ),
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'SUBMITTED', 'TIMED_OUT', 'ABANDONED')",
            name="chk_session_status",
        ),
    )


class AttemptRecord(Base):
    __tablename__ = "attempt_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True)
    submitted_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    score_awarded = Column(Numeric(5, 2), default=0.00, nullable=False)
    time_spent_ms = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    session = relationship("PracticeSession", back_populates="attempts")
    user = relationship("User", back_populates="attempt_records")
    question = relationship("Question", back_populates="attempts")
    mistake_entry = relationship("MistakeNotebookEntry", back_populates="attempt", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("time_spent_ms >= 0", name="chk_time_spent_positive"),
        UniqueConstraint("session_id", "question_id", name="uq_session_question_attempt"),
    )


class MistakeNotebookEntry(Base):
    __tablename__ = "mistake_notebook_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("attempt_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True)
    student_notes = Column(Text, nullable=True)
    error_tag = Column(String(50), nullable=True)
    mastery_status = Column(String(30), default="UNRESOLVED", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="mistake_entries")
    attempt = relationship("AttemptRecord", back_populates="mistake_entry")
    question = relationship("Question")

    __table_args__ = (
        CheckConstraint(
            "mastery_status IN ('UNRESOLVED', 'REVIEWED', 'MASTERED')",
            name="chk_mastery_status",
        ),
    )


class PreparationActivity(Base):
    __tablename__ = "preparation_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(40), nullable=False)
    category = Column(String(50), nullable=False)
    topic = Column(String(150), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    completion_state = Column(String(30), default="COMPLETED", nullable=False)
    provenance = Column(String(30), default="STUDENT_LOGGED", nullable=False)
    notes = Column(Text, nullable=True)
    activity_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preparation_activities")

    __table_args__ = (
        CheckConstraint(
            "activity_type IN ('PRACTICE_SESSION', 'MOCK_TEST', 'CONCEPT_REVISION', 'MISTAKE_REVIEW', 'SELF_STUDY')",
            name="chk_activity_type",
        ),
        CheckConstraint(
            "category IN ('QUANTITATIVE_APTITUDE', 'LOGICAL_REASONING', 'VERBAL_ABILITY', 'PROGRAMMING', 'SQL', 'CORE_TECHNICAL', 'HR_BEHAVIORAL', 'GENERAL')",
            name="chk_activity_category",
        ),
        CheckConstraint("duration_minutes > 0 AND duration_minutes <= 720", name="chk_activity_duration"),
        CheckConstraint(
            "completion_state IN ('COMPLETED', 'IN_PROGRESS', 'ABANDONED')",
            name="chk_activity_completion_state",
        ),
        CheckConstraint(
            "provenance IN ('STUDENT_LOGGED', 'SYSTEM_EVALUATED')",
            name="chk_activity_provenance",
        ),
    )


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    target_type = Column(String(30), nullable=False)
    target_value = Column(Numeric(8, 2), nullable=False)
    current_value = Column(Numeric(8, 2), default=0.00, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="IN_PROGRESS", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="learning_goals")

    __table_args__ = (
        CheckConstraint(
            "category IN ('QUANTITATIVE_APTITUDE', 'LOGICAL_REASONING', 'VERBAL_ABILITY', 'PROGRAMMING', 'SQL', 'CORE_TECHNICAL', 'HR_BEHAVIORAL', 'GENERAL')",
            name="chk_goal_category",
        ),
        CheckConstraint(
            "target_type IN ('QUESTIONS_COUNT', 'MINUTES_PRACTICED', 'ACCURACY_PERCENT')",
            name="chk_goal_target_type",
        ),
        CheckConstraint("target_value > 0", name="chk_goal_target_value_positive"),
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'COMPLETED', 'ARCHIVED')",
            name="chk_goal_status",
        ),
    )

