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
