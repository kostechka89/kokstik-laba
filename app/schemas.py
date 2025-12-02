from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, EmailStr, Field


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    news_id: int
    author_id: int


class CommentUpdate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    author_id: int
    news_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class NewsBase(BaseModel):
    title: str
    content: Any
    cover_url: Optional[str] = None


class NewsCreate(NewsBase):
    author_id: int


class NewsUpdate(NewsBase):
    pass


class News(NewsBase):
    id: int
    author_id: int
    published_at: datetime
    comments: List[Comment] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    is_verified_author: bool = False


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified_author: Optional[bool] = None


class User(UserBase):
    id: int
    registered_at: datetime
    is_verified_author: bool

    class Config:
        orm_mode = True
