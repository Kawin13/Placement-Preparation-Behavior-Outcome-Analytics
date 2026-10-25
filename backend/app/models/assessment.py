import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    instructions = Column(String(1000), nullable=True)
    category = Column(String(50), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    passing_score = Column(Numeric(5, 2), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    institution = relationship("Institution", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    sessions = relationship("PracticeSession", back_populates="assessment")

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="chk_assessment_duration"),
    )


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_index = Column(Integer, default=0, nullable=False)
    points = Column(Integer, default=1, nullable=False)

    assessment = relationship("Assessment", back_populates="questions")
    question = relationship("Question", back_populates="assessment_links")
