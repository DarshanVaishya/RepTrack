from pydantic import BaseModel

from app.models.workout_set import SetType


class CreateWorkoutSetPayload(BaseModel):
    reps: int
    weight: int
    set_type: SetType
    order_index: int
    notes: str
    workout_exercise_id: int
