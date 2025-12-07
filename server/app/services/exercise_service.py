from sqlite3 import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.exercise import CreateExercisePayload, UpdateExercisePayload
from app.utils.logger import logger
from app.models.exercise import Exercise
from app.models.user import User, UserRole


class ExerciseService:
    @staticmethod
    def create_exercise(
        exercise_data: CreateExercisePayload, current_user: User, db: Session
    ):
        if current_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin only method"
            )
        exercise_dict = exercise_data.model_dump()
        logger.debug(f"Creating new exercise - Name: {exercise_dict['name']}")

        try:
            new_exercise = Exercise(**exercise_dict)
            db.add(new_exercise)
            db.commit()
            db.refresh(new_exercise)

            logger.info(
                f"Successfully created new exercise - Name: {new_exercise.name}"
            )

            return new_exercise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Duplicate exercise name: {exercise_dict.get('name', 'unknown')}"
            )
            if "name" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Exercise name already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data provided"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating exercise: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during exercise creation",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating exercise: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_all_exercises(db: Session):
        try:
            exercises = db.query(Exercise).all()
            return exercises
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching exercises: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exercises",
            )

    @staticmethod
    def get_exercise_by_id(exercise_id: int, db: Session):
        try:
            exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Exercise with id {exercise_id} not found.",
                )
            return exercise
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exercise",
            )

    @staticmethod
    def update_exercise(
        exercise_id: int,
        current_user: User,
        update_data: UpdateExercisePayload,
        db: Session,
    ):
        try:
            if current_user.role is not UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Admin only method"
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

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to invalid data",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during update",
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def delete_exercise(exercise_id: int, current_user: User, db: Session):
        try:
            if current_user.role is not UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Admin only method"
                )
            exercise = ExerciseService.get_exercise_by_id(exercise_id, db)
            db.delete(exercise)
            db.commit()
            return exercise

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during deletion",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error deleting exercise {exercise_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
