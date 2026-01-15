from datetime import datetime
from pydantic import BaseModel

from app.schemas.workout_exercise import WorkoutExerciseSchema


class CreateWorkoutPayload(BaseModel):
    name: str
    notes: str | None = None


class UpdateWorkoutPayload(BaseModel):
    name: str | None = None
    notes: str | None = None


class WorkoutSchema(BaseModel):
    id: int
    name: str
    notes: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime
    workout_exercises: list[WorkoutExerciseSchema] | None


class AllWorkoutResponse(BaseModel):
    success: bool
    data: list[WorkoutSchema]


class WorkoutResponse(BaseModel):
    success: bool
    data: WorkoutSchema


class WorkoutResponseWithMsg(BaseModel):
    success: bool
    data: WorkoutSchema
    message: str
