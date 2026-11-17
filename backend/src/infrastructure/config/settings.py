"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for Insta Follow Manager backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    instagram_gateway: Literal["mock", "instagrapi"] = "mock"
    database_url: str = "sqlite:///./insta_manager.db"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    ig_username: str = ""
    ig_password: str = ""
    ig_session_path: str = "./session.json"

    @property
    def sqlite_path(self) -> str:
        """Extract the file path from a sqlite:/// URL."""
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix):
            return self.database_url[len(prefix) :]
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
