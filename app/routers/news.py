import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from datetime import datetime

from app import models, schemas
from app.cache import (
    cache_news,
    cache_news_list,
    get_cached_news_list,
    invalidate_news,
    invalidate_news_list,
)
from app.tasks import send_news_notifications
from app.db import get_db
from app.dependencies import (
    get_current_user,
    get_news_or_404,
    require_news_owner_or_admin,
    require_verified_author,
)

router = APIRouter(prefix="/news", tags=["news"], dependencies=[Depends(get_current_user)])
logger = logging.getLogger(__name__)


@router.post("", response_model=schemas.NewsRead, status_code=status.HTTP_201_CREATED)
def create_news(
    payload: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_verified_author),
):
    news = models.News(
        title=payload.title,
        content=payload.content,
        cover_url=payload.cover_url,
        author_id=current_user.id,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    cache_news(
        news.id,
        {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "published_at": news.published_at,
            "cover_url": news.cover_url,
            "author_id": news.author_id,
        },
    )
    invalidate_news_list()
    send_news_notifications.delay(news.id)
    return news


@router.get("", response_model=list[schemas.NewsRead])
def list_news(db: Session = Depends(get_db)):
    cached = get_cached_news_list()
    if cached:
        logger.info("news cache hit: list")
        news_items: list[models.News] = []
        for item in cached:
            item["published_at"] = datetime.fromisoformat(item["published_at"])
            news_items.append(models.News(**item))
        return news_items
    logger.info("news cache miss: list")
    news_items = db.query(models.News).order_by(models.News.id).all()
    cache_news_list(
        [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "published_at": item.published_at,
                "cover_url": item.cover_url,
                "author_id": item.author_id,
            }
            for item in news_items
        ]
    )
    return news_items


@router.get("/{news_id}", response_model=schemas.NewsRead)
def get_news(news: models.News = Depends(get_news_or_404)):
    logger.info("news cache check: detail %s", news.id)
    return news


@router.put("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    payload: schemas.NewsUpdate,
    db: Session = Depends(get_db),
    news: models.News = Depends(require_news_owner_or_admin),
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    cache_news(
        news.id,
        {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "published_at": news.published_at,
            "cover_url": news.cover_url,
            "author_id": news.author_id,
        },
    )
    invalidate_news_list()
    return news


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    db: Session = Depends(get_db),
    news: models.News = Depends(require_news_owner_or_admin),
):
    db.delete(news)
    db.commit()
    invalidate_news(news.id)
    invalidate_news_list()
    return None
