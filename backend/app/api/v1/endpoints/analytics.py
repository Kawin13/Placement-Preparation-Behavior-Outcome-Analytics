import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.institution import Cohort
from app.services.analytics import (
    calculate_student_analytics,
    calculate_cohort_analytics,
    export_cohort_analytics_csv,
)
from app.services.audit import AuditService
from app.schemas.analytics import (
    StudentAnalyticsResponse,
    CohortAnalyticsResponse,
    SkillGapItem,
)

router = APIRouter()


@router.get("/student", response_model=StudentAnalyticsResponse)
def get_student_performance_analytics(
    days: Optional[int] = Query(30, ge=1, le=365),
    skill_domain: Optional[str] = Query(None),
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns authentic performance analytics and skill-gap diagnostics.
    Server-side ownership: Students can only view their own analytics.
    Staff (Trainer/Placement Officer/Admin) can inspect any student in their institution.
    """
    target_id = current_user.id
    if student_id:
        if current_user.role == "STUDENT" and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students are restricted from viewing peer analytics records",
            )
        target_student = db.query(User).filter(User.id == student_id).first()
        if not target_student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        if target_student.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Student does not belong to your institution",
            )
        target_id = student_id

    try:
        analytics = calculate_student_analytics(
            db=db,
            user_id=target_id,
            days=days,
            skill_domain=skill_domain,
        )
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/cohort", response_model=CohortAnalyticsResponse)
def get_cohort_performance_analytics(
    cohort_id: Optional[uuid.UUID] = Query(None),
    department_id: Optional[uuid.UUID] = Query(None),
    days: Optional[int] = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns institutional cohort analytics, participation rates, and placement correlation status.
    """
    if cohort_id:
        cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
        if not cohort or cohort.department.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort not found within your institution",
            )
    if department_id:
        dept = db.query(Department).filter(Department.id == department_id).first()
        if not dept or dept.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found within your institution",
            )

    try:
        analytics = calculate_cohort_analytics(
            db=db,
            institution_id=current_user.institution_id,
            cohort_id=cohort_id,
            department_id=department_id,
            days=days,
        )
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/skill-gaps", response_model=List[SkillGapItem])
def get_skill_gaps_diagnostic(
    student_id: Optional[uuid.UUID] = Query(None),
    days: Optional[int] = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the multi-domain skill-gap diagnostic index with attempt evidence and threshold warnings.
    """
    target_id = current_user.id
    if student_id:
        if current_user.role == "STUDENT" and student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students are restricted from inspecting peer skill-gap records",
            )
        target_student = db.query(User).filter(User.id == student_id).first()
        if not target_student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        if target_student.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Student does not belong to your institution",
            )
        target_id = student_id

    try:
        analytics = calculate_student_analytics(db=db, user_id=target_id, days=days)
        return analytics.skill_gaps
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/export")
def export_cohort_report(
    cohort_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates an accredited CSV export of cohort telemetry.
    Strictly restricted to Staff (Admin, Placement Officer, Trainer).
    Logs an audit event for compliance.
    """
    if current_user.role not in ["ADMIN", "PLACEMENT_OFFICER", "TRAINER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institutional staff can export cohort analytical reports",
        )

    cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort or cohort.department.institution_id != current_user.institution_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found in institution")

    csv_data = export_cohort_analytics_csv(
        db=db,
        institution_id=current_user.institution_id,
        cohort_id=cohort_id,
    )

    AuditService.record_event(
        db=db,
        institution_id=current_user.institution_id,
        actor_user_id=current_user.id,
        action="EXPORT_COHORT_ANALYTICS_CSV",
        entity_type="cohorts",
        entity_id=str(cohort_id),
        details_json={"cohort_year": cohort.graduation_year, "section": cohort.section},
    )

    filename = f"cohort_{cohort.graduation_year}_{cohort.section or 'general'}_telemetry.csv"
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
