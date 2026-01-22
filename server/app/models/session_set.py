from enum import Enum as PyEnum
from app.database import Base
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


class SessionSetStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SessionSet(Base):
    __tablename__ = "session_set"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_exercise_id = Column(
        Integer, ForeignKey("session_exercise.id"), nullable=False
    )
    workout_set_id = Column(Integer, ForeignKey("workout_set.id"), nullable=True)

    planned_reps = Column(Integer, nullable=False)
    planned_weight = Column(Integer, nullable=False)

    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Integer, nullable=True)

    order_index = Column(Integer, nullable=False)
    status = Column(
        Enum(SessionSetStatus, name="sessionsetstatus", create_type=False),
        nullable=False,
        default=SessionSetStatus.PENDING,
    )
    notes = Column(String(500))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session_exercise = relationship("SessionExercise", back_populates="session_sets")
    workout_set = relationship("WorkoutSet")
