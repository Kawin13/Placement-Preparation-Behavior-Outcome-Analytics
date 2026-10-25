import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    question_type = Column(String(30), nullable=False)
    difficulty = Column(String(20), nullable=False, default="MEDIUM")
    default_points = Column(Integer, default=1, nullable=False)
    explanation = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skill = relationship("Skill", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    test_cases = relationship("QuestionTestCase", back_populates="question", cascade="all, delete-orphan")
    assessment_links = relationship("AssessmentQuestion", back_populates="question")
    attempts = relationship("AttemptRecord", back_populates="question")

    __table_args__ = (
        CheckConstraint(
            "question_type IN ('MCQ_SINGLE', 'MCQ_MULTI', 'NUMERICAL', 'CODE', 'SQL', 'SUBJECTIVE')",
            name="chk_question_type",
        ),
        CheckConstraint(
            "difficulty IN ('EASY', 'MEDIUM', 'HARD')",
            name="chk_question_difficulty",
        ),
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    feedback = Column(Text, nullable=True)

    question = relationship("Question", back_populates="options")


class QuestionTestCase(Base):
    __tablename__ = "question_test_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)

    question = relationship("Question", back_populates="test_cases")
