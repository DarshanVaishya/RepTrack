from pydantic import BaseModel


class CreateWorkoutPayload(BaseModel):
    name: str
    notes: str | None = None
    user_id: int


class UpdateWorkoutPayload(BaseModel):
    name: str | None = None
    notes: str | None = None
