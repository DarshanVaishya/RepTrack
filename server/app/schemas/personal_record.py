from datetime import datetime
from pydantic import BaseModel

from app.models.personal_record import PRType


class PersonalRecordSchema(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    exercise_name: str | None = None
    session_id: int | None
    session_set_id: int | None
    pr_type: PRType
    value: int
    notes: str | None
    achieved_at: datetime

    class Config:
        from_attributes = True


class PersonalRecordsByExercise(BaseModel):
    exercise_id: int
    exercise_name: str
    records: dict[PRType, PersonalRecordSchema]


class PersonalRecordResponse(BaseModel):
    success: bool
    data: PersonalRecordSchema


class AllPersonalRecordsResponse(BaseModel):
    success: bool
    data: list[PersonalRecordSchema]


class PersonalRecordsByExerciseResponse(BaseModel):
    success: bool
    data: list[PersonalRecordsByExercise]


class PRSummary(BaseModel):
    total_prs: int
    recent_prs: list[PersonalRecordSchema]
    prs_by_type: dict[str, int]


class PRSummaryResponse(BaseModel):
    success: bool
    data: PRSummary
