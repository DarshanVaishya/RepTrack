from pydantic import BaseModel


class CreateWorkoutExercisePayload(BaseModel):
    exercise_id: int
    order_index: int
    notes: str | None = None
    workout_id: int


class UpdateWorkoutExercisePayload(BaseModel):
    order_index: int | None = None
    notes: str | None = None


class WorkoutExerciseSchema(BaseModel):
    id: int
    notes: str
    order_index: int
    exercise_id: int
    workout_id: int


class AllWorkoutExercisesResponse(BaseModel):
    success: bool
    data: list[WorkoutExerciseSchema]


class WorkoutExerciseResponse(BaseModel):
    success: bool
    data: WorkoutExerciseSchema


class WorkoutExerciseResponseWithMsg(BaseModel):
    success: bool
    data: WorkoutExerciseSchema
    message: str
