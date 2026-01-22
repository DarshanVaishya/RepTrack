from app.config import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    user,
    exercise,
    workout_set,
    workout_exercise,
    workout,
    workout_session,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(exercise.router)
app.include_router(workout_set.router)
app.include_router(workout_exercise.router)
app.include_router(workout.router)
app.include_router(workout_session.router)
