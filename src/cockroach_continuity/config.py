from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CC_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://root@localhost:26257/defaultdb?sslmode=disable"
    database_required: bool = False
    app_name: str = "Cockroach Continuity"
    aws_region: str = "us-east-1"
    candidate_model_id: str = "amazon.nova-lite-v1:0"
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
