from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_verified: bool = False
    avatar_url: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_verified: bool | None = None
    avatar_url: str | None = None


class UserRead(UserBase):
    id: int
    registered_at: datetime

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    title: str
    content: dict[str, Any] = Field(default_factory=dict)
    cover_url: str | None = None


class NewsCreate(NewsBase):
    author_id: int


class NewsUpdate(BaseModel):
    title: str | None = None
    content: dict[str, Any] | None = None
    cover_url: str | None = None


class NewsRead(NewsBase):
    id: int
    published_at: datetime
    author_id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    news_id: int
    author_id: int


class CommentUpdate(BaseModel):
    text: str | None = None


class CommentRead(CommentBase):
    id: int
    published_at: datetime
    news_id: int
    author_id: int

    class Config:
        from_attributes = True
