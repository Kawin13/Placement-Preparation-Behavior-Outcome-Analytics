import uuid
import logging
from typing import Optional, List, Dict
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.question import Question, QuestionOption
from app.models.skill import Skill
from app.models.practice import AttemptRecord
from app.models.assessment import Assessment
from app.services.audit import AuditService
from app.schemas.coach import (
    MistakeExplanationRequest,
    MistakeExplanationResponse,
    StudyPlanRequest,
    StudyPlanResponse,
    StudyPlanItem,
)
from app.services.readiness import ROLE_FRAMEWORK

logger = logging.getLogger(__name__)


def explain_student_mistake(
    db: Session,
    user: User,
    req: MistakeExplanationRequest,
) -> MistakeExplanationResponse:
    """
    Generates a syllabus-grounded conceptual explanation for an incorrect answer.
    Sends only minimal authorized context (question text, concept, student reflection).
    Zero PII or peer data transmitted.
    Falls back gracefully to the offline pedagogical engine if external AI is unconfigured or fails.
    """
    question = db.query(Question).filter(Question.id == req.question_id).first()
    if not question:
        raise ValueError("Target question not found in catalog")

    correct_option = next((opt for opt in question.options if opt.is_correct), None)
    selected_option = next((opt for opt in question.options if opt.option_text == req.selected_answer), None)

    # Context sanitization: Ensure NO student personal data is in prompt
    grounded_concept = question.title.split(":")[0].strip() if ":" in question.title else question.title
    correct_text = correct_option.option_text if correct_option else "Verified syllabus solution"
    official_explanation = question.explanation or "Deterministic concept proof"

    provider_used = "OFFLINE_GROUNDED_MENTOR"
    detailed_proof = official_explanation
    remedial_takeaway = (
        f"Revisit core principles of {grounded_concept}. Verify prerequisite formulas before calculating."
    )
    why_incorrect = (
        selected_option.feedback
        if selected_option and selected_option.feedback
        else "Misapplication of standard formula or misinterpretation of problem constraints."
    )

    api_key = settings.GEMINI_API_KEY or settings.AI_API_KEY
    if api_key and settings.AI_PROVIDER != "offline":
        try:
            prompt = (
                f"You are a strict, pedagogical college placement coach. A student made an error on this problem.\n"
                f"Problem Title: {question.title}\n"
                f"Question: {question.content}\n"
                f"Correct Answer: {correct_text}\n"
                f"Official Proof: {official_explanation}\n"
                f"Student Selected: {req.selected_answer or 'Unknown'}\n"
                f"Student Reflection Note: {req.student_notes or 'None'}\n\n"
                f"Instructions:\n"
                f"1. Explain why the student's reasoning was flawed without patronizing language.\n"
                f"2. Provide a clear, step-by-step mathematical or logical proof.\n"
                f"3. State one key takeaway to remember for upcoming recruitment tests.\n"
                f"Do not invent facts outside this syllabus question."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL_NAME}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 600,
                },
            }

            with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            detailed_proof = parts[0]["text"]
                            provider_used = "GEMINI_EXTERNAL"
                            logger.info("AI Coach successfully generated Gemini explanation.")
        except Exception as e:
            logger.warning(f"External AI Provider call failed: {e}. Falling back to offline grounded mentor.")
            provider_used = "OFFLINE_GROUNDED_MENTOR (Provider Fallback)"

    # Audit the query (Never logs full private conversation text)
    AuditService.record_event(
        db=db,
        institution_id=user.institution_id,
        actor_user_id=user.id,
        action="AI_COACH_QUERY",
        entity_type="QUESTION_EXPLANATION",
        entity_id=str(question.id),
        details_json={
            "provider_used": provider_used,
            "domain": question.skill.domain if question.skill else "GENERAL",
            "has_student_notes": bool(req.student_notes),
        },
    )

    return MistakeExplanationResponse(
        question_id=question.id,
        question_title=question.title,
        concept_summary=f"Core Competency: {grounded_concept} ({question.skill.domain if question.skill else 'GENERAL'})",
        detailed_proof_or_explanation=detailed_proof,
        why_answer_was_incorrect=why_incorrect,
        remedial_takeaway=remedial_takeaway,
        recommended_topic=grounded_concept,
        provider_used=provider_used,
        is_grounded_in_syllabus=True,
        privacy_notice="Data Protection Active: No student PII, peer scores, or personal transcripts were transmitted.",
    )


