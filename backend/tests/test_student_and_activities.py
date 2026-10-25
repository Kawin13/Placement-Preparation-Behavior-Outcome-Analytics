import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.rate_limit import login_rate_limiter, register_rate_limiter, reset_rate_limiter
from app.models.institution import Institution, Department, Cohort
from app.models.user import User, StudentProfile
from app.models.practice import PreparationActivity, LearningGoal
from app.models.audit import AuditLog

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_limiters():
    login_rate_limiter.reset_for_test()
    register_rate_limiter.reset_for_test()
    reset_rate_limiter.reset_for_test()
    yield


@pytest.fixture
def test_setup():
    db = SessionLocal()
    try:
        import uuid as _uuid
        uid = str(_uuid.uuid4())[:8].upper()
        # Create test institution
        inst = Institution(name=f"Testing Institute of Technology {uid}", code=f"TIT-{uid}")
        db.add(inst)
        db.flush()

        # Create department
        dept = Department(institution_id=inst.id, name=f"Computer Science {uid}", code=f"CS{uid[:4].upper()}")
        db.add(dept)
        db.flush()

        # Create cohort
        cohort = Cohort(department_id=dept.id, graduation_year=2026, section="A")
        db.add(cohort)
        db.flush()

        # Create Student A
        pw = hash_password("ValidPassword123!")
        student_a = User(
            institution_id=inst.id,
            email=f"student.a.{uid.lower()}@testinst.edu",
            password_hash=pw,
            full_name="Alice Student",
            role="STUDENT",
            is_active=True,
        )
        db.add(student_a)
        db.flush()

        profile_a = StudentProfile(
            user_id=student_a.id,
            cohort_id=cohort.id,
            roll_number=f"22CS{uid.upper()}A",
            cgpa=8.50,
            placement_status="NOT_PLACED",
        )
        db.add(profile_a)

        # Create Student B
        student_b = User(
            institution_id=inst.id,
            email=f"student.b.{uid.lower()}@testinst.edu",
            password_hash=pw,
            full_name="Bob Student",
            role="STUDENT",
            is_active=True,
        )
        db.add(student_b)
        db.flush()

        profile_b = StudentProfile(
            user_id=student_b.id,
            cohort_id=cohort.id,
            roll_number=f"22CS{uid.upper()}B",
            cgpa=7.20,
            placement_status="NOT_PLACED",
        )
        db.add(profile_b)

        # Create Admin
        admin_user = User(
            institution_id=inst.id,
            email=f"admin.{uid.lower()}@testinst.edu",
            password_hash=pw,
            full_name="Admin Officer",
            role="ADMIN",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()

        # Fetch tokens
        token_a = client.post(
            "/api/v1/auth/login",
            json={"email": student_a.email, "password": "ValidPassword123!"},
        ).json()["access_token"]

        token_b = client.post(
            "/api/v1/auth/login",
            json={"email": student_b.email, "password": "ValidPassword123!"},
        ).json()["access_token"]

        token_admin = client.post(
            "/api/v1/auth/login",
            json={"email": admin_user.email, "password": "ValidPassword123!"},
        ).json()["access_token"]

        yield {
            "institution": inst,
            "department": dept,
            "cohort": cohort,
            "student_a": student_a,
            "profile_a": profile_a,
            "token_a": token_a,
            "student_b": student_b,
            "profile_b": profile_b,
            "token_b": token_b,
            "admin": admin_user,
            "token_admin": token_admin,
        }
    finally:
        db.close()


def test_student_profile_detailed_fetch_and_update(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}

    # 1. Fetch own detailed profile
    res = client.get("/api/v1/student/profile", headers=headers_a)
    assert res.status_code == 200
    data = res.json()
    assert data["user_full_name"] == "Alice Student"
    assert data["roll_number"] == test_setup["profile_a"].roll_number
    assert data["department_name"] == test_setup["department"].name
    assert data["cohort_graduation_year"] == 2026
    assert data["cohort_section"] == "A"
    assert data["cgpa"] == 8.50

    # 2. Update profile
    new_roll = f"22CS999A"
    update_res = client.put(
        "/api/v1/student/profile",
        headers=headers_a,
        json={
            "full_name": "Alice M. Student",
            "roll_number": new_roll,
            "cgpa": 8.95,
            "placement_status": "IN_PROCESS",
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["user_full_name"] == "Alice M. Student"
    assert updated["roll_number"] == new_roll
    assert updated["cgpa"] == 8.95
    assert updated["placement_status"] == "IN_PROCESS"


def test_student_profile_duplicate_roll_and_validation(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}

    # Attempt to take Student B's roll number -> 400 Bad Request
    res = client.put(
        "/api/v1/student/profile",
        headers=headers_a,
        json={"roll_number": test_setup["profile_b"].roll_number},
    )
    assert res.status_code == 400
    res_body = res.json()
    assert "already in use" in (res_body.get("message") or res_body.get("detail", ""))

    # Invalid CGPA > 10.0 -> 422
    res_cgpa = client.put(
        "/api/v1/student/profile",
        headers=headers_a,
        json={"cgpa": 11.5},
    )
    assert res_cgpa.status_code == 422


def test_preparation_activities_crud_and_cross_student_isolation(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}
    headers_b = {"Authorization": f"Bearer {test_setup['token_b']}"}

    # 1. Student A logs preparation activity
    create_res = client.post(
        "/api/v1/student/activities",
        headers=headers_a,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "QUANTITATIVE_APTITUDE",
            "topic": "Time and Work",
            "duration_minutes": 45,
            "completion_state": "COMPLETED",
            "notes": "Solved 15 efficiency ratio problems.",
        },
    )
    assert create_res.status_code == 201
    act_a = create_res.json()
    act_id = act_a["id"]
    assert act_a["duration_minutes"] == 45
    assert act_a["provenance"] == "STUDENT_LOGGED"

    # 2. Student A reads own activity
    res_get = client.get(f"/api/v1/student/activities/{act_id}", headers=headers_a)
    assert res_get.status_code == 200
    assert res_get.json()["topic"] == "Time and Work"

    # 3. Security Test: Student B tries to access Student A's activity -> 403 Forbidden
    res_unauth = client.get(f"/api/v1/student/activities/{act_id}", headers=headers_b)
    assert res_unauth.status_code == 403

    # 4. Security Test: Student B tries to update Student A's activity -> 403 Forbidden
    res_hack_update = client.put(
        f"/api/v1/student/activities/{act_id}",
        headers=headers_b,
        json={"topic": "Hacked Topic"},
    )
    assert res_hack_update.status_code == 403

    # 5. Security Test: Student B tries to delete Student A's activity -> 403 Forbidden
    res_hack_del = client.delete(f"/api/v1/student/activities/{act_id}", headers=headers_b)
    assert res_hack_del.status_code == 403

    # 6. Student A updates own activity
    res_upd = client.put(
        f"/api/v1/student/activities/{act_id}",
        headers=headers_a,
        json={"duration_minutes": 55, "notes": "Solved 20 problems with shortcut formulas."},
    )
    assert res_upd.status_code == 200
    assert res_upd.json()["duration_minutes"] == 55

    # 7. Student A deletes own activity
    res_del = client.delete(f"/api/v1/student/activities/{act_id}", headers=headers_a)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "deleted"


def test_activity_validation_rules(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}

    # Invalid category
    res = client.post(
        "/api/v1/student/activities",
        headers=headers_a,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "INVALID_CATEGORY_NAME",
            "topic": "Matrices",
            "duration_minutes": 30,
        },
    )
    assert res.status_code == 422

    # Duration > 720 minutes (12 hours cap)
    res_dur = client.post(
        "/api/v1/student/activities",
        headers=headers_a,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "QUANTITATIVE_APTITUDE",
            "topic": "Percentages",
            "duration_minutes": 999,
        },
    )
    assert res_dur.status_code == 422


