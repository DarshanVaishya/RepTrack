from pydantic import BaseModel

from app.models.workout_set import SetType


# TODO: Do I set order_index from the backend or frontend?
class CreateWorkoutSetPayload(BaseModel):
    reps: int
    weight: int
    set_type: SetType
    order_index: int
    notes: str


class UpdateWorkoutSetPayload(BaseModel):
    reps: int | None = None
    weight: int | None = None
    set_type: SetType | None = None
    order_index: int | None = None
    notes: str | None = None


class WorkoutSetSchema(BaseModel):
    id: int
    reps: int
    weight: int
    set_type: SetType
    order_index: int
    notes: str
    workout_exercise_id: int


class WorkoutSetResponse(BaseModel):
    success: bool
    data: WorkoutSetSchema


class AllWorkoutSetResponse(BaseModel):
    success: bool
    data: list[WorkoutSetSchema]


class WorkoutSetResponseWithMsg(BaseModel):
    success: bool
    data: WorkoutSetSchema
    message: str
