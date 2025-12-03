import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import redis

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        if settings.redis_url:
            try:
                self.client = redis.from_url(settings.redis_url)
                self.client.ping()
                logger.info("Connected to Redis cache")
            except Exception as exc:
                logger.warning("Redis unavailable: %s", exc)
                self.client = None
        self.fallback: dict[str, Any] = {}

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        if self.client:
            self.client.setex(key, ttl_seconds or 300, json.dumps(value, default=str))
        else:
            expire = datetime.utcnow() + timedelta(seconds=ttl_seconds or 300)
            self.fallback[key] = (value, expire)

    def get_json(self, key: str) -> Any | None:
        if self.client:
            raw = self.client.get(key)
            if raw:
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return None
            return None
        value = self.fallback.get(key)
        if not value:
            return None
        payload, expire = value
        if datetime.utcnow() > expire:
            self.fallback.pop(key, None)
            return None
        return payload

    def delete(self, key: str) -> None:
        if self.client:
            self.client.delete(key)
        else:
            self.fallback.pop(key, None)

    def set_session(self, session_id: str, data: dict, ttl_seconds: int) -> None:
        self.set_json(f"session:{session_id}", data, ttl_seconds)

    def get_session(self, session_id: str) -> Optional[dict]:
        return self.get_json(f"session:{session_id}")

    def delete_session(self, session_id: str) -> None:
        self.delete(f"session:{session_id}")


cache_client = CacheClient()
