from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.workout_exercise import (
    AllWorkoutExercisesResponse,
    CreateWorkoutExercisePayload,
    UpdateWorkoutExercisePayload,
    WorkoutExerciseResponse,
    WorkoutExerciseResponseWithMsg,
)
from app.utils.auth import get_current_user
from app.services.workout_exercise_service import WorkoutExerciseService
from app.utils.formatter import format_response
from fastapi_throttle import RateLimiter


router = APIRouter(prefix="/workout/{workout_id}/exercise", tags=["workout_exercise"])
limiter = RateLimiter(times=120, seconds=60)
router.dependencies = [Depends(limiter)]


@router.post("", response_model=WorkoutExerciseResponse, status_code=201)
def create_workout_exercise(
    data: CreateWorkoutExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_workout_exercise = WorkoutExerciseService.create_workout_exercise(data, db)
    return format_response(new_workout_exercise)


@router.get("", response_model=AllWorkoutExercisesResponse, status_code=200)
def get_all_workout_exercises(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercises = WorkoutExerciseService.get_all_workout_exercises(
        workout_id, current_user, db
    )
    return format_response(exercises)


@router.get("/{exercise_id}", response_model=WorkoutExerciseResponse, status_code=200)
def get_workout_exercise_by_id(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = WorkoutExerciseService.get_workout_exercise(exercise_id, db)
    return format_response(exercise)


@router.put(
    "/{exercise_id}", response_model=WorkoutExerciseResponseWithMsg, status_code=200
)
def update_workout_exercise(
    exercise_id: int,
    data: UpdateWorkoutExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = WorkoutExerciseService.update_workout_exercise(exercise_id, data, db)
    return format_response(
        exercise, f"Successfully updated workout exercise with id {exercise_id}"
    )


@router.delete("/{exercise_id}")
def delete_workout_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = WorkoutExerciseService.delete_workout_exercise(exercise_id, db)
    return format_response(
        exercise, f"Successfully deleted workout exercise with id {exercise_id}"
    )
