from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.workout_set import CreateWorkoutSetPayload
from app.services.workout_set_service import WorkoutSetService
from app.utils.auth import get_current_user


router = APIRouter(prefix="/sets", tags=["sets"])


@router.post("")
def create_workout_set(
    data: CreateWorkoutSetPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_set = WorkoutSetService.create_workout_set(data, db)
    return new_set
