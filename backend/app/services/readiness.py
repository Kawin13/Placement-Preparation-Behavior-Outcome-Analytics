import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, StudentProfile
from app.models.skill import Skill
from app.models.question import Question
from app.models.practice import AttemptRecord
from app.models.assessment import Assessment, AssessmentQuestion
from app.schemas.readiness import (
    RoleDefinition,
    DomainWeightRequirement,
    DomainEvidenceItem,
    PracticeRecommendation,
    RoleReadinessResponse,
)

# --------------------------------------------------------------------------
# Institutional Role Definitions and Competency Framework
# --------------------------------------------------------------------------
ROLE_FRAMEWORK: Dict[str, RoleDefinition] = {
    "SDE": RoleDefinition(
        role_id="SDE",
        role_name="Software Development Engineer",
        description="Core algorithmic problem solving, computational complexity, tree/graph traversal, and logical deduction.",
        target_industry_tier="Tier-1 Product & Tech Core (CTC > 10 LPA)",
        domain_requirements=[
            DomainWeightRequirement(
                domain="PROGRAMMING",
                domain_name="Algorithms & Data Structures",
                weight=0.35,
                min_attempts=5,
                target_accuracy=65.0,
            ),
            DomainWeightRequirement(
                domain="QUANT",
                domain_name="Quantitative Aptitude",
                weight=0.25,
                min_attempts=5,
                target_accuracy=60.0,
            ),
            DomainWeightRequirement(
                domain="LOGICAL",
                domain_name="Logical Reasoning",
                weight=0.25,
                min_attempts=5,
                target_accuracy=65.0,
            ),
            DomainWeightRequirement(
                domain="VERBAL",
                domain_name="Verbal Ability",
                weight=0.15,
                min_attempts=5,
                target_accuracy=55.0,
            ),
        ],
    ),
    "DATA_ANALYST": RoleDefinition(
        role_id="DATA_ANALYST",
        role_name="Data Analyst / SQL Specialist",
        description="Relational database queries, complex aggregations, statistical aptitude, and structured problem solving.",
        target_industry_tier="Product Analytics, Business Intelligence & Tech Consulting",
        domain_requirements=[
            DomainWeightRequirement(
                domain="SQL",
                domain_name="Relational Queries & SQL",
                weight=0.35,
                min_attempts=5,
                target_accuracy=65.0,
            ),
            DomainWeightRequirement(
                domain="QUANT",
                domain_name="Quantitative Aptitude",
                weight=0.30,
                min_attempts=5,
                target_accuracy=65.0,
            ),
            DomainWeightRequirement(
                domain="LOGICAL",
                domain_name="Logical Reasoning",
                weight=0.20,
                min_attempts=5,
                target_accuracy=60.0,
            ),
            DomainWeightRequirement(
                domain="VERBAL",
                domain_name="Verbal Ability",
                weight=0.15,
                min_attempts=5,
                target_accuracy=50.0,
            ),
        ],
    ),
    "CORE_TECH": RoleDefinition(
        role_id="CORE_TECH",
        role_name="Core Technology Graduate",
        description="Foundational problem solving, formal deduction, precision syntax, and engineering aptitude.",
        target_industry_tier="Engineering Core, Manufacturing & Technology Services",
        domain_requirements=[
            DomainWeightRequirement(
                domain="QUANT",
                domain_name="Quantitative Aptitude",
                weight=0.40,
                min_attempts=5,
                target_accuracy=60.0,
            ),
            DomainWeightRequirement(
                domain="LOGICAL",
                domain_name="Logical Reasoning",
                weight=0.35,
                min_attempts=5,
                target_accuracy=60.0,
            ),
            DomainWeightRequirement(
                domain="VERBAL",
                domain_name="Verbal Ability",
                weight=0.25,
                min_attempts=5,
                target_accuracy=55.0,
            ),
        ],
    ),
}


def list_approved_roles() -> List[RoleDefinition]:
    """Returns the list of all approved placement roles and their skill frameworks."""
    return list(ROLE_FRAMEWORK.values())