def test_activity_filtering_and_pagination(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}

    # Create 5 distinct activities for Student A
    for i in range(3):
        client.post(
            "/api/v1/student/activities",
            headers=headers_a,
            json={
                "activity_type": "PRACTICE_SESSION",
                "category": "QUANTITATIVE_APTITUDE",
                "topic": f"Quant Topic {i}",
                "duration_minutes": 30,
                "completion_state": "COMPLETED",
            },
        )

    for i in range(2):
        client.post(
            "/api/v1/student/activities",
            headers=headers_a,
            json={
                "activity_type": "MOCK_TEST",
                "category": "LOGICAL_REASONING",
                "topic": f"Logic Topic {i}",
                "duration_minutes": 45,
                "completion_state": "IN_PROGRESS",
            },
        )

    # Filter by category
    res_quant = client.get("/api/v1/student/activities?category=QUANTITATIVE_APTITUDE", headers=headers_a)
    assert res_quant.status_code == 200
    assert res_quant.json()["total"] == 3
    for item in res_quant.json()["items"]:
        assert item["category"] == "QUANTITATIVE_APTITUDE"

    # Filter by completion state
    res_prog = client.get("/api/v1/student/activities?completion_state=IN_PROGRESS", headers=headers_a)
    assert res_prog.status_code == 200
    assert res_prog.json()["total"] == 2

    # Pagination: page_size=2
    res_p1 = client.get("/api/v1/student/activities?page=1&page_size=2", headers=headers_a)
    assert res_p1.status_code == 200
    p1_data = res_p1.json()
    assert len(p1_data["items"]) == 2
    assert p1_data["total"] == 5
    assert p1_data["total_pages"] == 3


