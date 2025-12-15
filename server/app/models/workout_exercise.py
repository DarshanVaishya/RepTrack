from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base
from app.models.exercise import MuscleGroup, Equipment


class WorkoutExercise(Base):
    __tablename__ = "workout_exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    notes = Column(String(500))
    workout_id = Column(Integer, ForeignKey("workout.id"), nullable=False)

    # Relationships
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise")
    sets = relationship(
        "WorkoutSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.order_index",
    )
