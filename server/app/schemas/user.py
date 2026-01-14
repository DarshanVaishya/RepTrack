from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class CreateUserPayload(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class UpdateUserPayload(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: UserRole | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    success: bool
    data: UserSchema


class AllUsersResponse(BaseModel):
    success: bool
    data: list[UserSchema]


class UserResponseWithMsg(BaseModel):
    success: bool
    message: str
    data: UserSchema