def test_learning_goals_lifecycle_and_auto_progress(test_setup):
    headers_a = {"Authorization": f"Bearer {test_setup['token_a']}"}
    headers_b = {"Authorization": f"Bearer {test_setup['token_b']}"}

    # 1. Create goal: 60 minutes of PROGRAMMING
    create_goal_res = client.post(
        "/api/v1/student/goals",
        headers=headers_a,
        json={
            "title": "Master Binary Search",
            "category": "PROGRAMMING",
            "target_type": "MINUTES_PRACTICED",
            "target_value": 60.0,
        },
    )
    assert create_goal_res.status_code == 201
    goal = create_goal_res.json()
    goal_id = goal["id"]
    assert goal["progress_percentage"] == 0.0
    assert goal["status"] == "IN_PROGRESS"

    # 2. Student A logs 30 minutes in PROGRAMMING
    client.post(
        "/api/v1/student/activities",
        headers=headers_a,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "PROGRAMMING",
            "topic": "Binary Search on Arrays",
            "duration_minutes": 30,
            "completion_state": "COMPLETED",
        },
    )

    # 3. Check goal progress -> should now be 50%
    goals_res = client.get("/api/v1/student/goals", headers=headers_a)
    assert goals_res.status_code == 200
    matching_goal = next(g for g in goals_res.json() if g["id"] == goal_id)
    assert matching_goal["current_value"] == 30.0
    assert matching_goal["progress_percentage"] == 50.0
    assert matching_goal["status"] == "IN_PROGRESS"

    # 4. Student A logs another 30 minutes -> reaches 60 minutes -> should auto-complete!
    client.post(
        "/api/v1/student/activities",
        headers=headers_a,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "PROGRAMMING",
            "topic": "Binary Search on Answer Space",
            "duration_minutes": 30,
            "completion_state": "COMPLETED",
        },
    )

    goals_res2 = client.get("/api/v1/student/goals", headers=headers_a)
    matching_goal2 = next(g for g in goals_res2.json() if g["id"] == goal_id)
    assert matching_goal2["current_value"] == 60.0
    assert matching_goal2["progress_percentage"] == 100.0
    assert matching_goal2["status"] == "COMPLETED"

    # 5. Security test: Student B cannot delete Student A's goal -> 403 Forbidden
    res_hack_del = client.delete(f"/api/v1/student/goals/{goal_id}", headers=headers_b)
    assert res_hack_del.status_code == 403


