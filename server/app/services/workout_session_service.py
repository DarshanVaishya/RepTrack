from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models import User
from app.models.workout_session import WorkoutSession, SessionStatus
from app.models.session_exercise import SessionExercise
from app.models.session_set import SessionSet, SessionSetStatus
from app.schemas.workout_session import (
    CreateWorkoutSessionPayload,
    CompleteSessionSetPayload,
)
from app.utils.logger import logger
from app.services.workout_service import WorkoutService
from app.models.workout_exercise import WorkoutExercise
from app.services.personal_record_service import PersonalRecordService


class WorkoutSessionService:
    @staticmethod
    def start_session(
        data: CreateWorkoutSessionPayload, current_user: User, db: Session
    ):
        """
        Start a new workout session based on a workout template.
        Creates session records with planned values from the template.
        """
        try:
            # Verify workout exists and get it with all exercises and sets
            workout = WorkoutService.get_workout_by_id(data.workout_id, db)

            # Verify user owns the workout or it's a shared template
            if workout.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot start session for workout you don't own",
                )

            logger.debug(
                f"Starting workout session for user {current_user.id}, workout {data.workout_id}"
            )

            # Create the session
            new_session = WorkoutSession(
                workout_id=data.workout_id,
                user_id=current_user.id,
                status=SessionStatus.IN_PROGRESS,
                notes=data.notes or "",
            )
            db.add(new_session)
            db.flush()  # Get the session ID

            # Copy workout exercises to session exercises
            for workout_exercise in workout.workout_exercises:
                session_exercise = SessionExercise(
                    session_id=new_session.id,
                    workout_exercise_id=workout_exercise.id,
                    order_index=workout_exercise.order_index,
                    notes=workout_exercise.notes,
                )
                db.add(session_exercise)
                db.flush()

                # Copy sets from workout template
                for workout_set in workout_exercise.sets:
                    session_set = SessionSet(
                        session_exercise_id=session_exercise.id,
                        workout_set_id=workout_set.id,
                        planned_reps=workout_set.reps,
                        planned_weight=workout_set.weight,
                        order_index=workout_set.order_index,
                        status=SessionSetStatus.PENDING,
                    )
                    db.add(session_set)

            db.commit()
            db.refresh(new_session)

            logger.info(f"Successfully started workout session ID: {new_session.id}")
            return WorkoutSessionService.get_session_by_id(
                new_session.id, current_user, db
            )

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error starting session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data for workout session",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error starting session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while starting session",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error starting session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_session_by_id(session_id: int, current_user: User, db: Session):
        """Retrieve a workout session with all its exercises and sets."""
        try:
            session = (
                db.query(WorkoutSession)
                .options(
                    joinedload(WorkoutSession.workout),
                    joinedload(WorkoutSession.session_exercises)
                    .joinedload(SessionExercise.workout_exercise)
                    .joinedload(WorkoutExercise.exercise),
                    joinedload(WorkoutSession.session_exercises).joinedload(
                        SessionExercise.session_sets
                    ),
                )
                .filter(WorkoutSession.id == session_id)
                .first()
            )

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session with id {session_id} not found",
                )

            if session.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access another user's session",
                )

            return session

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching session {session_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching session",
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching session {session_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def get_user_sessions(
        current_user: User, db: Session, status: SessionStatus = None
    ):
        """Get all sessions for a user, optionally filtered by status."""
        try:
            query = db.query(WorkoutSession).filter(
                WorkoutSession.user_id == current_user.id
            )

            if status:
                query = query.filter(WorkoutSession.status == status)

            sessions = query.order_by(WorkoutSession.started_at.desc()).all()

            logger.info(f"Fetched {len(sessions)} sessions for user {current_user.id}")
            return sessions

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user sessions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while fetching sessions",
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching user sessions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def complete_set(
        session_id: int,
        set_id: int,
        data: CompleteSessionSetPayload,
        current_user: User,
        db: Session,
    ):
        """Record the completion of a set with actual reps and weight."""
        try:
            # Verify session belongs to user
            session = WorkoutSessionService.get_session_by_id(
                session_id, current_user, db
            )

            if session.status != SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update sets in a completed or cancelled session",
                )

            # Get the set
            session_set = db.query(SessionSet).filter(SessionSet.id == set_id).first()
            if not session_set:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Set with id {set_id} not found",
                )

            # Verify set belongs to this session
            session_exercise = (
                db.query(SessionExercise)
                .filter(
                    SessionExercise.id == session_set.session_exercise_id,
                    SessionExercise.session_id == session_id,
                )
                .first()
            )

            if not session_exercise:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Set does not belong to this session",
                )

            # Update the set
            session_set.actual_reps = data.actual_reps
            session_set.actual_weight = data.actual_weight
            session_set.status = SessionSetStatus.COMPLETED
            session_set.completed_at = datetime.now(timezone.utc)
            if data.notes:
                session_set.notes = data.notes

            db.commit()
            db.refresh(session_set)

            logger.info(f"Completed set {set_id} in session {session_id}")
            return session_set

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error completing set: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while completing set",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error completing set: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def complete_session(session_id: int, current_user: User, db: Session):
        """Mark a workout session as completed."""
        try:
            session = WorkoutSessionService.get_session_by_id(
                session_id, current_user, db
            )

            if session.status != SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session is not in progress",
                )

            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)

            # Calculate duration
            if session.started_at:
                duration = (
                    session.completed_at - session.started_at
                ).total_seconds() / 60
                session.duration_minutes = int(duration)

            total_volume = 0
            for exercise in session.session_exercises:
                for session_set in exercise.session_sets:
                    if session_set.actual_reps and session_set.actual_weight:
                        total_volume += (
                            session_set.actual_reps * session_set.actual_weight
                        )
            session.total_volume = total_volume
            logger.info(f"Session total volume: {total_volume}")

            db.commit()
            db.refresh(session)

            new_prs = PersonalRecordService.check_and_update_prs_for_session(
                session=session, db=db
            )

            logger.info(f"Completed session {session_id}")
            return session

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error completing session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while completing session",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error completing session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    @staticmethod
    def cancel_session(session_id: int, current_user: User, db: Session):
        """Cancel a workout session."""
        try:
            session = WorkoutSessionService.get_session_by_id(
                session_id, current_user, db
            )

            if session.status != SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only cancel sessions that are in progress",
                )

            session.status = SessionStatus.CANCELLED
            session.completed_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(session)

            logger.info(f"Cancelled session {session_id}")
            return session

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error cancelling session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error while cancelling session",
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error cancelling session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
