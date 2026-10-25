import uuid
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.institution import Institution, Department, Cohort
from app.models.user import User
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.practice import PracticeSession, AttemptRecord, MistakeNotebookEntry, PreparationActivity
from app.core.security import hash_password, create_access_token

client = TestClient(app)

@pytest.fixture
def assessment_setup():
    db = SessionLocal()
    uid = uuid.uuid4().hex[:8]

    inst = Institution(
        name=f"Assessment Test Inst {uid}",
        code=f"ATI_{uid.upper()}",
        is_active=True,
    )
    db.add(inst)
    db.flush()

    # Create Student
    student_email = f"student_{uid}@inst.edu"
    student = User(
        institution_id=inst.id,
        email=student_email,
        password_hash=hash_password("Password@123"),
        full_name="Assessment Student",
        role="STUDENT",
        is_active=True,
    )
    db.add(student)
    db.flush()

    # Create Admin
    admin_email = f"admin_{uid}@inst.edu"
    admin = User(
        institution_id=inst.id,
        email=admin_email,
        password_hash=hash_password("Password@123"),
        full_name="Assessment Admin",
        role="ADMIN",
        is_active=True,
    )
    db.add(admin)
    db.flush()

    # Skill
    skill = Skill(
        name=f"Skill {uid}",
        domain="QUANT",
        description="Testing quantitative skill",
    )
    db.add(skill)
    db.flush()

    # Question 1: MCQ with 4 options
    q1 = Question(
        skill_id=skill.id,
        title=f"Sample Question 1 {uid}",
        content="What is 12 * 12?",
        question_type="MCQ_SINGLE",
        difficulty="EASY",
        default_points=1,
        explanation="12 multiplied by 12 equals 144 by standard multiplication.",
        is_verified=True,
    )
    db.add(q1)
    db.flush()

    opt1_correct = QuestionOption(question_id=q1.id, option_text="144", is_correct=True, feedback="Accurate calculation.")
    opt1_wrong1 = QuestionOption(question_id=q1.id, option_text="124", is_correct=False, feedback="Calculation error.")
    opt1_wrong2 = QuestionOption(question_id=q1.id, option_text="134", is_correct=False, feedback="Off by 10.")
    db.add_all([opt1_correct, opt1_wrong1, opt1_wrong2])

    # Question 2: MCQ with 4 options
    q2 = Question(
        skill_id=skill.id,
        title=f"Sample Question 2 {uid}",
        content="What is 15 + 25?",
        question_type="MCQ_SINGLE",
        difficulty="EASY",
        default_points=1,
        explanation="15 + 25 = 40.",
        is_verified=True,
    )
    db.add(q2)
    db.flush()

    opt2_correct = QuestionOption(question_id=q2.id, option_text="40", is_correct=True, feedback="Accurate addition.")
    opt2_wrong1 = QuestionOption(question_id=q2.id, option_text="30", is_correct=False, feedback="Too low.")
    db.add_all([opt2_correct, opt2_wrong1])

    # Assessment
    assessment = Assessment(
        institution_id=inst.id,
        title=f"Test Assessment {uid}",
        description="Automated test assessment",
        instructions="Complete both questions.",
        category="QUANTITATIVE_APTITUDE",
        duration_minutes=10,
        passing_score=Decimal("2.00"),
        is_published=True,
        version=1,
    )
    db.add(assessment)
    db.flush()

    db.add(AssessmentQuestion(assessment_id=assessment.id, question_id=q1.id, order_index=1, points=1))
    db.add(AssessmentQuestion(assessment_id=assessment.id, question_id=q2.id, order_index=2, points=1))

    db.commit()

    student_token = create_access_token({"sub": str(student.id), "role": "STUDENT"})
    admin_token = create_access_token({"sub": str(admin.id), "role": "ADMIN"})

    yield {
        "student": student,
        "admin": admin,
        "student_token": student_token,
        "admin_token": admin_token,
        "assessment": assessment,
        "q1": q1,
        "opt1_correct": opt1_correct,
        "opt1_wrong1": opt1_wrong1,
        "q2": q2,
        "opt2_correct": opt2_correct,
        "opt2_wrong1": opt2_wrong1,
    }
    db.close()


