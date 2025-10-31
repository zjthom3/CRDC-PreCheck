from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
