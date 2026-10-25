import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class PlacementOutcomeBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=150)
    job_title: str = Field(..., min_length=2, max_length=150)
    tier: str = Field(..., description="TIER_1_PRODUCT, TIER_2_TECH, CORE_ENG, MASS_IT")
    ctc_lpa: Optional[float] = Field(None, gt=0, le=150.0, description="Annual CTC in Lakhs Per Annum")
    offer_date: Optional[date] = None
    proof_document_url: Optional[str] = Field(None, max_length=500)

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        allowed = {"TIER_1_PRODUCT", "TIER_2_TECH", "CORE_ENG", "MASS_IT"}
        if v not in allowed:
            raise ValueError(f"Tier must be one of {allowed}")
        return v


class PlacementOutcomeCreate(PlacementOutcomeBase):
    target_student_id: Optional[uuid.UUID] = Field(
        None,
        description="Optional student UUID if submitted by Placement Officer/Admin. If None, defaults to current user.",
    )


class PlacementOutcomeUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=150)
    job_title: Optional[str] = Field(None, min_length=2, max_length=150)
    tier: Optional[str] = None
    ctc_lpa: Optional[float] = Field(None, gt=0, le=150.0)
    offer_date: Optional[date] = None
    proof_document_url: Optional[str] = Field(None, max_length=500)

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"TIER_1_PRODUCT", "TIER_2_TECH", "CORE_ENG", "MASS_IT"}
            if v not in allowed:
                raise ValueError(f"Tier must be one of {allowed}")
        return v


class PlacementOutcomeVerifyRequest(BaseModel):
    verification_status: str = Field(
        ...,
        description="OFFICIALLY_VERIFIED, REJECTED, or PENDING_REVIEW",
    )
    rejection_reason: Optional[str] = Field(None, max_length=1000)

    @field_validator("verification_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"OFFICIALLY_VERIFIED", "REJECTED", "PENDING_REVIEW"}
        if v not in allowed:
            raise ValueError(f"Verification status must be one of {allowed}")
        return v


class PlacementOutcomeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    student_name: str
    student_roll: Optional[str] = None
    department_name: Optional[str] = None
    cohort_year: Optional[int] = None
    company_name: str
    job_title: str
    tier: str
    ctc_lpa: Optional[float] = None
    offer_date: Optional[date] = None
    verification_status: str  # PENDING_REVIEW, OFFICIALLY_VERIFIED, REJECTED, WITHDRAWN
    proof_document_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    verified_by_user_id: Optional[uuid.UUID] = None
    verified_by_name: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlacementBatchImportItem(BaseModel):
    roll_number: str
    company_name: str
    job_title: str
    tier: str
    ctc_lpa: Optional[float] = None
    offer_date: Optional[date] = None
    auto_verify: bool = False


class PlacementBatchImportResponse(BaseModel):
    total_processed: int
    created_count: int
    duplicate_count: int
    error_count: int
    errors: List[str]
    created_ids: List[uuid.UUID]
