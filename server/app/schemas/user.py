from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class CreateUserPayload(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
