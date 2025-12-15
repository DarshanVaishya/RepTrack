from pydantic import BaseModel


class CreateWorkoutExercisePayload(BaseModel):
    exercise_id: int
    order_index: int
    notes: str | None = None
    workout_id: int


class UpdateWorkoutExercisePayload(BaseModel):
    order_index: int | None = None
    notes: str | None = None
