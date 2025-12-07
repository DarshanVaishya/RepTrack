from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import CreateUserPayload, UpdateUserPayload
from app.models import User
from app.utils.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
def create_new_user(user_data: CreateUserPayload, db: Session = Depends(get_db)):
    new_user = UserService.create_new_user(user_data, db)
    return new_user


@router.get("")
def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    users = UserService.get_all_users(db)
    return users


@router.get("/{user_id}")
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.get_user_by_id(user_id, db)
    return user


@router.put("/{user_id}")
def update_user_details(
    user_id: int,
    update_data: UpdateUserPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.update_user_details(user_id, update_data, db)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.delete_user(user_id, db)
    return user


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    token = UserService.login_user(form_data, db)
    return token
