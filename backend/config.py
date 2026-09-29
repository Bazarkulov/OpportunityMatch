"""Environment-backed application configuration."""
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./opportunitymatch.db"
    auth_secret: str = "development-only-change-me"
    access_token_minutes: int = 1440
    cors_origins: str = "http://localhost:3000"
    greenhouse_boards: str = "figma"
    lever_sites: str = "xcimer,anybotics,hermeus"
    collector_timeout_seconds: float = 20.0
    collection_admin_token: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def csv(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
