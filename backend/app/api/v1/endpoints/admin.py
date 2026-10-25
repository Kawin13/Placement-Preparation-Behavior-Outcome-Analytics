import csv
import io
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import hash_password, validate_password_strength
from app.core.rate_limit import get_client_ip
from app.api.deps import require_roles, verify_institution_boundary
from app.services.audit import AuditService
from app.models.user import User, StudentProfile
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
from app.schemas.student import (
    BatchStudentImportPreviewRequest,
    BatchStudentImportPreviewResponse,
    BatchStudentImportCommitRequest,
    BatchStudentImportCommitResponse,
    BatchStudentImportRow,
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


# ---------------------------------------------------------------------------
# Batch Student Import (Task 12: Dry-run Validation & Atomic Commit)
# ---------------------------------------------------------------------------

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@router.post(
    "/students/import-preview",
    response_model=BatchStudentImportPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Student CSV Import File (Dry-Run)",
    description="Validates CSV header structure, duplicate records within the file, institutional duplicates, and department mapping before committing."
)
def preview_student_import(
    payload: BatchStudentImportPreviewRequest,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> BatchStudentImportPreviewResponse:
    content = payload.csv_content.strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV content cannot be empty",
        )

    f = io.StringIO(content)
    reader = csv.DictReader(f)

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains no headers.",
        )

    required_fields = {"roll_number", "full_name", "email", "department_code", "graduation_year"}
    normalized_headers = {h.strip().lower(): h for h in reader.fieldnames if h}
    missing = required_fields - set(normalized_headers.keys())
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV is missing required columns: {', '.join(sorted(missing))}. Expected headers: roll_number, full_name, email, department_code, graduation_year, section, cgpa",
        )

    # Pre-cache institutional departments
    departments = db.query(Department).filter(Department.institution_id == current_admin.institution_id).all()
    dept_map = {d.code.upper(): d for d in departments}

    seen_emails_in_file = set()
    seen_rolls_in_file = set()

    valid_rows: List[BatchStudentImportRow] = []
    rejected_rows: List[BatchStudentImportRow] = []

    for idx, row in enumerate(reader, start=1):
        # Extract fields
        roll = (row.get(normalized_headers.get("roll_number", "")) or "").strip().upper()
        name = (row.get(normalized_headers.get("full_name", "")) or "").strip()
        email = (row.get(normalized_headers.get("email", "")) or "").strip().lower()
        dept_code = (row.get(normalized_headers.get("department_code", "")) or "").strip().upper()
        grad_year_str = (row.get(normalized_headers.get("graduation_year", "")) or "").strip()
        section_key = normalized_headers.get("section")
        section = (row.get(section_key) or "").strip().upper() if section_key else None
        cgpa_key = normalized_headers.get("cgpa")
        cgpa_str = (row.get(cgpa_key) or "").strip() if cgpa_key else None

        row_obj = BatchStudentImportRow(
            row_number=idx,
            roll_number=roll,
            full_name=name,
            email=email,
            department_code=dept_code,
            graduation_year=int(grad_year_str) if grad_year_str.isdigit() else 0,
            section=section if section else None,
            cgpa=None,
            status="VALID",
            error_reason=None,
        )

        # Validation rules
        if not roll:
            row_obj.status = "REJECTED"
            row_obj.error_reason = "Missing roll_number"
            rejected_rows.append(row_obj)
            continue

        if not name:
            row_obj.status = "REJECTED"
            row_obj.error_reason = "Missing full_name"
            rejected_rows.append(row_obj)
            continue

        if not email or not EMAIL_REGEX.match(email):
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Invalid email format: '{email}'"
            rejected_rows.append(row_obj)
            continue

        if not grad_year_str.isdigit() or int(grad_year_str) < 2000 or int(grad_year_str) > 2100:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Invalid graduation year: '{grad_year_str}'"
            rejected_rows.append(row_obj)
            continue

        if cgpa_str:
            try:
                cgpa_val = float(cgpa_str)
                if cgpa_val < 0.0 or cgpa_val > 10.0:
                    row_obj.status = "REJECTED"
                    row_obj.error_reason = f"CGPA must be between 0.00 and 10.00 (got {cgpa_val})"
                    rejected_rows.append(row_obj)
                    continue
                row_obj.cgpa = round(cgpa_val, 2)
            except ValueError:
                row_obj.status = "REJECTED"
                row_obj.error_reason = f"Malformed CGPA value: '{cgpa_str}'"
                rejected_rows.append(row_obj)
                continue

        # Check department existence
        if dept_code not in dept_map:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Department code '{dept_code}' not found in institution"
            rejected_rows.append(row_obj)
            continue

        # Duplicate in file
        if email in seen_emails_in_file:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Duplicate email in upload file: '{email}'"
            rejected_rows.append(row_obj)
            continue
        seen_emails_in_file.add(email)

        if roll in seen_rolls_in_file:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Duplicate roll number in upload file: '{roll}'"
            rejected_rows.append(row_obj)
            continue
        seen_rolls_in_file.add(roll)

        # Duplicate in Database: check email across system
        db_user_exists = db.query(User).filter(User.email == email).first()
        if db_user_exists:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Email '{email}' is already registered in the system"
            rejected_rows.append(row_obj)
            continue

        # Duplicate in Database: check roll_number in this institution
        db_roll_exists = (
            db.query(StudentProfile)
            .join(User, StudentProfile.user_id == User.id)
            .filter(User.institution_id == current_admin.institution_id, func.upper(StudentProfile.roll_number) == roll)
            .first()
        )
        if db_roll_exists:
            row_obj.status = "REJECTED"
            row_obj.error_reason = f"Roll number '{roll}' is already assigned in this institution"
            rejected_rows.append(row_obj)
            continue

        valid_rows.append(row_obj)

    return BatchStudentImportPreviewResponse(
        total_rows=len(valid_rows) + len(rejected_rows),
        valid_rows_count=len(valid_rows),
        rejected_rows_count=len(rejected_rows),
        valid_rows=valid_rows,
        rejected_rows=rejected_rows,
    )


