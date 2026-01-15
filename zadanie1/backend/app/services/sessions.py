import uuid
from datetime import timedelta
from app.core.config import get_settings
from app.services.cache import cache_service


class SessionStore:
    def create(self, user_id: int, user_agent: str) -> str:
        session_id = str(uuid.uuid4())
        settings = get_settings()
        ttl = int(timedelta(minutes=settings.refresh_token_expire_minutes).total_seconds())
        cache_service.set_json(
            f"session:{session_id}",
            {"user_id": user_id, "user_agent": user_agent},
            ttl,
        )
        cache_service.set_json(f"user_sessions:{user_id}:{session_id}", True, ttl)
        return session_id

    def get(self, session_id: str) -> dict | None:
        return cache_service.get_json(f"session:{session_id}")

    def delete(self, session_id: str) -> None:
        cache_service.delete(f"session:{session_id}")

    def list_for_user(self, user_id: int) -> list[dict]:
        sessions = []
        if cache_service.client:
            keys = cache_service.client.keys(f"user_sessions:{user_id}:*")
        else:
            keys = [key for key in cache_service.local_cache if key.startswith(f"user_sessions:{user_id}:")]
        for key in keys:
            session_id = key.split(":")[-1]
            data = self.get(session_id)
            if data:
                sessions.append({"session_id": session_id, "user_agent": data["user_agent"]})
        return sessions


session_store = SessionStore()
