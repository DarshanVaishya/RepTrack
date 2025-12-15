from sqlalchemy.orm import Session
from app.config import get_settings
from fastapi import Depends, FastAPI
from app.database import get_db

from app.routers import user, exercise, workout_set, workout_exercise, workout


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
)

app.include_router(user.router)
app.include_router(exercise.router)
app.include_router(workout_set.router)
app.include_router(workout_exercise.router)
app.include_router(workout.router)
