import math
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, StudentProfile
from app.models.institution import Cohort, Department
from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance
from app.models.practice import PracticeSession, AttemptRecord
from app.models.question import Question
from app.models.skill import Skill
from app.schemas.training import (
    TrainingProgramCreate,
    TrainingProgramResponse,
    TrainingSessionCreate,
    TrainingSessionResponse,
    BatchAttendanceRequest,
    AttendanceRecordResponse,
    PrePostStudentScore,
    TrainingEffectivenessReport,
)
from app.services.audit import AuditService


def _map_program_to_response(db: Session, prog: TrainingProgram) -> TrainingProgramResponse:
    trainer_name = prog.trainer.full_name if prog.trainer else None
    sessions_count = db.query(TrainingSession).filter(TrainingSession.program_id == prog.id).count()

    # Enrolled students = distinct students who have attendance marked in any session of this program
    enrolled_count = (
        db.query(TrainingAttendance.user_id)
        .join(TrainingAttendance.session)
        .filter(TrainingSession.program_id == prog.id)
        .distinct()
        .count()
    )

    return TrainingProgramResponse(
        id=prog.id,
        institution_id=prog.institution_id,
        title=prog.title,
        description=prog.description,
        domain=prog.domain,
        start_date=prog.start_date,
        end_date=prog.end_date,
        total_planned_hours=prog.total_planned_hours,
        trainer_id=prog.trainer_id,
        trainer_name=trainer_name,
        total_sessions_count=sessions_count,
        total_enrolled_students=enrolled_count,
        created_at=prog.created_at,
    )


def create_training_program(
    db: Session,
    actor: User,
    req: TrainingProgramCreate,
) -> TrainingProgramResponse:
    if actor.role not in ("TRAINER", "PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Trainers, Placement Officers, and Administrators can create training programmes",
        )

    trainer_id = req.trainer_id or (actor.id if actor.role == "TRAINER" else None)

    prog = TrainingProgram(
        institution_id=actor.institution_id,
        title=req.title.strip(),
        description=req.description.strip() if req.description else None,
        domain=req.domain,
        start_date=req.start_date,
        end_date=req.end_date,
        total_planned_hours=req.total_planned_hours,
        trainer_id=trainer_id,
    )
    db.add(prog)
    db.commit()
    db.refresh(prog)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="TRAINING_PROGRAM_CREATED",
        entity_type="training_programs",
        entity_id=str(prog.id),
        details_json={"title": prog.title, "domain": prog.domain},
    )

    return _map_program_to_response(db, prog)


def list_training_programs(
    db: Session,
    actor: User,
    domain_filter: Optional[str] = None,
) -> List[TrainingProgramResponse]:
    query = db.query(TrainingProgram).filter(TrainingProgram.institution_id == actor.institution_id)
    if domain_filter:
        query = query.filter(TrainingProgram.domain == domain_filter)

    programs = query.order_by(TrainingProgram.start_date.desc()).all()
    return [_map_program_to_response(db, p) for p in programs]


