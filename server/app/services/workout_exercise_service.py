from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.workout_exercise import (
    CreateWorkoutExercisePayload,
    UpdateWorkoutExercisePayload,
)
from app.models import Exercise, User, WorkoutExercise
from app.utils.logger import logger
from app.services.workout_service import WorkoutService


class WorkoutExerciseService:
    @staticmethod
    # TODO: Use the workout_id from the url
    def create_workout_exercise(data: CreateWorkoutExercisePayload, db: Session):
        """
        Create a new workout exercise record linked to an existing workout.

        Args:
            data (CreateWorkoutExercisePayload): The payload containing details for the new workout exercise.
            db (Session): The active SQLAlchemy database session.

        Returns:
            WorkoutExercise: The newly created workout exercise instance.

        Raises:
            HTTPException:
                - 404: If the referenced catalog exercise does not exist.
                - 400: If the input data is invalid.
                - 500: For database or internal errors.

        Logging:
            - Debug: Before creating a new workout exercise.
            - Info: Upon successful creation.
            - Error: On database or integrity constraint failures.
        """
        try:
            data_dict = data.model_dump()
            # TODO: Also check if workout exists before moving forward
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

    # TODO: Add exception handling
    @staticmethod
    def get_all_workout_exercises(workout_id: int, current_user: User, db: Session):
        """
        Retrieve all exercises associated with a specific user’s workout.

        Args:
            workout_id (int): The ID of the parent workout.
            current_user (User): The currently authenticated user requesting the data.
            db (Session): The active SQLAlchemy database session.

        Returns:
            list[WorkoutExercise]: List of all exercises linked to the specified workout.

        Raises:
            HTTPException:
                - 404: If the workout does not exist.
                - 500: If an internal or database error occurs.

        Logging:
            - Info: Implicitly handled by the linked `WorkoutService`.
        """
        workout = WorkoutService.get_workout_by_id(workout_id, db)
        exercises = workout.workout_exercises
        return exercises

    @staticmethod
    def get_workout_exercise(exercise_id: int, db: Session):
        """
        Retrieve a specific workout exercise by its ID.

        Args:
            exercise_id (int): The unique identifier of the workout exercise to fetch.
            db (Session): The active SQLAlchemy session.

        Returns:
            WorkoutExercise: The matched workout exercise.

        Raises:
            HTTPException:
                - 404: If the record does not exist.
                - 500: For database or internal errors.

        Logging:
            - Error: On database or unexpected failures.
        """
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
        """
        Delete a workout exercise by its ID.

        Args:
            exercise_id (int): The ID of the workout exercise to delete.
            db (Session): The active SQLAlchemy session.

        Returns:
            WorkoutExercise: The deleted workout exercise.

        Raises:
            HTTPException:
                - 404: If the workout exercise is not found.
                - 500: For database or internal system errors.

        Logging:
            - Info: On successful deletion.
            - Error: On SQL or unexpected exceptions.
        """
        try:
            exercise = WorkoutExerciseService.get_workout_exercise(exercise_id, db)
            db.delete(exercise)
            db.commit()
            logger.info(f"Deleted workout exercise ID: {exercise_id}")
            return exercise

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
        """
        Update an existing workout exercise entry.

        Args:
            exercise_id (int): The ID of the workout exercise to update.
            data (UpdateWorkoutExercisePayload): The payload containing fields to update.
            db (Session): The active SQLAlchemy session.

        Returns:
            WorkoutExercise: The updated workout exercise object.

        Raises:
            HTTPException:
                - 400: If no fields are provided for update.
                - 404: If the target workout exercise does not exist.
                - 500: On database or unexpected system failures.

        Logging:
            - Debug: Before applying updates, showing modified fields.
            - Info: On successful update.
            - Error: On integrity or database conflicts.
        """
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
