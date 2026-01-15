from sqlalchemy.orm import Session
from app.db.models import News
from app.schemas.news import NewsCreate, NewsUpdate


def create_news(db: Session, author_id: int, payload: NewsCreate) -> News:
    news = News(
        title=payload.title,
        content=payload.content,
        cover=payload.cover,
        author_id=author_id,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def list_news(db: Session) -> list[News]:
    return db.query(News).all()


def get_news(db: Session, news_id: int) -> News | None:
    return db.query(News).filter(News.id == news_id).first()


def update_news(db: Session, news: News, payload: NewsUpdate) -> News:
    if payload.title is not None:
        news.title = payload.title
    if payload.content is not None:
        news.content = payload.content
    if payload.cover is not None:
        news.cover = payload.cover
    db.commit()
    db.refresh(news)
    return news


def delete_news(db: Session, news: News) -> None:
    db.delete(news)
    db.commit()
