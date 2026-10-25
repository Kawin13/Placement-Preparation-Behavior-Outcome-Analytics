import uuid
from datetime import date, datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password, create_access_token
from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.placement import PlacementOutcome
from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance
from app.models.skill import Skill
from app.models.question import Question
from app.models.practice import PracticeSession, AttemptRecord

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_placement_and_training():
    db: Session = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:8]

    # 1. Institution, Dept, Cohort
    inst = Institution(
        name=f"Placement Tech Institute {unique_suffix}",
        code=f"PTI_{unique_suffix}".upper()[:10],
    )
    db.add(inst)
    db.flush()

    dept = Department(
        institution_id=inst.id,
        name=f"Computer Science {unique_suffix}",
        code=f"CS_{unique_suffix}".upper()[:10],
    )
    db.add(dept)
    db.flush()

    cohort = Cohort(department_id=dept.id, graduation_year=2026, section="A")
    db.add(cohort)
    db.flush()

    # 2. Users: Student A, Student B, Placement Officer, Trainer
    pw = hash_password("ValidPass123!")

    student_a = User(
        institution_id=inst.id,
        email=f"student_a_{unique_suffix}@placement.edu",
        password_hash=pw,
        full_name="Aarav Sharma",
        role="STUDENT",
    )
    student_b = User(
        institution_id=inst.id,
        email=f"student_b_{unique_suffix}@placement.edu",
        password_hash=pw,
        full_name="Bhavya Patel",
        role="STUDENT",
    )
    officer = User(
        institution_id=inst.id,
        email=f"officer_{unique_suffix}@placement.edu",
        password_hash=pw,
        full_name="Dr. Placement Officer",
        role="PLACEMENT_OFFICER",
    )
    trainer = User(
        institution_id=inst.id,
        email=f"trainer_{unique_suffix}@placement.edu",
        password_hash=pw,
        full_name="Prof. Lead Trainer",
        role="TRAINER",
    )
    db.add_all([student_a, student_b, officer, trainer])
    db.flush()

    # Student profiles
    prof_a = StudentProfile(
        user_id=student_a.id,
        cohort_id=cohort.id,
        roll_number=f"26CS_{unique_suffix}_A",
        placement_status="NOT_PLACED",
    )
    prof_b = StudentProfile(
        user_id=student_b.id,
        cohort_id=cohort.id,
        roll_number=f"26CS_{unique_suffix}_B",
        placement_status="NOT_PLACED",
    )
    db.add_all([prof_a, prof_b])

    # Skill and Question for training pre/post evaluation
    skill = Skill(
        name=f"Quantitative Analytics {unique_suffix}",
        domain="QUANT",
        description="Math logic",
    )
    db.add(skill)
    db.flush()

    q1 = Question(
        skill_id=skill.id,
        title="Diagnostic Pre Q1",
        content="2 + 2 = ?",
        question_type="MCQ_SINGLE",
        difficulty="MEDIUM",
        status="PUBLISHED",
    )
    db.add(q1)
    db.commit()

    tokens = {
        "student_a": create_access_token(data={"sub": str(student_a.id), "role": "STUDENT", "institution_id": str(inst.id)}),
        "student_b": create_access_token(data={"sub": str(student_b.id), "role": "STUDENT", "institution_id": str(inst.id)}),
        "officer": create_access_token(data={"sub": str(officer.id), "role": "PLACEMENT_OFFICER", "institution_id": str(inst.id)}),
        "trainer": create_access_token(data={"sub": str(trainer.id), "role": "TRAINER", "institution_id": str(inst.id)}),
    }

    yield {
        "inst": inst,
        "student_a": student_a,
        "student_b": student_b,
        "prof_a": prof_a,
        "prof_b": prof_b,
        "officer": officer,
        "trainer": trainer,
        "tokens": tokens,
        "skill": skill,
        "question": q1,
    }
    db.close()


