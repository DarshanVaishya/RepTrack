from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, session
from sqlalchemy import desc, func

from app.models import WorkoutSession
from app.models.personal_record import PersonalRecord, PRType
from app.utils.logger import logger


class PersonalRecordService:
    """Service for managing personal records."""

    @staticmethod
    def check_and_update_prs_for_session(
        session: WorkoutSession, db: Session
    ) -> list[PersonalRecord]:
        """
        Check if any PRs were achieved in a completed session and update them.

        Args:
            session: The completed workout session
            db: Database session

        Returns:
            List of new PRs that were achieved
        """
        new_prs = []

        try:
            exercise_data = {}

            for session_exercise in session.session_exercises:
                exercise_id = session_exercise.workout_exercise.exercise_id

                if exercise_id not in exercise_data:
                    exercise_data[exercise_id] = {"sets": [], "total_volume": 0}

                for session_set in session_exercise.session_sets:
                    if session_set.actual_reps and session_set.actual_weight:
                        set_volume = session_set.actual_reps * session_set.actual_weight
                        exercise_data[exercise_id]["sets"].append(
                            {
                                "set": session_set,
                                "volume": set_volume,
                                "weight": session_set.actual_weight,
                                "reps": session_set.actual_reps,
                            }
                        )
                        exercise_data[exercise_id]["total_volume"] += set_volume

            for exercise_id, data in exercise_data.items():
                volume_pr = PersonalRecordService._check_and_update_pr(
                    user_id=session.user_id,
                    exercise_id=exercise_id,
                    pr_type=PRType.MAX_VOLUME,
                    value=data["total_volume"],
                    session_id=session.id,
                    session_set_id=None,
                    db=db,
                )
                if volume_pr:
                    new_prs.append(volume_pr)

                if data["sets"]:
                    best_set = max(data["sets"], key=lambda x: x["volume"])
                    single_set_pr = PersonalRecordService._check_and_update_pr(
                        user_id=session.user_id,
                        exercise_id=exercise_id,
                        pr_type=PRType.MAX_SINGLE_SET,
                        value=best_set["volume"],
                        session_id=session.id,
                        session_set_id=best_set["set"].id,
                        db=db,
                    )
                    if single_set_pr:
                        new_prs.append(single_set_pr)

                    heaviest = max(data["sets"], key=lambda x: x["weight"])
                    weight_pr = PersonalRecordService._check_and_update_pr(
                        user_id=session.user_id,
                        exercise_id=exercise_id,
                        pr_type=PRType.MAX_WEIGHT,
                        value=heaviest["weight"],
                        session_id=session.id,
                        session_set_id=heaviest["set"].id,
                        db=db,
                    )
                    if weight_pr:
                        new_prs.append(weight_pr)

                    most_reps = max(data["sets"], key=lambda x: x["reps"])
                    reps_pr = PersonalRecordService._check_and_update_pr(
                        user_id=session.user_id,
                        exercise_id=exercise_id,
                        pr_type=PRType.MAX_REPS,
                        value=most_reps["reps"],
                        session_id=session.id,
                        session_set_id=most_reps["set"].id,
                        db=db,
                    )
                    if reps_pr:
                        new_prs.append(reps_pr)

            if new_prs:
                logger.info(f"Achieved {len(new_prs)} new PRs in session {session.id}")

            return new_prs

        except Exception as e:
            logger.error(f"Error checking PRs for session {session.id}: {str(e)}")
            return []

    @staticmethod
    def _check_and_update_pr(
        user_id: int,
        exercise_id: int,
        pr_type: PRType,
        value: int,
        session_id: int,
        session_set_id: Optional[int],
        db: Session,
    ) -> Optional[PersonalRecord]:
        """
        Check if a value represents a new PR and update if so.

        Returns:
            The new PR record if it was a PR, None otherwise
        """
        try:
            current_pr = (
                db.query(PersonalRecord)
                .filter(
                    PersonalRecord.user_id == user_id,
                    PersonalRecord.exercise_id == exercise_id,
                    PersonalRecord.pr_type == pr_type,
                )
                .order_by(desc(PersonalRecord.value))
                .first()
            )

            if current_pr is None or value > current_pr.value:
                new_pr = PersonalRecord(
                    user_id=user_id,
                    exercise_id=exercise_id,
                    session_id=session_id,
                    session_set_id=session_set_id,
                    pr_type=pr_type,
                    value=value,
                    achieved_at=datetime.now(timezone.utc),
                )
                db.add(new_pr)
                db.commit()
                db.refresh(new_pr)

                logger.info(
                    f"New PR! User {user_id} achieved {pr_type.value}={value} "
                    f"for exercise {exercise_id}"
                )
                return new_pr

            return None

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating PR: {str(e)}")
            return None

    @staticmethod
    def get_user_prs(
        user_id: int,
        exercise_id: Optional[int],
        pr_type: Optional[PRType],
        session_id: Optional[int],
        db: Session,
    ) -> list[PersonalRecord]:
        """
        Get personal records for a user.

        Args:
            user_id: ID of the user
            exercise_id: Optional filter by exercise
            pr_type: Optional filter by PR type
            db: Database session

        Returns:
            List of personal records
        """
        try:
            query = db.query(PersonalRecord).filter(PersonalRecord.user_id == user_id)

            if exercise_id:
                query = query.filter(PersonalRecord.exercise_id == exercise_id)

            if pr_type:
                query = query.filter(PersonalRecord.pr_type == pr_type)

            if session_id:
                query = query.filter(PersonalRecord.session_id == session_id)

            prs = query.order_by(desc(PersonalRecord.achieved_at)).all()

            return prs

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching PRs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch personal records",
            )

    @staticmethod
    def get_current_prs_by_exercise(user_id: int, db: Session) -> dict:
        """
        Get the current (best) PR for each exercise and PR type.

        Args:
            user_id: ID of the user
            db: Database session

        Returns:
            Dictionary organized by exercise_id, then pr_type
        """
        try:
            prs = (
                db.query(PersonalRecord)
                .filter(PersonalRecord.user_id == user_id)
                .order_by(
                    PersonalRecord.exercise_id,
                    PersonalRecord.pr_type,
                    desc(PersonalRecord.value),
                )
                .all()
            )

            result = {}
            seen = set()

            for pr in prs:
                key = (pr.exercise_id, pr.pr_type)
                if key not in seen:
                    if pr.exercise_id not in result:
                        result[pr.exercise_id] = {}
                    result[pr.exercise_id][pr.pr_type] = pr
                    seen.add(key)

            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching current PRs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch personal records",
            )

    @staticmethod
    def get_pr_summary(user_id: int, db: Session) -> dict:
        """
        Get a summary of PRs for a user.

        Args:
            user_id: ID of the user
            db: Database session

        Returns:
            Summary statistics about PRs
        """
        try:
            total_prs = (
                db.query(PersonalRecord)
                .filter(PersonalRecord.user_id == user_id)
                .count()
            )

            recent_prs = (
                db.query(PersonalRecord)
                .filter(PersonalRecord.user_id == user_id)
                .order_by(desc(PersonalRecord.achieved_at))
                .limit(10)
                .all()
            )

            prs_by_type = (
                db.query(PersonalRecord.pr_type, func.count(PersonalRecord.id))
                .filter(PersonalRecord.user_id == user_id)
                .group_by(PersonalRecord.pr_type)
                .all()
            )

            prs_by_type_dict = {pr_type.value: count for pr_type, count in prs_by_type}

            return {
                "total_prs": total_prs,
                "recent_prs": recent_prs,
                "prs_by_type": prs_by_type_dict,
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching PR summary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch PR summary",
            )

    @staticmethod
    def delete_pr(pr_id: int, user_id: int, db: Session) -> PersonalRecord:
        """
        Delete a personal record (if user owns it).

        Args:
            pr_id: ID of the PR to delete
            user_id: ID of the user (for authorization)
            db: Database session

        Returns:
            The deleted PR
        """
        try:
            pr = (
                db.query(PersonalRecord)
                .filter(PersonalRecord.id == pr_id, PersonalRecord.user_id == user_id)
                .first()
            )

            if not pr:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Personal record not found",
                )

            db.delete(pr)
            db.commit()

            logger.info(f"Deleted PR {pr_id} for user {user_id}")
            return pr

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting PR: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete personal record",
            )
