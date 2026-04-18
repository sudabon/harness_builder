from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Harness Builder API"
    api_prefix: str = "/api/v1"
    database_url: str = Field(
        default="sqlite:///./harness_builder.db",
        alias="DATABASE_URL",
    )
    session_secret: str = Field(
        default="change-me-in-production",
        alias="SESSION_SECRET",
    )
    frontend_origin: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_ORIGIN",
    )
    session_cookie_secure: bool = Field(default=False, alias="SESSION_COOKIE_SECURE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
