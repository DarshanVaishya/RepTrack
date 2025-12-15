from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.workout_exercise import CreateWorkoutExercisePayload
from app.utils.auth import get_current_user
from app.services.workout_exercise_service import WorkoutExerciseService


router = APIRouter(prefix="/workout_exercise", tags=["workout_exercise"])


@router.post("")
def create_workout_exercise(
    data: CreateWorkoutExercisePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_workout_exercise = WorkoutExerciseService.create_workout_exercise(data, db)
    return new_workout_exercise
