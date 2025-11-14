from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    verified_author: bool = Field(False, alias="is_verified_author")
    avatar_url: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    verified_author: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    verified_author: bool
    avatar_url: Optional[str] = None
    registered_at: datetime
    is_admin: bool


class NewsCreate(BaseModel):
    title: str
    content: Dict[str, Any]
    author_id: int
    cover_url: Optional[str] = None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    cover_url: Optional[str] = None


class NewsOut(BaseModel):
    id: int
    title: str
    content: Dict[str, Any]
    cover_url: Optional[str] = None
    author_id: int
    published_at: datetime


class CommentCreate(BaseModel):
    news_id: int
    author_id: int = Field(..., alias="user_id")
    text: str = Field(..., alias="content")

    model_config = ConfigDict(populate_by_name=True)


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentOut(BaseModel):
    id: int
    news_id: int
    author_id: int
    text: str
    published_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class SessionOut(BaseModel):
    session_id: str
    user_agent: str
    expires_at: datetime