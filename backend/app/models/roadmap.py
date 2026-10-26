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


class CareerPath(Base):
    """
    Career Path Target (e.g., Software Development Engineer, Full-Stack Developer, AI/ML Engineer).
    Students select a target career path which determines their multi-subject preparation roadmap.
    """
    __tablename__ = "career_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    target_role = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    subjects = relationship(
        "RoadmapSubject",
        back_populates="career_path",
        cascade="all, delete-orphan",
        order_by="RoadmapSubject.display_order",
    )
    student_goals = relationship("StudentCareerGoal", back_populates="career_path")


class RoadmapSubject(Base):
    """
    Subject domain under a career path (e.g., Programming, DSA, Core CS, Aptitude, Logical Reasoning, Verbal).
    """
    __tablename__ = "roadmap_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_path_id = Column(UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="BookOpen", nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    career_path = relationship("CareerPath", back_populates="subjects")
    topics = relationship(
        "RoadmapTopic",
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="RoadmapTopic.display_order",
    )


class RoadmapTopic(Base):
    """
    Specific topic under a subject (e.g., Arrays, Trees, DBMS, Percentages).
    Connects learning materials, practice questions, and DSA coding challenges.
    """
    __tablename__ = "roadmap_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    learning_objectives = Column(Text, nullable=True)
    difficulty = Column(String(20), default="BEGINNER", nullable=False)
    estimated_minutes = Column(Integer, default=60, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    dsa_topic_id = Column(UUID(as_uuid=True), ForeignKey("dsa_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    subject = relationship("RoadmapSubject", back_populates="topics")
    subtopics = relationship(
        "RoadmapSubtopic",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="RoadmapSubtopic.display_order",
    )
    resources = relationship(
        "LearningResource",
        back_populates="topic",
        cascade="all, delete-orphan",
    )
    skill = relationship("Skill")
    dsa_topic = relationship("DSATopic")
    assessment = relationship("Assessment")

    __table_args__ = (
        CheckConstraint("difficulty IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')", name="chk_roadmap_topic_difficulty"),
    )


class RoadmapSubtopic(Base):
    """
    Granular subtopic under a topic (e.g., Two Pointers, Binary Search on Answer).
    """
    __tablename__ = "roadmap_subtopics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    topic = relationship("RoadmapTopic", back_populates="subtopics")
    resources = relationship("LearningResource", back_populates="subtopic")


class LearningResource(Base):
    """
    Database-backed learning materials (concept notes, interactive tutorials, video guides, cheat sheets).
    """
    __tablename__ = "learning_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    subtopic_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_subtopics.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(30), default="ARTICLE", nullable=False)
    content = Column(Text, nullable=True)
    external_url = Column(String(500), nullable=True)
    difficulty = Column(String(20), default="MEDIUM", nullable=False)
    estimated_duration_min = Column(Integer, default=15, nullable=False)
    status = Column(String(20), default="PUBLISHED", nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    topic = relationship("RoadmapTopic", back_populates="resources")
    subtopic = relationship("RoadmapSubtopic", back_populates="resources")
    author = relationship("User")

    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('ARTICLE', 'VIDEO', 'DOCUMENT', 'EXERCISE', 'CHEATSHEET')",
            name="chk_resource_type",
        ),
        CheckConstraint(
            "difficulty IN ('EASY', 'MEDIUM', 'HARD')",
            name="chk_resource_difficulty",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')",
            name="chk_resource_status",
        ),
    )


class StudentCareerGoal(Base):
    """
    Active career goal chosen by the student (e.g., student selects SDE or Full-Stack).
    """
    __tablename__ = "student_career_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    career_path_id = Column(UUID(as_uuid=True), ForeignKey("career_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")
    career_path = relationship("CareerPath", back_populates="student_goals")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'COMPLETED', 'PAUSED')", name="chk_career_goal_status"),
    )


class StudentTopicProgress(Base):
    """
    Tracks topic completion, accuracy, and practice counts for a student.
    """
    __tablename__ = "student_topic_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="NOT_STARTED", nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)
    questions_attempted = Column(Integer, default=0, nullable=False)
    questions_correct = Column(Integer, default=0, nullable=False)
    coding_problems_solved = Column(Integer, default=0, nullable=False)
    resources_completed = Column(Integer, default=0, nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")
    topic = relationship("RoadmapTopic")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),
        CheckConstraint(
            "status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'NEEDS_REVISION')",
            name="chk_student_topic_status",
        ),
    )


class StudentBehaviorEvent(Base):
    """
    Auditable student behavior event record.
    Tracks session cadence, active days, abandonment, mistake review frequency, and topic transitions
    using verified server-side timestamps.
    """
    __tablename__ = "student_behavior_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=True)
    entity_id = Column(String(100), nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user = relationship("User")

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('SESSION_START', 'SESSION_COMPLETE', 'SESSION_ABANDONED', "
            "'PRACTICE_ATTEMPT', 'MISTAKE_REVIEWED', 'RESOURCE_OPENED', 'RESOURCE_COMPLETED', "
            "'CODING_SUBMIT', 'TOPIC_SWITCH')",
            name="chk_behavior_event_type",
        ),
    )
