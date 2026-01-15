from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime, timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings
from app.services.metrics import NOTIFICATIONS_SENT


settings = get_settings()
celery_app = Celery("worker", broker=settings.redis_url, backend=settings.redis_url)


celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "app.workers.tasks.send_weekly_digest_for_all",
        "schedule": crontab(minute=0, hour=9, day_of_week="sun"),
    }
}


logger = logging.getLogger("notifications")
log_path = Path("/var/log/app/notifications.log")
log_path.parent.mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(log_path)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_news_notification(self, user_email: str, news_id: int):
    """Send single-news notification.

    For this educational project we only write into notifications.log.
    """
    message = f"{datetime.utcnow().isoformat()} send news {news_id} to {user_email}"
    logger.info(message)
    NOTIFICATIONS_SENT.inc()
    return message


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_weekly_digest(self, user_email: str, news_ids: list[int]):
    """Send digest for a single user."""
    message = f"{datetime.utcnow().isoformat()} digest {news_ids} to {user_email}"
    logger.info(message)
    NOTIFICATIONS_SENT.inc(len(news_ids))
    return message


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def send_weekly_digest_for_all(self):
    """Build and send weekly digest to all users.

    Designed to be scheduled by celery beat.
    Includes an idempotency guard via Redis (if available).
    """
    from sqlalchemy.orm import Session

    from app.db.models import News, User
    from app.db.session import SessionLocal

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        news_ids = [n.id for n in db.query(News).filter(News.published_at >= week_ago).all()]

        for user in users:
            digest_key = f"digest:{now.date().isoformat()}:{user.id}"
            try:
                from app.services.cache import cache_service

                if cache_service.get_json(digest_key):
                    continue
                cache_service.set_json(digest_key, True, ttl=60 * 60 * 24 * 8)
            except Exception:
                pass

            try:
                send_weekly_digest.delay(user.email, news_ids)
            except Exception:
                pass
    finally:
        db.close()

    return {"users": len(users), "news": len(news_ids)}
