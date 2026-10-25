import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.user import User, StudentProfile
from app.models.institution import Department, Cohort
from app.models.placement import PlacementOutcome
from app.schemas.placement import (
    PlacementOutcomeCreate,
    PlacementOutcomeUpdate,
    PlacementOutcomeVerifyRequest,
    PlacementOutcomeResponse,
    PlacementBatchImportItem,
    PlacementBatchImportResponse,
)
from app.services.audit import AuditService


def _map_to_response(outcome: PlacementOutcome) -> PlacementOutcomeResponse:
    student_name = outcome.user.full_name if outcome.user else "Unknown Student"
    student_roll = None
    department_name = None
    cohort_year = None

    if outcome.user and outcome.user.student_profile:
        prof = outcome.user.student_profile
        student_roll = prof.roll_number
        if prof.cohort:
            cohort_year = prof.cohort.graduation_year
            if prof.cohort.department:
                department_name = prof.cohort.department.name

    verified_by_name = outcome.verified_by.full_name if outcome.verified_by else None

    return PlacementOutcomeResponse(
        id=outcome.id,
        user_id=outcome.user_id,
        student_name=student_name,
        student_roll=student_roll,
        department_name=department_name,
        cohort_year=cohort_year,
        company_name=outcome.company_name,
        job_title=outcome.job_title,
        tier=outcome.tier,
        ctc_lpa=float(outcome.ctc_lpa) if outcome.ctc_lpa is not None else None,
        offer_date=outcome.offer_date,
        verification_status=outcome.verification_status,
        proof_document_url=outcome.proof_document_url,
        rejection_reason=outcome.rejection_reason,
        verified_by_user_id=outcome.verified_by_user_id,
        verified_by_name=verified_by_name,
        created_at=outcome.created_at,
        verified_at=outcome.verified_at,
    )


def create_placement_outcome(
    db: Session,
    actor: User,
    req: PlacementOutcomeCreate,
) -> PlacementOutcomeResponse:
    target_user_id = actor.id

    if actor.role in ("PLACEMENT_OFFICER", "ADMIN") and req.target_student_id:
        # Staff can record on behalf of an institutional student
        target_student = (
            db.query(User)
            .filter(User.id == req.target_student_id, User.institution_id == actor.institution_id)
            .first()
        )
        if not target_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target student not found in this institution",
            )
        target_user_id = target_student.id

    # Duplicate check: same user, company, and job title
    existing = (
        db.query(PlacementOutcome)
        .filter(
            PlacementOutcome.user_id == target_user_id,
            func.lower(PlacementOutcome.company_name) == func.lower(req.company_name.strip()),
            func.lower(PlacementOutcome.job_title) == func.lower(req.job_title.strip()),
            PlacementOutcome.verification_status != "WITHDRAWN",
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An active placement outcome with {req.company_name} for this position is already recorded",
        )

    # Initial status: Staff can directly create verified records; Students enter PENDING_REVIEW
    initial_status = "PENDING_REVIEW"
    verified_by_id = None
    verified_at = None

    if actor.role in ("PLACEMENT_OFFICER", "ADMIN"):
        initial_status = "OFFICIALLY_VERIFIED"
        verified_by_id = actor.id
        verified_at = datetime.now(timezone.utc)

    outcome = PlacementOutcome(
        user_id=target_user_id,
        company_name=req.company_name.strip(),
        job_title=req.job_title.strip(),
        tier=req.tier,
        ctc_lpa=req.ctc_lpa,
        offer_date=req.offer_date,
        proof_document_url=req.proof_document_url,
        verification_status=initial_status,
        verified_by_user_id=verified_by_id,
        verified_at=verified_at,
    )
    db.add(outcome)
    db.flush()

    # If officially verified, update student profile placement status
    if initial_status == "OFFICIALLY_VERIFIED":
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == target_user_id).first()
        if prof:
            prof.placement_status = "PLACED"

    db.commit()
    db.refresh(outcome)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="PLACEMENT_OUTCOME_CREATED",
        entity_type="placement_outcomes",
        entity_id=str(outcome.id),
        details_json={
            "target_user_id": str(target_user_id),
            "company_name": outcome.company_name,
            "tier": outcome.tier,
            "ctc_lpa": outcome.ctc_lpa,
            "verification_status": outcome.verification_status,
        },
    )

    return _map_to_response(outcome)


