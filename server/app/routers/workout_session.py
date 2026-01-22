from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.models.workout_session import SessionStatus
from app.utils.auth import get_current_user
from app.schemas.workout_session import (
    CreateWorkoutSessionPayload,
    CompleteSessionSetPayload,
    WorkoutSessionResponse,
    AllWorkoutSessionsResponse,
    WorkoutSessionResponseWithMsg,
    SessionSetResponseWithMsg,
)
from app.services.workout_session_service import WorkoutSessionService
from app.utils.formatter import format_response
from fastapi_throttle import RateLimiter
import os


router = APIRouter(prefix="/sessions", tags=["workout_sessions"])
if os.getenv("TESTING"):
    router.dependencies = []
else:
    limiter = RateLimiter(times=120, seconds=60)
    router.dependencies = [Depends(limiter)]


@router.post("", response_model=WorkoutSessionResponseWithMsg, status_code=201)
def start_workout_session(
    data: CreateWorkoutSessionPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new workout session based on a workout template."""
    session = WorkoutSessionService.start_session(data, current_user, db)
    return format_response(session, "Successfully started workout session")


@router.get("", response_model=AllWorkoutSessionsResponse, status_code=200)
def get_user_sessions(
    status: SessionStatus = Query(None, description="Filter by session status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all workout sessions for the current user."""
    sessions = WorkoutSessionService.get_user_sessions(current_user, db, status)
    return format_response(sessions)


@router.get("/{session_id}", response_model=WorkoutSessionResponse, status_code=200)
def get_session_by_id(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific workout session with all exercises and sets."""
    session = WorkoutSessionService.get_session_by_id(session_id, current_user, db)
    return format_response(session)


@router.put(
    "/{session_id}/set/{set_id}",
    response_model=SessionSetResponseWithMsg,
    status_code=200,
)
def complete_set(
    session_id: int,
    set_id: int,
    data: CompleteSessionSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record completion of a set with actual reps and weight performed."""
    completed_set = WorkoutSessionService.complete_set(
        session_id, set_id, data, current_user, db
    )
    return format_response(completed_set, f"Successfully completed set {set_id}")


@router.post(
    "/{session_id}/complete",
    response_model=WorkoutSessionResponseWithMsg,
    status_code=200,
)
def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a workout session as completed."""
    session = WorkoutSessionService.complete_session(session_id, current_user, db)
    return format_response(
        session, f"Successfully completed workout session {session_id}"
    )


@router.post(
    "/{session_id}/cancel",
    response_model=WorkoutSessionResponseWithMsg,
    status_code=200,
)
def cancel_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a workout session."""
    session = WorkoutSessionService.cancel_session(session_id, current_user, db)
    return format_response(
        session, f"Successfully cancelled workout session {session_id}"
    )
