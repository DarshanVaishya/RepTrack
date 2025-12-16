from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.workout_set import CreateWorkoutSetPayload, UpdateWorkoutSetPayload
from app.services.workout_set_service import WorkoutSetService
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/workout/{workout_id}/exercise/{exercise_id}/set", tags=["sets"]
)


@router.post("")
def create_workout_set(
    data: CreateWorkoutSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_set = WorkoutSetService.create_workout_set(data, db)
    return new_set


@router.get("/{set_id}")
def get_workout_set_by_id(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.get_workout_set_by_id(set_id, db)
    return set


@router.delete("/{set_id}")
def delete_workout_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.delete_workout_set(set_id, db)
    return set


@router.put("/{set_id}")
def update_workout_set(
    set_id: int,
    data: UpdateWorkoutSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.update_workout_set(set_id, data, db)
    return set