def test_workspace_summary_telemetry_accuracy(test_setup):
    headers_b = {"Authorization": f"Bearer {test_setup['token_b']}"}

    # 1. Fresh student B has 0 activities (Rule 8: Honest empty states)
    res_empty = client.get("/api/v1/student/workspace-summary", headers=headers_b)
    assert res_empty.status_code == 200
    empty_data = res_empty.json()
    assert empty_data["total_activities"] == 0
    assert empty_data["total_duration_minutes"] == 0
    assert empty_data["completed_activities"] == 0
    assert empty_data["unique_topics_count"] == 0
    assert empty_data["active_goals_count"] == 0
    assert empty_data["recent_activities"] == []

    # 2. Add an activity for Student B
    client.post(
        "/api/v1/student/activities",
        headers=headers_b,
        json={
            "activity_type": "PRACTICE_SESSION",
            "category": "SQL",
            "topic": "Window Functions & CTEs",
            "duration_minutes": 40,
            "completion_state": "COMPLETED",
        },
    )

    res_updated = client.get("/api/v1/student/workspace-summary", headers=headers_b)
    assert res_updated.status_code == 200
    summary = res_updated.json()
    assert summary["total_activities"] == 1
    assert summary["total_duration_minutes"] == 40
    assert summary["completed_activities"] == 1
    assert summary["unique_topics_count"] == 1
    assert summary["category_minutes"]["SQL"] == 40
    assert len(summary["recent_activities"]) == 1


def test_admin_batch_student_import_preview_and_commit(test_setup):
    headers_admin = {"Authorization": f"Bearer {test_setup['token_admin']}"}
    headers_student = {"Authorization": f"Bearer {test_setup['token_a']}"}
    dept_code = test_setup["department"].code

    # 1. Unprivileged student cannot access batch import -> 403 Forbidden
    res_unauth = client.post(
        "/api/v1/admin/students/import-preview",
        headers=headers_student,
        json={"csv_content": "dummy"},
    )
    assert res_unauth.status_code == 403

    import uuid as _uuid
    import_uid = str(_uuid.uuid4())[:8]
    roll1 = f"22CS{import_uid.upper()}1"
    email1 = f"valid.student.{import_uid.lower()}@testinst.edu"

    # 2. Admin previews CSV with 1 valid row and 3 invalid rows (bad email, invalid dept, duplicate roll)
    csv_payload = f"""roll_number,full_name,email,department_code,graduation_year,section,cgpa
{roll1},Valid Student,{email1},{dept_code},2026,B,8.25
22CS802,Bad Email Student,bad-email,{dept_code},2026,B,7.50
22CS803,Bad Dept Student,bad.dept@testinst.edu,NONEXISTENT_DEPT,2026,B,8.00
{test_setup['profile_a'].roll_number},Existing Roll Student,roll.dup@testinst.edu,{dept_code},2026,A,7.00
"""

    preview_res = client.post(
        "/api/v1/admin/students/import-preview",
        headers=headers_admin,
        json={"csv_content": csv_payload},
    )
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["total_rows"] == 4
    assert preview_data["valid_rows_count"] == 1
    assert preview_data["rejected_rows_count"] == 3

    # Check rejection reasons
    rejections = {r["roll_number"]: r["error_reason"] for r in preview_data["rejected_rows"]}
    assert "Invalid email format" in rejections["22CS802"]
    assert "not found in institution" in rejections["22CS803"]
    assert "already assigned in this institution" in rejections[test_setup["profile_a"].roll_number]

    # 3. Admin commits valid rows
    commit_res = client.post(
        "/api/v1/admin/students/import-commit",
        headers=headers_admin,
        json={"rows": preview_data["valid_rows"]},
    )
    assert commit_res.status_code == 201
    commit_data = commit_res.json()
    assert commit_data["created_count"] == 1
    assert commit_data["status"] == "COMMITTED"

    # 4. Verify newly committed student can login and has profile
    login_new = client.post(
        "/api/v1/auth/login",
        json={"email": email1, "password": "Student@Placement2026!"},
    )
    assert login_new.status_code == 200
    token_new = login_new.json()["access_token"]

    profile_new = client.get("/api/v1/student/profile", headers={"Authorization": f"Bearer {token_new}"})
    assert profile_new.status_code == 200
    assert profile_new.json()["roll_number"] == roll1
    assert profile_new.json()["cgpa"] == 8.25
    assert profile_new.json()["cohort_graduation_year"] == 2026
    assert profile_new.json()["cohort_section"] == "B"
