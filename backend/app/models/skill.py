import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    domain = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    parent = relationship("Skill", remote_side=[id], backref="children")
    questions = relationship("Question", back_populates="skill")

    __table_args__ = (
        CheckConstraint(
            "domain IN ('QUANT', 'LOGICAL', 'VERBAL', 'PROGRAMMING', 'SQL', 'TECH_CORE', 'HR')",
            name="chk_skill_domain",
        ),
    )
