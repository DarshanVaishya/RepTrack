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
