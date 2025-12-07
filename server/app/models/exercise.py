from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class MuscleGroup(PyEnum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    LEGS = "legs"
    CORE = "core"
    CALVES = "calves"
    FULL_BODY = "full_body"


class Equipment(PyEnum):
    BARBELL = "barbell"
    DUMBBELLS = "dumbbells"
    CABLE_MACHINE = "cable_machine"
    MACHINE = "machine"
    BODYWEIGHT = "bodyweight"
    KETTLEBELL = "kettlebell"
    MEDICINE_BALL = "medicine_ball"
    RESISTANCE_BAND = "resistance_band"
    CARDIO = "cardio"


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000))
    muscle_group = Column(Enum(MuscleGroup), nullable=True)
    equipment = Column(Enum(Equipment), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
