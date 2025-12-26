from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar: str | None = None
    is_verified_author: bool = False
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True
