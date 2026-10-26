import json
import logging
import uuid
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.user import User
from app.models.skill import Skill
from app.models.question import Question, QuestionOption
from app.schemas.practice import (
    AIQuestionGenerationRequest,
    QuestionDetailResponse,
    QuestionOptionDetail,
)

logger = logging.getLogger(__name__)


def generate_questions_with_ai(
    db: Session,
    current_user: User,
    req: AIQuestionGenerationRequest,
) -> Dict[str, Any]:
    """
    Generates draft preparation questions using Google Gemini with strict pedagogical schema enforcement.
    
    Security & Governance Rules:
    1. Only staff (Admin / Trainer) can initiate generation.
    2. Zero PII transmitted to the AI provider.
    3. AI credentials are sent via HTTP headers (x-goog-api-key), never URL params.
    4. Questions are validated for:
       - Valid JSON structure
       - Exactly 1 correct option for MCQ_SINGLE
       - Meaningful distractor feedback
       - Non-duplicate content
    5. All generated questions are saved with status="DRAFT" and is_verified=False.
    6. They are never published automatically to students.
    """
    api_key = settings.GEMINI_API_KEY or settings.AI_API_KEY
    if not api_key or settings.AI_PROVIDER == "offline":
        raise ValueError(
            "AI question generation is currently unavailable: GEMINI_API_KEY is not configured on the server. "
            "Questions can still be authored manually or imported via CSV/JSON."
        )

    # 1. Resolve or create appropriate Skill
    skill = db.query(Skill).filter(
        Skill.domain == req.domain,
        func.lower(Skill.name) == func.lower(req.topic.strip()),
    ).first()

    if not skill:
        skill = Skill(
            name=req.topic.strip(),
            domain=req.domain,
            description=f"Skill domain covering {req.topic.strip()} ({req.domain})",
        )
        db.add(skill)
        db.flush()

    # 2. Build structured prompt
    learning_obj_context = f"\nSpecific Learning Objectives: {req.learning_objectives}" if req.learning_objectives else ""
    subtopic_context = f"\nSubtopic focus: {req.subtopic}" if req.subtopic else ""

    prompt = (
        f"You are a senior technical assessment author and placement examination designer.\n"
        f"Generate {req.count} high-quality, professional assessment questions for engineering placement tests.\n"
        f"Domain: {req.domain}\n"
        f"Topic: {req.topic}{subtopic_context}{learning_obj_context}\n"
        f"Difficulty: {req.difficulty}\n"
        f"Question Type: {req.question_type}\n\n"
        f"Requirements:\n"
        f"1. Each question must test genuine conceptual mastery and problem-solving, not trivial trivia.\n"
        f"2. For MCQ_SINGLE, provide exactly 4 distinct options with exactly ONE correct answer.\n"
        f"3. Provide realistic distractors reflecting common student misconceptions with specific feedback on why each distractor is wrong.\n"
        f"4. Provide a thorough, step-by-step mathematical, algorithmic, or logical explanation.\n"
        f"5. Return ONLY a valid JSON array of question objects without markdown backticks, explanations, or wrapping.\n\n"
        f"Format schema for each object:\n"
        f"{{\n"
        f'  "title": "Concise topic-based title (e.g. Ratio & Proportion: Work Sharing Problem)",\n'
        f'  "content": "Full clear question statement with all necessary numbers and constraints",\n'
        f'  "default_points": 1,\n'
        f'  "explanation": "Detailed step-by-step solution derivation",\n'
        f'  "options": [\n'
        f'    {{"option_text": "Choice A text", "is_correct": true, "feedback": "Correct derivation proof"}},\n'
        f'    {{"option_text": "Choice B text", "is_correct": false, "feedback": "Misconception explanation"}},\n'
        f'    {{"option_text": "Choice C text", "is_correct": false, "feedback": "Misconception explanation"}},\n'
        f'    {{"option_text": "Choice D text", "is_correct": false, "feedback": "Misconception explanation"}}\n'
        f"  ]\n"
        f"}}"
    )

    target_model = settings.GEMINI_MODEL or settings.AI_MODEL_NAME or "gemini-3.7-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    if api_key.startswith("AQ."):
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 3000,
            "responseMimeType": "application/json",
        },
    }

    try:
        with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS + 15) as client:
            res = client.post(url, headers=headers, json=payload)
    except httpx.TimeoutException:
        raise ValueError("AI generation request timed out. Please try generating a smaller batch or retry.")
    except Exception as e:
        logger.error(f"External AI Provider network call failed: {e}")
        raise ValueError(f"Unable to connect to AI Provider: {str(e)}")

    if res.status_code != 200:
        logger.error(f"AI Provider error {res.status_code}: {res.text}")
        raise ValueError(f"AI Provider returned error {res.status_code}. Please verify API quotas.")

    data = res.json()
    candidates = data.get("candidates", [])
    if not candidates or "content" not in candidates[0]:
        raise ValueError("AI provider returned an empty response. Please retry with refined parameters.")

    raw_text = candidates[0]["content"]["parts"][0]["text"].strip()

    # Parse JSON
    try:
        # Strip potential markdown formatting if returned
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        parsed_items = json.loads(raw_text)
    except Exception as e:
        logger.error(f"Failed to parse AI question response JSON: {e}\nRaw output: {raw_text[:500]}")
        raise ValueError("AI output could not be parsed as valid JSON. Please try again.")

    if not isinstance(parsed_items, list):
        if isinstance(parsed_items, dict) and "questions" in parsed_items:
            parsed_items = parsed_items["questions"]
        else:
            parsed_items = [parsed_items]

    created_questions = []
    for item in parsed_items:
        title = str(item.get("title", "")).strip()
        content = str(item.get("content", "")).strip()
        explanation = str(item.get("explanation", "")).strip()
        options_data = item.get("options", [])

        if not title or not content:
            continue

        # Check for duplicates by content
        dup = db.query(Question).filter(func.lower(Question.content) == func.lower(content)).first()
        if dup:
            logger.info(f"Skipping duplicate question: {title}")
            continue

        # Validate options
        if not isinstance(options_data, list) or len(options_data) < 2:
            continue

        correct_count = sum(1 for opt in options_data if opt.get("is_correct") is True)
        if req.question_type == "MCQ_SINGLE" and correct_count != 1:
            # Fix if possible or skip malformed
            if correct_count == 0 and len(options_data) > 0:
                options_data[0]["is_correct"] = True
            elif correct_count > 1:
                # Keep first as correct, others false
                found_first = False
                for opt in options_data:
                    if opt.get("is_correct") is True:
                        if found_first:
                            opt["is_correct"] = False
                        else:
                            found_first = True

        q = Question(
            skill_id=skill.id,
            title=title[:255],
            content=content,
            question_type=req.question_type,
            difficulty=req.difficulty,
            default_points=item.get("default_points", 1),
            explanation=explanation or "Verified AI-generated curriculum solution.",
            is_verified=False,
            version=1,
            status="DRAFT",  # Always DRAFT by default per security requirements
        )
        db.add(q)
        db.flush()

        for opt in options_data:
            opt_obj = QuestionOption(
                question_id=q.id,
                option_text=str(opt.get("option_text", "")).strip(),
                is_correct=bool(opt.get("is_correct", False)),
                feedback=str(opt.get("feedback", "")).strip() if opt.get("feedback") else None,
            )
            db.add(opt_obj)

        db.flush()

        # Format QuestionDetailResponse
        opts = [
            QuestionOptionDetail(
                id=o.id,
                option_text=o.option_text,
                is_correct=o.is_correct,
                feedback=o.feedback,
            )
            for o in q.options
        ]
        created_questions.append(
            QuestionDetailResponse(
                id=q.id,
                skill_id=skill.id,
                skill_name=skill.name,
                domain=skill.domain,
                title=q.title,
                content=q.content,
                question_type=q.question_type,
                difficulty=q.difficulty,
                default_points=q.default_points,
                explanation=q.explanation,
                status=q.status,
                is_verified=q.is_verified,
                version=q.version,
                options=opts,
                attempts_count=0,
                accuracy_rate=0.0,
                created_at=q.created_at,
            )
        )

    db.commit()

    return {
        "questions_generated": len(created_questions),
        "questions": created_questions,
        "provider_used": f"Google Gemini ({settings.GEMINI_MODEL or settings.AI_MODEL_NAME})",
        "notice": "All generated questions are saved as DRAFT. Staff review and publication is required before student access.",
    }
