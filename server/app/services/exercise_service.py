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
        """
        Create a new exercise in the database. Only accessible by admin users.

        Args:
            exercise_data (CreateExercisePayload): The data payload containing exercise details.
            current_user (User): The currently authenticated user.
            db (Session): The active SQLAlchemy session for database operations.

        Returns:
            Exercise: The newly created exercise object.

        Raises:
            HTTPException:
                - 403: If the user is not an admin.
                - 400: If duplicate or invalid data is provided.
                - 500: On database or unexpected internal errors.

        Logging:
            - Debug: When a new exercise is being created.
            - Info: After successful creation.
            - Error: On integrity or database failures.
        """
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
        """
        Retrieve all available exercises.

        Args:
            db (Session): The active SQLAlchemy session.

        Returns:
            list[Exercise]: A list of all exercise objects available in the database.

        Raises:
            HTTPException:
                - 500: If a database or internal error occurs.

        Logging:
            - Error: If database access fails.
        """
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
        """
        Retrieve a specific exercise by its ID.

        Args:
            exercise_id (int): The unique ID of the exercise to fetch.
            db (Session): The active SQLAlchemy session.

        Returns:
            Exercise: The exercise object if found.

        Raises:
            HTTPException:
                - 404: If no exercise is found with the given ID.
                - 500: If a database error occurs.

        Logging:
            - Error: On database-level issues.
        """
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
        """
        Update an existing exercise. Only accessible by admin users.

        Args:
            exercise_id (int): The ID of the exercise to update.
            current_user (User): The admin user performing the update.
            update_data (UpdateExercisePayload): The payload with updated field values.
            db (Session): The active SQLAlchemy session.

        Returns:
            Exercise: The updated exercise object.

        Raises:
            HTTPException:
                - 403: If the user is not an admin.
                - 400: For invalid or conflicting update data.
                - 404: If the exercise does not exist.
                - 500: On database or internal system errors.

        Logging:
            - Debug: When listing updated fields.
            - Error: On integrity or database exceptions.
        """
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
        """
        Delete an exercise from the database. Only accessible by admin users.

        Args:
            exercise_id (int): The ID of the exercise to delete.
            current_user (User): The admin user performing the action.
            db (Session): The active SQLAlchemy session.

        Returns:
            Exercise: The deleted exercise object.

        Raises:
            HTTPException:
                - 403: If the user is not an admin.
                - 404: If the exercise does not exist.
                - 500: On database or unexpected internal errors.

        Logging:
            - Info: On successful deletion.
            - Error: On database or internal errors.
        """
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
