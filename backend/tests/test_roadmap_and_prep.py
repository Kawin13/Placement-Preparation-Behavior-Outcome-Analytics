import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.institution import Institution
from app.models.user import User
from app.models.roadmap import (
    CareerPath,
    RoadmapSubject,
    RoadmapTopic,
    LearningResource,
    StudentCareerGoal,
    StudentBehaviorEvent,
)
from app.core.security import hash_password, create_access_token

client = TestClient(app)


@pytest.fixture
def roadmap_setup():
    db = SessionLocal()
    uid = uuid.uuid4().hex[:8]

    inst = Institution(
        name=f"Roadmap Inst {uid}",
        code=f"RMI_{uid.upper()}",
        is_active=True,
    )
    db.add(inst)
    db.flush()

    student = User(
        institution_id=inst.id,
        email=f"roadmap_student_{uid}@inst.edu",
        password_hash=hash_password("Password@123"),
        full_name="Roadmap Student",
        role="STUDENT",
        is_active=True,
    )
    db.add(student)
    db.flush()

    # Create Career Path
    cpath = CareerPath(
        code=f"sde_{uid}",
        title="Software Development Engineer (Test)",
        target_role="Software Engineer",
        description="Path covering core CS, DSA, and problem solving",
        display_order=1,
    )
    db.add(cpath)
    db.flush()

    # Create Subject
    subj = RoadmapSubject(
        career_path_id=cpath.id,
        code="dsa",
        name="Data Structures & Algorithms",
        description="Core algorithmic problem solving",
        display_order=1,
    )
    db.add(subj)
    db.flush()

    # Create Topic
    topic = RoadmapTopic(
        subject_id=subj.id,
        slug=f"arrays-strings-{uid}",
        name="Arrays and Strings",
        description="Linear structures and operations",
        learning_objectives="Master prefix sums, two pointers, and frequency hashing.",
        difficulty="BEGINNER",
        estimated_minutes=45,
        display_order=1,
    )
    db.add(topic)
    db.flush()

    # Create Learning Resource
    res = LearningResource(
        topic_id=topic.id,
        title="Prefix Sums & Range Queries Guide",
        description="Comprehensive notes on O(1) subarray query processing.",
        resource_type="ARTICLE",
        content="Prefix sum array P[i] = P[i-1] + A[i]. Range sum from L to R = P[R] - P[L-1].",
        difficulty="EASY",
        estimated_duration_min=15,
    )
    db.add(res)
    db.commit()

    token = create_access_token({"sub": str(student.id), "role": "STUDENT"})

    yield {
        "student_token": token,
        "student_id": str(student.id),
        "path_id": str(cpath.id),
        "topic_id": str(topic.id),
        "resource_id": str(res.id),
    }
    db.close()


def test_career_paths_and_goal_selection(roadmap_setup):
    """Students can list available career paths and select their target preparation goal."""
    headers = {"Authorization": f"Bearer {roadmap_setup['student_token']}"}

    # 1. List career paths
    res = client.get("/api/v1/roadmap/career-paths", headers=headers)
    assert res.status_code == 200
    paths = res.json()
    assert len(paths) >= 1
    target_path = next((p for p in paths if p["id"] == roadmap_setup["path_id"]), None)
    assert target_path is not None

    # 2. Select path
    select_payload = {
        "career_path_id": roadmap_setup["path_id"],
        "target_company_tier": "PRODUCT_TIER_1",
    }
    sel_res = client.post("/api/v1/roadmap/select-path", json=select_payload, headers=headers)
    assert sel_res.status_code == 200
    goal = sel_res.json()
    assert goal["career_path_id"] == roadmap_setup["path_id"]
    assert goal["target_role"] == "Software Engineer"

    # 3. Verify goal retrieval
    my_goal_res = client.get("/api/v1/roadmap/my-goal", headers=headers)
    assert my_goal_res.status_code == 200
    assert my_goal_res.json()["career_path_id"] == roadmap_setup["path_id"]


def test_roadmap_tree_and_topic_detail(roadmap_setup):
    """Students can retrieve their hierarchical syllabus tree and inspect topic details."""
    headers = {"Authorization": f"Bearer {roadmap_setup['student_token']}"}

    # First select the goal
    client.post(
        "/api/v1/roadmap/select-path",
        json={"career_path_id": roadmap_setup["path_id"]},
        headers=headers,
    )

    # 1. Fetch roadmap tree
    tree_res = client.get("/api/v1/roadmap/tree", headers=headers)
    assert tree_res.status_code == 200
    tree = tree_res.json()
    assert len(tree["subjects"]) >= 1
    assert tree["subjects"][0]["topics"][0]["id"] == roadmap_setup["topic_id"]

    # 2. Fetch topic details
    topic_res = client.get(f"/api/v1/roadmap/topics/{roadmap_setup['topic_id']}", headers=headers)
    assert topic_res.status_code == 200
    topic = topic_res.json()
    assert topic["name"] == "Arrays and Strings"
    assert "prefix sums" in topic["learning_objectives"].lower()
    assert len(topic["resources"]) >= 1


def test_resource_completion_and_behavior_tracking(roadmap_setup):
    """Students can mark learning resources as studied and log server-verified behavior events."""
    headers = {"Authorization": f"Bearer {roadmap_setup['student_token']}"}

    # First select goal
    client.post(
        "/api/v1/roadmap/select-path",
        json={"career_path_id": roadmap_setup["path_id"]},
        headers=headers,
    )

    # 1. Read resource content
    res_detail = client.get(f"/api/v1/roadmap/resources/{roadmap_setup['resource_id']}", headers=headers)
    assert res_detail.status_code == 200
    assert "Prefix sum array" in res_detail.json()["content"]

    # 2. Mark resource as completed
    comp_res = client.post(
        f"/api/v1/roadmap/resources/{roadmap_setup['resource_id']}/complete?duration_seconds=120",
        headers=headers,
    )
    assert comp_res.status_code == 200

    # 3. Verify topic reflects resource completion
    topic_after = client.get(f"/api/v1/roadmap/topics/{roadmap_setup['topic_id']}", headers=headers).json()
    assert topic_after["resources"][0]["is_completed"] is True

    # 4. Track student behavior event
    event_payload = {
        "event_type": "MISTAKE_REVIEWED",
        "category": "REVISION",
        "entity_id": roadmap_setup["topic_id"],
        "metadata_json": {"study_session_notes": "Reviewed range query proofs."},
    }
    track_res = client.post("/api/v1/roadmap/track-event", json=event_payload, headers=headers)
    assert track_res.status_code == 201
    assert track_res.json()["status"] == "recorded"

    # 5. Retrieve dynamic intelligent recommended next step
    rec_res = client.get("/api/v1/roadmap/next-recommended-action", headers=headers)
    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["action_type"] in ["STUDY_RESOURCE", "SOLVE_PRACTICE", "SOLVE_DSA", "REVIEW_MISTAKES"]
