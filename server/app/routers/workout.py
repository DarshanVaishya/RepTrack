from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.schemas.workout import (
    AllWorkoutResponse,
    CreateWorkoutPayload,
    UpdateWorkoutPayload,
    WorkoutResponse,
    WorkoutResponseWithMsg,
)
from app.services.workout_service import WorkoutService
from app.utils.formatter import format_response
from fastapi_throttle import RateLimiter
import os


router = APIRouter(prefix="/workout", tags=["workout"])
if os.getenv("TESTING"):
    router.dependencies = []
else:
    limiter = RateLimiter(times=120, seconds=60)
    router.dependencies = [Depends(limiter)]


@router.post("", response_model=WorkoutResponseWithMsg, status_code=201)
def create_workout(
    data: CreateWorkoutPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_workout = WorkoutService.create_workout(data, current_user, db)
    print(new_workout)
    return format_response(new_workout, "Successfully created new workout")


@router.get("", response_model=AllWorkoutResponse, status_code=200)
def get_all_workouts_for_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workouts = WorkoutService.get_all_workouts_for_user(current_user, db)
    return format_response(workouts)


@router.get("/{workout_id}", response_model=WorkoutResponse, status_code=200)
def get_workout_by_id(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.get_workout_by_id(workout_id, db)
    return format_response(workout)


@router.put("/{workout_id}", response_model=WorkoutResponseWithMsg, status_code=200)
def update_workout(
    workout_id: int,
    data: UpdateWorkoutPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.update_workout(workout_id, data, current_user, db)
    return format_response(
        workout, f"successfully updated workout with id {workout_id}"
    )


@router.delete("/{workout_id}", status_code=200)
def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.delete_workout(workout_id, current_user, db)
    return format_response(
        workout, f"successfully deleted workout with id {workout_id}"
    )