def test_student_self_report_placement_outcome_pending_review(setup_placement_and_training):
    env = setup_placement_and_training
    token = env["tokens"]["student_a"]

    payload = {
        "company_name": "Google India",
        "job_title": "Associate Software Engineer",
        "tier": "TIER_1_PRODUCT",
        "ctc_lpa": 18.5,
        "offer_date": "2026-10-15",
        "proof_document_url": "https://storage.college.edu/offers/aarav_google_offer.pdf",
    }
    res = client.post(
        "/api/v1/placement/outcomes",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["company_name"] == "Google India"
    assert data["verification_status"] == "PENDING_REVIEW"
    assert data["verified_by_user_id"] is None
    assert data["user_id"] == str(env["student_a"].id)


def test_peer_student_placement_inspection_and_tampering_forbidden(setup_placement_and_training):
    env = setup_placement_and_training
    token_a = env["tokens"]["student_a"]
    token_b = env["tokens"]["student_b"]

    # Student A creates an offer
    payload = {
        "company_name": "Microsoft IDC",
        "job_title": "Software Engineer 1",
        "tier": "TIER_1_PRODUCT",
        "ctc_lpa": 20.0,
    }
    create_res = client.post(
        "/api/v1/placement/outcomes",
        json=payload,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    outcome_id = create_res.json()["id"]

    # Student B attempts to read A's outcome by ID
    get_res = client.get(
        f"/api/v1/placement/outcomes/{outcome_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert get_res.status_code == 403

    # Student B attempts to withdraw A's offer
    withdraw_res = client.post(
        f"/api/v1/placement/outcomes/{outcome_id}/withdraw",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert withdraw_res.status_code == 403


def test_placement_officer_verify_and_reject_lifecycle(setup_placement_and_training):
    env = setup_placement_and_training
    token_student = env["tokens"]["student_a"]
    token_officer = env["tokens"]["officer"]

    # 1. Student submits offer
    create_res = client.post(
        "/api/v1/placement/outcomes",
        json={
            "company_name": "Oracle Financial",
            "job_title": "Database Analyst",
            "tier": "TIER_2_TECH",
            "ctc_lpa": 12.0,
        },
        headers={"Authorization": f"Bearer {token_student}"},
    )
    outcome_id = create_res.json()["id"]

    # 2. Officer rejects offer with reason
    reject_res = client.patch(
        f"/api/v1/placement/outcomes/{outcome_id}/verify",
        json={
            "verification_status": "REJECTED",
            "rejection_reason": "Offer letter signature is missing date and HR stamp.",
        },
        headers={"Authorization": f"Bearer {token_officer}"},
    )
    assert reject_res.status_code == 200
    reject_data = reject_res.json()
    assert reject_data["verification_status"] == "REJECTED"
    assert "HR stamp" in reject_data["rejection_reason"]

    # 3. Officer later receives authentic copy and marks OFFICIALLY_VERIFIED
    verify_res = client.patch(
        f"/api/v1/placement/outcomes/{outcome_id}/verify",
        json={"verification_status": "OFFICIALLY_VERIFIED"},
        headers={"Authorization": f"Bearer {token_officer}"},
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["verification_status"] == "OFFICIALLY_VERIFIED"
    assert verify_data["verified_by_user_id"] == str(env["officer"].id)
    assert verify_data["verified_at"] is not None

    # Check student's profile status in DB is now PLACED
    db = SessionLocal()
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == env["student_a"].id).first()
    assert prof.placement_status == "PLACED"
    db.close()


def test_placement_batch_import_and_csv_export(setup_placement_and_training):
    env = setup_placement_and_training
    token_officer = env["tokens"]["officer"]
    roll_b = env["prof_b"].roll_number

    # Batch import
    items = [
        {
            "roll_number": roll_b,
            "company_name": "Goldman Sachs",
            "job_title": "Summer Analyst",
            "tier": "TIER_1_PRODUCT",
            "ctc_lpa": 24.0,
            "offer_date": "2026-10-20",
            "auto_verify": True,
        },
        {
            "roll_number": "NON_EXISTENT_ROLL",
            "company_name": "Dummy Corp",
            "job_title": "Intern",
            "tier": "MASS_IT",
        },
    ]

    import_res = client.post(
        "/api/v1/placement/batch-import",
        json=items,
        headers={"Authorization": f"Bearer {token_officer}"},
    )
    assert import_res.status_code == 200
    res_data = import_res.json()
    assert res_data["total_processed"] == 2
    assert res_data["created_count"] == 1
    assert res_data["error_count"] == 1
    assert "NON_EXISTENT_ROLL" in res_data["errors"][0]

    # CSV Export
    csv_res = client.get(
        "/api/v1/placement/export-csv",
        headers={"Authorization": f"Bearer {token_officer}"},
    )
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    csv_text = csv_res.text
    assert "Record ID,Roll Number,Student Name" in csv_text
    assert "Goldman Sachs" in csv_text


def test_training_program_and_attendance_lifecycle(setup_placement_and_training):
    env = setup_placement_and_training
    token_trainer = env["tokens"]["trainer"]
    student_a_id = str(env["student_a"].id)
    student_b_id = str(env["student_b"].id)

    # 1. Create Training Programme
    prog_payload = {
        "title": "Placement Aptitude & Quant Intensive 2026",
        "description": "Intensive 4-week diagnostic problem-solving programme.",
        "domain": "QUANT",
        "start_date": "2026-09-01",
        "end_date": "2026-09-30",
        "total_planned_hours": 30,
    }
    prog_res = client.post(
        "/api/v1/training/programs",
        json=prog_payload,
        headers={"Authorization": f"Bearer {token_trainer}"},
    )
    assert prog_res.status_code == 201
    prog_id = prog_res.json()["id"]

    # 2. Add Training Session
    sess_payload = {
        "program_id": prog_id,
        "session_date": "2026-09-05",
        "start_time": "09:00 AM",
        "duration_minutes": 120,
        "topic_covered": "Time, Work, Speed & Relative Velocity",
        "trainer_notes": "Focused on LCM method for multi-worker pipelines.",
    }
    sess_res = client.post(
        "/api/v1/training/sessions",
        json=sess_payload,
        headers={"Authorization": f"Bearer {token_trainer}"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    # 3. Mark Batch Attendance
    att_payload = {
        "session_id": session_id,
        "attendance_list": [
            {"user_id": student_a_id, "attendance_status": "PRESENT"},
            {"user_id": student_b_id, "attendance_status": "ABSENT"},
        ],
    }
    att_res = client.post(
        "/api/v1/training/attendance",
        json=att_payload,
        headers={"Authorization": f"Bearer {token_trainer}"},
    )
    assert att_res.status_code == 200
    att_data = att_res.json()
    assert len(att_data) == 2
    assert any(a["user_id"] == student_a_id and a["attendance_status"] == "PRESENT" for a in att_data)


def test_training_effectiveness_paired_comparison_and_causal_guardrails(setup_placement_and_training):
    env = setup_placement_and_training
    token_trainer = env["tokens"]["trainer"]
    student_a = env["student_a"]
    q1 = env["question"]
    db = SessionLocal()

    # 1. Create a programme
    prog = TrainingProgram(
        institution_id=env["inst"].id,
        title="Algebra Masterclass",
        domain="QUANT",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 20),
        total_planned_hours=20,
        trainer_id=env["trainer"].id,
    )
    db.add(prog)
    db.flush()

    # Session + Attendance for student A
    sess = TrainingSession(
        program_id=prog.id,
        session_date=date(2026, 8, 5),
        duration_minutes=90,
        topic_covered="Recurrence and quadratic factorization",
    )
    db.add(sess)
    db.flush()

    att = TrainingAttendance(
        session_id=sess.id,
        user_id=student_a.id,
        attendance_status="PRESENT",
    )
    db.add(att)

    # Create 4 distinct questions under QUANT skill
    qs = [
        Question(
            skill_id=env["skill"].id,
            title=f"Diagnostic Diag Q{i}",
            content=f"Question {i} content",
            question_type="MCQ_SINGLE",
            difficulty="MEDIUM",
            status="PUBLISHED",
        )
        for i in range(4)
    ]
    db.add_all(qs)
    db.flush()

    # 2. Add Pre-training attempt records (within 30 days before 2026-08-01: e.g. 2026-07-20)
    sess_pre = PracticeSession(user_id=student_a.id, session_type="PRACTICE", status="SUBMITTED")
    db.add(sess_pre)
    db.flush()

    for i in range(4):
        # 2 correct, 2 incorrect -> 50% baseline
        db.add(
            AttemptRecord(
                session_id=sess_pre.id,
                user_id=student_a.id,
                question_id=qs[i].id,
                submitted_answer="A",
                is_correct=(i % 2 == 0),
                score_awarded=1.0 if (i % 2 == 0) else 0.0,
                submitted_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
            )
        )

    # 3. Add Post-training attempt records (within 30 days after 2026-08-20: e.g. 2026-08-25)
    sess_post = PracticeSession(user_id=student_a.id, session_type="PRACTICE", status="SUBMITTED")
    db.add(sess_post)
    db.flush()

    for i in range(4):
        # 3 correct, 1 incorrect -> 75% post score
        db.add(
            AttemptRecord(
                session_id=sess_post.id,
                user_id=student_a.id,
                question_id=qs[i].id,
                submitted_answer="A",
                is_correct=(i < 3),
                score_awarded=1.0 if (i < 3) else 0.0,
                submitted_at=datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc),
            )
        )

    db.commit()
    prog_id = str(prog.id)
    db.close()

    # 4. Request Training Effectiveness Report
    res = client.get(
        f"/api/v1/training/programs/{prog_id}/effectiveness",
        headers={"Authorization": f"Bearer {token_trainer}"},
    )
    assert res.status_code == 200
    report = res.json()

    assert report["program_id"] == prog_id
    assert report["matched_pairs_count"] == 1
    assert report["mean_pre_score"] == 50.0
    assert report["mean_post_score"] == 75.0
    assert report["mean_score_delta"] == 25.0
    assert "Observational Association Notice" in report["non_causal_disclaimer"]
    assert "must not be interpreted as direct causal attribution" in report["non_causal_disclaimer"]
