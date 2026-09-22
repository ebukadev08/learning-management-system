from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    class config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"