def test_list_published_assessments(assessment_setup):
    token = assessment_setup["student_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/practice/assessments", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found = any(a["id"] == str(assessment_setup["assessment"].id) for a in data)
    assert found is True


def test_start_session_security_sanitization(assessment_setup):
    """
    CRITICAL SECURITY TEST:
    During an active session, options MUST NOT leak `is_correct` and questions MUST NOT leak `explanation`.
    """
    token = assessment_setup["student_token"]
    headers = {"Authorization": f"Bearer {token}"}
    asm_id = str(assessment_setup["assessment"].id)

    response = client.post(
        "/api/v1/practice/sessions",
        json={"assessment_id": asm_id, "session_type": "PRACTICE"},
        headers=headers,
    )
    assert response.status_code == 201
    session_data = response.json()
    assert session_data["status"] == "IN_PROGRESS"
    assert len(session_data["questions"]) == 2

    # Check question fields
    for q in session_data["questions"]:
        assert "explanation" not in q or q.get("explanation") is None
        for opt in q["options"]:
            assert "is_correct" not in opt
            assert "feedback" not in opt


def test_save_answer_upsert_no_duplicates(assessment_setup):
    """Saving answers repeatedly for the same question updates the row without duplicates."""
    token = assessment_setup["student_token"]
    headers = {"Authorization": f"Bearer {token}"}
    asm_id = str(assessment_setup["assessment"].id)

    # Start session
    start_res = client.post(
        "/api/v1/practice/sessions",
        json={"assessment_id": asm_id, "session_type": "PRACTICE"},
        headers=headers,
    )
    session_id = start_res.json()["session_id"]
    q1_id = str(assessment_setup["q1"].id)
    opt1_wrong = str(assessment_setup["opt1_wrong1"].id)
    opt1_correct = str(assessment_setup["opt1_correct"].id)

    # 1. Save wrong answer
    res1 = client.post(
        f"/api/v1/practice/sessions/{session_id}/save-answer",
        json={"question_id": q1_id, "submitted_answer": opt1_wrong, "time_spent_ms": 5000},
        headers=headers,
    )
    assert res1.status_code == 200

    # 2. Modify to correct answer
    res2 = client.post(
        f"/api/v1/practice/sessions/{session_id}/save-answer",
        json={"question_id": q1_id, "submitted_answer": opt1_correct, "time_spent_ms": 3000},
        headers=headers,
    )
    assert res2.status_code == 200

    # Query DB directly to assert only 1 AttemptRecord exists
    db = SessionLocal()
    attempts = db.query(AttemptRecord).filter(
        AttemptRecord.session_id == session_id,
        AttemptRecord.question_id == q1_id,
    ).all()
    assert len(attempts) == 1
    assert attempts[0].submitted_answer == opt1_correct
    assert attempts[0].time_spent_ms == 8000
    db.close()


def test_submit_session_and_mistake_notebook_sync(assessment_setup):
    """Submitting grades deterministically and syncs incorrect items to Mistake Notebook."""
    token = assessment_setup["student_token"]
    student = assessment_setup["student"]
    headers = {"Authorization": f"Bearer {token}"}
    asm_id = str(assessment_setup["assessment"].id)

    # Start session
    start_res = client.post(
        "/api/v1/practice/sessions",
        json={"assessment_id": asm_id, "session_type": "PRACTICE"},
        headers=headers,
    )
    session_id = start_res.json()["session_id"]

    # Answer Q1 correctly
    q1_id = str(assessment_setup["q1"].id)
    opt1_correct = str(assessment_setup["opt1_correct"].id)
    client.post(
        f"/api/v1/practice/sessions/{session_id}/save-answer",
        json={"question_id": q1_id, "submitted_answer": opt1_correct, "time_spent_ms": 4000},
        headers=headers,
    )

    # Answer Q2 incorrectly
    q2_id = str(assessment_setup["q2"].id)
    opt2_wrong = str(assessment_setup["opt2_wrong1"].id)
    client.post(
        f"/api/v1/practice/sessions/{session_id}/save-answer",
        json={"question_id": q2_id, "submitted_answer": opt2_wrong, "time_spent_ms": 6000},
        headers=headers,
    )

    # Submit session
    submit_res = client.post(
        f"/api/v1/practice/sessions/{session_id}/submit?time_spent_seconds=10",
        headers=headers,
    )
    assert submit_res.status_code == 200
    result = submit_res.json()
    assert result["status"] == "SUBMITTED"
    assert float(result["total_score"]) == 1.0  # Q1 correct (+1), Q2 incorrect (0)
    assert float(result["max_score"]) == 2.0
    assert result["correct_count"] == 1
    assert result["incorrect_count"] == 1
    assert result["unanswered_count"] == 0

    # Verify Mistake Notebook has Q2 recorded
    mistakes_res = client.get("/api/v1/practice/mistakes", headers=headers)
    assert mistakes_res.status_code == 200
    mistakes = mistakes_res.json()
    q2_mistake = next((m for m in mistakes if m["question_id"] == q2_id), None)
    assert q2_mistake is not None
    assert q2_mistake["mastery_status"] == "UNRESOLVED"

    # Verify PreparationActivity was automatically logged in DB
    db = SessionLocal()
    activity = db.query(PreparationActivity).filter(
        PreparationActivity.user_id == student.id,
        PreparationActivity.provenance == "SYSTEM_EVALUATED"
    ).first()
    assert activity is not None
    assert activity.activity_type == "PRACTICE_SESSION"
    db.close()


def test_post_submission_review_guards(assessment_setup):
    """Review endpoint is strictly guarded during active attempt, unlocked post-submission."""
    token = assessment_setup["student_token"]
    headers = {"Authorization": f"Bearer {token}"}
    asm_id = str(assessment_setup["assessment"].id)

    # Start session
    start_res = client.post(
        "/api/v1/practice/sessions",
        json={"assessment_id": asm_id, "session_type": "PRACTICE"},
        headers=headers,
    )
    session_id = start_res.json()["session_id"]

    # 1. Attempt review while IN_PROGRESS -> HTTP 403 Forbidden
    pre_review_res = client.get(f"/api/v1/practice/sessions/{session_id}/review", headers=headers)
    assert pre_review_res.status_code == 403

    # 2. Submit session
    client.post(f"/api/v1/practice/sessions/{session_id}/submit", headers=headers)

    # 3. Attempt review after SUBMITTED -> HTTP 200 OK with explanations
    post_review_res = client.get(f"/api/v1/practice/sessions/{session_id}/review", headers=headers)
    assert post_review_res.status_code == 200
    review_data = post_review_res.json()
    assert len(review_data["questions"]) == 2

    # Verify explanation and option feedback are now visible
    for q in review_data["questions"]:
        assert q["explanation"] is not None
        assert len(q["options"]) > 0
        assert any(opt["is_correct"] is True for opt in q["options"])
