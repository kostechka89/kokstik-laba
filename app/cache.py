import json
import os
from datetime import datetime
from typing import Any

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

NEWS_CACHE_TTL_SECONDS = int(os.getenv("NEWS_CACHE_TTL_SECONDS", "300"))
USER_CACHE_TTL_SECONDS = int(os.getenv("USER_CACHE_TTL_SECONDS", "300"))

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Type not serializable: {type(value)}")


def _json_loads(payload: str) -> dict[str, Any]:
    return json.loads(payload)


def cache_user(user_id: int, data: dict[str, Any]) -> None:
    redis_client.setex(
        f"user:{user_id}",
        USER_CACHE_TTL_SECONDS,
        json.dumps(data, default=_json_default),
    )


def get_cached_user(user_id: int) -> dict[str, Any] | None:
    payload = redis_client.get(f"user:{user_id}")
    if not payload:
        return None
    return _json_loads(payload)


def invalidate_user(user_id: int) -> None:
    redis_client.delete(f"user:{user_id}")


def cache_news(news_id: int, data: dict[str, Any]) -> None:
    redis_client.setex(
        f"news:{news_id}",
        NEWS_CACHE_TTL_SECONDS,
        json.dumps(data, default=_json_default),
    )


def get_cached_news(news_id: int) -> dict[str, Any] | None:
    payload = redis_client.get(f"news:{news_id}")
    if not payload:
        return None
    return _json_loads(payload)


def invalidate_news(news_id: int) -> None:
    redis_client.delete(f"news:{news_id}")


def cache_news_list(data: list[dict[str, Any]]) -> None:
    redis_client.setex(
        "news:list",
        NEWS_CACHE_TTL_SECONDS,
        json.dumps(data, default=_json_default),
    )


def get_cached_news_list() -> list[dict[str, Any]] | None:
    payload = redis_client.get("news:list")
    if not payload:
        return None
    return json.loads(payload)


def invalidate_news_list() -> None:
    redis_client.delete("news:list")


def cache_refresh_session(jti: str, data: dict[str, Any], ttl_seconds: int) -> None:
    redis_client.setex(
        f"refresh_session:{jti}",
        ttl_seconds,
        json.dumps(data, default=_json_default),
    )
    redis_client.sadd(f"user_sessions:{data['user_id']}", jti)


def get_refresh_session(jti: str) -> dict[str, Any] | None:
    payload = redis_client.get(f"refresh_session:{jti}")
    if not payload:
        return None
    return _json_loads(payload)


def remove_refresh_session(jti: str, user_id: int) -> None:
    redis_client.delete(f"refresh_session:{jti}")
    redis_client.srem(f"user_sessions:{user_id}", jti)


def replace_refresh_session(
    old_jti: str, new_jti: str, data: dict[str, Any], ttl_seconds: int
) -> None:
    remove_refresh_session(old_jti, data["user_id"])
    cache_refresh_session(new_jti, data, ttl_seconds)


def list_user_sessions(user_id: int) -> list[dict[str, Any]]:
    session_ids = redis_client.smembers(f"user_sessions:{user_id}")
    sessions: list[dict[str, Any]] = []
    for session_id in session_ids:
        payload = redis_client.get(f"refresh_session:{session_id}")
        if payload:
            sessions.append(_json_loads(payload))
        else:
            redis_client.srem(f"user_sessions:{user_id}", session_id)
    return sessions
