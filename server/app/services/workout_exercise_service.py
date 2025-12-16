from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.workout_exercise import (
    CreateWorkoutExercisePayload,
    UpdateWorkoutExercisePayload,
)
from app.models import Exercise, WorkoutExercise
from app.utils.logger import logger


class WorkoutExerciseService:
    @staticmethod
    def create_workout_exercise(data: CreateWorkoutExercisePayload, db: Session):
        try:
            data_dict = data.model_dump()
            exercise = (
                db.query(Exercise)
                .filter(Exercise.id == data_dict["exercise_id"])
                .first()
            )
            if not exercise:
                raise HTTPException(
                    status_code=404, detail="Catalog exercise not found"
                )

            logger.debug(f"Creating workout exercise with data: {data_dict}")

            new_workout_exercise = WorkoutExercise(**data_dict)
            db.add(new_workout_exercise)
            db.commit()
            db.refresh(new_workout_exercise)

            logger.info(
                f"Successfully created workout exercise ID: {new_workout_exercise.id}"
            )
            return new_workout_exercise

        except HTTPException:
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating workout exercise: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout exercise",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating workout exercise: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating workout exercise",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating workout exercise: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_workout_exercise(exercise_id: int, db: Session):
        try:
            exercise = (
                db.query(WorkoutExercise)
                .filter(WorkoutExercise.id == exercise_id)
                .first()
            )
            if exercise is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout exercise with id {exercise_id} not found",
                )
            return exercise

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching workout exercise",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error fetching workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def delete_workout_exercise(exercise_id: int, db: Session):
        try:
            exercise = WorkoutExerciseService.get_workout_exercise(exercise_id, db)
            db.delete(exercise)
            db.commit()
            logger.info(f"Deleted workout exercise ID: {exercise_id}")
            return {"detail": "Deleted"}

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error deleting workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while deleting workout exercise",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error deleting workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def update_workout_exercise(
        exercise_id: int, data: UpdateWorkoutExercisePayload, db: Session
    ):
        try:
            exercise = WorkoutExerciseService.get_workout_exercise(exercise_id, db)
            update_dict = data.model_dump(exclude_unset=True)

            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided to update",
                )

            fields_to_update = list(update_dict.keys())
            logger.debug(
                f"Updating fields for workout exercise {exercise_id}: "
                f"{', '.join(fields_to_update)}"
            )

            for field, value in update_dict.items():
                setattr(exercise, field, value)

            db.commit()
            db.refresh(exercise)
            logger.info(f"Successfully updated workout exercise ID: {exercise_id}")
            return exercise

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error updating workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout exercise update",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error updating workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating workout exercise",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error updating workout exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
