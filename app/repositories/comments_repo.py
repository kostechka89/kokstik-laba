from typing import Iterable, Optional
from sqlalchemy.orm import Session

from app.models.models import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, news_id: int, author_id: int, text: str) -> Comment:
        obj = Comment(news_id=news_id, author_id=author_id, text=text)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, comment_id: int) -> Optional[Comment]:
        return self.db.get(Comment, comment_id)

    def list(
        self, *, skip: int = 0, limit: int = 100, news_id: Optional[int] = None
    ) -> Iterable[Comment]:
        q = self.db.query(Comment).order_by(Comment.id.asc())
        if news_id is not None:
            q = q.filter(Comment.news_id == news_id)
        if skip:
            q = q.offset(skip)
        if limit:
            q = q.limit(limit)
        return q.all()

    def update(self, comment_id: int, **fields) -> Optional[Comment]:
        obj = self.get(comment_id)
        if not obj:
            return None
        if "text" in fields and fields["text"] is not None:
            obj.text = fields["text"]
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, comment_id: int) -> bool:
        obj = self.get(comment_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True