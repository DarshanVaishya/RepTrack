from sqlalchemy.orm import Session, joinedload
from app.models import Workout, WorkoutExercise
from app.schemas.workout import CreateWorkoutPayload


class WorkoutService:
    @staticmethod
    def create_workout(data: CreateWorkoutPayload, db: Session):
        data_dict = data.model_dump()
        new_workout = Workout(**data_dict)
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

        return new_workout

    @staticmethod
    def get_all_workouts(db: Session):
        workouts = (
            db.query(Workout)
            .options(
                joinedload(Workout.workout_exercises).joinedload(WorkoutExercise.sets),
                joinedload(Workout.workout_exercises).joinedload(
                    WorkoutExercise.exercise
                ),
            )
            .all()
        )
        return workouts
