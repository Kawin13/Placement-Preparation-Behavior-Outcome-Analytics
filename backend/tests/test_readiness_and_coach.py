import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password, create_access_token
from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.practice import PracticeSession, AttemptRecord

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_readiness_data():
    db: Session = SessionLocal()

    # 1. Institution, Dept, Cohort
    uid_suffix = uuid.uuid4().hex[:8]
    inst = Institution(name=f"Readiness College {uid_suffix}", code=f"RC_{uid_suffix}")
    db.add(inst)
    db.flush()

    dept = Department(institution_id=inst.id, name="Computer Science & Engineering", code="CSE")
    db.add(dept)
    db.flush()

    cohort = Cohort(department_id=dept.id, graduation_year=2026, section="A")
    db.add(cohort)
    db.flush()

    # 2. Users: Student A, Student B, Trainer
    user_a = User(
        institution_id=inst.id,
        email=f"student_a_{uid_suffix}@readiness.edu",
        password_hash=hash_password("Password@123"),
        full_name="Alice Candidate",
        role="STUDENT",
        is_active=True,
    )
    user_b = User(
        institution_id=inst.id,
        email=f"student_b_{uid_suffix}@readiness.edu",
        password_hash=hash_password("Password@123"),
        full_name="Bob Peer",
        role="STUDENT",
        is_active=True,
    )
    trainer = User(
        institution_id=inst.id,
        email=f"trainer_{uid_suffix}@readiness.edu",
        password_hash=hash_password("Password@123"),
        full_name="Dr. Smith Trainer",
        role="TRAINER",
        is_active=True,
    )
    db.add_all([user_a, user_b, trainer])
    db.flush()

    sp_a = StudentProfile(user_id=user_a.id, cohort_id=cohort.id, roll_number="26CS001")
    sp_b = StudentProfile(user_id=user_b.id, cohort_id=cohort.id, roll_number="26CS002")
    db.add_all([sp_a, sp_b])
    db.flush()

    token_a = create_access_token(data={"sub": str(user_a.id), "role": user_a.role, "institution_id": str(inst.id)})
    token_b = create_access_token(data={"sub": str(user_b.id), "role": user_b.role, "institution_id": str(inst.id)})

    # 3. Skills for 4 domains
    skills_map = {}
    for d, sname in [
        ("PROGRAMMING", "Algorithms & DSA Test"),
        ("QUANT", "Aptitude Math Test"),
        ("LOGICAL", "Logic Test"),
        ("VERBAL", "Verbal Syntax Test"),
    ]:
        s = Skill(name=sname, domain=d)
        db.add(s)
        db.flush()
        skills_map[d] = s

    # 4. Create 5 Questions per domain
    questions_by_domain = {}
    for d, s in skills_map.items():
        q_list = []
        for i in range(1, 6):
            q = Question(
                skill_id=s.id,
                title=f"{d} Core Concept {i}",
                content=f"Verify question content for {d} item {i}.",
                question_type="MCQ_SINGLE",
                difficulty="MEDIUM",
                default_points=1,
                explanation=f"Step-by-step mathematical proof for {d} question {i}.",
                is_verified=True,
                status="PUBLISHED",
            )
            db.add(q)
            db.flush()

            opt1 = QuestionOption(question_id=q.id, option_text="Correct Choice", is_correct=True, feedback="Well done.")
            opt2 = QuestionOption(question_id=q.id, option_text="Distractor Choice", is_correct=False, feedback="Incorrect derivation.")
            db.add_all([opt1, opt2])
            db.flush()
            q_list.append(q)
        questions_by_domain[d] = q_list

    # 5. Create published assessments
    assessments_by_domain = {}
    cat_map = {
        "QUANT": "QUANTITATIVE_APTITUDE",
        "LOGICAL": "LOGICAL_REASONING",
        "VERBAL": "VERBAL_ABILITY",
        "PROGRAMMING": "PROGRAMMING_DSA",
    }
    for d, q_list in questions_by_domain.items():
        asm = Assessment(
            institution_id=inst.id,
            title=f"Diagnostic Test: {d}",
            category=cat_map[d],
            duration_minutes=15,
            is_published=True,
            version=1,
        )
        db.add(asm)
        db.flush()
        for idx, q in enumerate(q_list, start=1):
            db.add(AssessmentQuestion(assessment_id=asm.id, question_id=q.id, order_index=idx, points=1))
        assessments_by_domain[d] = asm

    db.commit()

    yield {
        "inst": inst,
        "user_a": user_a,
        "user_b": user_b,
        "trainer": trainer,
        "token_a": token_a,
        "token_b": token_b,
        "skills": skills_map,
        "questions": questions_by_domain,
        "assessments": assessments_by_domain,
    }

    db.close()


