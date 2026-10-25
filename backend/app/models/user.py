import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="RESTRICT"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(30), nullable=False, default="STUDENT")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    institution = relationship("Institution", back_populates="users")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="user")
    attempt_records = relationship("AttemptRecord", back_populates="user")
    mistake_entries = relationship("MistakeNotebookEntry", back_populates="user")
    placement_outcomes = relationship("PlacementOutcome", back_populates="user", foreign_keys="PlacementOutcome.user_id")

    __table_args__ = (
        CheckConstraint("role IN ('STUDENT', 'TRAINER', 'PLACEMENT_OFFICER', 'ADMIN')", name="chk_user_role"),
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohorts.id", ondelete="RESTRICT"), nullable=False, index=True)
    roll_number = Column(String(50), nullable=False, index=True)
    cgpa = Column(Numeric(4, 2), nullable=True)
    placement_status = Column(String(30), default="NOT_PLACED", nullable=False)

    user = relationship("User", back_populates="student_profile")
    cohort = relationship("Cohort", back_populates="student_profiles")

    __table_args__ = (
        CheckConstraint("cgpa >= 0.00 AND cgpa <= 10.00", name="chk_student_cgpa"),
        CheckConstraint("placement_status IN ('NOT_PLACED', 'IN_PROCESS', 'PLACED', 'OPTED_OUT')", name="chk_placement_status"),
    )
