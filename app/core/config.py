from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "news_api"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str 

    DB_BACKEND: str = "postgres"

    JWT_SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GITHUB_CLIENT_ID: str = "your_github_client_id"
    GITHUB_CLIENT_SECRET: str = "your_github_client_secret"
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()