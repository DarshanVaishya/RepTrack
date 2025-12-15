from sqlalchemy.orm import Session
from app.models import User
from app.schemas.workout_set import CreateWorkoutSetPayload
from app.models.workout_set import WorkoutSet


class WorkoutSetService:
    @staticmethod
    def create_workout_set(data: CreateWorkoutSetPayload, db: Session):
        data_dict = data.model_dump()
        new_set = WorkoutSet(**data_dict)
        db.add(new_set)
        db.commit()
        db.refresh(new_set)

        return new_set
