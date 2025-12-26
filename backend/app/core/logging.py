import logging
import os
from pathlib import Path

import structlog


def configure_logging():
    """Configure structlog JSON logs.

    - Always logs to stdout (so `docker logs` works).
    - Optionally logs to a file if LOG_FILE is set (for ELK/Logstash file input).
    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Ensure at least one stdout handler exists
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        root.addHandler(sh)

    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.INFO)
            root.addHandler(fh)
        except Exception:
            # Never crash app because of logging file issues
            pass

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()
