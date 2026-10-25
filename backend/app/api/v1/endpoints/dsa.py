"""
DSA Problem-Solving Platform REST API Endpoints:
- Topic hierarchy & problem library with search, filtering, and POTD
- Code execution sandbox runner (public cases + custom input)
- Submission evaluation engine (hidden test cases, progress tracking, audit recording)
- User submission history and editorial solutions
- Behavioral analytics & personalized next-step problem recommendations
- Trainer authoring and question ingestion
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.dsa import (
    DSATopic,
    DSAProblem,
    DSATestCase,
    DSASubmission,
    DSAUserProgress,
)
from app.schemas.dsa import (
    DSATopicItem,
    DSAProblemListItem,
    DSAProblemDetail,
    VisibleTestCase,
    ExampleCase,
    DSARunCodeRequest,
    DSARunCodeResponse,
    DSARunCaseResult,
    DSASubmitRequest,
    DSASubmitResponse,
    DSASubmissionHistoryItem,
    DSAEditorialResponse,
    DSAStudentAnalyticsResponse,
    DSATopicStat,
    DSAProblemCreateRequest,
)
from app.services.judge import execute_test_case, evaluate_batch

router = APIRouter()


# --------------------------------------------------------------------------
# Topic Hierarchy
# --------------------------------------------------------------------------

@router.get("/topics", response_model=List[DSATopicItem])
def list_dsa_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns all 12 DSA topics with total problem counts and student's solved counts."""
    topics = db.query(DSATopic).order_by(DSATopic.order_index.asc()).all()

    # Pre-fetch user solved problem IDs
    solved_problem_ids = set(
        pid[0]
        for pid in db.query(DSAUserProgress.problem_id)
        .filter(
            DSAUserProgress.user_id == current_user.id,
            DSAUserProgress.status == "SOLVED",
        )
        .all()
    )

    result = []
    for t in topics:
        published_problems = [p for p in t.problems if p.status == "PUBLISHED"]
        total_p = len(published_problems)
        solved_p = sum(1 for p in published_problems if p.id in solved_problem_ids)

        result.append(
            DSATopicItem(
                id=t.id,
                slug=t.slug,
                name=t.name,
                order_index=t.order_index,
                summary=t.summary,
                problem_count=total_p,
                solved_count=solved_p,
            )
        )
    return result


# --------------------------------------------------------------------------
# Problem Catalog & Filtering
# --------------------------------------------------------------------------

