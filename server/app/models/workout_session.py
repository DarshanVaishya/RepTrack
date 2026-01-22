from enum import Enum as PyEnum
from app.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class SessionStatus(PyEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkoutSession(Base):
    __tablename__ = "workout_session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workout.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS
    )
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(1000))
    duration_minutes = Column(Integer, nullable=True)  # Total workout duration

    # Relationships
    workout = relationship("Workout")
    user = relationship("User", back_populates="workout_sessions")
    session_exercises = relationship(
        "SessionExercise", back_populates="session", cascade="all, delete-orphan"
    )