def test_list_approved_roles(setup_readiness_data):
    token = setup_readiness_data["token_a"]
    res = client.get("/api/v1/readiness/roles", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) == 3
    role_ids = [r["role_id"] for r in roles]
    assert "SDE" in role_ids
    assert "DATA_ANALYST" in role_ids
    assert "CORE_TECH" in role_ids


def test_readiness_insufficient_evidence_suppression(setup_readiness_data):
    """
    Student A has zero attempts: readiness_score must be None,
    readiness_tier must be INSUFFICIENT_EVIDENCE, and recommendations must be populated.
    """
    token = setup_readiness_data["token_a"]
    res = client.get(
        "/api/v1/readiness/evaluate?role_id=SDE",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["role_id"] == "SDE"
    assert data["has_sufficient_evidence"] is False
    assert data["readiness_score"] is None
    assert data["readiness_tier"] == "INSUFFICIENT_EVIDENCE"
    assert len(data["missing_evidence_summary"]) > 0
    assert len(data["recommendations"]) > 0
    assert "Institutional Non-Predictive Disclaimer" in data["non_predictive_disclaimer"]


def test_readiness_sufficient_evidence_calculation(setup_readiness_data):
    """
    Seed 5 verified attempts per domain for Student A.
    Readiness score must be calculated deterministically and score must not be None.
    """
    data_ctx = setup_readiness_data
    db: Session = SessionLocal()
    user_a = data_ctx["user_a"]

    # Seed 5 attempts for all 4 domains for user_a
    sess = PracticeSession(
        user_id=user_a.id,
        assessment_id=data_ctx["assessments"]["PROGRAMMING"].id,
        session_type="PRACTICE",
        status="COMPLETED",
    )
    db.add(sess)
    db.flush()

    for d, q_list in data_ctx["questions"].items():
        for q in q_list:
            att = AttemptRecord(
                session_id=sess.id,
                user_id=user_a.id,
                question_id=q.id,
                submitted_answer="Correct Choice",
                is_correct=True,
                score_awarded=1.0,
                time_spent_ms=45000,
            )
            db.add(att)
    db.commit()
    db.close()

    token = setup_readiness_data["token_a"]
    res = client.get(
        "/api/v1/readiness/evaluate?role_id=SDE",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["has_sufficient_evidence"] is True
    assert data["readiness_score"] is not None
    assert data["readiness_score"] > 50.0
    assert data["readiness_tier"] in ("ROLE_READY", "DEVELOPING")
    assert len(data["missing_evidence_summary"]) == 0


def test_peer_student_readiness_forbidden(setup_readiness_data):
    """
    Student B cannot inspect Student A's readiness telemetry.
    """
    data_ctx = setup_readiness_data
    token_b = data_ctx["token_b"]
    user_a_id = data_ctx["user_a"].id

    res = client.get(
        f"/api/v1/readiness/evaluate?role_id=SDE&student_id={user_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res.status_code == 403
    assert "restricted from inspecting peer" in res.json()["message"]


def test_ai_coach_explain_mistake_offline_fallback(setup_readiness_data):
    """
    Test that AI Coach returns a grounded pedagogical explanation with proof,
    and falls back to offline mentor cleanly without throwing 500.
    """
    data_ctx = setup_readiness_data
    token = data_ctx["token_a"]

    sample_q = data_ctx["questions"]["PROGRAMMING"][0]
    payload = {
        "question_id": str(sample_q.id),
        "selected_answer": "Distractor Choice",
        "student_notes": "Thought time complexity was linear instead of logarithmic.",
        "error_tag": "COMPUTATION_SLIP",
    }

    res = client.post(
        "/api/v1/coach/explain-mistake",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["question_id"] == str(sample_q.id)
    assert data["is_grounded_in_syllabus"] is True
    assert len(data["detailed_proof_or_explanation"]) > 0
    assert "No student PII" in data["privacy_notice"]


def test_ai_coach_study_plan_generation(setup_readiness_data):
    """
    Test that study plan is tailored to target role and grounded in real database assessments.
    """
    data_ctx = setup_readiness_data
    token = data_ctx["token_a"]

    payload = {"target_role_id": "SDE", "weekly_hours_available": 12}
    res = client.post(
        "/api/v1/coach/generate-plan",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    if res.status_code != 200:
        print("GENERATE_PLAN_ERROR:", res.status_code, res.json())
    assert res.status_code == 200
    data = res.json()
    assert data["target_role_id"] == "SDE"
    assert len(data["schedule"]) == 4  # SDE has 4 domains
    for item in data["schedule"]:
        assert item["suggested_duration_minutes"] > 0
        assert len(item["pedagogical_objective"]) > 0
