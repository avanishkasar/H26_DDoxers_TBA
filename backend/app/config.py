from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from env vars and the repo-root .env file."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "H26 DDoxers API"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # Local open-weight model served by Ollama. Cloud/paid APIs are banned by the event rules.
    ollama_base_url: HttpUrl = HttpUrl("http://localhost:11434")
    ollama_model: str = "gemma4"
    llm_connect_timeout_s: float = 5.0
    llm_read_timeout_s: float = 120.0
    llm_max_concurrency: int = Field(default=4, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
