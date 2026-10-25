import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)


class InstitutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    is_active: bool
    created_at: datetime


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=20)


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_id: uuid.UUID
    name: str
    code: str
    created_at: datetime


class CohortCreate(BaseModel):
    department_id: uuid.UUID
    graduation_year: int = Field(..., gt=2000, le=2100)
    section: Optional[str] = Field(None, max_length=10)


class CohortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    department_id: uuid.UUID
    graduation_year: int
    section: Optional[str]
    created_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_id: uuid.UUID
    actor_user_id: Optional[uuid.UUID]
    action: str
    entity_type: str
    entity_id: Optional[str]
    ip_address: Optional[str]
    details_json: Optional[Any]
    created_at: datetime
