import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(50), nullable=False)  # QUANT, LOGICAL, VERBAL, PROGRAMMING, SQL, FULL_STACK
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_planned_hours = Column(Integer, nullable=False, default=20)
    trainer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    institution = relationship("Institution")
    trainer = relationship("User", foreign_keys=[trainer_id])
    sessions = relationship(
        "TrainingSession",
        back_populates="program",
        cascade="all, delete-orphan",
        order_by="TrainingSession.session_date",
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="chk_training_program_dates"),
        CheckConstraint("total_planned_hours > 0", name="chk_training_planned_hours_positive"),
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id = Column(
        UUID(as_uuid=True),
        ForeignKey("training_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)  # e.g. "10:00 AM"
    duration_minutes = Column(Integer, nullable=False, default=60)
    topic_covered = Column(String(255), nullable=False)
    trainer_notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    program = relationship("TrainingProgram", back_populates="sessions")
    attendance_records = relationship(
        "TrainingAttendance",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="chk_session_duration_positive"),
    )


class TrainingAttendance(Base):
    __tablename__ = "training_attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attendance_status = Column(
        String(20),
        nullable=False,
        default="PRESENT",
    )  # PRESENT, ABSENT, EXCUSED
    marked_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    marked_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session = relationship("TrainingSession", back_populates="attendance_records")
    user = relationship("User", foreign_keys=[user_id])
    marked_by = relationship("User", foreign_keys=[marked_by_user_id])

    __table_args__ = (
        CheckConstraint(
            "attendance_status IN ('PRESENT', 'ABSENT', 'EXCUSED')",
            name="chk_training_attendance_status",
        ),
        UniqueConstraint("session_id", "user_id", name="uq_training_session_user"),
    )