def list_placement_outcomes(
    db: Session,
    actor: User,
    verification_status_filter: Optional[str] = None,
    department_id: Optional[uuid.UUID] = None,
    cohort_id: Optional[uuid.UUID] = None,
    tier_filter: Optional[str] = None,
    search: Optional[str] = None,
) -> List[PlacementOutcomeResponse]:
    query = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .outerjoin(User.student_profile)
        .outerjoin(StudentProfile.cohort)
        .filter(User.institution_id == actor.institution_id)
    )

    # Privacy constraint: Students can ONLY view their own records
    if actor.role == "STUDENT":
        query = query.filter(PlacementOutcome.user_id == actor.id)
    elif actor.role == "TRAINER":
        # Trainers can only see verified outcomes to measure curriculum alignment, never unverified/pending
        query = query.filter(PlacementOutcome.verification_status == "OFFICIALLY_VERIFIED")

    if verification_status_filter:
        query = query.filter(PlacementOutcome.verification_status == verification_status_filter)

    if tier_filter:
        query = query.filter(PlacementOutcome.tier == tier_filter)

    if cohort_id:
        query = query.filter(StudentProfile.cohort_id == cohort_id)

    if department_id:
        query = query.filter(Cohort.department_id == department_id)

    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (PlacementOutcome.company_name.ilike(pattern))
            | (PlacementOutcome.job_title.ilike(pattern))
            | (User.full_name.ilike(pattern))
            | (StudentProfile.roll_number.ilike(pattern))
        )

    outcomes = query.order_by(PlacementOutcome.created_at.desc()).all()
    return [_map_to_response(o) for o in outcomes]


def get_placement_outcome_by_id(
    db: Session,
    actor: User,
    outcome_id: uuid.UUID,
) -> PlacementOutcomeResponse:
    outcome = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .filter(
            PlacementOutcome.id == outcome_id,
            User.institution_id == actor.institution_id,
        )
        .first()
    )
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement outcome not found",
        )

    # Student peer protection
    if actor.role == "STUDENT" and outcome.user_id != actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students are restricted from inspecting peer placement records",
        )

    return _map_to_response(outcome)


def update_placement_outcome(
    db: Session,
    actor: User,
    outcome_id: uuid.UUID,
    req: PlacementOutcomeUpdate,
) -> PlacementOutcomeResponse:
    outcome = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .filter(
            PlacementOutcome.id == outcome_id,
            User.institution_id == actor.institution_id,
        )
        .first()
    )
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement outcome not found",
        )

    # Permission check
    if actor.role == "STUDENT":
        if outcome.user_id != actor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only modify their own submissions",
            )
        if outcome.verification_status == "OFFICIALLY_VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verified placement outcomes cannot be modified by students. Contact the Placement Cell.",
            )

    # Apply updates
    if req.company_name is not None:
        outcome.company_name = req.company_name.strip()
    if req.job_title is not None:
        outcome.job_title = req.job_title.strip()
    if req.tier is not None:
        outcome.tier = req.tier
    if req.ctc_lpa is not None:
        outcome.ctc_lpa = req.ctc_lpa
    if req.offer_date is not None:
        outcome.offer_date = req.offer_date
    if req.proof_document_url is not None:
        outcome.proof_document_url = req.proof_document_url

    db.commit()
    db.refresh(outcome)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="PLACEMENT_OUTCOME_UPDATED",
        entity_type="placement_outcomes",
        entity_id=str(outcome.id),
        details_json={"updated_fields": list(req.model_dump(exclude_unset=True).keys())},
    )

    return _map_to_response(outcome)


