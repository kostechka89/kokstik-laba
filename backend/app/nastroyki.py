from pydantic_settings import BaseSettings, SettingsConfigDict


class Nastroyki(BaseSettings):
    database_url: str = "postgresql+psycopg2://registr:registr@db:5432/registr"
    hash_scheme: str = "argon2"
    secret_key: str = "lokalnyy-sekret"
    app_env: str = "dev"
    port: int = 8000
    argon2_time_cost: int = 2
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


nastroyki = Nastroyki()
