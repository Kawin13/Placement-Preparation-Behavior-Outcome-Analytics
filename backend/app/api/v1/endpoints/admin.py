import csv
from datetime import date, datetime, timezone
import io
import re
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
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
from app.schemas.intelligence import (
    CollegeIntelligenceOverview,
    UserStatusUpdateRequest,
    UserRoleUpdateRequest,
    ContentBankSummary,
    StudentCohortAssignmentRequest,
    StudentCohortAssignmentResponse,
)
from app.services.intelligence import (
    get_college_intelligence_overview,
    export_college_intelligence_csv,
    get_content_bank_summary,
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
    description="Lists all users enrolled within the administrator's institution with optional filtering and pagination."
)
def list_institution_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[UserSummary]:
    query = db.query(User).filter(User.institution_id == current_admin.institution_id)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_pattern = f"%{search.strip().lower()}%"
        query = query.filter(
            func.lower(User.email).like(search_pattern) | func.lower(User.full_name).like(search_pattern)
        )
    users = query.order_by(User.created_at.desc()).offset(offset).limit(min(limit, 500)).all()
    return [UserSummary.model_validate(u) for u in users]


@router.put(
    "/users/{user_id}/status",
    response_model=UserSummary,
    status_code=status.HTTP_200_OK,
    summary="Update User Active Status",
    description="Allows administrators to activate or deactivate a user account within the institution."
)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdateRequest,
    request: Request,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> UserSummary:
    client_ip = get_client_ip(request)
    target = db.query(User).filter(
        User.id == user_id,
        User.institution_id == current_admin.institution_id,
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Administrators cannot deactivate their own account")

    old_status = target.is_active
    target.is_active = payload.is_active
    db.commit()
    db.refresh(target)

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="USER_STATUS_UPDATED",
        entity_type="User",
        entity_id=str(target.id),
        ip_address=client_ip,
        details_json={"old_status": old_status, "new_status": target.is_active, "target_email": target.email},
    )
    return UserSummary.model_validate(target)


@router.put(
    "/users/{user_id}/role",
    response_model=UserSummary,
    status_code=status.HTTP_200_OK,
    summary="Update User Staff Role",
    description="Promotes or updates a user's role within the institution."
)
def update_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdateRequest,
    request: Request,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> UserSummary:
    client_ip = get_client_ip(request)
    target = db.query(User).filter(
        User.id == user_id,
        User.institution_id == current_admin.institution_id,
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Administrators cannot modify their own role")

    old_role = target.role
    target.role = payload.role
    db.commit()
    db.refresh(target)

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="USER_ROLE_UPDATED",
        entity_type="User",
        entity_id=str(target.id),
        ip_address=client_ip,
        details_json={"old_role": old_role, "new_role": target.role, "target_email": target.email},
    )
    return UserSummary.model_validate(target)


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


@router.post(
    "/cohorts/{cohort_id}/assign-students",
    response_model=StudentCohortAssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign Students to Cohort",
    description="Maps a batch of students to an academic cohort."
)
def assign_students_to_cohort(
    cohort_id: uuid.UUID,
    payload: StudentCohortAssignmentRequest,
    request: Request,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> StudentCohortAssignmentResponse:
    client_ip = get_client_ip(request)
    cohort = (
        db.query(Cohort)
        .join(Department)
        .filter(
            Cohort.id == cohort_id,
            Department.institution_id == current_admin.institution_id,
        )
        .first()
    )
    if not cohort:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohort not found")

    assigned_count = 0
    errors = []
    for uid in payload.user_ids:
        prof = (
            db.query(StudentProfile)
            .join(User, StudentProfile.user_id == User.id)
            .filter(
                StudentProfile.user_id == uid,
                User.institution_id == current_admin.institution_id,
            )
            .first()
        )
        if not prof:
            errors.append(f"Student profile not found for user {uid}")
            continue
        prof.cohort_id = cohort.id
        assigned_count += 1

    db.commit()

    AuditService.record_event(
        db=db,
        institution_id=current_admin.institution_id,
        actor_user_id=current_admin.id,
        action="COHORT_STUDENTS_ASSIGNED",
        entity_type="Cohort",
        entity_id=str(cohort.id),
        ip_address=client_ip,
        details_json={"cohort_id": str(cohort.id), "assigned_count": assigned_count},
    )
    return StudentCohortAssignmentResponse(assigned_count=assigned_count, cohort_id=cohort.id, errors=errors)


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="View Institutional Security Audit Trail",
    description="Accesses the immutable audit logs for the authenticated administrator's institution."
)
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> List[AuditLogResponse]:
    query = db.query(AuditLog).filter(AuditLog.institution_id == current_admin.institution_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    logs = (
        query.order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )
    return [AuditLogResponse.model_validate(l) for l in logs]


@router.get(
    "/audit-logs/export/csv",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Export Security Audit Logs CSV",
    description="Exports the immutable audit trail for the administrator's institution as CSV."
)
def export_audit_logs_csv(
    current_admin: User = Depends(require_roles(["ADMIN"])),
    db: Session = Depends(get_db),
) -> PlainTextResponse:
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.institution_id == current_admin.institution_id)
        .order_by(AuditLog.created_at.desc())
        .limit(1000)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp (UTC)", "Action", "Entity Type", "Entity ID", "Actor ID", "IP Address", "Details JSON"])
    for l in logs:
        writer.writerow([
            l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "",
            l.action,
            l.entity_type,
            l.entity_id or "",
            str(l.actor_user_id) if l.actor_user_id else "SYSTEM",
            l.ip_address or "",
            str(l.details_json) if l.details_json else "",
        ])
    filename = f"audit_trail_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/intelligence/overview",
    response_model=CollegeIntelligenceOverview,
    status_code=status.HTTP_200_OK,
    summary="Institutional Intelligence Executive Overview",
    description="Returns the 4-pillar institutional analytics dossier with small-cell privacy suppression."
)
def get_institutional_overview(
    department_id: Optional[uuid.UUID] = None,
    cohort_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_roles(["ADMIN", "PLACEMENT_OFFICER", "TRAINER"])),
    db: Session = Depends(get_db),
) -> CollegeIntelligenceOverview:
    return get_college_intelligence_overview(
        db=db,
        actor=current_user,
        department_id=department_id,
        cohort_id=cohort_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/intelligence/export/csv",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Export Institutional Intelligence CSV",
    description="Generates an audit-logged CSV summary report of institutional intelligence metrics."
)
def export_intelligence_csv(
    department_id: Optional[uuid.UUID] = None,
    cohort_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(require_roles(["ADMIN", "PLACEMENT_OFFICER"])),
    db: Session = Depends(get_db),
) -> PlainTextResponse:
    csv_content = export_college_intelligence_csv(
        db=db,
        actor=current_user,
        department_id=department_id,
        cohort_id=cohort_id,
    )
    filename = f"college_intelligence_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/content/summary",
    response_model=ContentBankSummary,
    status_code=status.HTTP_200_OK,
    summary="Content & Assessment Bank Summary",
    description="Returns question count, assessment count, and attempt volume across academic domains."
)
def get_content_summary(
    current_user: User = Depends(require_roles(["ADMIN", "TRAINER", "PLACEMENT_OFFICER"])),
    db: Session = Depends(get_db),
) -> ContentBankSummary:
    return get_content_bank_summary(db=db, actor=current_user)


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