def get_training_program_by_id(
    db: Session,
    actor: User,
    program_id: uuid.UUID,
) -> TrainingProgramResponse:
    prog = (
        db.query(TrainingProgram)
        .filter(
            TrainingProgram.id == program_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training program not found")
    return _map_program_to_response(db, prog)


def create_training_session(
    db: Session,
    actor: User,
    req: TrainingSessionCreate,
) -> TrainingSessionResponse:
    if actor.role not in ("TRAINER", "PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Trainers and Placement Officers can add training sessions",
        )

    prog = (
        db.query(TrainingProgram)
        .filter(
            TrainingProgram.id == req.program_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training program not found")

    sess = TrainingSession(
        program_id=req.program_id,
        session_date=req.session_date,
        start_time=req.start_time,
        duration_minutes=req.duration_minutes,
        topic_covered=req.topic_covered.strip(),
        trainer_notes=req.trainer_notes.strip() if req.trainer_notes else None,
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="TRAINING_SESSION_CREATED",
        entity_type="training_sessions",
        entity_id=str(sess.id),
        details_json={"program_id": str(prog.id), "topic": sess.topic_covered},
    )

    return TrainingSessionResponse(
        id=sess.id,
        program_id=sess.program_id,
        session_date=sess.session_date,
        start_time=sess.start_time,
        duration_minutes=sess.duration_minutes,
        topic_covered=sess.topic_covered,
        trainer_notes=sess.trainer_notes,
        attendance_count=0,
        created_at=sess.created_at,
    )


def list_training_sessions(
    db: Session,
    actor: User,
    program_id: uuid.UUID,
) -> List[TrainingSessionResponse]:
    prog = (
        db.query(TrainingProgram)
        .filter(
            TrainingProgram.id == program_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training program not found")

    sessions = (
        db.query(TrainingSession)
        .filter(TrainingSession.program_id == program_id)
        .order_by(TrainingSession.session_date.asc())
        .all()
    )

    results = []
    for s in sessions:
        att_count = (
            db.query(TrainingAttendance)
            .filter(
                TrainingAttendance.session_id == s.id,
                TrainingAttendance.attendance_status == "PRESENT",
            )
            .count()
        )
        results.append(
            TrainingSessionResponse(
                id=s.id,
                program_id=s.program_id,
                session_date=s.session_date,
                start_time=s.start_time,
                duration_minutes=s.duration_minutes,
                topic_covered=s.topic_covered,
                trainer_notes=s.trainer_notes,
                attendance_count=att_count,
                created_at=s.created_at,
            )
        )
    return results


def mark_batch_attendance(
    db: Session,
    actor: User,
    req: BatchAttendanceRequest,
) -> List[AttendanceRecordResponse]:
    if actor.role not in ("TRAINER", "PLACEMENT_OFFICER", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Trainers and Placement Officers can mark attendance",
        )

    session_obj = (
        db.query(TrainingSession)
        .join(TrainingSession.program)
        .filter(
            TrainingSession.id == req.session_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    saved_records = []
    for item in req.attendance_list:
        student = (
            db.query(User)
            .filter(User.id == item.user_id, User.institution_id == actor.institution_id)
            .first()
        )
        if not student:
            continue

        existing = (
            db.query(TrainingAttendance)
            .filter(
                TrainingAttendance.session_id == req.session_id,
                TrainingAttendance.user_id == item.user_id,
            )
            .first()
        )
        if existing:
            existing.attendance_status = item.attendance_status
            existing.marked_by_user_id = actor.id
            existing.marked_at = datetime.now(timezone.utc)
            record = existing
        else:
            record = TrainingAttendance(
                session_id=req.session_id,
                user_id=item.user_id,
                attendance_status=item.attendance_status,
                marked_by_user_id=actor.id,
                marked_at=datetime.now(timezone.utc),
            )
            db.add(record)
        saved_records.append(record)

    db.commit()

    AuditService.record_event(
        db=db,
        actor_user_id=actor.id,
        institution_id=actor.institution_id,
        action="TRAINING_ATTENDANCE_RECORDED",
        entity_type="training_attendance",
        entity_id=str(req.session_id),
        details_json={"student_count": len(saved_records)},
    )

    results = []
    for r in saved_records:
        student = r.user
        roll = student.student_profile.roll_number if (student and student.student_profile) else None
        results.append(
            AttendanceRecordResponse(
                id=r.id,
                session_id=r.session_id,
                user_id=r.user_id,
                student_name=student.full_name if student else "Unknown",
                student_roll=roll,
                attendance_status=r.attendance_status,
                marked_by_name=actor.full_name,
                marked_at=r.marked_at,
            )
        )
    return results


def get_session_attendance(
    db: Session,
    actor: User,
    session_id: uuid.UUID,
) -> List[AttendanceRecordResponse]:
    session_obj = (
        db.query(TrainingSession)
        .join(TrainingSession.program)
        .filter(
            TrainingSession.id == session_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training session not found")

    query = (
        db.query(TrainingAttendance)
        .join(TrainingAttendance.user)
        .filter(TrainingAttendance.session_id == session_id)
    )

    # Student peer privacy: students can only see their own attendance record
    if actor.role == "STUDENT":
        query = query.filter(TrainingAttendance.user_id == actor.id)

    records = query.all()
    results = []
    for r in records:
        student = r.user
        roll = student.student_profile.roll_number if (student and student.student_profile) else None
        marker_name = r.marked_by.full_name if r.marked_by else None
        results.append(
            AttendanceRecordResponse(
                id=r.id,
                session_id=r.session_id,
                user_id=r.user_id,
                student_name=student.full_name if student else "Unknown",
                student_roll=roll,
                attendance_status=r.attendance_status,
                marked_by_name=marker_name,
                marked_at=r.marked_at,
            )
        )
    return results


def calculate_program_effectiveness(
    db: Session,
    actor: User,
    program_id: uuid.UUID,
) -> TrainingEffectivenessReport:
    """
    Evaluates training programme effectiveness using the approved Paired Assessment Window methodology:
    - Pre-training baseline: verified attempts logged within 30 days prior to program.start_date
    - Post-training window: verified attempts logged within 30 days following program.end_date
    - Matched pairs: students with verified attempts in BOTH pre and post windows for program.domain
    - Strict Non-Causal Reporting & Statistical Limitations explicitly surfaced.
    """
    prog = (
        db.query(TrainingProgram)
        .filter(
            TrainingProgram.id == program_id,
            TrainingProgram.institution_id == actor.institution_id,
        )
        .first()
    )
    if not prog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training program not found")

    total_sessions = db.query(TrainingSession).filter(TrainingSession.program_id == prog.id).count()

    # Find all enrolled students (any attendance recorded in this program)
    enrolled_students = (
        db.query(User)
        .join(TrainingAttendance, TrainingAttendance.user_id == User.id)
        .join(TrainingSession, TrainingAttendance.session_id == TrainingSession.id)
        .filter(TrainingSession.program_id == prog.id)
        .distinct()
        .all()
    )

    pre_start = prog.start_date - timedelta(days=30)
    pre_end = prog.start_date
    post_start = prog.end_date
    post_end = prog.end_date + timedelta(days=30)

    # Domain mapping (e.g. QUANT -> QUANT)
    target_domain = prog.domain

    breakdown: List[PrePostStudentScore] = []
    attendance_percentages: List[float] = []
    pre_scores: List[float] = []
    post_scores: List[float] = []
    score_deltas: List[float] = []

    missing_pre = 0
    missing_post = 0
    matched_pairs = 0

    for st in enrolled_students:
        # 1. Attendance rate
        attended_sessions = (
            db.query(TrainingAttendance)
            .join(TrainingAttendance.session)
            .filter(
                TrainingSession.program_id == prog.id,
                TrainingAttendance.user_id == st.id,
                TrainingAttendance.attendance_status == "PRESENT",
            )
            .count()
        )
        att_pct = (attended_sessions / total_sessions * 100.0) if total_sessions > 0 else 0.0
        attendance_percentages.append(att_pct)

        # 2. Pre-training accuracy in target domain
        pre_attempts = (
            db.query(AttemptRecord)
            .join(AttemptRecord.question)
            .join(Question.skill)
            .filter(
                AttemptRecord.user_id == st.id,
                func.date(AttemptRecord.submitted_at) >= pre_start,
                func.date(AttemptRecord.submitted_at) < pre_end,
                Skill.domain == target_domain,
            )
            .all()
        )
        pre_score: Optional[float] = None
        if len(pre_attempts) >= 3:  # minimum 3 attempts to establish reliable pre-baseline
            pre_correct = sum(1 for a in pre_attempts if a.is_correct)
            pre_score = (pre_correct / len(pre_attempts)) * 100.0

        # 3. Post-training accuracy in target domain
        post_attempts = (
            db.query(AttemptRecord)
            .join(AttemptRecord.question)
            .join(Question.skill)
            .filter(
                AttemptRecord.user_id == st.id,
                func.date(AttemptRecord.submitted_at) >= post_start,
                func.date(AttemptRecord.submitted_at) <= post_end,
                Skill.domain == target_domain,
            )
            .all()
        )
        post_score: Optional[float] = None
        if len(post_attempts) >= 3:
            post_correct = sum(1 for a in post_attempts if a.is_correct)
            post_score = (post_correct / len(post_attempts)) * 100.0

        is_matched = pre_score is not None and post_score is not None
        delta = (post_score - pre_score) if is_matched else None

        if is_matched:
            matched_pairs += 1
            pre_scores.append(pre_score)
            post_scores.append(post_score)
            score_deltas.append(delta)
        else:
            if pre_score is None:
                missing_pre += 1
            if post_score is None:
                missing_post += 1

        roll = st.student_profile.roll_number if st.student_profile else None
        dept = (
            st.student_profile.cohort.department.name
            if (st.student_profile and st.student_profile.cohort and st.student_profile.cohort.department)
            else None
        )

        breakdown.append(
            PrePostStudentScore(
                user_id=st.id,
                student_name=st.full_name,
                student_roll=roll,
                department_name=dept,
                sessions_attended=attended_sessions,
                attendance_percentage=round(att_pct, 1),
                pre_training_score=round(pre_score, 1) if pre_score is not None else None,
                post_training_score=round(post_score, 1) if post_score is not None else None,
                score_delta=round(delta, 1) if delta is not None else None,
                is_matched_pair=is_matched,
            )
        )

    # Aggregate summaries
    mean_att = (sum(attendance_percentages) / len(attendance_percentages)) if attendance_percentages else 0.0
    mean_pre = (sum(pre_scores) / len(pre_scores)) if pre_scores else None
    mean_post = (sum(post_scores) / len(post_scores)) if post_scores else None
    mean_delta = (sum(score_deltas) / len(score_deltas)) if score_deltas else None

    # Pearson correlation r between attendance % and score delta (only if N >= 5)
    correlation_val: Optional[float] = None
    if matched_pairs >= 5:
        # calculate pearson r
        matched_items = [b for b in breakdown if b.is_matched_pair]
        xs = [m.attendance_percentage for m in matched_items]
        ys = [m.score_delta for m in matched_items]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        var_x = sum((x - mean_x) ** 2 for x in xs)
        var_y = sum((y - mean_y) ** 2 for y in ys)
        cov_xy = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(len(xs)))
        if var_x > 0 and var_y > 0:
            correlation_val = round(cov_xy / math.sqrt(var_x * var_y), 3)

    return TrainingEffectivenessReport(
        program_id=prog.id,
        program_title=prog.title,
        domain=prog.domain,
        total_sessions_completed=total_sessions,
        total_enrolled=len(enrolled_students),
        matched_pairs_count=matched_pairs,
        missing_pre_count=missing_pre,
        missing_post_count=missing_post,
        mean_attendance_percentage=round(mean_att, 1),
        mean_pre_score=round(mean_pre, 1) if mean_pre is not None else None,
        mean_post_score=round(mean_post, 1) if mean_post is not None else None,
        mean_score_delta=round(mean_delta, 1) if mean_delta is not None else None,
        correlation_attendance_and_gain=correlation_val,
        student_breakdown=breakdown,
        non_causal_disclaimer=(
            "Observational Association Notice: Performance differences between pre- and post-training "
            "windows reflect statistical association and must not be interpreted as direct causal attribution. "
            "Concurrent college coursework, unmeasured independent study, and practice test familiarity may influence observed score changes."
        ),
        data_limitations=(
            f"Pre/post window: 30 days pre-commencement vs 30 days post-conclusion. "
            f"Matched sample: {matched_pairs} students. {missing_pre} students missing baseline; {missing_post} students missing post-evaluations."
        ),
    )