@router.post(
    "/students/import-commit",
    response_model=BatchStudentImportCommitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Commit Validated Student Import Records",
    description="Atomically provisions user accounts, student profiles, and cohort memberships with administrative audit trail."
)
def commit_student_import(
    payload: BatchStudentImportCommitRequest,
    request: Request,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> BatchStudentImportCommitResponse:
    client_ip = get_client_ip(request)

    if not payload.rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No rows provided to commit",
        )

    departments = db.query(Department).filter(Department.institution_id == current_admin.institution_id).all()
    dept_map = {d.code.upper(): d for d in departments}

    cohorts = (
        db.query(Cohort)
        .join(Department, Cohort.department_id == Department.id)
        .filter(Department.institution_id == current_admin.institution_id)
        .all()
    )
    cohort_cache = {}
    for c in cohorts:
        key = (c.department_id, c.graduation_year, c.section or "")
        cohort_cache[key] = c

    created_count = 0
    skipped_count = 0

    # Default initial password for batch imported accounts (Must be changed upon first login)
    default_pw_hash = hash_password("Student@Placement2026!")

    for row in payload.rows:
        if row.status != "VALID":
            skipped_count += 1
            continue

        dept = dept_map.get(row.department_code.upper())
        if not dept:
            skipped_count += 1
            continue

        sec_key = row.section.upper() if row.section else ""
        cohort_key = (dept.id, row.graduation_year, sec_key)
        cohort = cohort_cache.get(cohort_key)
        if not cohort:
            cohort = Cohort(
                department_id=dept.id,
                graduation_year=row.graduation_year,
                section=row.section.upper() if row.section else None,
            )
            db.add(cohort)
            db.flush()
            cohort_cache[cohort_key] = cohort

        user = User(
            institution_id=current_admin.institution_id,
            email=row.email.lower(),
            password_hash=default_pw_hash,
            full_name=row.full_name.strip(),
            role="STUDENT",
            is_active=True,
        )
        db.add(user)
        db.flush()

        profile = StudentProfile(
            user_id=user.id,
            cohort_id=cohort.id,
            roll_number=row.roll_number.upper(),
            cgpa=row.cgpa,
            placement_status="NOT_PLACED",
        )
        db.add(profile)
        created_count += 1

    db.commit()

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="BATCH_STUDENT_IMPORT_COMMITTED",
        entity_type="StudentProfile",
        entity_id=str(current_admin.institution_id),
        ip_address=client_ip,
        details_json={
            "created_count": created_count,
            "skipped_count": skipped_count,
        },
    )

    return BatchStudentImportCommitResponse(
        created_count=created_count,
        skipped_count=skipped_count,
        status="COMMITTED",
    )
