from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.exercise import CreateExercisePayload, UpdateExercisePayload
from app.utils.logger import logger
from app.models.exercise import Exercise
from app.models.user import User, UserRole


# TODO: Add error handling
class ExerciseService:
    @staticmethod
    def create_exercise(
        exercise_data: CreateExercisePayload, current_user: User, db: Session
    ):
        if current_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin only method"
            )

        exercise_dict = exercise_data.model_dump()
        logger.debug(f"Creating new exercise - Name: {exercise_dict['name']}")

        new_exercise = Exercise(**exercise_dict)
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)

        logger.info(f"Successfully created new exercise - Name: {new_exercise.name}")

        return new_exercise

    @staticmethod
    def get_all_exercises(db: Session):
        exercises = db.query(Exercise).all()
        return exercises

    @staticmethod
    def get_exercise_by_id(exercise_id: int, db: Session):
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {exercise_id} not found.",
            )
        return exercise

    @staticmethod
    def update_exercise(
        exercise_id: int,
        current_user: User,
        update_data: UpdateExercisePayload,
        db: Session,
    ):
        if current_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin only method"
            )

        exercise = ExerciseService.get_exercise_by_id(exercise_id, db)
        update_dict = update_data.model_dump(exclude_unset=True)

        fields_to_update = [k for k in update_dict.keys() if k != "password"]
        if fields_to_update:
            logger.debug(
                f"Updating fields for exercise {exercise_id}: {', '.join(fields_to_update)}"
            )

        for field, value in update_dict.items():
            setattr(exercise, field, value)

        db.commit()
        db.refresh(exercise)
        return exercise

    @staticmethod
    def delete_exercise(exercise_id: int, current_user: User, db: Session):
        if current_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin only method"
            )
        exercise = ExerciseService.get_exercise_by_id(exercise_id, db)
        db.delete(exercise)
        db.commit()
        return exercise
