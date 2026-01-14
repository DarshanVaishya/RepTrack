from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.workout_set import (
    AllWorkoutSetResponse,
    CreateWorkoutSetPayload,
    UpdateWorkoutSetPayload,
    WorkoutSetResponse,
    WorkoutSetResponseWithMsg,
)
from app.services.workout_set_service import WorkoutSetService
from app.utils.auth import get_current_user
from app.utils.formatter import format_response


router = APIRouter(
    prefix="/workout/{workout_id}/exercise/{exercise_id}/set", tags=["sets"]
)


@router.post("", response_model=WorkoutSetResponseWithMsg, status_code=201)
def create_workout_set(
    exercise_id: int,
    data: CreateWorkoutSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_set = WorkoutSetService.create_workout_set(exercise_id, data, db)
    return format_response(new_set, "Successfully created new workout set")


@router.get("/{set_id}", response_model=WorkoutSetResponse, status_code=200)
def get_workout_set_by_id(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.get_workout_set_by_id(set_id, db)
    return format_response(set)


@router.get("", response_model=AllWorkoutSetResponse, status_code=200)
def get_all_workout_sets(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sets = WorkoutSetService.get_all_workout_sets(exercise_id, db)
    return format_response(sets)


@router.delete("/{set_id}", response_model=WorkoutSetResponseWithMsg, status_code=200)
def delete_workout_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.delete_workout_set(set_id, db)
    return format_response(set, f"Successfully deleted workout set with id {set_id}")


@router.put("/{set_id}", response_model=WorkoutSetResponseWithMsg, status_code=200)
def update_workout_set(
    set_id: int,
    data: UpdateWorkoutSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = WorkoutSetService.update_workout_set(set_id, data, db)
    return format_response(set, f"Successfully deleted workout set with id {set_id}")