def calculate_role_readiness(
    db: Session,
    user_id: uuid.UUID,
    role_id: str = "SDE",
) -> RoleReadinessResponse:
    """
    Computes deterministic role-specific readiness using verified database records.
    Enforces minimum sample thresholds (N >= 5 per domain).
    Suppresses readiness scores where evidence is insufficient.
    """
    if role_id not in ROLE_FRAMEWORK:
        raise ValueError(f"Unrecognized role '{role_id}'. Approved roles: {list(ROLE_FRAMEWORK.keys())}")

    role = ROLE_FRAMEWORK[role_id]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User record not found")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    roll_number = profile.roll_number if profile else None

    # Fetch all evaluated attempt records for user
    evaluated_attempts = (
        db.query(AttemptRecord)
        .join(Question, AttemptRecord.question_id == Question.id)
        .join(Skill, Question.skill_id == Skill.id)
        .filter(
            AttemptRecord.user_id == user_id,
            AttemptRecord.submitted_answer.isnot(None),
        )
        .all()
    )

    now = datetime.now(timezone.utc)
    domain_evidence_list: List[DomainEvidenceItem] = []
    missing_evidence_summary: List[str] = []
    has_sufficient_evidence = True
    total_role_attempts = 0
    weighted_score_accum = 0.0

    domain_difficulty_weights = {"EASY": 1.0, "MEDIUM": 1.25, "HARD": 1.5}

    for req in role.domain_requirements:
        # Filter attempts matching this domain
        dom_attempts = [
            a for a in evaluated_attempts
            if a.question and a.question.skill and a.question.skill.domain == req.domain
        ]
        att_count = len(dom_attempts)
        total_role_attempts += att_count

        corr_count = sum(1 for a in dom_attempts if a.is_correct)

        # Recency check
        recency_days_ago: Optional[int] = None
        recency_label = "No attempts recorded"
        if dom_attempts:
            submitted_dates = [a.submitted_at for a in dom_attempts if a.submitted_at]
            if submitted_dates:
                latest_sub = max(submitted_dates)
                if latest_sub.tzinfo is None:
                    latest_sub = latest_sub.replace(tzinfo=timezone.utc)
                recency_days_ago = max(0, (now - latest_sub).days)
                if recency_days_ago == 0:
                    recency_label = "Active today"
                elif recency_days_ago < 30:
                    recency_label = f"Active ({recency_days_ago} days ago)"
                elif recency_days_ago <= 90:
                    recency_label = f"Recent ({recency_days_ago} days ago)"
                else:
                    recency_label = f"Stale ({recency_days_ago} days ago)"

        # Check evidence threshold (N >= 5)
        if att_count < req.min_attempts:
            has_sufficient_evidence = False
            needed = req.min_attempts - att_count
            missing_evidence_summary.append(
                f"{req.domain_name}: {att_count}/{req.min_attempts} attempts logged (Need {needed} more to evaluate)."
            )
            domain_evidence_list.append(
                DomainEvidenceItem(
                    domain=req.domain,
                    domain_name=req.domain_name,
                    weight=req.weight,
                    attempts_count=att_count,
                    correct_count=corr_count,
                    raw_accuracy_percentage=None,
                    weighted_domain_score=None,
                    meets_threshold=False,
                    attempts_needed=needed,
                    recency_days_ago=recency_days_ago,
                    recency_label=recency_label,
                    status="INSUFFICIENT_EVIDENCE",
                    evidence_note=f"Sample size below institutional minimum ({att_count}/{req.min_attempts}).",
                )
            )
        else:
            raw_acc = (corr_count / att_count) * 100.0

            # Difficulty adjustment factor
            diff_sum = sum(domain_difficulty_weights.get(a.question.difficulty, 1.0) for a in dom_attempts)
            diff_factor = diff_sum / (1.5 * att_count)
            domain_score = round(min(100.0, raw_acc * diff_factor), 1)

            weighted_score_accum += req.weight * domain_score

            status = (
                "PROFICIENT"
                if domain_score >= req.target_accuracy
                else "MODERATE"
                if domain_score >= (req.target_accuracy - 15.0)
                else "NEEDS_ATTENTION"
            )

            domain_evidence_list.append(
                DomainEvidenceItem(
                    domain=req.domain,
                    domain_name=req.domain_name,
                    weight=req.weight,
                    attempts_count=att_count,
                    correct_count=corr_count,
                    raw_accuracy_percentage=round(raw_acc, 1),
                    weighted_domain_score=domain_score,
                    meets_threshold=True,
                    attempts_needed=0,
                    recency_days_ago=recency_days_ago,
                    recency_label=recency_label,
                    status=status,
                    evidence_note=f"Evaluated across {att_count} verified attempts with difficulty weighting.",
                )
            )

    # Determine Overall Readiness Score and Tier
    if not has_sufficient_evidence:
        final_score = None
        final_tier = "INSUFFICIENT_EVIDENCE"
    else:
        final_score = round(weighted_score_accum, 1)
        if final_score >= 75.0:
            final_tier = "ROLE_READY"
        elif final_score >= 50.0:
            final_tier = "DEVELOPING"
        else:
            final_tier = "FOUNDATION_NEEDED"

    # Query Real Catalogue Assessments for Practice Recommendations
    recommendations: List[PracticeRecommendation] = []
    published_assessments = (
        db.query(Assessment)
        .filter(Assessment.is_published == True)
        .all()
    )

    # Map assessment categories to domains
    category_to_domain = {
        "QUANTITATIVE_APTITUDE": "QUANT",
        "LOGICAL_REASONING": "LOGICAL",
        "VERBAL_ABILITY": "VERBAL",
        "PROGRAMMING_DSA": "PROGRAMMING",
        "SQL_DATABASE": "SQL",
    }

    for ev in domain_evidence_list:
        if ev.status in ("INSUFFICIENT_EVIDENCE", "NEEDS_ATTENTION", "MODERATE"):
            # Find matching assessments
            matching = [
                a for a in published_assessments
                if category_to_domain.get(a.category) == ev.domain
            ]
            for asm in matching:
                priority = (
                    "CRITICAL_DEFICIT"
                    if ev.status == "INSUFFICIENT_EVIDENCE"
                    else "HIGH_PRIORITY"
                    if ev.status == "NEEDS_ATTENTION"
                    else "REINFORCEMENT"
                )
                rationale = (
                    f"Required to unlock readiness evaluation: logged {ev.attempts_count}/{req.min_attempts} attempts."
                    if ev.status == "INSUFFICIENT_EVIDENCE"
                    else f"Recommended to address demonstrated accuracy gap ({ev.weighted_domain_score}% vs target {req.target_accuracy}%)."
                )
                recommendations.append(
                    PracticeRecommendation(
                        assessment_id=asm.id,
                        assessment_title=asm.title,
                        domain=ev.domain,
                        category=asm.category or "PRACTICE",
                        duration_minutes=asm.duration_minutes,
                        priority=priority,
                        rationale=rationale,
                    )
                )

    return RoleReadinessResponse(
        student_id=user.id,
        student_name=user.full_name,
        roll_number=roll_number,
        role_id=role.role_id,
        role_name=role.role_name,
        role_description=role.description,
        target_industry_tier=role.target_industry_tier,
        readiness_score=final_score,
        readiness_tier=final_tier,
        has_sufficient_evidence=has_sufficient_evidence,
        total_role_attempts=total_role_attempts,
        domain_evidence=domain_evidence_list,
        missing_evidence_summary=missing_evidence_summary,
        recommendations=recommendations,
        non_predictive_disclaimer=(
            "Institutional Non-Predictive Disclaimer: Role Readiness reflects demonstrated skill mastery "
            "across verified syllabus assessments. It is a formative learning diagnostic and does not guarantee "
            "placement, hiring selection, or predict job offer outcomes."
        ),
        formula_documentation=(
            "Readiness Score = SUM(Domain_Weight * Domain_Score), where Domain_Score = Accuracy * Difficulty_Factor. "
            "Enforces a strict minimum threshold of 5 evaluated attempts per domain. "
            "Readiness is suppressed to None when any domain has insufficient evidence."
        ),
        last_evaluated_at=now,
    )
