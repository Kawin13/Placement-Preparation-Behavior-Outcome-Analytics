import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password, verify_password
from app.core.rate_limit import login_rate_limiter, register_rate_limiter, reset_rate_limiter
from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.audit import AuditLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_limiters():
    """Reset rate limiters between tests to prevent test cross-interference."""
    login_rate_limiter.reset_for_test()
    register_rate_limiter.reset_for_test()
    reset_rate_limiter.reset_for_test()
    yield


@pytest.fixture(scope="module")
def setup_test_data():
    """Sets up an isolated institution and departments for automated security testing."""
    db = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:6]

    # Institution A
    inst_a = Institution(
        name=f"College of Engineering {unique_suffix}",
        code=f"COE_{unique_suffix}".upper(),
        is_active=True,
    )
    # Institution B (for cross-institution testing)
    inst_b = Institution(
        name=f"Institute of Technology {unique_suffix}",
        code=f"IOT_{unique_suffix}".upper(),
        is_active=True,
    )
    db.add_all([inst_a, inst_b])
    db.commit()
    db.refresh(inst_a)
    db.refresh(inst_b)

    # Department under Institution A
    dept_a = Department(
        institution_id=inst_a.id,
        name="Computer Science & Engineering",
        code="CSE",
    )
    db.add(dept_a)
    db.commit()
    db.refresh(dept_a)

    # Cohort under Department A
    cohort_a = Cohort(
        department_id=dept_a.id,
        graduation_year=2026,
        section="A",
    )
    db.add(cohort_a)

    # Admin user for Institution A
    admin_a = User(
        institution_id=inst_a.id,
        email=f"admin_{unique_suffix}@coe.edu",
        password_hash=hash_password("AdminSecurePass123!"),
        full_name="Admin User A",
        role="ADMIN",
        is_active=True,
    )

    # Admin user for Institution B
    admin_b = User(
        institution_id=inst_b.id,
        email=f"admin_{unique_suffix}@iot.edu",
        password_hash=hash_password("AdminSecurePass123!"),
        full_name="Admin User B",
        role="ADMIN",
        is_active=True,
    )

    db.add_all([cohort_a, admin_a, admin_b])
    db.commit()
    db.refresh(cohort_a)
    db.refresh(admin_a)
    db.refresh(admin_b)

    data = {
        "inst_a_id": str(inst_a.id),
        "inst_b_id": str(inst_b.id),
        "dept_a_id": str(dept_a.id),
        "cohort_a_id": str(cohort_a.id),
        "admin_a_email": admin_a.email,
        "admin_a_id": str(admin_a.id),
        "admin_b_email": admin_b.email,
        "admin_b_id": str(admin_b.id),
        "suffix": unique_suffix,
    }

    db.close()
    return data


