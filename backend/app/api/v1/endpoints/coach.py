from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.coach import (
    MistakeExplanationRequest,
    MistakeExplanationResponse,
    StudyPlanRequest,
    StudyPlanResponse,
)
from app.services.coach import explain_student_mistake, generate_targeted_study_plan

router = APIRouter()


@router.post("/explain-mistake", response_model=MistakeExplanationResponse)
def get_mistake_explanation(
    req: MistakeExplanationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns a grounded conceptual explanation for an incorrect answer attempt.
    Sends only minimal authorized context with zero student PII.
    Falls back gracefully to offline pedagogical mentor if external AI is unconfigured or fails.
    """
    try:
        explanation = explain_student_mistake(db=db, user=current_user, req=req)
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Coach service encounter: {str(e)}",
        )


@router.post("/generate-plan", response_model=StudyPlanResponse)
def get_targeted_study_plan(
    req: StudyPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a personalized, evidence-grounded study plan based on student's verified
    attempt records and targeted job role requirements.
    """
    try:
        plan = generate_targeted_study_plan(db=db, user=current_user, req=req)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Study plan generation encounter: {str(e)}",
        )
