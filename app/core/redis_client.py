import redis
from app.core.config import get_settings

settings = get_settings()
redis_client: redis.Redis | None = None

def init_redis() -> None:
    global redis_client
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)

def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        redis_client.close()
        redis_client = None