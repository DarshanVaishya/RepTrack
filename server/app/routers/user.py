from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import CreateUserPayload, UpdateUserPayload


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


@router.put("/{user_id}")
def update_user_details(
    user_id: int, update_data: UpdateUserPayload, db: Session = Depends(get_db)
):
    user = UserService.update_user_details(user_id, update_data, db)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.delete_user(user_id, db)
    return user
