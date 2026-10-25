import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PlacementOutcome(Base):
    __tablename__ = "placement_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    job_title = Column(String(150), nullable=False)
    tier = Column(String(30), nullable=False)
    ctc_lpa = Column(Numeric(5, 2), nullable=True)
    verification_status = Column(String(30), default="PENDING_REVIEW", nullable=False)
    proof_document_url = Column(String(500), nullable=True)
    verified_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="placement_outcomes")
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])

    __table_args__ = (
        CheckConstraint(
            "tier IN ('TIER_1_PRODUCT', 'TIER_2_TECH', 'CORE_ENG', 'MASS_IT')",
            name="chk_placement_tier",
        ),
        CheckConstraint(
            "verification_status IN ('PENDING_REVIEW', 'OFFICIALLY_VERIFIED', 'REJECTED')",
            name="chk_verification_status",
        ),
        CheckConstraint("ctc_lpa IS NULL OR ctc_lpa > 0", name="chk_ctc_positive"),
    )
