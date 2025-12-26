from datetime import datetime
from pydantic import BaseModel


class NewsBase(BaseModel):
    title: str
    content: dict
    cover: str | None = None


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: str | None = None
    content: dict | None = None
    cover: str | None = None


class NewsRead(NewsBase):
    id: int
    published_at: datetime
    author_id: int

    class Config:
        from_attributes = True
