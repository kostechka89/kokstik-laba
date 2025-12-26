import logging
import os

NOTIFY_LOG_FILE = os.getenv("NOTIFY_LOG_FILE", "logs/notifications.log")


def get_notifications_logger() -> logging.Logger:
    logger = logging.getLogger("notifications")
    if logger.handlers:
        return logger
    os.makedirs(os.path.dirname(NOTIFY_LOG_FILE), exist_ok=True)
    handler = logging.FileHandler(NOTIFY_LOG_FILE)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
