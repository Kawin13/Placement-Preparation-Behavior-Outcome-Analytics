import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, CheckConstraint
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
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Numeric(6, 2), nullable=True)

    user = relationship("User", back_populates="practice_sessions")
    assessment = relationship("Assessment", back_populates="sessions")
    attempts = relationship("AttemptRecord", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "session_type IN ('PRACTICE', 'TIMED_MOCK', 'REVISE_MISTAKES')",
            name="chk_session_type",
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
