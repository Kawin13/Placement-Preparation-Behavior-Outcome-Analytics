from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Active Institutions",
    description="Returns public active institutions for onboarding and registration."
)
def list_institutions(db: Session = Depends(get_db)) -> List[InstitutionResponse]:
    institutions = db.query(Institution).filter(Institution.is_active == True).all()
    return [InstitutionResponse.model_validate(inst) for inst in institutions]


@router.post(
    "/",
    response_model=InstitutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Institution",
    description="Provisions an institution in the platform."
)
def register_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
) -> InstitutionResponse:
    existing = db.query(Institution).filter(
        (Institution.name == payload.name.strip()) | (Institution.code == payload.code.strip().upper())
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An institution with this name or code already exists",
        )

    inst = Institution(
        name=payload.name.strip(),
        code=payload.code.strip().upper(),
        is_active=True,
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return InstitutionResponse.model_validate(inst)
