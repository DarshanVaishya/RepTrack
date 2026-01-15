from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models import User, Workout
from app.schemas.workout import CreateWorkoutPayload, UpdateWorkoutPayload
from app.utils.logger import logger
from app.models.workout_exercise import WorkoutExercise


class WorkoutService:
    @staticmethod
    def create_workout(data: CreateWorkoutPayload, current_user: User, db: Session):
        """
        Create a new workout record for the given user.

        Args:
            data (CreateWorkoutPayload): The payload containing workout details.
            current_user (User): The user creating the workout.
            db (Session): The active SQLAlchemy session used for database operations.

        Returns:
            Workout: The newly created workout instance.

        Raises:
            HTTPException: If invalid workout data is provided or a database error occurs.

        Logging:
            - Debug: When starting to create a workout.
            - Info: When the workout is successfully created.
            - Error: On integrity or database-related issues.
        """
        try:
            data_dict = data.model_dump()
            if data_dict["notes"] is None:
                data_dict["notes"] = ""
            data_dict["user_id"] = current_user.id

            logger.debug(f"Creating workout for user {current_user.id}: {data_dict}")

            new_workout = Workout(**data_dict)
            db.add(new_workout)
            db.commit()
            db.refresh(new_workout)

            logger.info(f"Successfully created workout ID: {new_workout.id}")
            return new_workout

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Integrity error creating workout for user {current_user.id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating workout: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while creating workout",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating workout: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_all_workouts_for_user(current_user: User, db: Session):
        """
        Retrieve all workouts belonging to the specified user.

        Args:
            current_user (User): The user whose workouts should be fetched.
            db (Session): The active SQLAlchemy session.

        Returns:
            list[Workout]: A list of workout objects associated with the user.

        Raises:
            HTTPException: If a database or internal error occurs.

        Logging:
            - Debug: When fetching workouts starts.
            - Info: When workouts are successfully retrieved.
            - Error: On database or unexpected errors.
        """
        try:
            logger.debug(f"Fetching workouts for user {current_user.id}")
            # workouts = (
            #     db.query(Workout)
            #     .filter(Workout.user_id == current_user.id)
            #     .options(
            #         joinedload(Workout.workout_exercises).joinedload(
            #             WorkoutExercise.sets
            #         ),
            #         joinedload(Workout.workout_exercises).joinedload(
            #             WorkoutExercise.exercise
            #         ),
            #     )
            #     .all()
            # )
            workouts = (
                db.query(Workout).filter(Workout.user_id == current_user.id).all()
            )
            logger.info(f"Fetched {len(workouts)} workouts for user {current_user.id}")
            return workouts

        except SQLAlchemyError as e:
            logger.error(
                f"Database error fetching workouts for user {current_user.id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching workouts",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error fetching workouts for user {current_user.id}: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_workout_by_id(workout_id: int, db: Session):
        """
        Retrieve a single workout by its ID.

        Args:
            workout_id (int): The ID of the workout to retrieve.
            db (Session): The active SQLAlchemy session.

        Returns:
            Workout: The workout object if found.

        Raises:
            HTTPException:
                - 400: If the provided workout ID is invalid.
                - 404: If no workout is found with the given ID.
                - 500: For database or unexpected server errors.
        """
        try:
            if workout_id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid workout ID",
                )

            workout = (
                db.query(Workout)
                .options(
                    joinedload(Workout.workout_exercises).options(
                        joinedload(WorkoutExercise.sets),
                        joinedload(WorkoutExercise.exercise),
                    )
                )
                .filter(Workout.id == workout_id)
                .first()
            )

            if not workout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout with id {workout_id} not found",
                )

            return workout

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching workout",
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def update_workout(
        workout_id: int, data: UpdateWorkoutPayload, current_user: User, db: Session
    ):
        """
        Update an existing workout owned by the current user.

        Args:
            workout_id (int): The ID of the workout to update.
            data (UpdateWorkoutPayload): The update payload containing fields to modify.
            current_user (User): The user requesting the update.
            db (Session): The active SQLAlchemy session.

        Returns:
            Workout: The updated workout object.

        Raises:
            HTTPException:
                - 400: If no update fields are provided.
                - 403: If the user doesn't own the workout.
                - 404: If the workout does not exist.
                - 500: For database or internal errors.

        Logging:
            - Debug: Before performing an update, listing fields being modified.
            - Info: After a successful update.
            - Error: On SQL, integrity, or unexpected issues.
        """
        try:
            workout = WorkoutService.get_workout_by_id(workout_id, db)
            if workout.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only workout creator can update it",
                )

            update_dict = data.model_dump(exclude_unset=True)
            if not update_dict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided to update",
                )

            fields_to_update = list(update_dict.keys())
            logger.debug(
                f"Updating workout {workout_id} for user {current_user.id}: {', '.join(fields_to_update)}"
            )

            for field, value in update_dict.items():
                setattr(workout, field, value)

            db.commit()
            db.refresh(workout)
            logger.info(f"Successfully updated workout ID: {workout_id}")
            return workout

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error updating workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout update",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while updating workout",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error updating workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def delete_workout(workout_id: int, current_user: User, db: Session):
        """
        Delete a workout if it belongs to the current user.

        Args:
            workout_id (int): The ID of the workout to delete.
            current_user (User): The authenticated user requesting deletion.
            db (Session): The current SQLAlchemy session.

        Returns:
            Workout: The deleted workout object.

        Raises:
            HTTPException:
                - 403: If the user does not own the workout.
                - 404: If the workout does not exist.
                - 500: On database or internal failures.

        Logging:
            - Info: On successful deletion.
            - Error: On database or unexpected issues.
        """
        try:
            workout = WorkoutService.get_workout_by_id(workout_id, db)
            if workout.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only workout creator can delete it",
                )

            db.delete(workout)
            db.commit()
            logger.info(f"Deleted workout ID: {workout_id} for user {current_user.id}")
            return workout

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while deleting workout",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error deleting workout {workout_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
