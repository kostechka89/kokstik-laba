import os

from celery import Celery
from celery.signals import worker_shutdown

from app.logging_utils import get_notifications_logger

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "news_service",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)


@worker_shutdown.connect
def handle_worker_shutdown(sig, how, exitcode, **kwargs) -> None:  # noqa: ANN001
    logger = get_notifications_logger()
    logger.info("celery worker shutdown sig=%s how=%s exitcode=%s", sig, how, exitcode)
