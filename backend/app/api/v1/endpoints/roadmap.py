import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.roadmap import (
    CareerPath,
    RoadmapSubject,
    RoadmapTopic,
    RoadmapSubtopic,
    LearningResource,
    StudentCareerGoal,
    StudentTopicProgress,
    StudentBehaviorEvent,
)
from app.models.practice import MistakeNotebookEntry, AttemptRecord
from app.models.question import Question
from app.models.dsa import DSAProblem, DSAUserProgress
from app.models.assessment import Assessment, AssessmentQuestion
from app.schemas.roadmap import (
    CareerPathResponse,
    SelectCareerGoalRequest,
    StudentCareerGoalResponse,
    LearningResourceSummary,
    LearningResourceDetail,
    RoadmapTopicSummary,
    RoadmapSubjectTree,
    RoadmapTreeResponse,
    TopicAssessmentInfo,
    TopicDetailResponse,
    TopicPracticeQuestionItem,
    TopicDSAProblemItem,
    TrackEventRequest,
    RecommendedActionResponse,
)

router = APIRouter()


@router.get("/career-paths", response_model=List[CareerPathResponse])
def get_career_paths(db: Session = Depends(get_db)):
    """Returns active, database-backed career paths configured for institutional students."""
    paths = db.query(CareerPath).filter(CareerPath.is_active == True).order_by(CareerPath.display_order).all()
    return paths


