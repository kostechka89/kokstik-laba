from typing import Iterable, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import News


class NewsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        title: str,
        content: Dict[str, Any],
        author_id: int,
        cover_url: Optional[str] = None,
    ) -> News:
        obj = News(
            title=title,
            content=content,
            author_id=author_id,
            cover_url=cover_url,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, news_id: int) -> Optional[News]:
        return self.db.get(News, news_id)

    def list(self, *, skip: int = 0, limit: int = 100) -> Iterable[News]:
        q = self.db.query(News).order_by(News.id.asc())
        if skip:
            q = q.offset(skip)
        if limit:
            q = q.limit(limit)
        return q.all()

    def update(self, news_id: int, **fields) -> Optional[News]:
        obj = self.get(news_id)
        if not obj:
            return None
        for key in ("title", "content", "cover_url"):
            if key in fields and fields[key] is not None:
                setattr(obj, key, fields[key])
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, news_id: int) -> bool:
        obj = self.get(news_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True