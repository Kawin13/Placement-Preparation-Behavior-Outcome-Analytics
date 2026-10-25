"""
Integration tests for DSA Preparation Module API endpoints:
- Topic hierarchy retrieval
- Problem listing with difficulty and status filtering
- POTD retrieval
- Individual problem details retrieval
- Run code sandbox (public cases)
- Submit solution (hidden test cases, progress update, submission recording)
- Submissions history
- Student DSA analytics
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.user import User
from app.models.dsa import DSATopic, DSAProblem, DSATestCase, DSASubmission, DSAUserProgress
from app.core.security import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture
def dsa_test_user():
    db = SessionLocal()
    uid = uuid.uuid4().hex[:8]

    inst = Institution(
        name=f"DSA Inst {uid}",
        code=f"DS_{uid.upper()}",
        is_active=True,
    )
    db.add(inst)
    db.flush()

    user = User(
        email=f"dsa_student_{uid}@example.com",
        password_hash=hash_password("StudentPass123!"),
        full_name=f"DSA Student {uid}",
        role="STUDENT",
        institution_id=inst.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    yield {"user": user, "headers": headers, "db": db}

    db.query(DSASubmission).filter(DSASubmission.user_id == user.id).delete()
    db.query(DSAUserProgress).filter(DSAUserProgress.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.query(Institution).filter(Institution.id == inst.id).delete()
    db.commit()
    db.close()


def test_list_dsa_topics(dsa_test_user):
    headers = dsa_test_user["headers"]
    resp = client.get("/api/v1/dsa/topics", headers=headers)
    assert resp.status_code == 200
    topics = resp.json()
    assert len(topics) >= 12
    slugs = [t["slug"] for t in topics]
    assert "arrays-strings" in slugs
    assert "dynamic-programming" in slugs


def test_list_dsa_problems_with_filters(dsa_test_user):
    headers = dsa_test_user["headers"]
    # All problems
    resp = client.get("/api/v1/dsa/problems", headers=headers)
    assert resp.status_code == 200
    problems = resp.json()
    assert len(problems) >= 10

    # Filter by difficulty
    resp_easy = client.get("/api/v1/dsa/problems?difficulty=EASY", headers=headers)
    assert resp_easy.status_code == 200
    for p in resp_easy.json():
        assert p["difficulty"] == "EASY"

    # Filter by topic
    resp_topic = client.get("/api/v1/dsa/problems?topic_slug=arrays-strings", headers=headers)
    assert resp_topic.status_code == 200
    for p in resp_topic.json():
        assert p["topic_slug"] == "arrays-strings"


def test_get_problem_of_the_day(dsa_test_user):
    headers = dsa_test_user["headers"]
    resp = client.get("/api/v1/dsa/problems/potd", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "slug" in data
    assert "title" in data


def test_get_problem_details(dsa_test_user):
    headers = dsa_test_user["headers"]
    resp = client.get("/api/v1/dsa/problems/two-sum", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "two-sum"
    assert "starter_code" in data
    assert "python" in data["starter_code"]
    assert "java" in data["starter_code"]
    assert len(data["sample_test_cases"]) >= 1


def test_run_dsa_code(dsa_test_user):
    headers = dsa_test_user["headers"]
    python_solution = """import sys
lines = sys.stdin.read().splitlines()
if len(lines) >= 2:
    nums = list(map(int, lines[0].strip().split()))
    target = int(lines[1].strip())
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            res = sorted([seen[diff], i])
            print(f"{res[0]} {res[1]}")
            break
        seen[num] = i
"""
    payload = {
        "language": "python",
        "code": python_solution,
        "custom_input": "1 2 3 4\n5",
    }
    resp = client.post("/api/v1/dsa/problems/two-sum/run", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert len(data["results"]) >= 1
    assert data["results"][0]["passed"] is True
    assert data["custom_result"] is not None


def test_submit_dsa_solution_and_progress(dsa_test_user):
    headers = dsa_test_user["headers"]
    python_solution = """import sys
lines = sys.stdin.read().splitlines()
if len(lines) >= 2:
    nums = list(map(int, lines[0].strip().split()))
    target = int(lines[1].strip())
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            res = sorted([seen[diff], i])
            print(f"{res[0]} {res[1]}")
            break
        seen[num] = i
"""
    payload = {
        "language": "python",
        "code": python_solution,
        "hints_viewed": 1,
    }
    resp = client.post("/api/v1/dsa/problems/two-sum/submit", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "ACCEPTED"
    assert data["test_cases_passed"] == data["total_test_cases"]
    assert data["is_first_solve"] is True

    # Check submissions history
    hist_resp = client.get("/api/v1/dsa/problems/two-sum/submissions", headers=headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 1
    assert history[0]["verdict"] == "ACCEPTED"

    # Check student analytics
    analytics_resp = client.get("/api/v1/dsa/analytics/me", headers=headers)
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["total_solved"] >= 1
    assert analytics["total_submissions"] >= 1
    assert analytics["acceptance_rate"] == 100.0
