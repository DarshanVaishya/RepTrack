from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.models.personal_record import PRType
from app.utils.auth import get_current_user
from app.schemas.personal_record import (
    PersonalRecordResponse,
    AllPersonalRecordsResponse,
    PersonalRecordsByExerciseResponse,
    PRSummaryResponse,
    PersonalRecordsByExercise,
    PersonalRecordSchema,
    PRSummary,
)
from app.services.personal_record_service import PersonalRecordService
from app.utils.formatter import format_response
from fastapi_throttle import RateLimiter
import os


router = APIRouter(prefix="/prs", tags=["personal_records"])
if os.getenv("TESTING"):
    router.dependencies = []
else:
    limiter = RateLimiter(times=120, seconds=60)
    router.dependencies = [Depends(limiter)]


@router.get("", response_model=AllPersonalRecordsResponse, status_code=200)
def get_personal_records(
    exercise_id: Optional[int] = Query(None, description="Filter by exercise ID"),
    pr_type: Optional[PRType] = Query(None, description="Filter by PR type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all personal records for the current user.

    Optional filters:
    - exercise_id: Get PRs for a specific exercise
    - pr_type: Get PRs of a specific type (max_volume, max_single_set, etc.)
    """
    prs = PersonalRecordService.get_user_prs(
        user_id=current_user.id, exercise_id=exercise_id, pr_type=pr_type, db=db
    )

    pr_schemas = []
    for pr in prs:
        pr_dict = {
            "id": pr.id,
            "user_id": pr.user_id,
            "exercise_id": pr.exercise_id,
            "exercise_name": pr.exercise.name if pr.exercise else None,
            "session_id": pr.session_id,
            "session_set_id": pr.session_set_id,
            "pr_type": pr.pr_type,
            "value": pr.value,
            "notes": pr.notes,
            "achieved_at": pr.achieved_at,
        }
        pr_schemas.append(PersonalRecordSchema(**pr_dict))

    return format_response(pr_schemas)


@router.get(
    "/by-exercise", response_model=PersonalRecordsByExerciseResponse, status_code=200
)
def get_prs_by_exercise(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current (best) PRs organized by exercise.

    Returns the current best PR for each exercise and PR type.
    Useful for displaying a user's current PRs across all exercises.
    """
    prs_by_exercise = PersonalRecordService.get_current_prs_by_exercise(
        user_id=current_user.id, db=db
    )

    result = []
    for exercise_id, pr_dict in prs_by_exercise.items():
        first_pr = next(iter(pr_dict.values()))
        exercise_name = (
            first_pr.exercise.name if first_pr.exercise else f"Exercise {exercise_id}"
        )

        records = {}
        for pr_type, pr in pr_dict.items():
            pr_schema_dict = {
                "id": pr.id,
                "user_id": pr.user_id,
                "exercise_id": pr.exercise_id,
                "exercise_name": exercise_name,
                "session_id": pr.session_id,
                "session_set_id": pr.session_set_id,
                "pr_type": pr.pr_type,
                "value": pr.value,
                "notes": pr.notes,
                "achieved_at": pr.achieved_at,
            }
            records[pr_type] = PersonalRecordSchema(**pr_schema_dict)

        result.append(
            PersonalRecordsByExercise(
                exercise_id=exercise_id, exercise_name=exercise_name, records=records
            )
        )

    return format_response(result)


@router.get("/summary", response_model=PRSummaryResponse, status_code=200)
def get_pr_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a summary of personal records.

    Returns:
    - Total number of PRs achieved
    - Most recent PRs
    - Breakdown by PR type
    """
    summary_data = PersonalRecordService.get_pr_summary(user_id=current_user.id, db=db)

    recent_pr_schemas = []
    for pr in summary_data["recent_prs"]:
        pr_dict = {
            "id": pr.id,
            "user_id": pr.user_id,
            "exercise_id": pr.exercise_id,
            "exercise_name": pr.exercise.name if pr.exercise else None,
            "session_id": pr.session_id,
            "session_set_id": pr.session_set_id,
            "pr_type": pr.pr_type,
            "value": pr.value,
            "notes": pr.notes,
            "achieved_at": pr.achieved_at,
        }
        recent_pr_schemas.append(PersonalRecordSchema(**pr_dict))

    summary = PRSummary(
        total_prs=summary_data["total_prs"],
        recent_prs=recent_pr_schemas,
        prs_by_type=summary_data["prs_by_type"],
    )

    return format_response(summary)


@router.delete("/{pr_id}", response_model=PersonalRecordResponse, status_code=200)
def delete_personal_record(
    pr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a personal record.

    Users can only delete their own PRs.
    """
    deleted_pr = PersonalRecordService.delete_pr(
        pr_id=pr_id, user_id=current_user.id, db=db
    )

    pr_dict = {
        "id": deleted_pr.id,
        "user_id": deleted_pr.user_id,
        "exercise_id": deleted_pr.exercise_id,
        "exercise_name": deleted_pr.exercise.name if deleted_pr.exercise else None,
        "session_id": deleted_pr.session_id,
        "session_set_id": deleted_pr.session_set_id,
        "pr_type": deleted_pr.pr_type,
        "value": deleted_pr.value,
        "notes": deleted_pr.notes,
        "achieved_at": deleted_pr.achieved_at,
    }

    return format_response(PersonalRecordSchema(**pr_dict))
