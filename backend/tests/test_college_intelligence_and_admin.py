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
from app.models.question import Question
from app.models.skill import Skill
from app.models.practice import PracticeSession, AttemptRecord, PreparationActivity, LearningGoal
from app.models.placement import PlacementOutcome
from app.models.training import TrainingProgram, TrainingSession, TrainingAttendance

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_intelligence_env():
    db: Session = SessionLocal()
    suffix = uuid.uuid4().hex[:8]

    # 1. Institution
    inst = Institution(
        name=f"Apex Technological University {suffix}",
        code=f"APX_{suffix}".upper()[:10],
    )
    db.add(inst)
    db.flush()

    # 2. Departments & Cohorts
    dept_cs = Department(
        institution_id=inst.id,
        name=f"Computer Science {suffix}",
        code=f"CS_{suffix}".upper()[:10],
    )
    dept_ec = Department(
        institution_id=inst.id,
        name=f"Electronics {suffix}",
        code=f"EC_{suffix}".upper()[:10],
    )
    db.add_all([dept_cs, dept_ec])
    db.flush()

    # Standard cohort with 6 students (N >= 5, unsuppressed)
    cohort_cs = Cohort(department_id=dept_cs.id, graduation_year=2026, section="A")
    # Small cohort with 2 students (N < 5, suppressed)
    cohort_ec = Cohort(department_id=dept_ec.id, graduation_year=2026, section="B")
    db.add_all([cohort_cs, cohort_ec])
    db.flush()

    # 3. Staff Users
    pw = hash_password("ValidAdminPass123!")
    admin_user = User(
        institution_id=inst.id,
        email=f"admin_{suffix}@apex.edu",
        password_hash=pw,
        full_name="Dean Administration",
        role="ADMIN",
    )
    officer_user = User(
        institution_id=inst.id,
        email=f"officer_{suffix}@apex.edu",
        password_hash=pw,
        full_name="Placement Director",
        role="PLACEMENT_OFFICER",
    )
    trainer_user = User(
        institution_id=inst.id,
        email=f"trainer_{suffix}@apex.edu",
        password_hash=pw,
        full_name="Master Faculty Trainer",
        role="TRAINER",
    )
    db.add_all([admin_user, officer_user, trainer_user])
    db.flush()

    # 4. Students for cohort_cs (6 students)
    cs_students = []
    for i in range(6):
        u = User(
            institution_id=inst.id,
            email=f"student_cs_{i}_{suffix}@apex.edu",
            password_hash=pw,
            full_name=f"CS Student {i}",
            role="STUDENT",
        )
        db.add(u)
        db.flush()
        prof = StudentProfile(
            user_id=u.id,
            cohort_id=cohort_cs.id,
            roll_number=f"26CS{i}_{suffix}",
            placement_status="NOT_PLACED",
        )
        db.add(prof)
        cs_students.append(u)

    # 5. Students for cohort_ec (2 students -> N < 5)
    ec_students = []
    for i in range(2):
        u = User(
            institution_id=inst.id,
            email=f"student_ec_{i}_{suffix}@apex.edu",
            password_hash=pw,
            full_name=f"EC Student {i}",
            role="STUDENT",
        )
        db.add(u)
        db.flush()
        prof = StudentProfile(
            user_id=u.id,
            cohort_id=cohort_ec.id,
            roll_number=f"26EC{i}_{suffix}",
            placement_status="NOT_PLACED",
        )
        db.add(prof)
        ec_students.append(u)

    # 6. Activities & Goals for CS students
    for u in cs_students[:4]:
        db.add(
            PreparationActivity(
                user_id=u.id,
                activity_type="PRACTICE_SESSION",
                category="PROGRAMMING",
                topic="Dynamic Programming Algorithms",
                duration_minutes=90,
                completion_state="COMPLETED",
                provenance="SYSTEM_EVALUATED",
                activity_date=datetime.now(timezone.utc),
            )
        )
        db.add(
            LearningGoal(
                user_id=u.id,
                title="Master Dynamic Programming",
                category="PROGRAMMING",
                target_type="MINUTES_PRACTICED",
                target_value=120.0,
                current_value=120.0,
                status="COMPLETED",
            )
        )

    # 7. Skills & Question attempts
    skill_quant = Skill(name=f"Quantitative Logic {suffix}", domain="QUANT", description="Math")
    skill_tech = Skill(name=f"Data Structures {suffix}", domain="PROGRAMMING", description="DSA")
    db.add_all([skill_quant, skill_tech])
    db.flush()

    q_quant = Question(
        skill_id=skill_quant.id,
        title="Quant Q",
        content="2 * 3 = ?",
        question_type="MCQ_SINGLE",
        difficulty="EASY",
        status="PUBLISHED",
    )
    q_tech = Question(
        skill_id=skill_tech.id,
        title="Tech Q",
        content="Stack FIFO or LIFO?",
        question_type="MCQ_SINGLE",
        difficulty="MEDIUM",
        status="PUBLISHED",
    )
    db.add_all([q_quant, q_tech])
    db.flush()

    for u in cs_students[:3]:
        p_sess = PracticeSession(user_id=u.id, session_type="PRACTICE", status="SUBMITTED")
        db.add(p_sess)
        db.flush()
        db.add(
            AttemptRecord(
                session_id=p_sess.id,
                user_id=u.id,
                question_id=q_quant.id,
                submitted_answer="A",
                is_correct=True,
                score_awarded=1.0,
                submitted_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            AttemptRecord(
                session_id=p_sess.id,
                user_id=u.id,
                question_id=q_tech.id,
                submitted_answer="B",
                is_correct=True,
                score_awarded=1.0,
                submitted_at=datetime.now(timezone.utc),
            )
        )

    # 8. Training Program & Attendance
    prog = TrainingProgram(
        institution_id=inst.id,
        title="Campus Placement BootCamp",
        domain="QUANT",
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() + timedelta(days=5),
        total_planned_hours=30,
        trainer_id=trainer_user.id,
    )
    db.add(prog)
    db.flush()

    sess = TrainingSession(
        program_id=prog.id,
        session_date=date.today() - timedelta(days=2),
        duration_minutes=120,
        topic_covered="Probability & Combinatorics",
    )
    db.add(sess)
    db.flush()

    for u in cs_students[:4]:
        db.add(
            TrainingAttendance(
                session_id=sess.id,
                user_id=u.id,
                attendance_status="PRESENT",
                marked_by_user_id=trainer_user.id,
            )
        )

    # 9. Verified Placement Outcomes
    db.add(
        PlacementOutcome(
            user_id=cs_students[0].id,
            company_name="Microsoft R&D",
            job_title="Software Development Engineer",
            tier="TIER_1_PRODUCT",
            ctc_lpa=24.5,
            verification_status="OFFICIALLY_VERIFIED",
            verified_by_user_id=officer_user.id,
            verified_at=datetime.now(timezone.utc),
        )
    )
    db.add(
        PlacementOutcome(
            user_id=cs_students[1].id,
            company_name="Stripe Payments",
            job_title="Fintech Systems Engineer",
            tier="TIER_2_TECH",
            ctc_lpa=16.0,
            verification_status="OFFICIALLY_VERIFIED",
            verified_by_user_id=officer_user.id,
            verified_at=datetime.now(timezone.utc),
        )
    )
    db.add(
        PlacementOutcome(
            user_id=cs_students[2].id,
            company_name="Pending Inc",
            job_title="Junior Analyst",
            tier="MASS_IT",
            ctc_lpa=8.0,
            verification_status="PENDING_REVIEW",
        )
    )

    db.commit()

    tokens = {
        "admin": create_access_token(data={"sub": str(admin_user.id), "role": "ADMIN", "institution_id": str(inst.id)}),
        "officer": create_access_token(data={"sub": str(officer_user.id), "role": "PLACEMENT_OFFICER", "institution_id": str(inst.id)}),
        "trainer": create_access_token(data={"sub": str(trainer_user.id), "role": "TRAINER", "institution_id": str(inst.id)}),
        "student": create_access_token(data={"sub": str(cs_students[0].id), "role": "STUDENT", "institution_id": str(inst.id)}),
    }

    yield {
        "inst": inst,
        "dept_cs": dept_cs,
        "dept_ec": dept_ec,
        "cohort_cs": cohort_cs,
        "cohort_ec": cohort_ec,
        "admin_user": admin_user,
        "officer_user": officer_user,
        "trainer_user": trainer_user,
        "cs_students": cs_students,
        "ec_students": ec_students,
        "tokens": tokens,
    }
    db.close()


def test_institutional_overview_4_pillars(setup_intelligence_env):
    env = setup_intelligence_env
    token = env["tokens"]["admin"]

    # Request institutional overview for CS cohort (N = 6, unsuppressed)
    res = client.get(
        f"/api/v1/admin/intelligence/overview?cohort_id={env['cohort_cs'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()

    assert data["is_suppressed"] is False
    assert data["cohort_sample_size"] == 6
    assert data["engagement"] is not None
    assert data["engagement"]["total_enrolled_students"] == 6
    assert data["engagement"]["total_preparation_hours"] >= 6.0
    assert data["engagement"]["goal_completion_rate"] == 100.0

    # Pillar 2: Assessments
    assert data["assessments"] is not None
    assert data["assessments"]["total_evaluations"] >= 6
    assert data["assessments"]["overall_accuracy_percentage"] == 100.0
    assert len(data["assessments"]["domain_breakdown"]) >= 2

    # Pillar 3: Training
    assert data["training"] is not None
    assert data["training"]["total_programs_count"] >= 1
    assert data["training"]["overall_attendance_rate"] == 100.0

    # Pillar 4: Verified Placement
    assert data["placement"] is not None
    assert data["placement"]["total_reported_offers"] == 3
    assert data["placement"]["verified_offers_count"] == 2
    assert data["placement"]["pending_review_count"] == 1
    assert data["placement"]["verified_placed_students_count"] == 2
    assert data["placement"]["mean_verified_ctc_lpa"] == 20.25  # (24.5 + 16.0) / 2
    assert data["placement"]["max_verified_ctc_lpa"] == 24.5

    # Non-causal policy statement
    assert "Rule 8" in data["non_causal_notice"]
    assert "must not be claimed as the direct or sole cause" in data["non_causal_notice"]


def test_small_cell_privacy_suppression(setup_intelligence_env):
    env = setup_intelligence_env
    token = env["tokens"]["admin"]

    # Query EC cohort with only 2 students (N < 5 threshold)
    res = client.get(
        f"/api/v1/admin/intelligence/overview?cohort_id={env['cohort_ec'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()

    # Must be suppressed!
    assert data["is_suppressed"] is True
    assert data["cohort_sample_size"] == 2
    assert "Small-cell privacy suppression enforced" in data["suppression_reason"]
    assert "N < 5" in data["suppression_reason"]
    assert data["engagement"] is None
    assert data["assessments"] is None
    assert data["training"] is None
    assert data["placement"] is None


def test_student_access_forbidden(setup_intelligence_env):
    env = setup_intelligence_env
    student_token = env["tokens"]["student"]

    res = client.get(
        "/api/v1/admin/intelligence/overview",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 403
    assert "Forbidden" in res.json().get("message", "") or "Forbidden" in res.text


def test_intelligence_csv_export_and_audit(setup_intelligence_env):
    env = setup_intelligence_env
    token = env["tokens"]["officer"]

    res = client.get(
        f"/api/v1/admin/intelligence/export/csv?cohort_id={env['cohort_cs'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    csv_text = res.text

    assert "INSTITUTIONAL INTELLIGENCE & ACCREDITATION REPORT" in csv_text
    assert "PILLAR 1: ENGAGEMENT & ACTIVITY VOLUME" in csv_text
    assert "PILLAR 2: ASSESSMENT & SKILL ACCURACY" in csv_text
    assert "PILLAR 3: TRAINING IMPACT & ATTENDANCE" in csv_text
    assert "PILLAR 4: VERIFIED PLACEMENT CONVERSION" in csv_text
    assert "Sample Size (N),6" in csv_text
    assert "POLICY NOTICE" in csv_text


def test_admin_user_management_status_and_role_lifecycle(setup_intelligence_env):
    env = setup_intelligence_env
    token = env["tokens"]["admin"]
    target_student = env["cs_students"][5]

    # 1. List users with search
    res = client.get(
        f"/api/v1/admin/users?role=STUDENT&search=CS Student 5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 1
    assert users[0]["id"] == str(target_student.id)

    # 2. Deactivate user account
    res_deact = client.put(
        f"/api/v1/admin/users/{target_student.id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": False},
    )
    assert res_deact.status_code == 200
    assert res_deact.json()["is_active"] is False

    # 3. Reactivate user account
    res_react = client.put(
        f"/api/v1/admin/users/{target_student.id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": True},
    )
    assert res_react.status_code == 200
    assert res_react.json()["is_active"] is True

    # 4. Promote student to Trainer
    res_role = client.put(
        f"/api/v1/admin/users/{target_student.id}/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "TRAINER"},
    )
    assert res_role.status_code == 200
    assert res_role.json()["role"] == "TRAINER"


def test_cohort_assignment_and_content_summary(setup_intelligence_env):
    env = setup_intelligence_env
    token = env["tokens"]["admin"]
    ec_student = env["ec_students"][0]

    # Reassign EC student to CS cohort
    res_assign = client.post(
        f"/api/v1/admin/cohorts/{env['cohort_cs'].id}/assign-students",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_ids": [str(ec_student.id)], "cohort_id": str(env["cohort_cs"].id)},
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["assigned_count"] == 1

    # Content bank summary
    res_content = client.get(
        "/api/v1/admin/content/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_content.status_code == 200
    content = res_content.json()
    assert content["total_questions"] >= 2
    assert len(content["domains"]) >= 2
