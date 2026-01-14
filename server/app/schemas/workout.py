from datetime import datetime
from pydantic import BaseModel


class CreateWorkoutPayload(BaseModel):
    name: str
    notes: str | None = None


class UpdateWorkoutPayload(BaseModel):
    name: str | None = None
    notes: str | None = None

    # "notes": "string",
    # "name": "string",
    # "created_at": "2025-12-13T13:45:13.087537-05:00",
    # "id": 1,
    # "user_id": 3,
    # "updated_at": "2025-12-13T13:45:13.087537-05:00"


class WorkoutSchema(BaseModel):
    id: int
    name: str
    notes: str
    user_id: int
    created_at: datetime
    updated_at: datetime


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