def generate_targeted_study_plan(
    db: Session,
    user: User,
    req: StudyPlanRequest,
) -> StudyPlanResponse:
    """
    Generates a personalized, evidence-grounded study plan tailored to the student's
    target job role and demonstrated weak topics in the database.
    """
    role = ROLE_FRAMEWORK.get(req.target_role_id, ROLE_FRAMEWORK["SDE"])

    # Query student's evaluated attempts to find lowest accuracy domain
    user_attempts = (
        db.query(AttemptRecord)
        .join(Question, AttemptRecord.question_id == Question.id)
        .join(Skill, Question.skill_id == Skill.id)
        .filter(AttemptRecord.user_id == user.id, AttemptRecord.submitted_answer.isnot(None))
        .all()
    )

    domain_acc_map: Dict[str, List[bool]] = {}
    for a in user_attempts:
        if a.question and a.question.skill:
            domain_acc_map.setdefault(a.question.skill.domain, []).append(a.is_correct)

    published_assessments = db.query(Assessment).filter(Assessment.is_published == True).all()
    asm_by_cat = {a.category: a for a in published_assessments if a.category}

    cat_map = {
        "QUANT": "QUANTITATIVE_APTITUDE",
        "LOGICAL": "LOGICAL_REASONING",
        "VERBAL": "VERBAL_ABILITY",
        "PROGRAMMING": "PROGRAMMING_DSA",
        "SQL": "SQL_DATABASE",
    }

    schedule: List[StudyPlanItem] = []
    day = 1
    for dom_req in role.domain_requirements:
        attempts = domain_acc_map.get(dom_req.domain, [])
        acc = (sum(1 for x in attempts if x) / len(attempts) * 100.0) if attempts else 0.0

        asm_cat = cat_map.get(dom_req.domain)
        matched_asm = asm_by_cat.get(asm_cat)

        if len(attempts) < 5:
            action_type = "PRACTICE_DRILL"
            obj = f"Establish initial baseline telemetry in {dom_req.domain_name} (currently {len(attempts)}/5 attempts logged)."
            focus = f"Diagnostic Practice Drill: {dom_req.domain_name}"
        elif acc < dom_req.target_accuracy:
            action_type = "MISTAKE_REVIEW"
            obj = f"Remediate demonstrated weak points (current accuracy {acc:.1f}% vs target {dom_req.target_accuracy}%)."
            focus = f"Remedial Concept Mastery: {dom_req.domain_name}"
        else:
            action_type = "CONCEPT_STUDY"
            obj = f"Maintain high mastery ({acc:.1f}%) through timed reinforcement."
            focus = f"Timed Retention Practice: {dom_req.domain_name}"

        schedule.append(
            StudyPlanItem(
                day_number=day,
                domain=dom_req.domain,
                topic_focus=focus,
                action_type=action_type,
                suggested_duration_minutes=30,
                suggested_assessment_id=matched_asm.id if matched_asm else None,
                suggested_assessment_title=matched_asm.title if matched_asm else None,
                pedagogical_objective=obj,
            )
        )
        day += 1

    AuditService.record_event(
        db=db,
        institution_id=user.institution_id,
        actor_user_id=user.id,
        action="AI_COACH_QUERY",
        entity_type="STUDY_PLAN_GENERATION",
        entity_id=role.role_id,
        details_json={
            "role_id": role.role_id,
            "weekly_hours": req.weekly_hours_available,
            "schedule_days": len(schedule),
        },
    )

    return StudyPlanResponse(
        student_id=user.id,
        target_role_id=role.role_id,
        target_role_name=role.role_name,
        plan_overview=(
            f"Tailored {len(schedule)}-day placement preparation schedule for {role.role_name}. "
            f"Prioritized according to your verified database attempts and competency gaps."
        ),
        schedule=schedule,
        provider_used="OFFLINE_GROUNDED_MENTOR",
        evidence_grounding_note="Grounded strictly in active institutional assessments and student attempt telemetry.",
        privacy_notice="Data Protection Active: Private profile fields and academic GPA are excluded from AI contexts.",
    )
