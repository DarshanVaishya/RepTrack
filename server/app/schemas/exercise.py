from datetime import datetime
from pydantic import BaseModel

from app.models.exercise import Equipment, MuscleGroup


class CreateExercisePayload(BaseModel):
    name: str
    description: str | None = None
    muscle_group: MuscleGroup
    equipment: Equipment


class UpdateExercisePayload(BaseModel):
    name: str | None = None
    description: str | None = None
    muscle_group: MuscleGroup | None = None
    equipment: Equipment | None = None


class ExerciseSchema(BaseModel):
    id: int
    name: str
    description: str | None = None
    muscle_group: MuscleGroup
    equipment: Equipment
    created_at: datetime


class AllExercisesResponse(BaseModel):
    success: bool
    data: list[ExerciseSchema]


class ExerciseResponse(BaseModel):
    success: bool
    data: ExerciseSchema


class ExerciseResponseWithMsg(BaseModel):
    success: bool
    message: str
    data: ExerciseSchema
