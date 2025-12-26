from datetime import datetime
import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models
from app.auth import decode_token
from app.cache import cache_user, get_cached_user
from app.db import get_db

security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user_id = int(payload.get("sub", 0))
    cached = get_cached_user(user_id)
    if cached:
        logger.info("user cache hit: %s", user_id)
        cached["registered_at"] = datetime.fromisoformat(cached["registered_at"])
        user = models.User(**cached)
        user.id = user_id
        return user
    logger.info("user cache miss: %s", user_id)
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    cache_user(
        user.id,
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "registered_at": user.registered_at,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "avatar_url": user.avatar_url,
        },
    )
    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


def require_verified_author(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not (current_user.is_verified or current_user.is_admin):
        raise HTTPException(status_code=403, detail="Author is not verified")
    return current_user


def get_news_or_404(news_id: int, db: Session = Depends(get_db)) -> models.News:
    from app.cache import cache_news, get_cached_news

    cached = get_cached_news(news_id)
    if cached:
        logger.info("news cache hit: %s", news_id)
        cached["published_at"] = datetime.fromisoformat(cached["published_at"])
        news = models.News(**cached)
        news.id = news_id
        return news
    logger.info("news cache miss: %s", news_id)
    news = db.get(models.News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
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
    return news


def get_comment_or_404(
    comment_id: int, db: Session = Depends(get_db)
) -> models.Comment:
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


def require_news_owner_or_admin(
    news: models.News = Depends(get_news_or_404),
    current_user: models.User = Depends(get_current_user),
) -> models.News:
    if not (current_user.is_admin or news.author_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return news


def require_comment_owner_or_admin(
    comment: models.Comment = Depends(get_comment_or_404),
    current_user: models.User = Depends(get_current_user),
) -> models.Comment:
    if not (current_user.is_admin or comment.author_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return comment


def get_user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "unknown")
