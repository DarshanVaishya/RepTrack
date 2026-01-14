from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.database import get_db
from app.schemas.user import (
    AllUsersResponse,
    CreateUserPayload,
    UpdateUserPayload,
    UserResponse,
    UserResponseWithMsg,
)
from app.models import User
from app.utils.auth import get_current_user
from app.utils.formatter import format_response


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponseWithMsg, status_code=201)
def create_new_user(user_data: CreateUserPayload, db: Session = Depends(get_db)):
    new_user = UserService.create_new_user(user_data, db)
    return format_response(new_user, "Successfully created new user.")


@router.get("", response_model=AllUsersResponse, status_code=200)
def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    users = UserService.get_all_users(db)
    return format_response(users)


@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.get_user_by_id(user_id, db)
    return format_response(user)


@router.put("/{user_id}", response_model=UserResponseWithMsg, status_code=200)
def update_user_details(
    user_id: int,
    update_data: UpdateUserPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.update_user_details(user_id, update_data, db)
    return format_response(user, f"Successfully updated user {user_id}")


@router.delete("/{user_id}", response_model=UserResponseWithMsg, status_code=200)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService.delete_user(user_id, db)
    return format_response(user, f"Successfully deleted user {user_id}")


@router.post("/login", status_code=200)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    token = UserService.login_user(form_data, db)
    return token
