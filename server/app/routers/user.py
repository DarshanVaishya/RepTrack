from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import CreateUserPayload


router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
def create_new_user(user_data: CreateUserPayload, db: Session = Depends(get_db)):
    new_user = UserService.create_new_user(user_data, db)
    return new_user


@router.get("")
def get_all_users(db: Session = Depends(get_db)):
    users = UserService.get_all_users(db)
    return users


@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(user_id, db)
    return user
