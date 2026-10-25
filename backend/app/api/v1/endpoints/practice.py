import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.question import Question, QuestionOption
from app.models.practice import PracticeSession, AttemptRecord, MistakeNotebookEntry, PreparationActivity
from app.models.skill import Skill
from app.schemas.practice import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentListItem,
    AssessmentDetailResponse,
    LinkQuestionsRequest,
    QuestionCreate,
    StartSessionRequest,
    ActiveSessionResponse,
    CandidateQuestionResponse,
    OptionCandidateResponse,
    SaveAnswerRequest,
    SubmitSessionResponse,
    SessionReviewResponse,
    ReviewQuestionResponse,
    OptionReviewResponse,
    MistakeEntryResponse,
    UpdateMistakeStatusRequest,
)

router = APIRouter()


# --------------------------------------------------------------------------
# Assessment Authoring & Listing
# --------------------------------------------------------------------------

@router.get("/assessments", response_model=List[AssessmentListItem])
def list_assessments(
    category: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists available assessments filtered by category and publication state."""
    query = db.query(Assessment)

    # Students only see published assessments for their institution or system-wide
    if current_user.role == "STUDENT":
        query = query.filter(Assessment.is_published == True)
        query = query.filter(
            (Assessment.institution_id == current_user.institution_id) |
            (Assessment.institution_id == None)
        )
    else:
        # Staff can filter by publication status
        if is_published is not None:
            query = query.filter(Assessment.is_published == is_published)
        query = query.filter(Assessment.institution_id == current_user.institution_id)

    if category:
        query = query.filter(Assessment.category == category)

    assessments = query.order_by(desc(Assessment.created_at)).all()

    items = []
    for a in assessments:
        q_count = db.query(func.count(AssessmentQuestion.id)).filter(AssessmentQuestion.assessment_id == a.id).scalar() or 0
        total_pts = db.query(func.sum(AssessmentQuestion.points)).filter(AssessmentQuestion.assessment_id == a.id).scalar() or 0
        items.append(
            AssessmentListItem(
                id=a.id,
                institution_id=a.institution_id,
                title=a.title,
                description=a.description,
                category=a.category,
                duration_minutes=a.duration_minutes,
                passing_score=a.passing_score,
                version=a.version,
                is_published=a.is_published,
                question_count=q_count,
                total_points=int(total_pts),
                created_at=a.created_at,
            )
        )
    return items


@router.get("/assessments/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment_details(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves assessment summary and instructions without revealing questions or answers."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if current_user.role == "STUDENT" and not assessment.is_published:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assessment is not published")

    q_count = db.query(func.count(AssessmentQuestion.id)).filter(AssessmentQuestion.assessment_id == assessment.id).scalar() or 0
    total_pts = db.query(func.sum(AssessmentQuestion.points)).filter(AssessmentQuestion.assessment_id == assessment.id).scalar() or 0

    return AssessmentDetailResponse(
        id=assessment.id,
        institution_id=assessment.institution_id,
        title=assessment.title,
        description=assessment.description,
        instructions=assessment.instructions,
        category=assessment.category,
        duration_minutes=assessment.duration_minutes,
        passing_score=assessment.passing_score,
        version=assessment.version,
        is_published=assessment.is_published,
        question_count=q_count,
        total_points=int(total_pts),
        created_at=assessment.created_at,
    )


@router.post("/assessments", response_model=AssessmentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Authorised endpoint (Admin/Trainer) to create a new assessment draft."""
    if current_user.role not in ["ADMIN", "TRAINER", "PLACEMENT_OFFICER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can create assessments")

    assessment = Assessment(
        institution_id=current_user.institution_id,
        title=payload.title,
        description=payload.description,
        instructions=payload.instructions,
        category=payload.category,
        duration_minutes=payload.duration_minutes,
        passing_score=payload.passing_score,
        is_published=payload.is_published,
        version=1,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentDetailResponse(
        id=assessment.id,
        institution_id=assessment.institution_id,
        title=assessment.title,
        description=assessment.description,
        instructions=assessment.instructions,
        category=assessment.category,
        duration_minutes=assessment.duration_minutes,
        passing_score=assessment.passing_score,
        version=assessment.version,
        is_published=assessment.is_published,
        question_count=0,
        total_points=0,
        created_at=assessment.created_at,
    )


@router.post("/assessments/{assessment_id}/publish")
def toggle_publish_assessment(
    assessment_id: uuid.UUID,
    publish: bool = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publishes or unpublishes an assessment draft."""
    if current_user.role not in ["ADMIN", "TRAINER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can publish assessments")

    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    assessment.is_published = publish
    db.commit()
    return {"message": f"Assessment {'published' if publish else 'unpublished'} successfully"}


@router.post("/assessments/{assessment_id}/link-questions")
def link_questions_to_assessment(
    assessment_id: uuid.UUID,
    payload: LinkQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Links questions into an assessment and increments assessment version."""
    if current_user.role not in ["ADMIN", "TRAINER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can configure assessment questions")

    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    current_count = db.query(func.count(AssessmentQuestion.id)).filter(AssessmentQuestion.assessment_id == assessment_id).scalar() or 0

    added = 0
    for idx, qid in enumerate(payload.question_ids):
        # Verify question exists
        q = db.query(Question).filter(Question.id == qid).first()
        if not q:
            continue
        # Avoid duplicate link
        existing = db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_id,
            AssessmentQuestion.question_id == qid
        ).first()
        if not existing:
            link = AssessmentQuestion(
                assessment_id=assessment_id,
                question_id=qid,
                order_index=current_count + idx + 1,
                points=payload.points_per_question,
            )
            db.add(link)
            added += 1

    assessment.version += 1
    db.commit()
    return {"message": f"Successfully linked {added} questions to assessment", "version": assessment.version}


# --------------------------------------------------------------------------
# Practice Session Lifecycle (Student Interactive Practice)
# --------------------------------------------------------------------------

@router.post("/sessions", response_model=ActiveSessionResponse, status_code=status.HTTP_201_CREATED)
def start_practice_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Initialises an interactive practice or timed mock session for a student.
    Crucial Security Rule: Correct answers, option correctness, and explanations are explicitly omitted.
    """
    assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    if not assessment.is_published and current_user.role == "STUDENT":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assessment is not published")

    # Fetch assessment questions in order
    links = (
        db.query(AssessmentQuestion, Question)
        .join(Question, AssessmentQuestion.question_id == Question.id)
        .filter(AssessmentQuestion.assessment_id == assessment.id)
        .order_by(AssessmentQuestion.order_index)
        .all()
    )

    if not links:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment has no questions configured")

    # Create session
    session = PracticeSession(
        user_id=current_user.id,
        assessment_id=assessment.id,
        session_type=payload.session_type,
        status="IN_PROGRESS",
        assessment_version=assessment.version,
        time_spent_seconds=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Format questions safely for the candidate
    candidate_questions = []
    for link, q in links:
        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.id)
            .all()
        )
        safe_options = [
            OptionCandidateResponse(id=opt.id, option_text=opt.option_text)
            for opt in options
        ]
        candidate_questions.append(
            CandidateQuestionResponse(
                id=q.id,
                title=q.title,
                content=q.content,
                question_type=q.question_type,
                difficulty=q.difficulty,
                points=link.points,
                order_index=link.order_index,
                options=safe_options,
                saved_answer=None,
            )
        )

    return ActiveSessionResponse(
        session_id=session.id,
        assessment_id=assessment.id,
        assessment_title=assessment.title,
        assessment_category=assessment.category,
        session_type=session.session_type,
        status=session.status,
        duration_minutes=assessment.duration_minutes,
        time_spent_seconds=session.time_spent_seconds,
        started_at=session.started_at,
        questions=candidate_questions,
    )


@router.get("/sessions/{session_id}", response_model=ActiveSessionResponse)
def get_active_session_state(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recovers the active session state and saved answers for uninterrupted student flow."""
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.user_id != current_user.id and current_user.role not in ["ADMIN", "TRAINER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    assessment = session.assessment
    links = (
        db.query(AssessmentQuestion, Question)
        .join(Question, AssessmentQuestion.question_id == Question.id)
        .filter(AssessmentQuestion.assessment_id == assessment.id)
        .order_by(AssessmentQuestion.order_index)
        .all()
    )

    # Fetch already saved attempt records for this session
    attempts = db.query(AttemptRecord).filter(AttemptRecord.session_id == session.id).all()
    attempt_map = {att.question_id: att.submitted_answer for att in attempts}

    candidate_questions = []
    for link, q in links:
        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.id)
            .all()
        )
        safe_options = [
            OptionCandidateResponse(id=opt.id, option_text=opt.option_text)
            for opt in options
        ]
        candidate_questions.append(
            CandidateQuestionResponse(
                id=q.id,
                title=q.title,
                content=q.content,
                question_type=q.question_type,
                difficulty=q.difficulty,
                points=link.points,
                order_index=link.order_index,
                options=safe_options,
                saved_answer=attempt_map.get(q.id),
            )
        )

    return ActiveSessionResponse(
        session_id=session.id,
        assessment_id=assessment.id,
        assessment_title=assessment.title,
        assessment_category=assessment.category,
        session_type=session.session_type,
        status=session.status,
        duration_minutes=assessment.duration_minutes,
        time_spent_seconds=session.time_spent_seconds,
        started_at=session.started_at,
        questions=candidate_questions,
    )


@router.post("/sessions/{session_id}/save-answer")
def save_session_answer(
    session_id: uuid.UUID,
    payload: SaveAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upserts a candidate's answer for a question.
    Guarantees no duplicate attempt records per session and question.
    """
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session.status != "IN_PROGRESS":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session has already been submitted or completed")

    attempt = db.query(AttemptRecord).filter(
        AttemptRecord.session_id == session.id,
        AttemptRecord.question_id == payload.question_id
    ).first()

    if attempt:
        attempt.submitted_answer = payload.submitted_answer
        attempt.time_spent_ms += payload.time_spent_ms
        attempt.submitted_at = datetime.now(timezone.utc)
    else:
        attempt = AttemptRecord(
            session_id=session.id,
            user_id=current_user.id,
            question_id=payload.question_id,
            submitted_answer=payload.submitted_answer,
            is_correct=False,  # Evaluated upon submission
            score_awarded=Decimal("0.00"),
            time_spent_ms=payload.time_spent_ms,
        )
        db.add(attempt)

    # Accumulate active duration
    session.time_spent_seconds += max(0, payload.time_spent_ms // 1000)
    db.commit()
    return {"status": "saved", "question_id": payload.question_id}


@router.post("/sessions/{session_id}/submit", response_model=SubmitSessionResponse)
def submit_practice_session(
    session_id: uuid.UUID,
    time_spent_seconds: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Grades the session deterministically using the approved Formative Mastery pattern:
    - +1.0 (or full question points) for correct answers
    - 0 penalty for incorrect or unanswered questions
    - Automatically syncs incorrect responses into student's Mistake Notebook
    - Automatically registers a PreparationActivity record
    """
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session.status == "SUBMITTED":
        # Safe retry: return already graded summary
        max_s = session.max_score or Decimal("1.00")
        tot_s = session.total_score or Decimal("0.00")
        pct = float((tot_s / max_s) * 100) if max_s > 0 else 0.0
        q_count = db.query(func.count(AssessmentQuestion.id)).filter(AssessmentQuestion.assessment_id == session.assessment_id).scalar() or 0
        corr_count = db.query(func.count(AttemptRecord.id)).filter(
            AttemptRecord.session_id == session.id, AttemptRecord.is_correct == True
        ).scalar() or 0
        incorr_count = db.query(func.count(AttemptRecord.id)).filter(
            AttemptRecord.session_id == session.id, AttemptRecord.is_correct == False, AttemptRecord.submitted_answer != None
        ).scalar() or 0

        return SubmitSessionResponse(
            session_id=session.id,
            status=session.status,
            total_score=tot_s,
            max_score=max_s,
            percentage=round(pct, 1),
            is_passed=tot_s >= (session.assessment.passing_score or Decimal("0.00")),
            questions_count=q_count,
            correct_count=corr_count,
            incorrect_count=incorr_count,
            unanswered_count=q_count - (corr_count + incorr_count),
            time_spent_seconds=session.time_spent_seconds,
            completed_at=session.completed_at or datetime.now(timezone.utc),
        )

    # Fetch assessment questions
    assessment = session.assessment
    links = (
        db.query(AssessmentQuestion, Question)
        .join(Question, AssessmentQuestion.question_id == Question.id)
        .filter(AssessmentQuestion.assessment_id == assessment.id)
        .all()
    )

    total_possible_score = sum(Decimal(str(link.points)) for link, _ in links)
    awarded_score = Decimal("0.00")
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    now = datetime.now(timezone.utc)
    if time_spent_seconds is not None and time_spent_seconds > 0:
        session.time_spent_seconds = time_spent_seconds

    for link, q in links:
        attempt = db.query(AttemptRecord).filter(
            AttemptRecord.session_id == session.id,
            AttemptRecord.question_id == q.id
        ).first()

        # If question was not attempted
        if not attempt or not attempt.submitted_answer:
            unanswered_count += 1
            if not attempt:
                attempt = AttemptRecord(
                    session_id=session.id,
                    user_id=current_user.id,
                    question_id=q.id,
                    submitted_answer=None,
                    is_correct=False,
                    score_awarded=Decimal("0.00"),
                    time_spent_ms=0,
                )
                db.add(attempt)
                db.flush()
            continue

        # Evaluate answer
        is_correct = False
        if q.question_type == "MCQ_SINGLE":
            # Compare submitted option id with the correct option id
            correct_opt = db.query(QuestionOption).filter(
                QuestionOption.question_id == q.id,
                QuestionOption.is_correct == True
            ).first()
            if correct_opt and str(correct_opt.id) == attempt.submitted_answer.strip():
                is_correct = True

        elif q.question_type == "NUMERICAL":
            # Direct normalized string match or explanation key
            correct_opt = db.query(QuestionOption).filter(
                QuestionOption.question_id == q.id,
                QuestionOption.is_correct == True
            ).first()
            if correct_opt and correct_opt.option_text.strip().lower() == attempt.submitted_answer.strip().lower():
                is_correct = True
        else:
            # Multi/Subjective: check if matches correct option text or id
            correct_opts = db.query(QuestionOption).filter(
                QuestionOption.question_id == q.id,
                QuestionOption.is_correct == True
            ).all()
            correct_ids = {str(o.id) for o in correct_opts}
            submitted_ids = {s.strip() for s in attempt.submitted_answer.split(",") if s.strip()}
            if correct_ids and correct_ids == submitted_ids:
                is_correct = True

        attempt.is_correct = is_correct
        if is_correct:
            attempt.score_awarded = Decimal(str(link.points))
            awarded_score += attempt.score_awarded
            correct_count += 1
        else:
            attempt.score_awarded = Decimal("0.00")
            incorrect_count += 1

            # Auto-sync to Mistake Notebook
            existing_mistake = db.query(MistakeNotebookEntry).filter(
                MistakeNotebookEntry.user_id == current_user.id,
                MistakeNotebookEntry.question_id == q.id
            ).first()
            if not existing_mistake:
                mistake = MistakeNotebookEntry(
                    user_id=current_user.id,
                    attempt_id=attempt.id,
                    question_id=q.id,
                    error_tag="PRACTICE_INCORRECT",
                    mastery_status="UNRESOLVED",
                    student_notes=f"Attempted '{attempt.submitted_answer}' during {assessment.title}",
                )
                db.add(mistake)

    session.status = "SUBMITTED"
    session.completed_at = now
    session.total_score = awarded_score
    session.max_score = total_possible_score

    # Auto-record authentic PreparationActivity
    duration_mins = max(1, session.time_spent_seconds // 60)
    activity = PreparationActivity(
        user_id=current_user.id,
        activity_type="MOCK_TEST" if session.session_type == "TIMED_MOCK" else "PRACTICE_SESSION",
        category=assessment.category or "GENERAL",
        topic=assessment.title,
        duration_minutes=duration_mins,
        completion_state="COMPLETED",
        provenance="SYSTEM_EVALUATED",
        notes=f"Scored {awarded_score}/{total_possible_score} points ({float((awarded_score / total_possible_score) * 100) if total_possible_score > 0 else 0.0:.1f}%)",
        activity_date=now,
    )
    db.add(activity)

    db.commit()

    pct = float((awarded_score / total_possible_score) * 100) if total_possible_score > 0 else 0.0
    return SubmitSessionResponse(
        session_id=session.id,
        status=session.status,
        total_score=awarded_score,
        max_score=total_possible_score,
        percentage=round(pct, 1),
        is_passed=awarded_score >= (assessment.passing_score or Decimal("0.00")),
        questions_count=len(links),
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unanswered_count=unanswered_count,
        time_spent_seconds=session.time_spent_seconds,
        completed_at=session.completed_at,
    )


@router.get("/sessions/{session_id}/review", response_model=SessionReviewResponse)
def get_session_review(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Post-submission review: provides detailed step-by-step proofs,
    explanations, distractor feedback, and student's submitted response.
    Accessible ONLY after the session is SUBMITTED or TIMED_OUT.
    """
    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.user_id != current_user.id and current_user.role not in ["ADMIN", "TRAINER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if session.status == "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session is still in progress. Submit the session to review answers.",
        )

    assessment = session.assessment
    links = (
        db.query(AssessmentQuestion, Question)
        .join(Question, AssessmentQuestion.question_id == Question.id)
        .filter(AssessmentQuestion.assessment_id == assessment.id)
        .order_by(AssessmentQuestion.order_index)
        .all()
    )

    review_questions = []
    for link, q in links:
        attempt = db.query(AttemptRecord).filter(
            AttemptRecord.session_id == session.id,
            AttemptRecord.question_id == q.id
        ).first()

        options = (
            db.query(QuestionOption)
            .filter(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.id)
            .all()
        )
        review_options = [
            OptionReviewResponse(
                id=opt.id,
                option_text=opt.option_text,
                is_correct=opt.is_correct,
                feedback=opt.feedback,
            )
            for opt in options
        ]

        review_questions.append(
            ReviewQuestionResponse(
                id=q.id,
                title=q.title,
                content=q.content,
                question_type=q.question_type,
                difficulty=q.difficulty,
                points=link.points,
                order_index=link.order_index,
                explanation=q.explanation,
                options=review_options,
                submitted_answer=attempt.submitted_answer if attempt else None,
                is_correct=attempt.is_correct if attempt else False,
                score_awarded=attempt.score_awarded if attempt else Decimal("0.00"),
                time_spent_ms=attempt.time_spent_ms if attempt else 0,
            )
        )

    tot_s = session.total_score or Decimal("0.00")
    max_s = session.max_score or Decimal("1.00")
    pct = float((tot_s / max_s) * 100) if max_s > 0 else 0.0

    return SessionReviewResponse(
        session_id=session.id,
        assessment_title=assessment.title,
        assessment_category=assessment.category,
        status=session.status,
        total_score=tot_s,
        max_score=max_s,
        percentage=round(pct, 1),
        time_spent_seconds=session.time_spent_seconds,
        started_at=session.started_at,
        completed_at=session.completed_at,
        questions=review_questions,
    )


# --------------------------------------------------------------------------
# Student Mistake Notebook
# --------------------------------------------------------------------------

@router.get("/mistakes", response_model=List[MistakeEntryResponse])
def get_student_mistakes(
    mastery_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves mistakes logged during student practice for targeted review."""
    query = db.query(MistakeNotebookEntry, Question).join(
        Question, MistakeNotebookEntry.question_id == Question.id
    ).filter(MistakeNotebookEntry.user_id == current_user.id)

    if mastery_status:
        query = query.filter(MistakeNotebookEntry.mastery_status == mastery_status)

    entries = query.order_by(desc(MistakeNotebookEntry.created_at)).all()

    results = []
    for m, q in entries:
        results.append(
            MistakeEntryResponse(
                id=m.id,
                question_id=q.id,
                question_title=q.title,
                question_content=q.content,
                question_type=q.question_type,
                skill_domain=q.skill.domain if q.skill else None,
                student_notes=m.student_notes,
                error_tag=m.error_tag,
                mastery_status=m.mastery_status,
                created_at=m.created_at,
                resolved_at=m.resolved_at,
            )
        )
    return results


@router.put("/mistakes/{mistake_id}")
def update_mistake_entry(
    mistake_id: uuid.UUID,
    payload: UpdateMistakeStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates the status or notes for an error logged in the notebook."""
    entry = db.query(MistakeNotebookEntry).filter(
        MistakeNotebookEntry.id == mistake_id,
        MistakeNotebookEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake entry not found")

    entry.mastery_status = payload.mastery_status
    if payload.student_notes is not None:
        entry.student_notes = payload.student_notes
    if payload.error_tag is not None:
        entry.error_tag = payload.error_tag
    if payload.mastery_status == "MASTERED" and not entry.resolved_at:
        entry.resolved_at = datetime.now(timezone.utc)

    db.commit()
    return {"message": "Mistake notebook entry updated successfully", "mastery_status": entry.mastery_status}
