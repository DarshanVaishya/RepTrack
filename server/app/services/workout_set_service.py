from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from app.schemas.workout_set import CreateWorkoutSetPayload, UpdateWorkoutSetPayload
from app.models.workout_set import WorkoutSet
from app.utils.logger import logger
from app.services.workout_exercise_service import WorkoutExerciseService


class WorkoutSetService:
    @staticmethod
    def create_workout_set(
        exercise_id: int, data: CreateWorkoutSetPayload, db: Session
    ):
        """
        Create a new workout set for a specific workout exercise.

        Args:
            exercise_id (int): The ID of the associated workout exercise.
            data (CreateWorkoutSetPayload): The payload containing set details (e.g., reps, weight, duration).
            db (Session): The active SQLAlchemy database session.

        Returns:
            WorkoutSet: The newly created workout set instance.

        Raises:
            HTTPException:
                - 400: If provided data violates constraints.
                - 500: For database or unexpected internal errors.

        Logging:
            - Debug: When attempting to create a set.
            - Info: After successful creation.
            - Error: On integrity, SQL, or unexpected issues.
        """
        try:
            data_dict = data.model_dump()
            logger.debug(f"Creating workout set with data: {data_dict}")

            data_dict["workout_exercise_id"] = exercise_id
            new_set = WorkoutSet(**data_dict)
            db.add(new_set)
            db.commit()
            db.refresh(new_set)

            logger.info(f"Successfully created workout set ID: {new_set.id}")
            return new_set

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating workout set: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout set",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating workout set: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating workout set",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating workout set: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_workout_set_by_id(set_id: int, db: Session):
        """
        Retrieve a single workout set by its unique ID.

        Args:
            set_id (int): The ID of the set to retrieve.
            db (Session): The active SQLAlchemy session.

        Returns:
            WorkoutSet: The retrieved set object.

        Raises:
            HTTPException:
                - 404: If the set does not exist.
                - 500: On database or internal server errors.

        Logging:
            - Error: For database or unexpected failures.
        """
        try:
            set = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
            if set is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout set with id {set_id} not found",
                )
            return set

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching workout set",
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_all_workout_sets(exercise_id: int, db: Session):
        """
        Retrieve all workout sets associated with a specific workout exercise.

        Args:
            exercise_id (int): The ID of the workout exercise whose sets should be fetched.
            db (Session): The active SQLAlchemy database session.

        Returns:
            list[WorkoutSet]: All sets belonging to the specified exercise.

        Raises:
            HTTPException:
                - 404: If the exercise is not found.
                - 500: On SQL or internal processing errors.

        Logging:
            - Info: Lists total fetched sets.
            - Error: For database or unexpected issues.
        """
        try:
            exercise = WorkoutExerciseService.get_workout_exercise(exercise_id, db)
            sets = exercise.sets

            logger.info(
                f"Fetched {len(sets)} sets for workout exercise ID: {exercise_id}"
            )
            return sets

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching workout sets for exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching workout sets",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error fetching workout sets for exercise {exercise_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def delete_workout_set(set_id: int, db: Session):
        """
        Delete a workout set by its ID.

        Args:
            set_id (int): The ID of the workout set to delete.
            db (Session): The active SQLAlchemy session.

        Returns:
            WorkoutSet: The deleted workout set instance.

        Raises:
            HTTPException:
                - 404: If the set does not exist.
                - 500: On database or internal errors.

        Logging:
            - Info: On successful deletion.
            - Error: On SQL or transactional failures.
        """
        try:
            set = WorkoutSetService.get_workout_set_by_id(set_id, db)
            db.delete(set)
            db.commit()
            logger.info(f"Deleted workout set ID: {set_id}")
            return set

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while deleting workout set",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error deleting workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def update_workout_set(set_id: int, data: UpdateWorkoutSetPayload, db: Session):
        """
        Update an existing workout set with new values.

        Args:
            set_id (int): The ID of the set to update.
            data (UpdateWorkoutSetPayload): The payload containing updated set values.
            db (Session): The active SQLAlchemy database session.

        Returns:
            WorkoutSet: The updated workout set object.

        Raises:
            HTTPException:
                - 400: If no updated fields were provided.
                - 404: If the workout set does not exist.
                - 500: For database or internal system errors.

        Logging:
            - Debug: Before updates, listing modified fields.
            - Info: On success.
            - Error: On integrity or SQL conflicts.
        """
        try:
            set = WorkoutSetService.get_workout_set_by_id(set_id, db)
            update_dict = data.model_dump(exclude_unset=True)

            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided to update",
                )

            fields_to_update = list(update_dict.keys())
            logger.debug(
                f"Updating fields for workout set {set_id}: {', '.join(fields_to_update)}"
            )

            for field, value in update_dict.items():
                setattr(set, field, value)

            db.commit()
            db.refresh(set)
            logger.info(f"Successfully updated workout set ID: {set_id}")
            return set

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout set update",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating workout set",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating workout set {set_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
