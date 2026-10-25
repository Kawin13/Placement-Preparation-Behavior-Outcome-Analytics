import math
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import require_roles, verify_student_record_ownership
from app.services.audit import AuditService
from app.core.rate_limit import get_client_ip
from app.models.user import User, StudentProfile
from app.models.institution import Cohort, Department, Institution
from app.models.practice import PreparationActivity, LearningGoal
from app.schemas.student import (
    StudentProfileDetailed,
    StudentProfileUpdateRequest,
    PreparationActivityCreate,
    PreparationActivityUpdate,
    PreparationActivityResponse,
    PreparationActivityListResponse,
    LearningGoalCreate,
    LearningGoalUpdate,
    LearningGoalResponse,
    StudentWorkspaceSummary,
)

router = APIRouter()


def _build_student_detailed(profile: StudentProfile, user: User, db: Session) -> StudentProfileDetailed:
    cohort = db.query(Cohort).filter(Cohort.id == profile.cohort_id).first()
    dept = db.query(Department).filter(Department.id == cohort.department_id).first() if cohort else None
    inst = db.query(Institution).filter(Institution.id == user.institution_id).first()

    return StudentProfileDetailed(
        id=profile.id,
        user_id=user.id,
        roll_number=profile.roll_number,
        cgpa=float(profile.cgpa) if profile.cgpa is not None else None,
        placement_status=profile.placement_status,
        user_full_name=user.full_name,
        user_email=user.email,
        institution_id=user.institution_id,
        institution_name=inst.name if inst else "Unknown Institution",
        department_id=dept.id if dept else None,
        department_name=dept.name if dept else None,
        department_code=dept.code if dept else None,
        cohort_id=profile.cohort_id,
        cohort_graduation_year=cohort.graduation_year if cohort else None,
        cohort_section=cohort.section if cohort else None,
    )


# ---------------------------------------------------------------------------
# Student Academic Profile Management
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=StudentProfileDetailed,
    status_code=status.HTTP_200_OK,
    summary="Get Own Student Academic Profile",
    description="Enforces student record ownership and returns joined department, cohort, and institutional relationships."
)
def get_own_profile(
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> StudentProfileDetailed:
    verify_student_record_ownership(current_student.id, current_student)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_student.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile has not been initialized yet.",
        )
    return _build_student_detailed(profile, current_student, db)


@router.put(
    "/profile",
    response_model=StudentProfileDetailed,
    status_code=status.HTTP_200_OK,
    summary="Update Own Academic Profile Details",
    description="Allows students to update their verified academic details and profile with audit logging."
)
def update_own_profile(
    payload: StudentProfileUpdateRequest,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> StudentProfileDetailed:
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_student.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile does not exist.",
        )

    changes = {}

    if payload.full_name is not None and payload.full_name.strip() != current_student.full_name:
        current_student.full_name = payload.full_name.strip()
        changes["full_name"] = current_student.full_name

    if payload.roll_number is not None:
        clean_roll = payload.roll_number.strip().upper()
        if clean_roll != profile.roll_number:
            # Check for uniqueness in the institution
            duplicate = (
                db.query(StudentProfile)
                .join(User, StudentProfile.user_id == User.id)
                .filter(
                    User.institution_id == current_student.institution_id,
                    func.upper(StudentProfile.roll_number) == clean_roll,
                    StudentProfile.id != profile.id,
                )
                .first()
            )
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Roll number '{clean_roll}' is already in use by another student in this institution.",
                )
            profile.roll_number = clean_roll
            changes["roll_number"] = clean_roll

    if payload.cgpa is not None and payload.cgpa != profile.cgpa:
        profile.cgpa = payload.cgpa
        changes["cgpa"] = float(payload.cgpa)

    if payload.placement_status is not None and payload.placement_status != profile.placement_status:
        profile.placement_status = payload.placement_status
        changes["placement_status"] = payload.placement_status

    db.commit()
    db.refresh(profile)
    db.refresh(current_student)

    if changes:
        AuditService.record_event(
            db=db,
            institution_id=current_student.institution_id,
            actor_user_id=current_student.id,
            action="STUDENT_PROFILE_UPDATED",
            entity_type="StudentProfile",
            entity_id=str(profile.id),
            ip_address=client_ip,
            details_json=changes,
        )

    return _build_student_detailed(profile, current_student, db)


# ---------------------------------------------------------------------------
# Preparation Activities (Task 3, 5, 6, 7, 8, 9, 11)
# ---------------------------------------------------------------------------

