import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.user import User
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.core.security import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture
def qbank_setup():
    db = SessionLocal()
    uid = uuid.uuid4().hex[:8]

    inst = Institution(
        name=f"QBank Test Inst {uid}",
        code=f"QBI_{uid.upper()}",
        is_active=True,
    )
    db.add(inst)
    db.flush()

    student = User(
        institution_id=inst.id,
        email=f"qstudent_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="QBank Student",
        role="STUDENT",
        is_active=True,
    )
    admin = User(
        institution_id=inst.id,
        email=f"qadmin_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="QBank Admin",
        role="ADMIN",
        is_active=True,
    )
    trainer = User(
        institution_id=inst.id,
        email=f"qtrainer_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="QBank Trainer",
        role="TRAINER",
        is_active=True,
    )
    db.add_all([student, admin, trainer])
    db.flush()

    skill = Skill(
        name=f"Percentages & Ratios {uid}",
        domain="QUANT",
        description="Aptitude arithmetic concepts",
    )
    db.add(skill)
    db.flush()

    # Seed 1 published and 1 draft question
    q_pub = Question(
        skill_id=skill.id,
        title=f"Published Percentage Question {uid}",
        content="What is 20% of 250?",
        question_type="MCQ_SINGLE",
        difficulty="EASY",
        default_points=1,
        explanation="20% of 250 = (20/100) * 250 = 50.",
        status="PUBLISHED",
        is_verified=True,
    )
    db.add(q_pub)
    db.flush()

    opt1 = QuestionOption(question_id=q_pub.id, option_text="50", is_correct=True, feedback="Accurate.")
    opt2 = QuestionOption(question_id=q_pub.id, option_text="40", is_correct=False, feedback="Too low.")
    db.add_all([opt1, opt2])

    q_draft = Question(
        skill_id=skill.id,
        title=f"Draft Work Question {uid}",
        content="A can do work in 10 days, B in 15 days...",
        question_type="MCQ_SINGLE",
        difficulty="MEDIUM",
        default_points=2,
        explanation="Combined rate = 1/10 + 1/15 = 1/6, so 6 days.",
        status="DRAFT",
        is_verified=False,
    )
    db.add(q_draft)
    db.flush()

    opt_d1 = QuestionOption(question_id=q_draft.id, option_text="6 days", is_correct=True, feedback="Accurate.")
    opt_d2 = QuestionOption(question_id=q_draft.id, option_text="8 days", is_correct=False, feedback="Incorrect calculation.")
    db.add_all([opt_d1, opt_d2])

    db.commit()

    student_token = create_access_token({"sub": str(student.id), "role": "STUDENT"})
    admin_token = create_access_token({"sub": str(admin.id), "role": "ADMIN"})
    trainer_token = create_access_token({"sub": str(trainer.id), "role": "TRAINER"})

    yield {
        "student_token": student_token,
        "admin_token": admin_token,
        "trainer_token": trainer_token,
        "skill_id": str(skill.id),
        "q_pub_id": str(q_pub.id),
        "q_draft_id": str(q_draft.id),
    }
    db.close()


