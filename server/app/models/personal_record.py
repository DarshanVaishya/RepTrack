from enum import Enum as PyEnum
from datetime import datetime

from app.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class PRType(PyEnum):
    MAX_VOLUME = "max_volume"
    MAX_SINGLE_SET = "max_single_set"
    MAX_WEIGHT = "max_weight"
    MAX_REPS = "max_reps"


class PersonalRecord(Base):
    __tablename__ = "personal_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("workout_session.id"), nullable=True)

    pr_type = Column(
        Enum(PRType, name="prtype", create_type=False),
        nullable=False,
    )
    value = Column(Integer, nullable=False)
    session_set_id = Column(Integer, ForeignKey("session_set.id"), nullable=True)
    notes = Column(String(500), nullable=True)

    achieved_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
    )

    # Relationships
    user = relationship("User")
    exercise = relationship("Exercise")
    session = relationship("WorkoutSession")
    session_set = relationship("SessionSet")

    def __repr__(self):
        return f"<PersonalRecord {self.pr_type.value}={self.value} for exercise_id={self.exercise_id} user_id={self.user_id}>"
