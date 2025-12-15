from sqlalchemy.orm import Session
from app.schemas.workout_exercise import CreateWorkoutExercisePayload
from app.models import WorkoutExercise


class WorkoutExerciseService:
    @staticmethod
    def create_workout_exercise(data: CreateWorkoutExercisePayload, db: Session):
        data_dict = data.model_dump()
        new_workout_exercise = WorkoutExercise(**data_dict)

        db.add(new_workout_exercise)
        db.commit()
        db.refresh(new_workout_exercise)

        return new_workout_exercise
