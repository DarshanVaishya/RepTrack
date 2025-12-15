from enum import Enum as PyEnum

from app.database import Base
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class SetType(PyEnum):
    WARMUP = "warmup"
    NORMAL = "normal"
    FAILURE = "failure"
    DROPSET = "dropset"


class WorkoutSet(Base):
    __tablename__ = "workout_set"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reps = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    set_type = Column(Enum(SetType), nullable=False, default=SetType.NORMAL)
    order_index = Column(Integer, nullable=False)
    notes = Column(String(500))
    workout_exercise_id = Column(
        Integer, ForeignKey("workout_exercise.id"), nullable=False
    )

    # Relationships
    workout_exercise = relationship("WorkoutExercise", back_populates="sets")
