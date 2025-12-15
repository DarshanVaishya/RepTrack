from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.schemas.workout import CreateWorkoutPayload, UpdateWorkoutPayload
from app.services.workout_service import WorkoutService


router = APIRouter(prefix="/workout", tags=["workout"])


@router.post("")
def create_workout(
    data: CreateWorkoutPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_workout = WorkoutService.create_workout(data, db)
    return new_workout


@router.get("")
def get_all_workouts_for_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workouts = WorkoutService.get_all_workouts_for_user(current_user, db)
    return workouts


@router.get("/{workout_id}")
def get_workout_by_id(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.get_workout_by_id(workout_id, db)
    return workout


@router.put("/{workout_id}")
def update_workout(
    workout_id: int,
    data: UpdateWorkoutPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.update_workout(workout_id, data, current_user, db)
    return workout


@router.delete("/{workout_id}")
def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workout = WorkoutService.delete_workout(workout_id, current_user, db)
    return workout
