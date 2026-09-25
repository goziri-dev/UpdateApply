from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    app_name: str = "UpdateApply"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    openrouter_api_key=""

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> _Settings:
    """Helper function to load settings once and cache them across imports."""
    return _Settings()

settings = get_settings()
