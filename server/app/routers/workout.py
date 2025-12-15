from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.schemas.workout import CreateWorkoutPayload
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
def get_all_workouts(db: Session = Depends(get_db)):
    workouts = WorkoutService.get_all_workouts(db)
    return workouts