@router.post("/select-path", response_model=StudentCareerGoalResponse, status_code=status.HTTP_200_OK)
def select_career_path(
    payload: SelectCareerGoalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assigns or updates the authenticated student's active career goal."""
    path = db.query(CareerPath).filter(CareerPath.id == payload.career_path_id, CareerPath.is_active == True).first()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified career path is not available")

    goal = db.query(StudentCareerGoal).filter(StudentCareerGoal.user_id == current_user.id).first()
    if not goal:
        goal = StudentCareerGoal(
            user_id=current_user.id,
            career_path_id=path.id,
            target_date=payload.target_date,
            status="ACTIVE",
        )
        db.add(goal)
    else:
        goal.career_path_id = path.id
        goal.status = "ACTIVE"
        if payload.target_date is not None:
            goal.target_date = payload.target_date

    # Record behavior event
    event = StudentBehaviorEvent(
        user_id=current_user.id,
        event_type="TOPIC_SWITCH",
        category="CAREER_PATH_SELECTED",
        entity_id=str(path.id),
        metadata_json={"career_path_code": path.code, "career_path_title": path.title},
    )
    db.add(event)

    db.commit()
    db.refresh(goal)

    return StudentCareerGoalResponse(
        id=goal.id,
        career_path_id=goal.career_path_id,
        career_path_code=path.code,
        career_path_title=path.title,
        target_role=path.target_role,
        status=goal.status,
        target_date=goal.target_date,
        created_at=goal.created_at,
    )


@router.get("/my-goal", response_model=Optional[StudentCareerGoalResponse])
def get_my_career_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the active student's career preparation goal."""
    goal = db.query(StudentCareerGoal).filter(StudentCareerGoal.user_id == current_user.id).first()
    if not goal:
        # Default to SDE if available
        sde = db.query(CareerPath).filter(CareerPath.code == "SDE").first()
        if sde:
            goal = StudentCareerGoal(
                user_id=current_user.id,
                career_path_id=sde.id,
                status="ACTIVE",
            )
            db.add(goal)
            db.commit()
            db.refresh(goal)
        else:
            return None

    path = goal.career_path
    return StudentCareerGoalResponse(
        id=goal.id,
        career_path_id=goal.career_path_id,
        career_path_code=path.code,
        career_path_title=path.title,
        target_role=path.target_role,
        status=goal.status,
        target_date=goal.target_date,
        created_at=goal.created_at,
    )


@router.get("/tree", response_model=RoadmapTreeResponse)
def get_roadmap_tree(
    career_path_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the complete hierarchical preparation roadmap for a career path:
    Career Path -> Subjects -> Topics -> Student Progress & Metrics.
    """
    # Resolve target career path
    if career_path_id:
        path = db.query(CareerPath).filter(CareerPath.id == career_path_id).first()
    else:
        goal = db.query(StudentCareerGoal).filter(StudentCareerGoal.user_id == current_user.id).first()
        if goal:
            path = goal.career_path
        else:
            path = db.query(CareerPath).filter(CareerPath.code == "SDE").first()

    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found")

    subjects = (
        db.query(RoadmapSubject)
        .filter(RoadmapSubject.career_path_id == path.id)
        .order_by(RoadmapSubject.display_order)
        .all()
    )

    # Preload student progress records
    progress_map = {
        p.topic_id: p
        for p in db.query(StudentTopicProgress).filter(StudentTopicProgress.user_id == current_user.id).all()
    }

    subject_trees = []
    total_topics = 0
    completed_topics = 0

    for s in subjects:
        topics_summary = []
        for t in s.topics:
            total_topics += 1
            res_count = len(t.resources)
            # Count practice questions matching assessment or skill
            q_count = 0
            if t.assessment_id:
                q_count = db.query(func.count(AssessmentQuestion.id)).filter(AssessmentQuestion.assessment_id == t.assessment_id).scalar() or 0
            elif t.skill_id:
                q_count = db.query(func.count(Question.id)).filter(Question.skill_id == t.skill_id).scalar() or 0
            else:
                q_count = 3

            # Count DSA problems
            dsa_count = 0
            if t.dsa_topic_id:
                dsa_count = db.query(func.count(DSAProblem.id)).filter(DSAProblem.topic_id == t.dsa_topic_id).scalar() or 0

            # Progress
            prog = progress_map.get(t.id)
            status_val = prog.status if prog else "NOT_STARTED"
            pct = prog.completion_percentage if prog else 0

            if status_val == "COMPLETED" or pct >= 100:
                completed_topics += 1

            topics_summary.append(
                RoadmapTopicSummary(
                    id=t.id,
                    subject_id=t.subject_id,
                    slug=t.slug,
                    name=t.name,
                    description=t.description,
                    learning_objectives=t.learning_objectives,
                    difficulty=t.difficulty,
                    estimated_minutes=t.estimated_minutes,
                    display_order=t.display_order,
                    resources_count=res_count,
                    practice_questions_count=q_count,
                    dsa_problems_count=dsa_count,
                    completion_percentage=pct,
                    status=status_val,
                    assessment_id=t.assessment_id,
                )
            )

        subject_trees.append(
            RoadmapSubjectTree(
                id=s.id,
                code=s.code,
                name=s.name,
                description=s.description,
                icon=s.icon,
                display_order=s.display_order,
                topics=topics_summary,
            )
        )

    overall_pct = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

    return RoadmapTreeResponse(
        career_path=CareerPathResponse.model_validate(path),
        subjects=subject_trees,
        overall_progress_percentage=overall_pct,
        completed_topics_count=completed_topics,
        total_topics_count=total_topics,
    )


@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
def get_topic_detail(
    topic_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns granular topic information with database learning resources,
    practice questions, and linked DSA coding challenges.
    """
    topic = db.query(RoadmapTopic).filter(RoadmapTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Completed resources for user
    completed_res_ids = {
        e.entity_id
        for e in db.query(StudentBehaviorEvent.entity_id).filter(
            StudentBehaviorEvent.user_id == current_user.id,
            StudentBehaviorEvent.event_type == "RESOURCE_COMPLETED",
        ).all()
        if e.entity_id
    }

    # Fetch resources
    resources = [
        LearningResourceSummary(
            id=r.id,
            topic_id=r.topic_id,
            subtopic_id=r.subtopic_id,
            title=r.title,
            description=r.description,
            resource_type=r.resource_type,
            external_url=r.external_url,
            difficulty=r.difficulty,
            estimated_duration_min=r.estimated_duration_min,
            status=r.status,
            is_completed=str(r.id) in completed_res_ids,
        )
        for r in topic.resources if r.status == "PUBLISHED"
    ]

    # Fetch assessment info & questions
    assessment_info = None
    questions = []

    # 1. Lookup assessment via topic.assessment or Assessment.topic == topic.name
    assessment_obj = topic.assessment
    if not assessment_obj and topic.assessment_id:
        assessment_obj = db.query(Assessment).filter(Assessment.id == topic.assessment_id).first()
    if not assessment_obj:
        assessment_obj = db.query(Assessment).filter(
            Assessment.topic == topic.name,
            Assessment.is_published == True
        ).first()

    if assessment_obj:
        aq_links = db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_obj.id
        ).order_by(AssessmentQuestion.order_index).all()

        assessment_info = TopicAssessmentInfo(
            id=assessment_obj.id,
            title=assessment_obj.title,
            duration_minutes=assessment_obj.duration_minutes,
            passing_score=float(assessment_obj.passing_score) if assessment_obj.passing_score is not None else None,
            questions_count=len(aq_links),
            category=assessment_obj.category,
        )

        for aq in aq_links:
            q = aq.question
            if not q:
                continue
            attempts = db.query(AttemptRecord).filter(
                AttemptRecord.user_id == current_user.id,
                AttemptRecord.question_id == q.id
            ).all()
            attempts_cnt = len(attempts)
            correct_cnt = sum(1 for a in attempts if a.is_correct)
            user_acc = round((correct_cnt / attempts_cnt) * 100, 1) if attempts_cnt > 0 else None
            is_solved = correct_cnt > 0

            questions.append(
                TopicPracticeQuestionItem(
                    id=q.id,
                    title=q.title,
                    content=q.content,
                    difficulty=q.difficulty,
                    question_type=q.question_type or "MCQ_SINGLE",
                    points=aq.points or q.default_points or 2,
                    attempts_count=attempts_cnt,
                    user_accuracy=user_acc,
                    is_solved=is_solved,
                )
            )

    # Fallback to skill_id if no assessment questions found
    if not questions and topic.skill_id:
        raw_qs = db.query(Question).filter(Question.skill_id == topic.skill_id, Question.status == "PUBLISHED").limit(10).all()
        for q in raw_qs:
            attempts = db.query(AttemptRecord).filter(
                AttemptRecord.user_id == current_user.id,
                AttemptRecord.question_id == q.id
            ).all()
            attempts_cnt = len(attempts)
            correct_cnt = sum(1 for a in attempts if a.is_correct)
            user_acc = round((correct_cnt / attempts_cnt) * 100, 1) if attempts_cnt > 0 else None
            is_solved = correct_cnt > 0
            questions.append(
                TopicPracticeQuestionItem(
                    id=q.id,
                    title=q.title,
                    content=q.content,
                    difficulty=q.difficulty,
                    question_type=q.question_type or "MCQ_SINGLE",
                    points=q.default_points or 2,
                    attempts_count=attempts_cnt,
                    user_accuracy=user_acc,
                    is_solved=is_solved,
                )
            )

    # Fetch DSA problems
    dsa_problems = []
    if topic.dsa_topic_id:
        problems = db.query(DSAProblem).filter(DSAProblem.topic_id == topic.dsa_topic_id, DSAProblem.status == "PUBLISHED").all()
        for p in problems:
            prog = db.query(DSAUserProgress).filter(
                DSAUserProgress.user_id == current_user.id,
                DSAUserProgress.problem_id == p.id,
            ).first()
            p_status = prog.status if prog else "UNSOLVED"
            dsa_problems.append(
                TopicDSAProblemItem(
                    id=p.id,
                    problem_number=p.problem_number,
                    slug=p.slug,
                    title=p.title,
                    difficulty=p.difficulty,
                    status=p_status,
                )
            )

    # User progress
    prog = db.query(StudentTopicProgress).filter(
        StudentTopicProgress.user_id == current_user.id,
        StudentTopicProgress.topic_id == topic.id,
    ).first()

    q_attempted = prog.questions_attempted if prog else 0
    q_correct = prog.questions_correct if prog else 0
    accuracy = int((q_correct / q_attempted) * 100) if q_attempted > 0 else 0

    if q_attempted >= 5:
        evidence_conf = "HIGH"
    elif q_attempted >= 2:
        evidence_conf = "MODERATE"
    elif q_attempted >= 1:
        evidence_conf = "LOW"
    else:
        evidence_conf = "INSUFFICIENT"

    rec_step = "Take the Verified GFG Assessment drill to benchmark your skills." if assessment_info else "Study the learning resources."

    return TopicDetailResponse(
        id=topic.id,
        subject_id=topic.subject_id,
        subject_name=topic.subject.name,
        slug=topic.slug,
        name=topic.name,
        description=topic.description,
        learning_objectives=topic.learning_objectives,
        difficulty=topic.difficulty,
        estimated_minutes=topic.estimated_minutes,
        resources=resources,
        practice_questions=questions,
        dsa_problems=dsa_problems,
        assessment=assessment_info,
        completion_percentage=prog.completion_percentage if prog else 0,
        status=prog.status if prog else "NOT_STARTED",
        questions_attempted=q_attempted,
        questions_correct=q_correct,
        coding_problems_solved=prog.coding_problems_solved if prog else 0,
        resources_completed=prog.resources_completed if prog else 0,
        accuracy_rate=accuracy,
        evidence_confidence=evidence_conf,
        recommended_next_step=rec_step,
    )


@router.get("/resources/{resource_id}", response_model=LearningResourceDetail)
def get_resource_detail(
    resource_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns authentic learning material with complete markdown explanations and logs access telemetry."""
    res = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning resource not found")

    # Record behavior telemetry event
    event = StudentBehaviorEvent(
        user_id=current_user.id,
        event_type="RESOURCE_OPENED",
        category="LEARNING_MATERIAL",
        entity_id=str(res.id),
        duration_seconds=0,
        metadata_json={"title": res.title, "resource_type": res.resource_type},
    )
    db.add(event)
    db.commit()

    # Check if resource completed
    is_completed = db.query(StudentBehaviorEvent).filter(
        StudentBehaviorEvent.user_id == current_user.id,
        StudentBehaviorEvent.event_type == "RESOURCE_COMPLETED",
        StudentBehaviorEvent.entity_id == str(res.id),
    ).first() is not None

    return LearningResourceDetail(
        id=res.id,
        topic_id=res.topic_id,
        subtopic_id=res.subtopic_id,
        title=res.title,
        description=res.description,
        resource_type=res.resource_type,
        content=res.content,
        external_url=res.external_url,
        difficulty=res.difficulty,
        estimated_duration_min=res.estimated_duration_min,
        status=res.status,
        is_completed=is_completed,
        updated_at=res.updated_at,
    )


@router.post("/resources/{resource_id}/complete")
def complete_resource(
    resource_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marks a learning resource as completed, updating the student's topic progress metrics."""
    res = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning resource not found")

    # Update topic progress
    prog = db.query(StudentTopicProgress).filter(
        StudentTopicProgress.user_id == current_user.id,
        StudentTopicProgress.topic_id == res.topic_id,
    ).first()
    if not prog:
        prog = StudentTopicProgress(
            user_id=current_user.id,
            topic_id=res.topic_id,
            status="IN_PROGRESS",
            completion_percentage=25,
            resources_completed=1,
            last_activity_at=datetime.now(timezone.utc),
        )
        db.add(prog)
    else:
        prog.resources_completed += 1
        prog.completion_percentage = min(100, prog.completion_percentage + 25)
        if prog.completion_percentage >= 100:
            prog.status = "COMPLETED"
        else:
            prog.status = "IN_PROGRESS"
        prog.last_activity_at = datetime.now(timezone.utc)

    # Record behavior event
    event = StudentBehaviorEvent(
        user_id=current_user.id,
        event_type="RESOURCE_COMPLETED",
        category="LEARNING_MATERIAL",
        entity_id=str(res.id),
        duration_seconds=res.estimated_duration_min * 60,
        metadata_json={"title": res.title},
    )
    db.add(event)
    db.commit()

    return {"message": "Resource completed successfully", "topic_progress": prog.completion_percentage}


@router.post("/track-event", status_code=status.HTTP_201_CREATED)
def track_behavior_event(
    payload: TrackEventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_event_types = {
        "SESSION_START", "SESSION_COMPLETE", "SESSION_ABANDONED",
        "PRACTICE_ATTEMPT", "MISTAKE_REVIEWED", "RESOURCE_OPENED",
        "RESOURCE_COMPLETED", "CODING_SUBMIT", "TOPIC_SWITCH"
    }
    if payload.event_type not in allowed_event_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type '{payload.event_type}'. Must be one of: {sorted(allowed_event_types)}"
        )

    duration = max(0, min(payload.duration_seconds, 7200))  # Cap at 2 hours to avoid idle manipulation
    event = StudentBehaviorEvent(
        user_id=current_user.id,
        event_type=payload.event_type,
        category=payload.category,
        entity_id=payload.entity_id,
        duration_seconds=duration,
        metadata_json=payload.metadata_json,
    )
    db.add(event)
    db.commit()
    return {"message": "Behavior event logged", "event_id": str(event.id), "status": "recorded"}


@router.get("/next-recommended-action", response_model=RecommendedActionResponse)
def get_next_recommended_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Intelligent curriculum engine: determines the student's highest priority next activity
    scoped to their active career goal, unresolved mistakes, incomplete resources, or pending topics.
    """
    # 0. Identify active career path
    goal = db.query(StudentCareerGoal).filter(StudentCareerGoal.user_id == current_user.id).first()
    active_path_id = goal.career_path_id if goal else None
    if not active_path_id:
        sde = db.query(CareerPath).filter(CareerPath.code == "SDE").first()
        active_path_id = sde.id if sde else None

    # 1. Check for unresolved mistakes
    unresolved_mistake = (
        db.query(MistakeNotebookEntry)
        .filter(
            MistakeNotebookEntry.user_id == current_user.id,
            MistakeNotebookEntry.mastery_status.in_(["NEEDS_REVIEW", "IN_REVISION"]),
        )
        .order_by(desc(MistakeNotebookEntry.created_at))
        .first()
    )
    if unresolved_mistake:
        q = unresolved_mistake.question
        return RecommendedActionResponse(
            action_type="REVIEW_MISTAKES",
            title=f"Review Mistake: {q.title if q else 'Concept Drill'}",
            reason="You have recorded mistakes awaiting revision. Re-evaluating past errors solidifies placement readiness.",
            target_id=str(unresolved_mistake.id),
            target_url="/mistakes",
            estimated_minutes=10,
        )

    # 2. Check for in-progress topic in student's active career path
    in_prog = None
    if active_path_id:
        in_prog = (
            db.query(StudentTopicProgress)
            .join(RoadmapTopic, StudentTopicProgress.topic_id == RoadmapTopic.id)
            .join(RoadmapSubject, RoadmapTopic.subject_id == RoadmapSubject.id)
            .filter(
                StudentTopicProgress.user_id == current_user.id,
                RoadmapSubject.career_path_id == active_path_id,
                StudentTopicProgress.status == "IN_PROGRESS",
            )
            .order_by(desc(StudentTopicProgress.last_activity_at))
            .first()
        )

    if in_prog and in_prog.topic:
        res = db.query(LearningResource).filter(LearningResource.topic_id == in_prog.topic_id).first()
        display_title = res.title if res else in_prog.topic.name
        return RecommendedActionResponse(
            action_type="STUDY_RESOURCE",
            title=f"Study: {display_title}",
            reason=f"Continue your in-progress study of {in_prog.topic.name}.",
            target_id=str(in_prog.topic.id),
            target_slug=in_prog.topic.slug,
            target_topic_id=str(in_prog.topic.id),
            target_url=f"/roadmap/topic/{in_prog.topic.id}",
            estimated_minutes=res.estimated_duration_min if res else (in_prog.topic.estimated_minutes or 20),
        )

    # 3. Check for next unstarted/uncompleted topic in student's active career path
    if active_path_id:
        completed_ids = {
            p.topic_id
            for p in db.query(StudentTopicProgress.topic_id)
            .filter(
                StudentTopicProgress.user_id == current_user.id,
                StudentTopicProgress.status == "COMPLETED",
            )
            .all()
        }
        next_topic = (
            db.query(RoadmapTopic)
            .join(RoadmapSubject, RoadmapTopic.subject_id == RoadmapSubject.id)
            .filter(
                RoadmapSubject.career_path_id == active_path_id,
                ~RoadmapTopic.id.in_(completed_ids) if completed_ids else True,
            )
            .order_by(RoadmapSubject.display_order, RoadmapTopic.display_order)
            .first()
        )
        if next_topic:
            res = db.query(LearningResource).filter(LearningResource.topic_id == next_topic.id).first()
            return RecommendedActionResponse(
                action_type="STUDY_RESOURCE",
                title=f"Study: {next_topic.name}",
                reason=f"Begin your foundational learning in {next_topic.subject.name}.",
                target_id=str(next_topic.id),
                target_slug=next_topic.slug,
                target_topic_id=str(next_topic.id),
                target_url=f"/roadmap/topic/{next_topic.id}",
                estimated_minutes=res.estimated_duration_min if res else (next_topic.estimated_minutes or 25),
            )

    # 4. Default to next DSA Problem
    unsolved_dsa = db.query(DSAProblem).filter(DSAProblem.status == "PUBLISHED").order_by(DSAProblem.problem_number).first()
    if unsolved_dsa:
        return RecommendedActionResponse(
            action_type="SOLVE_DSA",
            title=f"Solve Coding Problem: {unsolved_dsa.title}",
            reason="Sharpen your coding skills with algorithmic problem solving.",
            target_id=str(unsolved_dsa.id),
            target_slug=unsolved_dsa.slug,
            target_url=f"/dsa/{unsolved_dsa.slug}",
            estimated_minutes=25,
        )

    # 5. Fallback to general practice drill
    return RecommendedActionResponse(
        action_type="SOLVE_PRACTICE",
        title="Quantitative Aptitude Diagnostic Drill",
        reason="Take a timed assessment to benchmark your placement readiness score.",
        target_id=None,
        target_url="/assessments",
        estimated_minutes=15,
    )