def verify_placement_outcome(
    db: Session,
    actor: User,
    outcome_id: uuid.UUID,
    req: PlacementOutcomeVerifyRequest,
) -> PlacementOutcomeResponse:
    if actor.role not in ("PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Placement Officers and Administrators can verify or reject placement outcomes",
        )

    outcome = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .filter(
            PlacementOutcome.id == outcome_id,
            User.institution_id == actor.institution_id,
        )
        .first()
    )
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement outcome not found",
        )

    outcome.verification_status = req.verification_status
    if req.verification_status == "OFFICIALLY_VERIFIED":
        outcome.verified_by_user_id = actor.id
        outcome.verified_at = datetime.now(timezone.utc)
        outcome.rejection_reason = None

        # Set student placement status to PLACED
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == outcome.user_id).first()
        if prof:
            prof.placement_status = "PLACED"

    elif req.verification_status == "REJECTED":
        outcome.verified_by_user_id = actor.id
        outcome.verified_at = datetime.now(timezone.utc)
        outcome.rejection_reason = req.rejection_reason or "Offer documentation did not meet institutional verification requirements."

        # Re-check other verified offers
        _refresh_student_placement_status(db, outcome.user_id)

    elif req.verification_status == "PENDING_REVIEW":
        outcome.verified_by_user_id = None
        outcome.verified_at = None
        outcome.rejection_reason = None
        _refresh_student_placement_status(db, outcome.user_id)

    db.commit()
    db.refresh(outcome)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action=f"PLACEMENT_OUTCOME_{req.verification_status}",
        entity_type="placement_outcomes",
        entity_id=str(outcome.id),
        details_json={
            "new_status": outcome.verification_status,
            "rejection_reason": outcome.rejection_reason,
            "verified_by": str(actor.id),
        },
    )

    return _map_to_response(outcome)


def withdraw_placement_outcome(
    db: Session,
    actor: User,
    outcome_id: uuid.UUID,
) -> PlacementOutcomeResponse:
    outcome = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .filter(
            PlacementOutcome.id == outcome_id,
            User.institution_id == actor.institution_id,
        )
        .first()
    )
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement outcome not found",
        )

    if actor.role == "STUDENT" and outcome.user_id != actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot withdraw peer placement records",
        )

    outcome.verification_status = "WITHDRAWN"
    _refresh_student_placement_status(db, outcome.user_id)

    db.commit()
    db.refresh(outcome)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="PLACEMENT_OUTCOME_WITHDRAWN",
        entity_type="placement_outcomes",
        entity_id=str(outcome.id),
        details_json={"withdrawn_by": str(actor.id)},
    )

    return _map_to_response(outcome)


def _refresh_student_placement_status(db: Session, user_id: uuid.UUID) -> None:
    has_verified = (
        db.query(PlacementOutcome)
        .filter(
            PlacementOutcome.user_id == user_id,
            PlacementOutcome.verification_status == "OFFICIALLY_VERIFIED",
        )
        .first()
    )
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if prof:
        prof.placement_status = "PLACED" if has_verified else "NOT_PLACED"


