from __future__ import annotations

from datetime import datetime, timedelta

from celery.schedules import crontab
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.celery_app import celery_app
from app.db import SessionLocal
from app.logging_utils import get_notifications_logger
from app.models import News, User

logger = get_notifications_logger()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:  # noqa: ANN001
    sender.add_periodic_task(
        crontab(hour=9, minute=0, day_of_week="sun"),
        send_weekly_digest.s(),
        name="weekly_news_digest",
    )


def _get_session() -> Session:
    return SessionLocal()


def _log_notification(message: str) -> None:
    logger.info(message)


def _already_sent(key: str) -> bool:
    return redis_client.exists(key) == 1


def _mark_sent(key: str, ttl_seconds: int) -> None:
    redis_client.setex(key, ttl_seconds, "1")


@celery_app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_news_notifications(news_id: int) -> None:
    session = _get_session()
    try:
        _log_notification(f"task_start send_news_notifications news_id={news_id}")
        news = session.get(News, news_id)
        if not news:
            return
        users = session.query(User).order_by(User.id).all()
        for user in users:
            cache_key = f"notif:news:{news_id}:user:{user.id}"
            if _already_sent(cache_key):
                continue
            _log_notification(
                f"new_news email to={user.email} news_id={news.id} title={news.title}"
            )
            _mark_sent(cache_key, 60 * 60 * 24 * 7)
        _log_notification(f"task_done send_news_notifications news_id={news_id}")
    finally:
        session.close()


@celery_app.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_weekly_digest() -> None:
    session = _get_session()
    try:
        _log_notification("task_start send_weekly_digest")
        since = datetime.utcnow() - timedelta(days=7)
        news_items = (
            session.query(News)
            .filter(News.published_at >= since)
            .order_by(News.published_at.desc())
            .all()
        )
        users = session.query(User).order_by(User.id).all()
        for user in users:
            cache_key = f"notif:digest:{datetime.utcnow().date().isoformat()}:user:{user.id}"
            if _already_sent(cache_key):
                continue
            titles = ", ".join(item.title for item in news_items) or "no news"
            _log_notification(
                f"weekly_digest to={user.email} news_count={len(news_items)} titles={titles}"
            )
            _mark_sent(cache_key, 60 * 60 * 24 * 8)
        _log_notification("task_done send_weekly_digest")
    finally:
        session.close()
