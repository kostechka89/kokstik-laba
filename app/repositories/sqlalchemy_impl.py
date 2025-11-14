from sqlalchemy.orm import Session
from app.models.models import User, News, Comment

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, email: str, verified_author: bool, avatar_url: str):
        user = User(
            name=name,
            email=email,
            verified_author=verified_author,
            avatar_url=avatar_url
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get(self, user_id: int):
        return self.session.get(User, user_id)

    def list(self, skip: int = 0, limit: int = 100):
        return self.session.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, **kwargs):
        obj = self.session.get(User, user_id)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, user_id: int):
        obj = self.session.get(User, user_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True


class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, content: dict, author_id: int, cover_url: str | None = None):
        news = News(
            title=title,
            content=content,
            author_id=author_id,
            cover_url=cover_url
        )
        self.session.add(news)
        self.session.commit()
        self.session.refresh(news)
        return news

    def get(self, news_id: int):
        return self.session.get(News, news_id)

    def list(self, skip: int = 0, limit: int = 100):
        return self.session.query(News).offset(skip).limit(limit).all()

    def update(self, news_id: int, **kwargs):
        obj = self.session.get(News, news_id)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, news_id: int):
        obj = self.session.get(News, news_id)
        if not obj:
            return False
        
        self.session.query(Comment).filter(Comment.news_id == news_id).delete()
        self.session.delete(obj)
        self.session.commit()
        return True


class CommentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, news_id: int, author_id: int, text: str):
        comment = Comment(
            news_id=news_id,
            author_id=author_id,
            text=text
        )
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment

    def get(self, comment_id: int):
        return self.session.get(Comment, comment_id)

    def list(self, news_id: int):
        return self.session.query(Comment).filter(Comment.news_id == news_id).all()

    def update(self, comment_id: int, **kwargs):
        obj = self.session.get(Comment, comment_id)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, comment_id: int):
        obj = self.session.get(Comment, comment_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True