@router.post(
    "/activities",
    response_model=PreparationActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log Preparation Activity",
    description="Records an authentic preparation activity with category, topic, duration, and completion state."
)
def create_activity(
    payload: PreparationActivityCreate,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> PreparationActivityResponse:
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    activity = PreparationActivity(
        user_id=current_student.id,
        activity_type=payload.activity_type,
        category=payload.category,
        topic=payload.topic.strip(),
        duration_minutes=payload.duration_minutes,
        completion_state=payload.completion_state,
        provenance="STUDENT_LOGGED",
        notes=payload.notes.strip() if payload.notes else None,
        activity_date=payload.activity_date or datetime.utcnow(),
    )
    db.add(activity)

    # Automatically increment matching learning goals if active
    goals = (
        db.query(LearningGoal)
        .filter(
            LearningGoal.user_id == current_student.id,
            LearningGoal.category == payload.category,
            LearningGoal.status == "IN_PROGRESS",
        )
        .all()
    )
    for g in goals:
        if g.target_type == "MINUTES_PRACTICED":
            g.current_value = float(g.current_value) + payload.duration_minutes
            if g.current_value >= float(g.target_value):
                g.status = "COMPLETED"
        elif g.target_type == "QUESTIONS_COUNT" and payload.activity_type in ("PRACTICE_SESSION", "MOCK_TEST"):
            # Estimate 1 question per 3 minutes if not granularly tracked
            est_questions = max(1, payload.duration_minutes // 3)
            g.current_value = float(g.current_value) + est_questions
            if g.current_value >= float(g.target_value):
                g.status = "COMPLETED"

    db.commit()
    db.refresh(activity)

    AuditService.record_event(
        db=db,
        institution_id=current_student.institution_id,
        actor_user_id=current_student.id,
        action="PREPARATION_ACTIVITY_CREATED",
        entity_type="PreparationActivity",
        entity_id=str(activity.id),
        ip_address=client_ip,
        details_json={
            "activity_type": activity.activity_type,
            "category": activity.category,
            "duration_minutes": activity.duration_minutes,
        },
    )

    return PreparationActivityResponse.model_validate(activity)


@router.get(
    "/activities",
    response_model=PreparationActivityListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Preparation Activities",
    description="Returns paginated and filtered preparation activities with server-side ownership enforcement."
)
def list_activities(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    completion_state: Optional[str] = Query(None, description="Filter by completion state"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> PreparationActivityListResponse:
    verify_student_record_ownership(current_student.id, current_student)

    query = db.query(PreparationActivity).filter(PreparationActivity.user_id == current_student.id)

    if category:
        query = query.filter(PreparationActivity.category == category)
    if activity_type:
        query = query.filter(PreparationActivity.activity_type == activity_type)
    if completion_state:
        query = query.filter(PreparationActivity.completion_state == completion_state)
    if date_from:
        query = query.filter(PreparationActivity.activity_date >= date_from)
    if date_to:
        query = query.filter(PreparationActivity.activity_date <= date_to)

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size

    items = (
        query.order_by(PreparationActivity.activity_date.desc(), PreparationActivity.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return PreparationActivityListResponse(
        items=[PreparationActivityResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/activities/{activity_id}",
    response_model=PreparationActivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Preparation Activity",
    description="Enforces strict ownership: students may only access their own records."
)
def get_activity(
    activity_id: uuid.UUID,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> PreparationActivityResponse:
    verify_student_record_ownership(current_student.id, current_student)

    activity = db.query(PreparationActivity).filter(PreparationActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation activity not found.",
        )
    if activity.user_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view another student's activity.",
        )

    return PreparationActivityResponse.model_validate(activity)


@router.put(
    "/activities/{activity_id}",
    response_model=PreparationActivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Preparation Activity",
    description="Allows students to edit their logged activity with ownership verification and audit logging."
)
def update_activity(
    activity_id: uuid.UUID,
    payload: PreparationActivityUpdate,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> PreparationActivityResponse:
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    activity = db.query(PreparationActivity).filter(PreparationActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation activity not found.",
        )
    if activity.user_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you cannot modify another student's activity.",
        )

    changes = {}
    if payload.activity_type is not None and payload.activity_type != activity.activity_type:
        activity.activity_type = payload.activity_type
        changes["activity_type"] = payload.activity_type
    if payload.category is not None and payload.category != activity.category:
        activity.category = payload.category
        changes["category"] = payload.category
    if payload.topic is not None and payload.topic.strip() != activity.topic:
        activity.topic = payload.topic.strip()
        changes["topic"] = activity.topic
    if payload.duration_minutes is not None and payload.duration_minutes != activity.duration_minutes:
        activity.duration_minutes = payload.duration_minutes
        changes["duration_minutes"] = payload.duration_minutes
    if payload.completion_state is not None and payload.completion_state != activity.completion_state:
        activity.completion_state = payload.completion_state
        changes["completion_state"] = payload.completion_state
    if payload.notes is not None and payload.notes != activity.notes:
        activity.notes = payload.notes.strip() if payload.notes else None
        changes["notes_updated"] = True
    if payload.activity_date is not None:
        activity.activity_date = payload.activity_date
        changes["activity_date"] = payload.activity_date.isoformat()

    db.commit()
    db.refresh(activity)

    if changes:
        AuditService.record_event(
            db=db,
            institution_id=current_student.institution_id,
            actor_user_id=current_student.id,
            action="PREPARATION_ACTIVITY_UPDATED",
            entity_type="PreparationActivity",
            entity_id=str(activity.id),
            ip_address=client_ip,
            details_json=changes,
        )

    return PreparationActivityResponse.model_validate(activity)


@router.delete(
    "/activities/{activity_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Preparation Activity",
    description="Enforces ownership and records audit log before deletion."
)
def delete_activity(
    activity_id: uuid.UUID,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
):
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    activity = db.query(PreparationActivity).filter(PreparationActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation activity not found.",
        )
    if activity.user_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you cannot delete another student's activity.",
        )

    activity_details = {
        "activity_type": activity.activity_type,
        "category": activity.category,
        "duration_minutes": activity.duration_minutes,
        "topic": activity.topic,
    }

    db.delete(activity)
    db.commit()

    AuditService.record_event(
        db=db,
        institution_id=current_student.institution_id,
        actor_user_id=current_student.id,
        action="PREPARATION_ACTIVITY_DELETED",
        entity_type="PreparationActivity",
        entity_id=str(activity_id),
        ip_address=client_ip,
        details_json=activity_details,
    )

    return {"status": "deleted", "id": str(activity_id)}


# ---------------------------------------------------------------------------
# Student Preparation Workspace Telemetry Summary (Rule 8: Zero Fake Data)
# ---------------------------------------------------------------------------

@router.get(
    "/workspace-summary",
    response_model=StudentWorkspaceSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Workspace Real Telemetry Summary",
    description="Aggregates verified preparation statistics directly from persisted records (zero fake stats)."
)
def get_workspace_summary(
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> StudentWorkspaceSummary:
    verify_student_record_ownership(current_student.id, current_student)

    # Actual database counts & sums
    total_activities = (
        db.query(func.count(PreparationActivity.id))
        .filter(PreparationActivity.user_id == current_student.id)
        .scalar()
        or 0
    )

    total_duration_minutes = (
        db.query(func.sum(PreparationActivity.duration_minutes))
        .filter(PreparationActivity.user_id == current_student.id)
        .scalar()
        or 0
    )

    completed_activities = (
        db.query(func.count(PreparationActivity.id))
        .filter(
            PreparationActivity.user_id == current_student.id,
            PreparationActivity.completion_state == "COMPLETED",
        )
        .scalar()
        or 0
    )

    unique_topics_count = (
        db.query(func.count(func.distinct(PreparationActivity.topic)))
        .filter(PreparationActivity.user_id == current_student.id)
        .scalar()
        or 0
    )

    active_goals_count = (
        db.query(func.count(LearningGoal.id))
        .filter(
            LearningGoal.user_id == current_student.id,
            LearningGoal.status == "IN_PROGRESS",
        )
        .scalar()
        or 0
    )

    completed_goals_count = (
        db.query(func.count(LearningGoal.id))
        .filter(
            LearningGoal.user_id == current_student.id,
            LearningGoal.status == "COMPLETED",
        )
        .scalar()
        or 0
    )

    # Category breakdown
    category_rows = (
        db.query(
            PreparationActivity.category,
            func.sum(PreparationActivity.duration_minutes),
        )
        .filter(PreparationActivity.user_id == current_student.id)
        .group_by(PreparationActivity.category)
        .all()
    )
    category_minutes = {cat: int(mins) for cat, mins in category_rows}

    # Recent 5 activities
    recent = (
        db.query(PreparationActivity)
        .filter(PreparationActivity.user_id == current_student.id)
        .order_by(PreparationActivity.activity_date.desc(), PreparationActivity.created_at.desc())
        .limit(5)
        .all()
    )

    return StudentWorkspaceSummary(
        total_activities=total_activities,
        total_duration_minutes=int(total_duration_minutes),
        completed_activities=completed_activities,
        unique_topics_count=unique_topics_count,
        active_goals_count=active_goals_count,
        completed_goals_count=completed_goals_count,
        category_minutes=category_minutes,
        recent_activities=[PreparationActivityResponse.model_validate(r) for r in recent],
    )


# ---------------------------------------------------------------------------
# Learning Goals (Task 4)
# ---------------------------------------------------------------------------

def _build_goal_response(g: LearningGoal) -> LearningGoalResponse:
    target = float(g.target_value)
    curr = float(g.current_value)
    pct = round(min(100.0, (curr / target) * 100), 1) if target > 0 else 0.0

    return LearningGoalResponse(
        id=g.id,
        user_id=g.user_id,
        title=g.title,
        category=g.category,
        target_type=g.target_type,
        target_value=target,
        current_value=curr,
        deadline=g.deadline,
        status=g.status,
        progress_percentage=pct,
        created_at=g.created_at,
        updated_at=g.updated_at,
    )


@router.post(
    "/goals",
    response_model=LearningGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Learning Goal",
    description="Enables students to define actionable preparation goals with server-side validation."
)
def create_goal(
    payload: LearningGoalCreate,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> LearningGoalResponse:
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    goal = LearningGoal(
        user_id=current_student.id,
        title=payload.title.strip(),
        category=payload.category,
        target_type=payload.target_type,
        target_value=payload.target_value,
        current_value=0.00,
        deadline=payload.deadline,
        status="IN_PROGRESS",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    AuditService.record_event(
        db=db,
        institution_id=current_student.institution_id,
        actor_user_id=current_student.id,
        action="LEARNING_GOAL_CREATED",
        entity_type="LearningGoal",
        entity_id=str(goal.id),
        ip_address=client_ip,
        details_json={
            "title": goal.title,
            "category": goal.category,
            "target_type": goal.target_type,
            "target_value": float(goal.target_value),
        },
    )

    return _build_goal_response(goal)


@router.get(
    "/goals",
    response_model=List[LearningGoalResponse],
    status_code=status.HTTP_200_OK,
    summary="List Learning Goals",
    description="Returns goals belonging to the authenticated student with dynamic progress calculations."
)
def list_goals(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> List[LearningGoalResponse]:
    verify_student_record_ownership(current_student.id, current_student)

    query = db.query(LearningGoal).filter(LearningGoal.user_id == current_student.id)
    if status_filter:
        query = query.filter(LearningGoal.status == status_filter)

    goals = query.order_by(LearningGoal.created_at.desc()).all()
    return [_build_goal_response(g) for g in goals]


@router.put(
    "/goals/{goal_id}",
    response_model=LearningGoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Learning Goal",
    description="Allows students to update target values, current progress, or status with ownership enforcement."
)
def update_goal(
    goal_id: uuid.UUID,
    payload: LearningGoalUpdate,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
) -> LearningGoalResponse:
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    goal = db.query(LearningGoal).filter(LearningGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning goal not found.",
        )
    if goal.user_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you cannot modify another student's learning goal.",
        )

    changes = {}
    if payload.title is not None and payload.title.strip() != goal.title:
        goal.title = payload.title.strip()
        changes["title"] = goal.title
    if payload.category is not None and payload.category != goal.category:
        goal.category = payload.category
        changes["category"] = goal.category
    if payload.target_type is not None and payload.target_type != goal.target_type:
        goal.target_type = payload.target_type
        changes["target_type"] = goal.target_type
    if payload.target_value is not None:
        goal.target_value = payload.target_value
        changes["target_value"] = float(payload.target_value)
    if payload.current_value is not None:
        goal.current_value = payload.current_value
        changes["current_value"] = float(payload.current_value)
        if goal.current_value >= float(goal.target_value) and goal.status == "IN_PROGRESS":
            goal.status = "COMPLETED"
            changes["status"] = "COMPLETED"
    if payload.deadline is not None:
        goal.deadline = payload.deadline
        changes["deadline"] = payload.deadline.isoformat()
    if payload.status is not None and payload.status != goal.status:
        goal.status = payload.status
        changes["status"] = goal.status

    db.commit()
    db.refresh(goal)

    if changes:
        AuditService.record_event(
            db=db,
            institution_id=current_student.institution_id,
            actor_user_id=current_student.id,
            action="LEARNING_GOAL_UPDATED",
            entity_type="LearningGoal",
            entity_id=str(goal.id),
            ip_address=client_ip,
            details_json=changes,
        )

    return _build_goal_response(goal)


@router.delete(
    "/goals/{goal_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Learning Goal",
    description="Enforces ownership and deletes learning goal with audit record."
)
def delete_goal(
    goal_id: uuid.UUID,
    request: Request,
    current_student: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db),
):
    verify_student_record_ownership(current_student.id, current_student)
    client_ip = get_client_ip(request)

    goal = db.query(LearningGoal).filter(LearningGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning goal not found.",
        )
    if goal.user_id != current_student.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you cannot delete another student's learning goal.",
        )

    goal_details = {"title": goal.title, "category": goal.category}
    db.delete(goal)
    db.commit()

    AuditService.record_event(
        db=db,
        institution_id=current_student.institution_id,
        actor_user_id=current_student.id,
        action="LEARNING_GOAL_DELETED",
        entity_type="LearningGoal",
        entity_id=str(goal_id),
        ip_address=client_ip,
        details_json=goal_details,
    )

    return {"status": "deleted", "id": str(goal_id)}