def test_password_hashing_and_verification():
    raw_password = "StrongPass123!@#"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_unauthenticated_access_denied():
    # Protected routes must reject unauthenticated requests with 401
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_student_public_registration_and_anti_privilege_escalation(setup_test_data):
    unique = setup_test_data["suffix"]
    reg_payload = {
        "email": f"student_{unique}@coe.edu",
        "password": "ValidPassword123!",
        "full_name": "Test Student",
        "institution_id": setup_test_data["inst_a_id"],
        "roll_number": f"26CS001_{unique}",
        "cohort_id": setup_test_data["cohort_a_id"],
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    # Anti-Privilege Escalation: Public self-registration ALWAYS creates a STUDENT
    assert data["user"]["role"] == "STUDENT"
    assert data["user"]["email"] == f"student_{unique}@coe.edu"


def test_weak_password_rejected(setup_test_data):
    # Weak password test (too short, no special characters)
    weak_payload = {
        "email": "weakpassword@coe.edu",
        "password": "short",
        "full_name": "Weak User",
        "institution_id": setup_test_data["inst_a_id"],
    }
    response = client.post("/api/v1/auth/register", json=weak_payload)
    # Schema validation or business validation must reject with 400 or 422
    assert response.status_code in (400, 422)


def test_login_flow(setup_test_data):
    # Invalid password login
    bad_login = {
        "email": setup_test_data["admin_a_email"],
        "password": "IncorrectPassword123!",
    }
    resp = client.post("/api/v1/auth/login", json=bad_login)
    assert resp.status_code == 401

    # Valid admin login
    good_login = {
        "email": setup_test_data["admin_a_email"],
        "password": "AdminSecurePass123!",
    }
    resp = client.post("/api/v1/auth/login", json=good_login)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"


def test_unauthorized_role_access_denied(setup_test_data):
    unique = setup_test_data["suffix"]
    student_login = {
        "email": f"student_{unique}@coe.edu",
        "password": "ValidPassword123!",
    }
    resp = client.post("/api/v1/auth/login", json=student_login)
    assert resp.status_code == 200
    student_token = resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Student attempts to access ADMIN-only endpoint
    admin_resp = client.get("/api/v1/admin/users", headers=student_headers)
    assert admin_resp.status_code == 403

    # Student attempts to create an academic department
    dept_resp = client.post(
        "/api/v1/admin/departments",
        json={"name": "Hacked Department", "code": "HACK"},
        headers=student_headers,
    )
    assert dept_resp.status_code == 403


def test_admin_staff_provisioning(setup_test_data):
    admin_login = {
        "email": setup_test_data["admin_a_email"],
        "password": "AdminSecurePass123!",
    }
    resp = client.post("/api/v1/auth/login", json=admin_login)
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    unique = setup_test_data["suffix"]
    staff_payload = {
        "email": f"officer_{unique}@coe.edu",
        "password": "OfficerSecure123!",
        "full_name": "Placement Officer Sharma",
        "role": "PLACEMENT_OFFICER",
    }
    create_resp = client.post("/api/v1/admin/users", json=staff_payload, headers=admin_headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["role"] == "PLACEMENT_OFFICER"


def test_cross_institution_isolation(setup_test_data):
    # Admin B from Institution B attempts to modify resources of Institution A
    admin_b_login = {
        "email": setup_test_data["admin_b_email"],
        "password": "AdminSecurePass123!",
    }
    resp = client.post("/api/v1/auth/login", json=admin_b_login)
    admin_b_token = resp.json()["access_token"]
    admin_b_headers = {"Authorization": f"Bearer {admin_b_token}"}

    # Attempt to add cohort to Institution A's department
    cross_cohort_payload = {
        "department_id": setup_test_data["dept_a_id"],
        "graduation_year": 2027,
        "section": "B",
    }
    cross_resp = client.post(
        "/api/v1/admin/cohorts",
        json=cross_cohort_payload,
        headers=admin_b_headers,
    )
    assert cross_resp.status_code == 404
    assert "not found within your institution" in cross_resp.json()["message"]


def test_student_profile_ownership_and_self_service(setup_test_data):
    unique = setup_test_data["suffix"]
    student_login = {
        "email": f"student_{unique}@coe.edu",
        "password": "ValidPassword123!",
    }
    resp = client.post("/api/v1/auth/login", json=student_login)
    assert resp.status_code == 200
    student_token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {student_token}"}

    # Retrieve student's own profile
    prof_resp = client.get("/api/v1/student/profile", headers=headers)
    assert prof_resp.status_code == 200
    assert prof_resp.json()["roll_number"] == f"26CS001_{unique}"

    # Update own CGPA
    update_resp = client.put("/api/v1/student/profile", json={"cgpa": 8.75}, headers=headers)
    assert update_resp.status_code == 200
    assert float(update_resp.json()["cgpa"]) == 8.75


def test_password_reset_lifecycle(setup_test_data):
    unique = setup_test_data["suffix"]
    email = f"student_{unique}@coe.edu"

    # Step 1: Request reset
    req_resp = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert req_resp.status_code == 200
    reset_token = req_resp.json().get("dev_reset_token")
    assert reset_token is not None

    # Step 2: Attempt reset with weak password (must fail)
    fail_confirm = {
        "token": reset_token,
        "new_password": "short",
    }
    fail_resp = client.post("/api/v1/auth/reset-password", json=fail_confirm)
    assert fail_resp.status_code in (400, 422)

    # Step 3: Complete reset with strong password
    confirm_payload = {
        "token": reset_token,
        "new_password": "NewStrongPassword123!@",
    }
    confirm_resp = client.post("/api/v1/auth/reset-password", json=confirm_payload)
    assert confirm_resp.status_code == 200
    assert "successfully reset" in confirm_resp.json()["message"]

    # Step 4: Login with old password must fail
    old_login = client.post("/api/v1/auth/login", json={"email": email, "password": "ValidPassword123!"})
    assert old_login.status_code == 401

    # Step 5: Login with new password must succeed
    new_login = client.post("/api/v1/auth/login", json={"email": email, "password": "NewStrongPassword123!@"})
    assert new_login.status_code == 200


def test_audit_log_recording_and_privacy(setup_test_data):
    db = SessionLocal()
    inst_a_uuid = uuid.UUID(setup_test_data["inst_a_id"])
    logs = db.query(AuditLog).filter(AuditLog.institution_id == inst_a_uuid).all()
    assert len(logs) > 0

    # Confirm privacy: No password or token exists in details_json
    for log in logs:
        if log.details_json:
            for k, v in log.details_json.items():
                assert k != "password"
                assert k != "token"
                if "password" in k.lower():
                    assert v == "[REDACTED]"
    db.close()


def test_rate_limiting_enforced():
    """Verify that exceeding rate limits returns 429 Too Many Requests."""
    login_rate_limiter.reset_for_test()
    # Send 5 requests (the limit)
    for _ in range(5):
        resp = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "BadPassword123!"})
        assert resp.status_code == 401

    # 6th request must trigger rate limit
    limited_resp = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "BadPassword123!"})
    assert limited_resp.status_code == 429
    assert "Rate limit exceeded" in limited_resp.json()["message"]
