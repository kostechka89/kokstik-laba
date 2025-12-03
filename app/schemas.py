from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

from .models import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_verified_author: bool = False
    avatar: Optional[str] = None
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    registered_at: datetime

    class Config:
        orm_mode = True


class NewsBase(BaseModel):
    title: str
    content: Dict[str, Any]
    cover: Optional[str] = None


class NewsCreate(NewsBase):
    author_id: int


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    cover: Optional[str] = None


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    news_id: int
    author_id: int


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentOut(CommentBase):
    id: int
    news_id: int
    author_id: int
    published_at: datetime

    class Config:
        orm_mode = True


class NewsOut(NewsBase):
    id: int
    published_at: datetime
    author_id: int
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: UserRole


class SessionOut(BaseModel):
    session_id: str
    user_agent: str
    user_id: int
    expires_at: datetime