@router.get("/problems", response_model=List[DSAProblemListItem])
def list_dsa_problems(
    topic_slug: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    sheet_tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Searchable, filterable DSA problem library.
    Filters by topic, difficulty, status (UNSOLVED/ATTEMPTED/SOLVED), sheet tags, and keyword.
    """
    query = db.query(DSAProblem).filter(DSAProblem.status == "PUBLISHED")

    if topic_slug:
        query = query.join(DSATopic, DSAProblem.topic_id == DSATopic.id).filter(DSATopic.slug == topic_slug)

    if difficulty:
        query = query.filter(DSAProblem.difficulty == difficulty.upper())

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (DSAProblem.title.ilike(search_fmt)) | (DSAProblem.description.ilike(search_fmt))
        )

    problems = query.order_by(DSAProblem.problem_number.asc()).all()

    # Load user progress mapping
    user_progress_map = {
        prog.problem_id: prog.status
        for prog in db.query(DSAUserProgress).filter(DSAUserProgress.user_id == current_user.id).all()
    }

    # Pre-fetch acceptance rates
    submissions_stats = (
        db.query(
            DSASubmission.problem_id,
            func.count(DSASubmission.id).label("total_subs"),
            func.count(DSASubmission.id).filter(DSASubmission.verdict == "ACCEPTED").label("acc_subs"),
        )
        .group_by(DSASubmission.problem_id)
        .all()
    )
    acceptance_map = {}
    for pid, total_s, acc_s in submissions_stats:
        acceptance_map[pid] = round((acc_s / total_s * 100.0), 1) if total_s > 0 else 0.0

    items: List[DSAProblemListItem] = []
    for p in problems:
        # Sheet tag filter
        if sheet_tag and sheet_tag not in (p.sheet_tags or []):
            continue

        u_status = user_progress_map.get(p.id, "UNSOLVED")

        # Status filter
        if status_filter and status_filter.upper() != "ALL":
            if u_status != status_filter.upper():
                continue

        acc_rate = acceptance_map.get(p.id, 0.0)

        items.append(
            DSAProblemListItem(
                id=p.id,
                problem_number=p.problem_number,
                slug=p.slug,
                title=p.title,
                difficulty=p.difficulty,
                topic_name=p.topic.name if p.topic else None,
                topic_slug=p.topic.slug if p.topic else None,
                sheet_tags=p.sheet_tags or [],
                is_problem_of_the_day=p.is_problem_of_the_day,
                status=p.status,
                user_status=u_status,
                acceptance_rate=acc_rate,
            )
        )

    return items


@router.get("/problems/potd", response_model=DSAProblemListItem)
def get_problem_of_the_day(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns today's curated Problem of the Day."""
    problem = (
        db.query(DSAProblem)
        .filter(DSAProblem.is_problem_of_the_day == True, DSAProblem.status == "PUBLISHED")
        .first()
    )
    if not problem:
        problem = (
            db.query(DSAProblem)
            .filter(DSAProblem.status == "PUBLISHED")
            .order_by(DSAProblem.problem_number.asc())
            .first()
        )

    if not problem:
        raise HTTPException(status_code=404, detail="No problems published yet.")

    prog = (
        db.query(DSAUserProgress)
        .filter(DSAUserProgress.user_id == current_user.id, DSAUserProgress.problem_id == problem.id)
        .first()
    )
    u_status = prog.status if prog else "UNSOLVED"

    return DSAProblemListItem(
        id=problem.id,
        problem_number=problem.problem_number,
        slug=problem.slug,
        title=problem.title,
        difficulty=problem.difficulty,
        topic_name=problem.topic.name if problem.topic else None,
        topic_slug=problem.topic.slug if problem.topic else None,
        sheet_tags=problem.sheet_tags or [],
        is_problem_of_the_day=problem.is_problem_of_the_day,
        status=problem.status,
        user_status=u_status,
        acceptance_rate=85.0,
    )


@router.get("/problems/{slug}", response_model=DSAProblemDetail)
def get_dsa_problem_details(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns full problem description, examples, constraints, starter code,
    hints, and visible sample test cases for the coding studio.
    """
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found.")

    # Get sample test cases (non-hidden)
    sample_cases = (
        db.query(DSATestCase)
        .filter(DSATestCase.problem_id == problem.id, DSATestCase.is_hidden == False)
        .order_by(DSATestCase.order_index.asc())
        .all()
    )

    prog = (
        db.query(DSAUserProgress)
        .filter(DSAUserProgress.user_id == current_user.id, DSAUserProgress.problem_id == problem.id)
        .first()
    )
    u_status = prog.status if prog else "UNSOLVED"

    return DSAProblemDetail(
        id=problem.id,
        problem_number=problem.problem_number,
        slug=problem.slug,
        title=problem.title,
        difficulty=problem.difficulty,
        topic_id=problem.topic_id,
        topic_name=problem.topic.name if problem.topic else None,
        topic_slug=problem.topic.slug if problem.topic else None,
        description=problem.description,
        constraints=problem.constraints,
        input_format=problem.input_format,
        output_format=problem.output_format,
        examples=[ExampleCase(**ex) for ex in (problem.examples or [])],
        starter_code=problem.starter_code or {},
        expected_time_complexity=problem.expected_time_complexity,
        expected_space_complexity=problem.expected_space_complexity,
        hints=problem.hints or [],
        sample_test_cases=[
            VisibleTestCase(
                case_index=tc.order_index or idx,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
            )
            for idx, tc in enumerate(sample_cases, start=1)
        ],
        sheet_tags=problem.sheet_tags or [],
        is_problem_of_the_day=problem.is_problem_of_the_day,
        user_status=u_status,
    )


# --------------------------------------------------------------------------
# Code Execution & Online Judge
# --------------------------------------------------------------------------

@router.post("/problems/{slug}/run", response_model=DSARunCodeResponse)
def run_dsa_code(
    slug: str,
    payload: DSARunCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes student code against public sample test cases and optional custom input.
    Does NOT register a permanent submission or affect student solved progress.
    """
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    # 1. Fetch public test cases
    sample_cases = (
        db.query(DSATestCase)
        .filter(DSATestCase.problem_id == problem.id, DSATestCase.is_hidden == False)
        .order_by(DSATestCase.order_index.asc())
        .all()
    )

    results: List[DSARunCaseResult] = []
    overall_status = "SUCCESS"
    comp_error = None

    for idx, tc in enumerate(sample_cases, start=1):
        res = execute_test_case(
            language=payload.language,
            code=payload.code,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            time_limit_ms=tc.time_limit_ms,
        )

        if res["verdict"] == "COMPILATION_ERROR":
            overall_status = "COMPILATION_ERROR"
            comp_error = res["error"]
            results.append(
                DSARunCaseResult(
                    case_index=idx,
                    input_data=tc.input_data,
                    expected_output=tc.expected_output,
                    actual_output="",
                    passed=False,
                    execution_time_ms=0,
                    error=res["error"],
                )
            )
            break

        results.append(
            DSARunCaseResult(
                case_index=idx,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                actual_output=res["stdout"],
                passed=res["passed"],
                execution_time_ms=res["runtime_ms"],
                error=res["error"],
            )
        )

        if not res["passed"] and overall_status == "SUCCESS":
            overall_status = res["verdict"]

    # 2. Handle optional custom input
    custom_res = None
    if payload.custom_input is not None and overall_status != "COMPILATION_ERROR":
        c_exec = execute_test_case(
            language=payload.language,
            code=payload.code,
            input_data=payload.custom_input,
            expected_output=None,
            time_limit_ms=2000,
        )
        custom_res = DSARunCaseResult(
            case_index=999,
            input_data=payload.custom_input,
            expected_output="",
            actual_output=c_exec["stdout"],
            passed=c_exec["passed"],
            execution_time_ms=c_exec["runtime_ms"],
            error=c_exec["error"],
        )

    return DSARunCodeResponse(
        status=overall_status,
        results=results,
        custom_result=custom_res,
        compilation_error=comp_error,
    )


@router.post("/problems/{slug}/submit", response_model=DSASubmitResponse)
def submit_dsa_solution(
    slug: str,
    payload: DSASubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submits code for authoritative online judge grading against all test cases (public + hidden).
    Records DSASubmission and updates DSAUserProgress state.
    """
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    # Fetch all test cases ordered
    test_cases = (
        db.query(DSATestCase)
        .filter(DSATestCase.problem_id == problem.id)
        .order_by(DSATestCase.order_index.asc())
        .all()
    )

    tc_dicts = [
        {
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "time_limit_ms": tc.time_limit_ms,
            "is_hidden": tc.is_hidden,
            "order_index": tc.order_index,
        }
        for tc in test_cases
    ]

    eval_result = evaluate_batch(
        language=payload.language,
        code=payload.code,
        test_cases=tc_dicts,
        stop_on_first_failure=False,
    )

    # 1. Record Submission
    submission = DSASubmission(
        user_id=current_user.id,
        problem_id=problem.id,
        language=payload.language,
        code=payload.code,
        verdict=eval_result["verdict"],
        runtime_ms=eval_result["runtime_ms"],
        memory_kb=15420,  # Estimated baseline footprint
        test_cases_passed=eval_result["test_cases_passed"],
        total_test_cases=eval_result["total_test_cases"],
        failed_test_case_index=eval_result["failed_test_case_index"],
        error_message=eval_result["error_message"],
        stdout_sample=eval_result["stdout_sample"],
        hints_viewed=payload.hints_viewed,
    )
    db.add(submission)
    db.flush()

    # 2. Update User Progress
    progress = (
        db.query(DSAUserProgress)
        .filter(DSAUserProgress.user_id == current_user.id, DSAUserProgress.problem_id == problem.id)
        .first()
    )

    is_first_solve = False
    if not progress:
        progress = DSAUserProgress(
            user_id=current_user.id,
            problem_id=problem.id,
            status="SOLVED" if eval_result["verdict"] == "ACCEPTED" else "ATTEMPTED",
            attempts_count=1,
            best_runtime_ms=eval_result["runtime_ms"] if eval_result["verdict"] == "ACCEPTED" else None,
            solved_at=func.now() if eval_result["verdict"] == "ACCEPTED" else None,
        )
        if eval_result["verdict"] == "ACCEPTED":
            is_first_solve = True
        db.add(progress)
    else:
        progress.attempts_count += 1
        if eval_result["verdict"] == "ACCEPTED":
            if progress.status != "SOLVED":
                is_first_solve = True
                progress.status = "SOLVED"
                progress.solved_at = func.now()
            if progress.best_runtime_ms is None or eval_result["runtime_ms"] < progress.best_runtime_ms:
                progress.best_runtime_ms = eval_result["runtime_ms"]
        elif progress.status != "SOLVED":
            progress.status = "ATTEMPTED"

    db.commit()

    accuracy = (
        round((eval_result["test_cases_passed"] / eval_result["total_test_cases"]) * 100.0, 1)
        if eval_result["total_test_cases"] > 0
        else 0.0
    )

    return DSASubmitResponse(
        submission_id=submission.id,
        verdict=eval_result["verdict"],
        runtime_ms=eval_result["runtime_ms"],
        memory_kb=submission.memory_kb,
        test_cases_passed=eval_result["test_cases_passed"],
        total_test_cases=eval_result["total_test_cases"],
        failed_test_case_index=eval_result["failed_test_case_index"],
        error_message=eval_result["error_message"],
        is_first_solve=is_first_solve,
        accuracy_percentage=accuracy,
    )


@router.get("/problems/{slug}/submissions", response_model=List[DSASubmissionHistoryItem])
def get_submission_history(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns past submissions for this problem by the authenticated user."""
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    subs = (
        db.query(DSASubmission)
        .filter(DSASubmission.user_id == current_user.id, DSASubmission.problem_id == problem.id)
        .order_by(desc(DSASubmission.submitted_at))
        .limit(20)
        .all()
    )
    return subs


@router.get("/problems/{slug}/editorial", response_model=DSAEditorialResponse)
def get_dsa_editorial(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns official editorial breakdown, intuition, and complexity proofs."""
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    return DSAEditorialResponse(
        problem_id=problem.id,
        problem_number=problem.problem_number,
        title=problem.title,
        editorial=problem.editorial,
        expected_time_complexity=problem.expected_time_complexity,
        expected_space_complexity=problem.expected_space_complexity,
        reference_solutions=problem.starter_code or {},
    )


# --------------------------------------------------------------------------
# Student Analytics & Topic Mastery
# --------------------------------------------------------------------------

@router.get("/analytics/me", response_model=DSAStudentAnalyticsResponse)
def get_my_dsa_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Computes verified behavioral and outcome metrics for DSA mastery:
    - Solved by difficulty (Easy / Medium / Hard)
    - Acceptance rate and total submissions
    - Topic-wise mastery percentages
    - Intelligent next-problem recommendation
    """
    # 1. Total Problems & User Solved
    all_problems = db.query(DSAProblem).filter(DSAProblem.status == "PUBLISHED").all()
    total_problems = len(all_problems)

    user_progress = (
        db.query(DSAUserProgress)
        .filter(DSAUserProgress.user_id == current_user.id)
        .all()
    )
    progress_map = {p.problem_id: p.status for p in user_progress}

    easy_solved = 0
    medium_solved = 0
    hard_solved = 0
    total_solved = 0

    for p in all_problems:
        if progress_map.get(p.id) == "SOLVED":
            total_solved += 1
            if p.difficulty == "EASY":
                easy_solved += 1
            elif p.difficulty == "MEDIUM":
                medium_solved += 1
            elif p.difficulty == "HARD":
                hard_solved += 1

    # 2. Submissions acceptance rate
    total_subs = (
        db.query(func.count(DSASubmission.id))
        .filter(DSASubmission.user_id == current_user.id)
        .scalar()
        or 0
    )
    acc_subs = (
        db.query(func.count(DSASubmission.id))
        .filter(DSASubmission.user_id == current_user.id, DSASubmission.verdict == "ACCEPTED")
        .scalar()
        or 0
    )
    acc_rate = round((acc_subs / total_subs * 100.0), 1) if total_subs > 0 else 0.0

    # 3. Topic Stats
    topics = db.query(DSATopic).order_by(DSATopic.order_index.asc()).all()
    topic_stats: List[DSATopicStat] = []
    weakest_topic = None
    min_topic_ratio = 1.1

    for t in topics:
        t_probs = [p for p in t.problems if p.status == "PUBLISHED"]
        t_total = len(t_probs)
        t_solved = sum(1 for p in t_probs if progress_map.get(p.id) == "SOLVED")
        ratio = (t_solved / t_total) if t_total > 0 else 1.0

        if t_total > 0 and ratio < min_topic_ratio:
            min_topic_ratio = ratio
            weakest_topic = t

        topic_stats.append(
            DSATopicStat(
                topic_name=t.name,
                topic_slug=t.slug,
                total_problems=t_total,
                solved_problems=t_solved,
                accuracy_percentage=round(ratio * 100.0, 1),
            )
        )

    # 4. Recommendation
    recommended_slug = None
    recommended_title = None
    recommended_reason = None

    if weakest_topic:
        unsolved_in_topic = [
            p for p in weakest_topic.problems
            if p.status == "PUBLISHED" and progress_map.get(p.id) != "SOLVED"
        ]
        if unsolved_in_topic:
            rec_p = unsolved_in_topic[0]
            recommended_slug = rec_p.slug
            recommended_title = rec_p.title
            recommended_reason = f"Build mastery in '{weakest_topic.name}' ({weakest_topic.summary[:60]}...)"

    # Fallback to POTD or first unsolved
    if not recommended_slug:
        for p in all_problems:
            if progress_map.get(p.id) != "SOLVED":
                recommended_slug = p.slug
                recommended_title = p.title
                recommended_reason = "Continue your daily coding consistency streak."
                break

    return DSAStudentAnalyticsResponse(
        total_solved=total_solved,
        easy_solved=easy_solved,
        medium_solved=medium_solved,
        hard_solved=hard_solved,
        total_problems=total_problems,
        total_submissions=total_subs,
        acceptance_rate=acc_rate,
        topic_stats=topic_stats,
        recommended_problem_slug=recommended_slug,
        recommended_problem_title=recommended_title,
        recommended_reason=recommended_reason,
    )


# --------------------------------------------------------------------------
# Authoring / Trainer Ingestion
# --------------------------------------------------------------------------

@router.post("/author/problems", status_code=status.HTTP_201_CREATED)
def author_dsa_problem(
    payload: DSAProblemCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allows trainers or admins to create or import custom DSA problems with test cases."""
    if current_user.role not in ("TRAINER", "ADMIN", "INSTITUTION_ADMIN"):
        raise HTTPException(status_code=403, detail="Only trainers or administrators can author DSA problems.")

    topic = db.query(DSATopic).filter(DSATopic.slug == payload.topic_slug).first()
    if not topic:
        raise HTTPException(status_code=400, detail=f"Topic '{payload.topic_slug}' not found.")

    slug = payload.slug or payload.title.lower().replace(" ", "-").replace("'", "")
    existing = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Problem with slug '{slug}' already exists.")

    max_num = db.query(func.max(DSAProblem.problem_number)).scalar() or 0

    problem = DSAProblem(
        problem_number=max_num + 1,
        slug=slug,
        title=payload.title,
        difficulty=payload.difficulty,
        topic_id=topic.id,
        description=payload.description,
        constraints=payload.constraints,
        input_format=payload.input_format,
        output_format=payload.output_format,
        examples=[ex.model_dump() for ex in payload.examples],
        starter_code=payload.starter_code,
        expected_time_complexity=payload.expected_time_complexity,
        expected_space_complexity=payload.expected_space_complexity,
        hints=payload.hints,
        editorial=payload.editorial,
        sheet_tags=payload.sheet_tags,
        is_problem_of_the_day=payload.is_problem_of_the_day,
        status="PUBLISHED",
        author_id=current_user.id,
    )
    db.add(problem)
    db.flush()

    for idx, tc in enumerate(payload.test_cases, start=1):
        test_case = DSATestCase(
            problem_id=problem.id,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            is_hidden=tc.is_hidden,
            order_index=tc.order_index or idx,
        )
        db.add(test_case)

    db.commit()
    return {"message": "Problem created successfully", "slug": problem.slug, "id": problem.id}
