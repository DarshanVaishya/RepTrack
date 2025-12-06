from sqlalchemy.orm import Session
from app.config import get_settings
from fastapi import Depends, FastAPI
from app.database import get_db


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
)


@app.get("/")
def test():
    return "Hello, world!"
