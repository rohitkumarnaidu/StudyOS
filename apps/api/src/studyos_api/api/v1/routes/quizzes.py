"""Quiz API endpoints — session management, answers, results, mistakes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.quiz_service import QuizService

router = APIRouter()


def get_quiz_service() -> QuizService:
    return QuizService()


@router.post("")
@limiter.limit("10/minute")
async def create_quiz_session(
    request: Request,
    body: dict[str, Any],
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Create a new quiz session."""
    session = quiz_svc.create_session(
        profile_id=current_user["sub"],
        question_count=body.get("question_count", 10),
        quiz_type=body.get("quiz_type", "practice"),
        chapter_id=body.get("chapter_id"),
        topic_ids=body.get("topic_ids"),
        time_limit_minutes=body.get("time_limit_minutes"),
        difficulty=body.get("difficulty"),
    )
    return {
        "data": session.to_dict(),
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{session_id}/questions")
@limiter.limit("60/minute")
async def get_quiz_questions(
    request: Request,
    session_id: str,
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get questions for a quiz session."""
    questions = quiz_svc.get_questions(session_id, current_user["sub"])
    if questions is None:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    return {
        "data": questions,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/{session_id}/answers")
@limiter.limit("60/minute")
async def submit_answer(
    request: Request,
    session_id: str,
    body: dict[str, Any],
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Submit an answer for a question."""
    result = quiz_svc.submit_answer(
        session_id=session_id,
        profile_id=current_user["sub"],
        question_id=body.get("question_id", ""),
        answer=body.get("answer", ""),
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz session not found or already completed")
    return {
        "data": result,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/{session_id}/finish")
@limiter.limit("30/minute")
async def finish_quiz_session(
    request: Request,
    session_id: str,
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Finish a quiz session and get the result."""
    result = quiz_svc.finish_session(session_id, current_user["sub"])
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    return {
        "data": result,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{session_id}/result")
@limiter.limit("60/minute")
async def get_quiz_result(
    request: Request,
    session_id: str,
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get the result of a finished quiz session."""
    result = quiz_svc.get_result(session_id, current_user["sub"])
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz session not found or not yet completed")
    return {
        "data": result,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/sessions")
@limiter.limit("60/minute")
async def list_quiz_sessions(
    request: Request,
    chapter_id: str | None = Query(None),
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List all quiz sessions for the current user."""
    sessions = quiz_svc.list_sessions(current_user["sub"], chapter_id)
    return {
        "data": sessions,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/mistakes")
@limiter.limit("60/minute")
async def list_mistakes(
    request: Request,
    chapter_id: str | None = Query(None),
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List all mistakes for the current user."""
    mistakes = quiz_svc.list_mistakes(current_user["sub"], chapter_id)
    return {
        "data": mistakes,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/mistakes/{mistake_id}/review")
@limiter.limit("30/minute")
async def review_mistake(
    request: Request,
    mistake_id: str,
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Mark a mistake as reviewed."""
    success = quiz_svc.review_mistake(mistake_id, current_user["sub"])
    if not success:
        raise HTTPException(status_code=404, detail="Mistake not found")
    return {
        "data": {"reviewed": True},
        "meta": response_meta(request, api_version="v1"),
    }


@router.delete("/mistakes/{mistake_id}")
@limiter.limit("30/minute")
async def delete_mistake(
    request: Request,
    mistake_id: str,
    quiz_svc: Annotated[QuizService, Depends(get_quiz_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Delete a mistake entry."""
    success = quiz_svc.delete_mistake(mistake_id, current_user["sub"])
    if not success:
        raise HTTPException(status_code=404, detail="Mistake not found")
    return {
        "data": {"deleted": True},
        "meta": response_meta(request, api_version="v1"),
    }
