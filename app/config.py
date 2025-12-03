import os
from functools import lru_cache
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    app_name: str = "News API"
    database_url: AnyUrl | str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret")
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    redis_url: str | None = os.getenv("REDIS_URL")
    github_client_id: str = os.getenv("GITHUB_CLIENT_ID", "placeholder")
    github_client_secret: str = os.getenv("GITHUB_CLIENT_SECRET", "placeholder")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
