from datetime import datetime
from pydantic import BaseModel


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

    class Config:
        from_attributes = True
