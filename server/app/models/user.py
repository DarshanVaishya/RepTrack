from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import deferred, relationship
from app.database import Base


class UserRole(PyEnum):
    COACH = "coach"
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = deferred(Column(String(255), nullable=False))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    workouts = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    workout_sessions = relationship(
        "WorkoutSession", back_populates="user", cascade="all, delete-orphan"
    )
