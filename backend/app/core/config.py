from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FutureFit AI"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "futurefit"
    mongo_max_pool: int = 100

    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 14

    cors_origins: list[str] = ["http://localhost:5173"]
    frontend_host: str | None = None
    max_upload_mb: int = 5
    max_resumes_per_user: int = 25

    admin_email: str | None = None
    admin_password: str | None = None

    anthropic_api_key: str | None = None
    llm_model: str = "claude-sonnet-5-5"
    llm_timeout_s: float = 20.0

    seed_on_startup: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
