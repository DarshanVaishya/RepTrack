from datetime import datetime
from pydantic import BaseModel
from app.models.workout_session import SessionStatus
from app.models.session_set import SessionSetStatus


# Request Payloads
class CreateWorkoutSessionPayload(BaseModel):
    workout_id: int
    notes: str | None = None


class UpdateWorkoutSessionPayload(BaseModel):
    notes: str | None = None


class CompleteSessionSetPayload(BaseModel):
    actual_reps: int
    actual_weight: int
    notes: str | None = None


# Response Schemas
class SessionSetSchema(BaseModel):
    id: int
    session_exercise_id: int
    workout_set_id: int | None
    planned_reps: int
    planned_weight: int
    actual_reps: int | None
    actual_weight: int | None
    order_index: int
    status: SessionSetStatus
    notes: str | None
    completed_at: datetime | None


class SessionExerciseSchema(BaseModel):
    id: int
    session_id: int
    workout_exercise_id: int
    order_index: int
    notes: str | None
    is_completed: bool
    session_sets: list[SessionSetSchema]


class WorkoutSessionSchema(BaseModel):
    id: int
    workout_id: int
    user_id: int
    status: SessionStatus
    started_at: datetime
    completed_at: datetime | None
    notes: str | None
    duration_minutes: int | None
    session_exercises: list[SessionExerciseSchema] | None
    total_volume: int | None


class WorkoutSessionResponse(BaseModel):
    success: bool
    data: WorkoutSessionSchema


class AllWorkoutSessionsResponse(BaseModel):
    success: bool
    data: list[WorkoutSessionSchema]


class WorkoutSessionResponseWithMsg(BaseModel):
    success: bool
    message: str
    data: WorkoutSessionSchema


class SessionSetResponse(BaseModel):
    success: bool
    data: SessionSetSchema


class SessionSetResponseWithMsg(BaseModel):
    success: bool
    message: str
    data: SessionSetSchema