def batch_import_placement_outcomes(
    db: Session,
    actor: User,
    items: List[PlacementBatchImportItem],
) -> PlacementBatchImportResponse:
    if actor.role not in ("PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Placement Officers and Administrators can batch-import placement outcomes",
        )

    created_ids: List[uuid.UUID] = []
    errors: List[str] = []
    duplicate_count = 0

    for idx, item in enumerate(items, start=1):
        # 1. Lookup student by roll_number in institution
        prof = (
            db.query(StudentProfile)
            .join(StudentProfile.user)
            .filter(
                StudentProfile.roll_number == item.roll_number.strip(),
                User.institution_id == actor.institution_id,
            )
            .first()
        )
        if not prof:
            errors.append(f"Row {idx}: Student with roll number '{item.roll_number}' not found")
            continue

        # 2. Duplicate check
        existing = (
            db.query(PlacementOutcome)
            .filter(
                PlacementOutcome.user_id == prof.user_id,
                func.lower(PlacementOutcome.company_name) == func.lower(item.company_name.strip()),
                func.lower(PlacementOutcome.job_title) == func.lower(item.job_title.strip()),
                PlacementOutcome.verification_status != "WITHDRAWN",
            )
            .first()
        )
        if existing:
            duplicate_count += 1
            errors.append(
                f"Row {idx}: Duplicate record for {item.roll_number} at {item.company_name} already exists"
            )
            continue

        ver_status = "OFFICIALLY_VERIFIED" if item.auto_verify else "PENDING_REVIEW"
        outcome = PlacementOutcome(
            user_id=prof.user_id,
            company_name=item.company_name.strip(),
            job_title=item.job_title.strip(),
            tier=item.tier,
            ctc_lpa=item.ctc_lpa,
            offer_date=item.offer_date,
            verification_status=ver_status,
            verified_by_user_id=actor.id if item.auto_verify else None,
            verified_at=datetime.now(timezone.utc) if item.auto_verify else None,
        )
        db.add(outcome)
        db.flush()
        created_ids.append(outcome.id)

        if item.auto_verify:
            prof.placement_status = "PLACED"

    db.commit()

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="PLACEMENT_BATCH_IMPORTED",
        entity_type="placement_outcomes",
        entity_id=f"batch_n_{len(created_ids)}",
        details_json={
            "created_count": len(created_ids),
            "duplicate_count": duplicate_count,
            "error_count": len(errors),
        },
    )

    return PlacementBatchImportResponse(
        total_processed=len(items),
        created_count=len(created_ids),
        duplicate_count=duplicate_count,
        error_count=len(errors),
        errors=errors,
        created_ids=created_ids,
    )


def export_placement_outcomes_csv(
    db: Session,
    actor: User,
) -> str:
    if actor.role not in ("PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Placement Officers and Administrators can export placement reports",
        )

    outcomes = (
        db.query(PlacementOutcome)
        .join(PlacementOutcome.user)
        .outerjoin(User.student_profile)
        .outerjoin(StudentProfile.cohort)
        .filter(User.institution_id == actor.institution_id)
        .order_by(PlacementOutcome.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Record ID",
        "Roll Number",
        "Student Name",
        "Department",
        "Graduation Year",
        "Company Name",
        "Job Title",
        "Tier",
        "CTC (LPA)",
        "Offer Date",
        "Verification Status",
        "Verified At",
    ])

    for o in outcomes:
        roll = o.user.student_profile.roll_number if (o.user and o.user.student_profile) else ""
        dept = (
            o.user.student_profile.cohort.department.name
            if (o.user and o.user.student_profile and o.user.student_profile.cohort and o.user.student_profile.cohort.department)
            else ""
        )
        year = (
            o.user.student_profile.cohort.graduation_year
            if (o.user and o.user.student_profile and o.user.student_profile.cohort)
            else ""
        )
        writer.writerow([
            str(o.id),
            roll,
            o.user.full_name if o.user else "",
            dept,
            year,
            o.company_name,
            o.job_title,
            o.tier,
            f"{o.ctc_lpa:.2f}" if o.ctc_lpa is not None else "N/A",
            str(o.offer_date) if o.offer_date else "N/A",
            o.verification_status,
            o.verified_at.strftime("%Y-%m-%d %H:%M:%S") if o.verified_at else "N/A",
        ])

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="PLACEMENT_REPORT_EXPORTED_CSV",
        entity_type="placement_outcomes",
        entity_id=f"count_{len(outcomes)}",
        details_json={"record_count": len(outcomes)},
    )

    return output.getvalue()
