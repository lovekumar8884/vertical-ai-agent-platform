"""Typed application settings loaded from the environment (see .env.example).

Never log a ``Settings`` instance: it carries secrets. Read individual,
non-secret fields when you need to emit configuration to logs.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VSA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    sentry_dsn_api: str = ""

    # Database (async SQLAlchemy + asyncpg). Statement cache off for pooled Neon.
    db_url: str = "postgresql+asyncpg://vsa:vsa@localhost:5432/vsa"
    db_statement_cache_size: int = 0

    # Redis — two logical DBs: session (db 0) and cache (db 1).
    redis_session_url: str = "redis://localhost:6379/0"
    redis_cache_url: str = "redis://localhost:6379/1"

    # LLM — single provider in Sprint 1.
    llm_openai_api_key: SecretStr = SecretStr("")
    llm_default_model: str = "gpt-4o-mini"
    llm_chat_timeout_s: float = 20.0
    llm_embedding_timeout_s: float = 60.0
    llm_max_response_tokens: int = 800

    # Runtime caps
    agent_concurrent_sessions_max: int = 50

    # App URLs
    api_base_url: str = "http://localhost:8000"
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    # Clerk (identity + membership authoritative). No VSA_ prefix in the env.
    clerk_secret_key: SecretStr = Field(default=SecretStr(""), validation_alias="CLERK_SECRET_KEY")
    clerk_webhook_signing_secret: SecretStr = Field(
        default=SecretStr(""), validation_alias="CLERK_WEBHOOK_SIGNING_SECRET"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
