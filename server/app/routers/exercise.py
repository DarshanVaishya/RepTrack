from app.database import get_db
from app.models.user import User
from app.schemas.exercise import (
    AllExercisesResponse,
    CreateExercisePayload,
    ExerciseResponse,
    ExerciseResponseWithMsg,
    UpdateExercisePayload,
)
from app.services.exercise_service import ExerciseService
from app.utils.auth import get_current_user
from app.utils.formatter import format_response
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi_throttle import RateLimiter
import os

router = APIRouter(prefix="/exercises", tags=["exercises"])
if os.getenv("TESTING"):
    router.dependencies = []
else:
    exercise_limiter = RateLimiter(times=60, seconds=60)
    router.dependencies = [Depends(exercise_limiter)]


@router.post("", response_model=ExerciseResponse, status_code=201)
def create_exercise(
    exercise_data: CreateExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.create_exercise(exercise_data, current_user, db)
    return format_response(exercise)


@router.get("", response_model=AllExercisesResponse, status_code=200)
def get_all_exercises(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    exercises = ExerciseService.get_all_exercises(db)
    return format_response(exercises)


@router.get("/{exercise_id}", response_model=ExerciseResponse, status_code=200)
def get_exercise_by_id(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.get_exercise_by_id(exercise_id, db)
    return format_response(exercise)


@router.put("/{exercise_id}", response_model=ExerciseResponseWithMsg, status_code=200)
def update_exercise(
    exercise_id: int,
    update_data: UpdateExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.update_exercise(
        exercise_id, current_user, update_data, db
    )
    return format_response(
        exercise, f"Successfully updated exercise with id {exercise_id}"
    )


@router.delete(
    "/{exercise_id}", response_model=ExerciseResponseWithMsg, status_code=200
)
def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.delete_exercise(exercise_id, current_user, db)
    return format_response(
        exercise, f"Successfully deleted exercise with id {exercise_id}"
    )
