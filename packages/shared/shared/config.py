import os
from functools import lru_cache

from pydantic import BaseModel, Field

try:  # pragma: no cover - optional dependency
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # Fallback stub for test environments
    class SettingsConfigDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class BaseSettings(BaseModel):
        model_config = {"extra": "ignore"}

        def __init__(self, **data):
            env_values = {}
        for field in self.__class__.model_fields:
                env_key = field.upper()
                if env_key in os.environ:
                    env_values[field] = os.environ[env_key]
            env_values.update(data)
            super().__init__(**env_values)


class AppSettings(BaseSettings):
    """Common application settings shared across services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field("CRDC PreCheck", description="Human friendly service name.")
    environment: str = Field("local", description="Deployment environment label.")
    database_url: str = Field(
        "postgresql+psycopg://postgres:postgres@postgres:5432/crdc_precheck",
        description="SQLAlchemy-compatible database URL.",
    )
    redis_broker_url: str = Field(
        "redis://redis:6379/0", description="Redis URL for Celery broker."
    )
    redis_result_url: str = Field(
        "redis://redis:6379/1", description="Redis URL for Celery results."
    )
    minio_endpoint: str = Field(
        "http://minio:9000", description="Object storage endpoint for evidence assets."
    )


@lru_cache
def get_settings() -> AppSettings:
    """Return cached settings instance."""
    return AppSettings()