def test_student_lists_questions_sees_only_published_and_sanitized(qbank_setup):
    """Students must only see PUBLISHED questions, and answers/explanations must be sanitized."""
    headers = {"Authorization": f"Bearer {qbank_setup['student_token']}"}
    res = client.get("/api/v1/practice/questions", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    # Student should not see any DRAFT questions
    for q in data["items"]:
        assert q["status"] == "PUBLISHED"
        # Explanations stripped for candidate browsing
        assert q["explanation"] is None
        # Option correctness stripped
        for opt in q["options"]:
            assert opt["is_correct"] is False
            assert opt["feedback"] is None


def test_staff_sees_all_questions_with_answers_and_stats(qbank_setup):
    """Trainers and Admins can view all questions including draft status and solutions."""
    headers = {"Authorization": f"Bearer {qbank_setup['trainer_token']}"}
    res = client.get("/api/v1/practice/questions", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    # Find draft question
    draft_item = next((q for q in data["items"] if q["id"] == qbank_setup["q_draft_id"]), None)
    assert draft_item is not None
    assert draft_item["status"] == "DRAFT"
    assert draft_item["explanation"] is not None
    assert any(opt["is_correct"] is True for opt in draft_item["options"])


def test_staff_create_and_update_question(qbank_setup):
    """Staff can create, view, and edit questions."""
    headers = {"Authorization": f"Bearer {qbank_setup['admin_token']}"}

    create_payload = {
        "skill_id": qbank_setup["skill_id"],
        "title": "Speed, Time & Distance Problem",
        "content": "A train passes a pole in 15 seconds at 60 km/h. Find length.",
        "question_type": "MCQ_SINGLE",
        "difficulty": "EASY",
        "default_points": 1,
        "explanation": "60 km/h = 60 * 5/18 = 50/3 m/s. Length = (50/3) * 15 = 250 m.",
        "options": [
            {"option_text": "250 m", "is_correct": True, "feedback": "Accurate."},
            {"option_text": "200 m", "is_correct": False, "feedback": "Underestimated."},
            {"option_text": "300 m", "is_correct": False, "feedback": "Overestimated."},
        ],
    }

    create_res = client.post("/api/v1/practice/questions", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    q_created = create_res.json()
    q_id = q_created["id"]
    assert q_created["title"] == create_payload["title"]
    assert len(q_created["options"]) == 3

    # Update question
    update_payload = {
        "title": "Speed, Time & Distance Problem (Revised)",
        "difficulty": "MEDIUM",
        "default_points": 2,
    }
    update_res = client.put(f"/api/v1/practice/questions/{q_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Speed, Time & Distance Problem (Revised)"
    assert update_res.json()["difficulty"] == "MEDIUM"
    assert update_res.json()["default_points"] == 2
    assert update_res.json()["version"] == 2


def test_staff_status_lifecycle_and_student_forbidden(qbank_setup):
    """Staff can transition draft -> published -> archived. Students cannot."""
    staff_headers = {"Authorization": f"Bearer {qbank_setup['admin_token']}"}
    student_headers = {"Authorization": f"Bearer {qbank_setup['student_token']}"}

    draft_id = qbank_setup["q_draft_id"]

    # Student cannot change status
    stu_res = client.patch(f"/api/v1/practice/questions/{draft_id}/status", json={"status": "PUBLISHED"}, headers=student_headers)
    assert stu_res.status_code == 403

    # Staff publishes draft
    pub_res = client.patch(f"/api/v1/practice/questions/{draft_id}/status", json={"status": "PUBLISHED"}, headers=staff_headers)
    assert pub_res.status_code == 200

    # Verify student can now see it
    get_res = client.get(f"/api/v1/practice/questions/{draft_id}", headers=student_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == draft_id


def test_bulk_import_questions(qbank_setup):
    """Staff can bulk import questions with automated skill resolution."""
    headers = {"Authorization": f"Bearer {qbank_setup['admin_token']}"}

    bulk_payload = {
        "questions": [
            {
                "title": "Permutations Formula Test",
                "content": "Evaluate 5P2.",
                "skill_name": "Combinatorics",
                "domain": "QUANT",
                "difficulty": "EASY",
                "default_points": 1,
                "explanation": "5P2 = 5 * 4 = 20.",
                "options": [
                    {"option_text": "20", "is_correct": True, "feedback": "Accurate."},
                    {"option_text": "10", "is_correct": False, "feedback": "That is 5C2."},
                ],
            },
            {
                "title": "Combinations Formula Test",
                "content": "Evaluate 5C2.",
                "skill_name": "Combinatorics",
                "domain": "QUANT",
                "difficulty": "EASY",
                "default_points": 1,
                "explanation": "5C2 = (5 * 4)/(2 * 1) = 10.",
                "options": [
                    {"option_text": "10", "is_correct": True, "feedback": "Accurate."},
                    {"option_text": "20", "is_correct": False, "feedback": "That is 5P2."},
                ],
            },
        ]
    }

    res = client.post("/api/v1/practice/questions/import", json=bulk_payload, headers=headers)
    assert res.status_code == 200
    assert "imported 2 questions" in res.json()["message"]


def test_ai_question_generation_authorization_and_validation(qbank_setup):
    """Students cannot trigger AI question generation; staff requests are validated."""
    student_headers = {"Authorization": f"Bearer {qbank_setup['student_token']}"}
    ai_req = {
        "domain": "QUANT",
        "topic": "Profit and Loss",
        "difficulty": "MEDIUM",
        "question_type": "MCQ_SINGLE",
        "count": 2,
    }

    # Student forbidden
    stu_res = client.post("/api/v1/practice/questions/generate-ai", json=ai_req, headers=student_headers)
    assert stu_res.status_code == 403
