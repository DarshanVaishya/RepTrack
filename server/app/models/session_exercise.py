from app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship


class SessionExercise(Base):
    __tablename__ = "session_exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("workout_session.id"), nullable=False)
    workout_exercise_id = Column(
        Integer, ForeignKey("workout_exercise.id"), nullable=False
    )
    order_index = Column(Integer, nullable=False)
    notes = Column(String(500))
    is_completed = Column(Boolean, default=False)

    # Relationships
    session = relationship("WorkoutSession", back_populates="session_exercises")
    workout_exercise = relationship("WorkoutExercise")
    session_sets = relationship(
        "SessionSet",
        back_populates="session_exercise",
        cascade="all, delete-orphan",
        order_by="SessionSet.order_index",
    )
