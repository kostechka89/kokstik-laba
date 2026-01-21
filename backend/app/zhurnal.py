import json
import logging
import sys
from datetime import datetime, timezone


def nastroit_loger(app_env: str) -> logging.Logger:
    logger = logging.getLogger("registratsiya")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    zapis_eventa(logger, "INFO", "start", sreda=app_env)
    return logger


def zapis_eventa(logger: logging.Logger, uroven: str, sobytie: str, **dannye: str) -> None:
    zapis = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": uroven,
        "event": sobytie,
        "data": dannye,
    }
    logger.log(getattr(logging, uroven, logging.INFO), json.dumps(zapis, ensure_ascii=False))
