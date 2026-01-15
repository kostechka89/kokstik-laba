from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    redis_url: str = "redis://localhost:6379/0"
    github_client_id: str = "mock"
    github_client_secret: str = "mock"
    frontend_url: str = "http://localhost:5173"
    hawk_token: str | None = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
