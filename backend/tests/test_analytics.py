import uuid
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.practice import PracticeSession, AttemptRecord, MistakeNotebookEntry, PreparationActivity
from app.models.placement import PlacementOutcome
from app.models.audit import AuditLog
from app.core.security import hash_password, create_access_token

client = TestClient(app)

@pytest.fixture
def analytics_setup():
    db = SessionLocal()
    uid = uuid.uuid4().hex[:8]

    inst = Institution(
        name=f"Analytics Inst {uid}",
        code=f"AN_{uid.upper()}",
        is_active=True,
    )
    db.add(inst)
    db.flush()

    dept = Department(
        institution_id=inst.id,
        name=f"CSE Department {uid}",
        code="CSE",
    )
    db.add(dept)
    db.flush()

    cohort = Cohort(
        department_id=dept.id,
        graduation_year=2026,
        section="A",
    )
    db.add(cohort)
    db.flush()

    # Student 1
    s1 = User(
        institution_id=inst.id,
        email=f"student1_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="Alice Analytics",
        role="STUDENT",
        is_active=True,
    )
    db.add(s1)
    db.flush()
    sp1 = StudentProfile(user_id=s1.id, cohort_id=cohort.id, roll_number=f"26CS01_{uid[:4].upper()}", cgpa=8.5)
    db.add(sp1)

    # Student 2
    s2 = User(
        institution_id=inst.id,
        email=f"student2_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="Bob Analytics",
        role="STUDENT",
        is_active=True,
    )
    db.add(s2)
    db.flush()
    sp2 = StudentProfile(user_id=s2.id, cohort_id=cohort.id, roll_number=f"26CS02_{uid[:4].upper()}", cgpa=7.8)
    db.add(sp2)

    # Staff Admin
    admin = User(
        institution_id=inst.id,
        email=f"admin_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="Staff Admin",
        role="ADMIN",
        is_active=True,
    )
    db.add(admin)
    db.flush()

    # Skills
    skill_quant = Skill(name=f"Arithmetic {uid}", domain="QUANT", description="Numbers and algebra")
    skill_logical = Skill(name=f"Logic {uid}", domain="LOGICAL", description="Deduction and arrangements")
    db.add_all([skill_quant, skill_logical])
    db.flush()

    # 5 Questions in Quant to test the threshold >= 5
    quant_questions = []
    for i in range(5):
        q = Question(
            skill_id=skill_quant.id,
            title=f"Quant Problem {i+1} {uid}",
            content=f"What is {i+1} + {i+1}?",
            question_type="MCQ_SINGLE",
            difficulty="MEDIUM" if i % 2 == 0 else "EASY",
            default_points=1,
            is_verified=True,
        )
        db.add(q)
        db.flush()
        opt = QuestionOption(question_id=q.id, option_text=str((i+1)*2), is_correct=True)
        db.add(opt)
        quant_questions.append((q, opt))

    # Assessment
    asm = Assessment(
        institution_id=inst.id,
        title=f"Diagnostic {uid}",
        duration_minutes=20,
        passing_score=Decimal("3.00"),
        is_published=True,
        version=1,
    )
    db.add(asm)
    db.flush()

    for idx, (q, _) in enumerate(quant_questions, start=1):
        db.add(AssessmentQuestion(assessment_id=asm.id, question_id=q.id, order_index=idx, points=1))

    # Student 1 conducts a session
    sess = PracticeSession(
        user_id=s1.id,
        assessment_id=asm.id,
        session_type="PRACTICE",
        status="SUBMITTED",
        time_spent_seconds=600,
        total_score=Decimal("4.00"),
        max_score=Decimal("5.00"),
    )
    db.add(sess)
    db.flush()

    # 4 Correct, 1 Incorrect Attempt
    for idx, (q, opt) in enumerate(quant_questions):
        is_corr = idx < 4  # 4 correct, 1 wrong
        att = AttemptRecord(
            session_id=sess.id,
            user_id=s1.id,
            question_id=q.id,
            submitted_answer=str(opt.id) if is_corr else "wrong_id",
            is_correct=is_corr,
            score_awarded=Decimal("1.00") if is_corr else Decimal("0.00"),
            time_spent_ms=45000,
        )
        db.add(att)
        db.flush()
        if not is_corr:
            db.add(MistakeNotebookEntry(
                user_id=s1.id,
                attempt_id=att.id,
                question_id=q.id,
                mastery_status="UNRESOLVED",
            ))

    # Add a self-logged activity for Student 1
    db.add(PreparationActivity(
        user_id=s1.id,
        activity_type="SELF_STUDY",
        category="QUANTITATIVE_APTITUDE",
        topic="Formula Revision",
        duration_minutes=60,
        completion_state="COMPLETED",
        provenance="STUDENT_LOGGED",
    ))

    db.commit()

    s1_token = create_access_token({"sub": str(s1.id), "role": "STUDENT"})
    s2_token = create_access_token({"sub": str(s2.id), "role": "STUDENT"})
    admin_token = create_access_token({"sub": str(admin.id), "role": "ADMIN"})

    yield {
        "s1": s1,
        "s2": s2,
        "admin": admin,
        "cohort": cohort,
        "s1_token": s1_token,
        "s2_token": s2_token,
        "admin_token": admin_token,
        "quant_questions": quant_questions,
    }
    db.close()


