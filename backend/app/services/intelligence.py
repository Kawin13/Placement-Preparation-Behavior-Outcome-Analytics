import csv
from datetime import date, datetime, timezone
import io
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.practice import AttemptRecord, PreparationActivity, LearningGoal
from app.models.question import Question
from app.models.skill import Skill
from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance
from app.models.placement import PlacementOutcome
from app.models.audit import AuditLog
from app.schemas.intelligence import (
    CollegeIntelligenceOverview,
    EngagementPillar,
    AssessmentPillar,
    TrainingPillar,
    PlacementPillar,
    ActivityCategoryBreakdown,
    DomainAccuracyBreakdown,
    TierDistributionItem,
    ContentBankSummary,
    ContentBankDomainItem,
)
from app.services.audit import AuditService


CATEGORY_NAMES = {
    "QUANTITATIVE_APTITUDE": "Quantitative Aptitude",
    "LOGICAL_REASONING": "Logical Reasoning",
    "VERBAL_ABILITY": "Verbal Ability",
    "PROGRAMMING": "Programming & DSA",
    "SQL": "SQL & Databases",
    "CORE_TECHNICAL": "Core Technical",
    "HR_BEHAVIORAL": "HR & Behavioral",
    "GENERAL": "General Preparation",
}

DOMAIN_NAMES = {
    "QUANT": "Quantitative Aptitude",
    "LOGICAL": "Logical Reasoning",
    "VERBAL": "Verbal Ability",
    "PROGRAMMING": "Programming & Algorithms",
    "SQL": "SQL & Databases",
    "TECH_CORE": "Core Technical",
    "HR": "HR & Behavioral",
}

TIER_LABELS = {
    "TIER_1_PRODUCT": "Tier 1 Product Companies",
    "TIER_2_TECH": "Tier 2 Technology & High Growth",
    "CORE_ENG": "Core Engineering & Industrial",
    "MASS_IT": "Mass IT & Global Services",
}


