from fastapi import APIRouter, Depends
from pytest import Session
from app.database import get_db
from app.schemas.exercise import CreateExercisePayload, UpdateExercisePayload
from app.services.exercise_service import ExerciseService
from app.utils.auth import get_current_user
from app.models.user import User


router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.post("")
def create_exercise(
    exercise_data: CreateExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.create_exercise(exercise_data, current_user, db)
    return exercise


@router.get("")
def get_all_exercises(db: Session = Depends(get_db)):
    exercises = ExerciseService.get_all_exercises(db)
    return exercises


@router.get("/{exercise_id}")
def get_exercise_by_id(exercise_id: int, db: Session = Depends(get_db)):
    exercise = ExerciseService.get_exercise_by_id(exercise_id, db)
    return exercise


@router.put("/{exercise_id}")
def update_exercise(
    exercise_id: int,
    update_data: UpdateExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.update_exercise(
        exercise_id, current_user, update_data, db
    )
    return exercise


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = ExerciseService.delete_exercise(exercise_id, current_user, db)
    return exercise