def test_student_analytics_reproducible_and_provenance_labels(analytics_setup):
    """Verifies that student analytics accurately separates measured vs self-logged hours and calculates accuracy."""
    token = analytics_setup["s1_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/student?days=30", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["student_name"] == "Alice Analytics"
    assert data["prep_time"]["measured_platform_hours"] > 0
    assert data["prep_time"]["self_logged_hours"] == 1.0  # 60 mins = 1.0 hr
    assert data["total_evaluated_attempts"] == 5
    assert data["overall_accuracy_percentage"] == 80.0  # 4/5 = 80.0%
    assert data["total_mistakes_logged"] == 1
    assert data["mistake_remediation_rate"] == 0.0  # 0 mastered out of 1


def test_skill_gap_threshold_and_insufficient_data(analytics_setup):
    """Verifies that domains with < 5 attempts report INSUFFICIENT_DATA and suppress false accuracy."""
    token = analytics_setup["s1_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/analytics/skill-gaps", headers=headers)
    assert res.status_code == 200
    gaps = res.json()

    quant_gap = next((g for g in gaps if g["domain"] == "QUANT"), None)
    assert quant_gap is not None
    assert quant_gap["attempts_count"] == 5
    assert quant_gap["status"] in ["PROFICIENT", "MODERATE"]
    assert quant_gap["accuracy_percentage"] == 80.0

    logical_gap = next((g for g in gaps if g["domain"] == "LOGICAL"), None)
    assert logical_gap is not None
    assert logical_gap["attempts_count"] == 0
    assert logical_gap["status"] == "INSUFFICIENT_DATA"
    assert logical_gap["accuracy_percentage"] is None


def test_student_peer_analytics_access_forbidden(analytics_setup):
    """Students cannot snoop on peer analytics; server responds with HTTP 403."""
    s1_token = analytics_setup["s1_token"]
    s2_id = str(analytics_setup["s2"].id)
    headers = {"Authorization": f"Bearer {s1_token}"}

    res = client.get(f"/api/v1/analytics/student?student_id={s2_id}", headers=headers)
    assert res.status_code == 403

    # But staff admin can inspect student 2
    admin_token = analytics_setup["admin_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_admin = client.get(f"/api/v1/analytics/student?student_id={s2_id}", headers=admin_headers)
    assert res_admin.status_code == 200
    assert res_admin.json()["student_name"] == "Bob Analytics"


def test_cohort_analytics_and_participation(analytics_setup):
    """Verifies cohort participation rate and topic friction detection."""
    token = analytics_setup["admin_token"]
    cohort_id = str(analytics_setup["cohort"].id)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"/api/v1/analytics/cohort?cohort_id={cohort_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_enrolled_students"] == 2
    assert data["active_participating_students"] == 1
    assert data["participation_rate_percentage"] == 50.0  # 1 of 2 students active
    assert "QUANT" in data["skill_gap_distribution"]


def test_placement_correlation_non_causal_guardrails(analytics_setup):
    """Small sample size (n < 30) suppresses correlation metric with mandatory non-causal disclaimer."""
    token = analytics_setup["admin_token"]
    cohort_id = str(analytics_setup["cohort"].id)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"/api/v1/analytics/cohort?cohort_id={cohort_id}", headers=headers)
    assert res.status_code == 200
    corr = res.json()["placement_correlation"]

    assert corr["is_statistically_valid"] is False
    assert corr["spearman_rho"] is None
    assert "Statistical Notice" in corr["non_causal_disclaimer"]
    assert "n=30" in corr["significance_note"]


def test_cohort_csv_export_rbac_and_audit(analytics_setup):
    """Students cannot export cohort reports; staff can export and event is audit logged."""
    s1_token = analytics_setup["s1_token"]
    admin_token = analytics_setup["admin_token"]
    cohort_id = str(analytics_setup["cohort"].id)

    # Student denied
    res_denied = client.get(f"/api/v1/analytics/export?cohort_id={cohort_id}", headers={"Authorization": f"Bearer {s1_token}"})
    assert res_denied.status_code == 403

    # Admin allowed
    res_ok = client.get(f"/api/v1/analytics/export?cohort_id={cohort_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_ok.status_code == 200
    assert "text/csv" in res_ok.headers["content-type"]
    assert "Alice Analytics" in res_ok.text
    assert "Bob Analytics" in res_ok.text

    # Verify audit log was created
    db = SessionLocal()
    log = db.query(AuditLog).filter(
        AuditLog.action == "EXPORT_COHORT_ANALYTICS_CSV",
        AuditLog.entity_id == cohort_id
    ).first()
    assert log is not None
    db.close()