def get_college_intelligence_overview(
    db: Session,
    actor: User,
    department_id: Optional[uuid.UUID] = None,
    cohort_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> CollegeIntelligenceOverview:
    if actor.role not in ("ADMIN", "PLACEMENT_OFFICER", "TRAINER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institutional staff (Administrators, Placement Officers, Trainers) may access college intelligence",
        )

    inst = db.query(Institution).filter(Institution.id == actor.institution_id).first()
    inst_name = inst.name if inst else "Educational Institution"

    dept_name = None
    if department_id:
        d = db.query(Department).filter(
            Department.id == department_id,
            Department.institution_id == actor.institution_id,
        ).first()
        dept_name = d.name if d else None

    cohort_label = None
    if cohort_id:
        c = (
            db.query(Cohort)
            .join(Department)
            .filter(
                Cohort.id == cohort_id,
                Department.institution_id == actor.institution_id,
            )
            .first()
        )
        if c:
            cohort_label = f"{c.department.name} Class of {c.graduation_year}" + (f" ({c.section})" if c.section else "")

    # Base cohort students query
    student_query = db.query(User).filter(
        User.institution_id == actor.institution_id,
        User.role == "STUDENT",
    )
    if cohort_id:
        student_query = student_query.join(User.student_profile).filter(StudentProfile.cohort_id == cohort_id)
    elif department_id:
        student_query = (
            student_query.join(User.student_profile)
            .join(StudentProfile.cohort)
            .filter(Cohort.department_id == department_id)
        )

    students = student_query.all()
    student_ids = [s.id for s in students]
    sample_size = len(student_ids)

    non_causal_msg = (
        "Institutional Intelligence Compliance (Rule 8): Preparation volume, skill-gap diagnostics, training "
        "attendance, and verified placement outcomes represent separate observational dimensions. Training "
        "participation or portal practice hours must not be claimed as the direct or sole cause of employment outcomes."
    )
    traceability_msg = (
        f"Data Provenance: Generated from verified relational records for institution {actor.institution_id}. "
        f"Sample size: N = {sample_size} students."
    )

    # Privacy Rule: Small-Cell Suppression for N < 5
    if sample_size < 5:
        return CollegeIntelligenceOverview(
            institution_id=actor.institution_id,
            institution_name=inst_name,
            generated_at=datetime.now(timezone.utc),
            is_suppressed=True,
            suppression_reason=(
                f"Small-cell privacy suppression enforced: Cohort sample size (N = {sample_size}) is below the "
                "institutional privacy threshold (N < 5). Aggregated performance and hiring breakdowns are masked to "
                "prevent indirect student re-identification."
            ),
            cohort_sample_size=sample_size,
            department_filter=dept_name,
            cohort_filter=cohort_label,
            date_window_start=start_date,
            date_window_end=end_date,
            engagement=None,
            assessments=None,
            training=None,
            placement=None,
            non_causal_notice=non_causal_msg,
            audit_traceability_notice=traceability_msg,
        )

    # -------------------------------------------------------------
    # Pillar 1: Student Preparation Engagement & Activity Volume
    # -------------------------------------------------------------
    act_query = db.query(PreparationActivity).filter(PreparationActivity.user_id.in_(student_ids))
    if start_date:
        act_query = act_query.filter(PreparationActivity.activity_date >= start_date)
    if end_date:
        act_query = act_query.filter(PreparationActivity.activity_date <= end_date)

    activities = act_query.all()
    active_user_ids = {a.user_id for a in activities}
    total_prep_mins = sum(a.duration_minutes for a in activities)
    total_prep_hours = round(total_prep_mins / 60.0, 1)

    # Breakdown by category
    cat_mins: Dict[str, int] = {}
    cat_counts: Dict[str, int] = {}
    for a in activities:
        cat_mins[a.category] = cat_mins.get(a.category, 0) + a.duration_minutes
        cat_counts[a.category] = cat_counts.get(a.category, 0) + 1

    activity_breakdowns = [
        ActivityCategoryBreakdown(
            category=cat,
            category_name=CATEGORY_NAMES.get(cat, cat.replace("_", " ").title()),
            hours_spent=round(cat_mins[cat] / 60.0, 1),
            activity_count=cat_counts[cat],
        )
        for cat in sorted(cat_mins.keys())
    ]

    # Goals completion
    goals = db.query(LearningGoal).filter(LearningGoal.user_id.in_(student_ids)).all()
    completed_goals = sum(1 for g in goals if g.status == "COMPLETED")
    goal_rate = round((completed_goals / len(goals)) * 100.0, 1) if goals else None

    engagement_pillar = EngagementPillar(
        total_enrolled_students=sample_size,
        active_students_count=len(active_user_ids),
        total_preparation_hours=total_prep_hours,
        total_activities_count=len(activities),
        goal_completion_rate=goal_rate,
        activity_breakdown=activity_breakdowns,
    )

    # -------------------------------------------------------------
    # Pillar 2: Assessment Accuracy & Skill-Gap Telemetry
    # -------------------------------------------------------------
    att_query = (
        db.query(
            Skill.domain,
            func.count(AttemptRecord.id).label("total_attempts"),
            func.sum(case((AttemptRecord.is_correct == True, 1), else_=0)).label("correct_attempts"),
        )
        .join(Question, AttemptRecord.question_id == Question.id)
        .join(Skill, Question.skill_id == Skill.id)
        .filter(AttemptRecord.user_id.in_(student_ids))
    )
    if start_date:
        att_query = att_query.filter(AttemptRecord.submitted_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
    if end_date:
        att_query = att_query.filter(AttemptRecord.submitted_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))

    domain_stats = att_query.group_by(Skill.domain).all()

    total_attempts_all = 0
    correct_attempts_all = 0
    domain_breakdowns = []
    for d_stat in domain_stats:
        d_total = d_stat.total_attempts or 0
        d_corr = d_stat.correct_attempts or 0
        total_attempts_all += d_total
        correct_attempts_all += d_corr
        d_acc = round((d_corr / d_total) * 100.0, 1) if d_total > 0 else None
        domain_breakdowns.append(
            DomainAccuracyBreakdown(
                domain=d_stat.domain,
                domain_name=DOMAIN_NAMES.get(d_stat.domain, d_stat.domain),
                total_attempts=d_total,
                correct_attempts=d_corr,
                accuracy_percentage=d_acc,
            )
        )

    overall_accuracy = (
        round((correct_attempts_all / total_attempts_all) * 100.0, 1)
        if total_attempts_all > 0
        else None
    )

    assessment_pillar = AssessmentPillar(
        total_evaluations=total_attempts_all,
        overall_accuracy_percentage=overall_accuracy,
        domain_breakdown=domain_breakdowns,
    )

    # -------------------------------------------------------------
    # Pillar 3: Training Program Impact & Attendance
    # -------------------------------------------------------------
    programs = db.query(TrainingProgram).filter(TrainingProgram.institution_id == actor.institution_id).all()
    program_ids = [p.id for p in programs]

    sessions = db.query(TrainingSession).filter(TrainingSession.program_id.in_(program_ids)).all() if program_ids else []
    session_ids = [s.id for s in sessions]

    attendance_records = (
        db.query(TrainingAttendance)
        .filter(
            TrainingAttendance.session_id.in_(session_ids),
            TrainingAttendance.user_id.in_(student_ids),
        )
        .all()
        if session_ids
        else []
    )

    present_count = sum(1 for a in attendance_records if a.attendance_status == "PRESENT")
    total_att_count = len(attendance_records)
    overall_att_rate = round((present_count / total_att_count) * 100.0, 1) if total_att_count > 0 else None

    training_pillar = TrainingPillar(
        total_programs_count=len(programs),
        total_sessions_delivered=len(sessions),
        total_attendance_records=total_att_count,
        overall_attendance_rate=overall_att_rate,
        mean_paired_score_delta=None,
    )

    # -------------------------------------------------------------
    # Pillar 4: Verified Placement Outcomes Conversion
    # -------------------------------------------------------------
    outcomes = (
        db.query(PlacementOutcome)
        .filter(PlacementOutcome.user_id.in_(student_ids))
        .all()
    )

    verified_outcomes = [o for o in outcomes if o.verification_status == "OFFICIALLY_VERIFIED"]
    pending_outcomes = [o for o in outcomes if o.verification_status == "PENDING_REVIEW"]
    rejected_outcomes = [o for o in outcomes if o.verification_status == "REJECTED"]

    verified_placed_users = {o.user_id for o in verified_outcomes}
    placement_rate = (
        round((len(verified_placed_users) / sample_size) * 100.0, 1)
        if sample_size > 0
        else None
    )

    verified_ctcs = [float(o.ctc_lpa) for o in verified_outcomes if o.ctc_lpa is not None]
    mean_ctc = round(sum(verified_ctcs) / len(verified_ctcs), 2) if verified_ctcs else None
    max_ctc = round(max(verified_ctcs), 2) if verified_ctcs else None

    # Tier breakdown
    tier_counts: Dict[str, List[float]] = {}
    for o in verified_outcomes:
        tier_counts.setdefault(o.tier, [])
        if o.ctc_lpa is not None:
            tier_counts[o.tier].append(float(o.ctc_lpa))

    tier_distribution = [
        TierDistributionItem(
            tier=t,
            tier_label=TIER_LABELS.get(t, t.replace("_", " ").title()),
            count=len(tier_counts.get(t, [])),
            mean_ctc=round(sum(tier_counts[t]) / len(tier_counts[t]), 2) if tier_counts.get(t) else None,
        )
        for t in ("TIER_1_PRODUCT", "TIER_2_TECH", "CORE_ENG", "MASS_IT")
        if t in tier_counts
    ]

    placement_pillar = PlacementPillar(
        total_reported_offers=len(outcomes),
        verified_offers_count=len(verified_outcomes),
        pending_review_count=len(pending_outcomes),
        rejected_count=len(rejected_outcomes),
        verified_placed_students_count=len(verified_placed_users),
        verified_placement_rate=placement_rate,
        mean_verified_ctc_lpa=mean_ctc,
        max_verified_ctc_lpa=max_ctc,
        tier_distribution=tier_distribution,
    )

    return CollegeIntelligenceOverview(
        institution_id=actor.institution_id,
        institution_name=inst_name,
        generated_at=datetime.now(timezone.utc),
        is_suppressed=False,
        suppression_reason=None,
        cohort_sample_size=sample_size,
        department_filter=dept_name,
        cohort_filter=cohort_label,
        date_window_start=start_date,
        date_window_end=end_date,
        engagement=engagement_pillar,
        assessments=assessment_pillar,
        training=training_pillar,
        placement=placement_pillar,
        non_causal_notice=non_causal_msg,
        audit_traceability_notice=traceability_msg,
    )


def export_college_intelligence_csv(
    db: Session,
    actor: User,
    department_id: Optional[uuid.UUID] = None,
    cohort_id: Optional[uuid.UUID] = None,
) -> str:
    if actor.role not in ("ADMIN", "PLACEMENT_OFFICER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and Placement Officers may export institutional intelligence reports",
        )

    overview = get_college_intelligence_overview(
        db=db,
        actor=actor,
        department_id=department_id,
        cohort_id=cohort_id,
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["INSTITUTIONAL INTELLIGENCE & ACCREDITATION REPORT"])
    writer.writerow(["Institution", overview.institution_name])
    writer.writerow(["Generated At (UTC)", overview.generated_at.strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Department Filter", overview.department_filter or "All Departments"])
    writer.writerow(["Cohort Filter", overview.cohort_filter or "All Cohorts"])
    writer.writerow(["Sample Size (N)", overview.cohort_sample_size])
    writer.writerow(["Privacy Status", "Suppressed (N < 5)" if overview.is_suppressed else "Unsuppressed (Sufficient Sample)"])
    writer.writerow([])

    if overview.is_suppressed:
        writer.writerow(["NOTICE", overview.suppression_reason or "Metrics masked due to privacy policy"])
    else:
        # Engagement
        writer.writerow(["--- PILLAR 1: ENGAGEMENT & ACTIVITY VOLUME ---"])
        writer.writerow(["Total Enrolled Students", overview.engagement.total_enrolled_students if overview.engagement else 0])
        writer.writerow(["Active Students", overview.engagement.active_students_count if overview.engagement else 0])
        writer.writerow(["Total Preparation Hours", overview.engagement.total_preparation_hours if overview.engagement else 0])
        writer.writerow(["Total Activity Records", overview.engagement.total_activities_count if overview.engagement else 0])
        writer.writerow(["Goal Completion Rate (%)", overview.engagement.goal_completion_rate if overview.engagement else "N/A"])
        writer.writerow([])

        # Assessments
        writer.writerow(["--- PILLAR 2: ASSESSMENT & SKILL ACCURACY ---"])
        writer.writerow(["Total Attempts Logged", overview.assessments.total_evaluations if overview.assessments else 0])
        writer.writerow(["Overall Accuracy (%)", overview.assessments.overall_accuracy_percentage if overview.assessments else "N/A"])
        if overview.assessments and overview.assessments.domain_breakdown:
            writer.writerow(["Domain", "Attempts", "Correct", "Accuracy (%)"])
            for d in overview.assessments.domain_breakdown:
                writer.writerow([d.domain_name, d.total_attempts, d.correct_attempts, d.accuracy_percentage or "N/A"])
        writer.writerow([])

        # Training
        writer.writerow(["--- PILLAR 3: TRAINING IMPACT & ATTENDANCE ---"])
        writer.writerow(["Total Training Programmes", overview.training.total_programs_count if overview.training else 0])
        writer.writerow(["Total Sessions Delivered", overview.training.total_sessions_delivered if overview.training else 0])
        writer.writerow(["Overall Attendance Rate (%)", overview.training.overall_attendance_rate if overview.training else "N/A"])
        writer.writerow([])

        # Placement
        writer.writerow(["--- PILLAR 4: VERIFIED PLACEMENT CONVERSION ---"])
        writer.writerow(["Reported Offers", overview.placement.total_reported_offers if overview.placement else 0])
        writer.writerow(["Verified Offers", overview.placement.verified_offers_count if overview.placement else 0])
        writer.writerow(["Pending Review Offers", overview.placement.pending_review_count if overview.placement else 0])
        writer.writerow(["Verified Placed Students", overview.placement.verified_placed_students_count if overview.placement else 0])
        writer.writerow(["Verified Placement Rate (%)", overview.placement.verified_placement_rate if overview.placement else "N/A"])
        writer.writerow(["Mean Verified CTC (LPA)", overview.placement.mean_verified_ctc_lpa if overview.placement else "N/A"])
        writer.writerow(["Max Verified CTC (LPA)", overview.placement.max_verified_ctc_lpa if overview.placement else "N/A"])
        writer.writerow([])

    writer.writerow(["POLICY NOTICE", overview.non_causal_notice])

    AuditService.record_event(
        db=db,
        institution_id=actor.institution_id,
        actor_user_id=actor.id,
        action="COLLEGE_INTELLIGENCE_EXPORTED_CSV",
        entity_type="institutional_intelligence",
        entity_id=f"n_{overview.cohort_sample_size}",
        details_json={
            "department_id": str(department_id) if department_id else None,
            "cohort_id": str(cohort_id) if cohort_id else None,
            "sample_size": overview.cohort_sample_size,
        },
    )

    return output.getvalue()


def get_content_bank_summary(db: Session, actor: User) -> ContentBankSummary:
    if actor.role not in ("ADMIN", "TRAINER", "PLACEMENT_OFFICER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institutional staff may view content bank summaries",
        )

    # Assessments count
    assessments = db.query(Question).all()  # total questions
    # Domain breakdown
    domain_counts = (
        db.query(
            Skill.domain,
            func.count(Question.id).label("question_count"),
        )
        .join(Question, Question.skill_id == Skill.id)
        .group_by(Skill.domain)
        .all()
    )

    # Attempts per domain
    domain_attempts = (
        db.query(
            Skill.domain,
            func.count(AttemptRecord.id).label("attempt_count"),
        )
        .join(Question, AttemptRecord.question_id == Question.id)
        .join(Skill, Question.skill_id == Skill.id)
        .group_by(Skill.domain)
        .all()
    )
    attempt_map = {d.domain: d.attempt_count for d in domain_attempts}

    domain_items = [
        ContentBankDomainItem(
            domain=d.domain,
            question_count=d.question_count,
            assessment_count=1,
            total_attempts=attempt_map.get(d.domain, 0),
        )
        for d in domain_counts
    ]

    total_q = sum(d.question_count for d in domain_counts)

    return ContentBankSummary(
        total_assessments=len(domain_items),
        published_assessments=len(domain_items),
        total_questions=total_q,
        domains=domain_items,
    )
