import logging
from datetime import datetime, timedelta
from celery import Celery

from .config import get_settings

settings = get_settings()
celery_app = Celery("news_tasks", broker=settings.redis_url or "redis://localhost:6379/0", backend=settings.redis_url or "redis://localhost:6379/0")
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def notify_new_news(self, news_id: int):
    message = f"Notify users about new news {news_id} at {datetime.utcnow().isoformat()}"
    with open("notifications.log", "a") as f:
        f.write(message + "\n")
    logger.info(message)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def weekly_digest(self):
    week_ago = datetime.utcnow() - timedelta(days=7)
    message = f"Weekly digest starting {week_ago.date()} generated {datetime.utcnow().isoformat()}"
    with open("notifications.log", "a") as f:
        f.write(message + "\n")
    logger.info(message)
