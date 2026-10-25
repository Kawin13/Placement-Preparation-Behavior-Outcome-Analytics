from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, validate_password_strength
from app.core.rate_limit import get_client_ip
from app.api.deps import require_roles, verify_institution_boundary
from app.services.audit import AuditService
from app.models.user import User
from app.models.institution import Department, Cohort
from app.models.audit import AuditLog
from app.schemas.auth import StaffCreateRequest, UserSummary
from app.schemas.institution import (
    DepartmentCreate,
    DepartmentResponse,
    CohortCreate,
    CohortResponse,
    AuditLogResponse,
)

router = APIRouter()


@router.post(
    "/users",
    response_model=UserSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create Institutional Staff Account",
    description="Only authenticated administrators may provision staff (TRAINER, PLACEMENT_OFFICER, ADMIN)."
)
def create_staff_user(
    request: Request,
    payload: StaffCreateRequest,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> UserSummary:
    client_ip = get_client_ip(request)

    if payload.role not in ("TRAINER", "PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: TRAINER, PLACEMENT_OFFICER, ADMIN",
        )

    validate_password_strength(payload.password)

    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists",
        )

    staff_user = User(
        institution_id=current_admin.institution_id,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=payload.role,
        is_active=True,
    )
    db.add(staff_user)
    db.commit()
    db.refresh(staff_user)

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="STAFF_USER_PROVISIONED",
        entity_type="User",
        entity_id=str(staff_user.id),
        ip_address=client_ip,
        details_json={"email": staff_user.email, "role": staff_user.role},
    )

    return UserSummary.model_validate(staff_user)


@router.get(
    "/users",
    response_model=List[UserSummary],
    status_code=status.HTTP_200_OK,
    summary="List Institutional Users",
    description="Lists all users enrolled within the administrator's institution."
)
def list_institution_users(
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[UserSummary]:
    users = (
        db.query(User)
        .filter(User.institution_id == current_admin.institution_id)
        .order_by(User.created_at.desc())
        .all()
    )
    return [UserSummary.model_validate(u) for u in users]


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Department",
    description="Registers an academic department under the administrator's institution."
)
def create_department(
    request: Request,
    payload: DepartmentCreate,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> DepartmentResponse:
    client_ip = get_client_ip(request)

    dept = Department(
        institution_id=current_admin.institution_id,
        name=payload.name.strip(),
        code=payload.code.strip().upper(),
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="DEPARTMENT_CREATED",
        entity_type="Department",
        entity_id=str(dept.id),
        ip_address=client_ip,
        details_json={"name": dept.name, "code": dept.code},
    )

    return DepartmentResponse.model_validate(dept)


@router.get(
    "/departments",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Departments",
    description="Returns departments for the authenticated administrator's institution."
)
def list_departments(
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[DepartmentResponse]:
    departments = (
        db.query(Department)
        .filter(Department.institution_id == current_admin.institution_id)
        .order_by(Department.name.asc())
        .all()
    )
    return [DepartmentResponse.model_validate(d) for d in departments]


@router.post(
    "/cohorts",
    response_model=CohortResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Academic Cohort",
    description="Creates a graduation cohort for a department within the administrator's institution."
)
def create_cohort(
    request: Request,
    payload: CohortCreate,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> CohortResponse:
    client_ip = get_client_ip(request)

    # Verify department belongs to administrator's institution
    dept = db.query(Department).filter(
        Department.id == payload.department_id,
        Department.institution_id == current_admin.institution_id,
    ).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found within your institution",
        )

    cohort = Cohort(
        department_id=payload.department_id,
        graduation_year=payload.graduation_year,
        section=payload.section.strip().upper() if payload.section else None,
    )
    db.add(cohort)
    db.commit()
    db.refresh(cohort)

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="COHORT_CREATED",
        entity_type="Cohort",
        entity_id=str(cohort.id),
        ip_address=client_ip,
        details_json={"department_id": str(dept.id), "year": cohort.graduation_year},
    )

    return CohortResponse.model_validate(cohort)


@router.get(
    "/cohorts",
    response_model=List[CohortResponse],
    status_code=status.HTTP_200_OK,
    summary="List Cohorts",
    description="Returns all cohorts belonging to the administrator's institution."
)
def list_cohorts(
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[CohortResponse]:
    cohorts = (
        db.query(Cohort)
        .join(Department, Cohort.department_id == Department.id)
        .filter(Department.institution_id == current_admin.institution_id)
        .order_by(Cohort.graduation_year.desc(), Cohort.section.asc())
        .all()
    )
    return [CohortResponse.model_validate(c) for c in cohorts]


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="View Institutional Security Audit Trail",
    description="Accesses the immutable audit logs for the authenticated administrator's institution."
)
def get_audit_logs(
    limit: int = 50,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[AuditLogResponse]:
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.institution_id == current_admin.institution_id)
        .order_by(AuditLog.created_at.desc())
        .limit(min(limit, 100))
        .all()
    )
    return [AuditLogResponse.model_validate(l) for l in logs]
