import json
from typing import Any

import redis
from fastapi.encoders import jsonable_encoder
from redis import Redis

from app.core.config import get_settings


class CacheService:
    def __init__(self) -> None:
        settings = get_settings()
        try:
            self.client: Redis | None = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            self.client.ping()
        except Exception:
            self.client = None

        self.local_cache: dict[str, Any] = {}

    def get_json(self, key: str) -> Any | None:
        if self.client:
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        return self.local_cache.get(key)

    def set_json(self, key: str, value: Any, ttl: int) -> None:
        payload = jsonable_encoder(value)

        if self.client:
            self.client.setex(
                key,
                ttl,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            )
        else:
            self.local_cache[key] = payload

    def delete(self, key: str) -> None:
        if self.client:
            self.client.delete(key)
        else:
            self.local_cache.pop(key, None)


cache_service = CacheService()
