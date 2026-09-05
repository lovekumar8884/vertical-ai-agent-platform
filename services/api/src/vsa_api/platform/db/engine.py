"""Async SQLAlchemy engine and session factory.

``statement_cache_size=0`` is required for Neon's pooled (PgBouncer) endpoint,
which does not support server-side prepared statements. The engine and
sessionmaker are process singletons.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from vsa_api.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.db_url,
        connect_args={"statement_cache_size": settings.db_statement_cache_size},
        pool_pre_ping=True,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )
