import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.placement import (
    PlacementOutcomeCreate,
    PlacementOutcomeUpdate,
    PlacementOutcomeVerifyRequest,
    PlacementOutcomeResponse,
    PlacementBatchImportItem,
    PlacementBatchImportResponse,
)
from app.services.placement import (
    create_placement_outcome,
    list_placement_outcomes,
    get_placement_outcome_by_id,
    update_placement_outcome,
    verify_placement_outcome,
    withdraw_placement_outcome,
    batch_import_placement_outcomes,
    export_placement_outcomes_csv,
)

router = APIRouter()


@router.post("/outcomes", response_model=PlacementOutcomeResponse, status_code=status.HTTP_201_CREATED)
def record_outcome(
    req: PlacementOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submits a placement outcome record.
    Students submit self-reported offers entering PENDING_REVIEW.
    Placement Officers and Admins can record officially verified offers directly.
    """
    return create_placement_outcome(db=db, actor=current_user, req=req)


@router.get("/outcomes", response_model=List[PlacementOutcomeResponse])
def get_outcomes(
    verification_status: Optional[str] = Query(None, description="PENDING_REVIEW, OFFICIALLY_VERIFIED, REJECTED, WITHDRAWN"),
    department_id: Optional[uuid.UUID] = Query(None),
    cohort_id: Optional[uuid.UUID] = Query(None),
    tier: Optional[str] = Query(None, description="TIER_1_PRODUCT, TIER_2_TECH, CORE_ENG, MASS_IT"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists placement outcomes with institution-level scoping and role-based access control.
    Students are strictly restricted to inspecting their own submissions.
    Trainers can only view officially verified outcomes for curriculum alignment.
    """
    return list_placement_outcomes(
        db=db,
        actor=current_user,
        verification_status_filter=verification_status,
        department_id=department_id,
        cohort_id=cohort_id,
        tier_filter=tier,
        search=search,
    )


@router.get("/outcomes/{outcome_id}", response_model=PlacementOutcomeResponse)
def get_outcome_detail(
    outcome_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves detailed provenance and verification history for a single placement outcome.
    """
    return get_placement_outcome_by_id(db=db, actor=current_user, outcome_id=outcome_id)


@router.put("/outcomes/{outcome_id}", response_model=PlacementOutcomeResponse)
def modify_outcome(
    outcome_id: uuid.UUID,
    req: PlacementOutcomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates placement outcome fields.
    Students can only edit pending or rejected records.
    Placement Officers and Admins can update verified records with audit logging.
    """
    return update_placement_outcome(db=db, actor=current_user, outcome_id=outcome_id, req=req)


@router.patch("/outcomes/{outcome_id}/verify", response_model=PlacementOutcomeResponse)
def verify_or_reject_outcome(
    outcome_id: uuid.UUID,
    req: PlacementOutcomeVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Officially verifies or rejects an institutional placement outcome.
    Only authorized Placement Officers and Administrators can perform this action.
    """
    return verify_placement_outcome(db=db, actor=current_user, outcome_id=outcome_id, req=req)


@router.post("/outcomes/{outcome_id}/withdraw", response_model=PlacementOutcomeResponse)
def withdraw_outcome(
    outcome_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Withdraws a placement outcome record.
    Students can withdraw their own offers (e.g. if offer was superseded or revoked).
    """
    return withdraw_placement_outcome(db=db, actor=current_user, outcome_id=outcome_id)


@router.post("/batch-import", response_model=PlacementBatchImportResponse)
def batch_import_outcomes(
    items: List[PlacementBatchImportItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk imports verified or pending placement outcomes from authorized campus drive results.
    Validates institutional roll numbers and detects duplicate entries.
    """
    return batch_import_placement_outcomes(db=db, actor=current_user, items=items)


@router.get("/export-csv")
def export_outcomes_to_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Exports verified institutional placement outcomes as a downloadable CSV report.
    Access restricted to Placement Officers and Administrators with immutable audit tracking.
    """
    csv_data = export_placement_outcomes_csv(db=db, actor=current_user)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=placement_outcomes_report.csv"},
    )
