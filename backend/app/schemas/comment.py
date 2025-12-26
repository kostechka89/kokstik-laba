from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserPublic


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    news_id: int


class CommentUpdate(BaseModel):
    text: str


class CommentRead(CommentBase):
    id: int
    published_at: datetime
    news_id: int
    author_id: int
    author: UserPublic | None = None

    class Config:
        from_attributes = True
