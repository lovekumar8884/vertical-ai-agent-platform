"""Shared fixtures for real-PostgreSQL integration tests.

These tests require a live PostgreSQL + pgvector database and are skipped unless
``VSA_DB_URL`` is set. They exercise the real app primitives (engine,
``TenantScopedSession``) against the migrated schema.
"""

from __future__ import annotations

import os
import uuid

import pytest
import pytest_asyncio

# Import every model module so SQLAlchemy metadata (and cross-table FKs) resolve.
import vsa_api.modules.agents.models
import vsa_api.modules.iam.models
import vsa_api.modules.sessions.models  # noqa: F401
from sqlalchemy import text
from vsa_api.platform.db.engine import get_engine, get_sessionmaker

# Truncate order is irrelevant with CASCADE, but list every table we touch.
_TABLES = 'turn, session, agent_version, agent, membership, audit_log, chunk, "user", org'


def _db_configured() -> bool:
    return bool(os.environ.get("VSA_DB_URL"))


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    if not _db_configured():
        pytest.skip("VSA_DB_URL not set — real PostgreSQL required for integration tests")
    # Rebind the engine to the current test's event loop (asyncpg is loop-bound).
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()
    async with get_engine().begin() as conn:
        await conn.execute(text(f"TRUNCATE {_TABLES} CASCADE"))
    yield


@pytest_asyncio.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Real Redis is deferred; share one fakeredis so idempotency/concurrency
    state persists across requests within a test."""
    from fakeredis import FakeAsyncRedis
    from vsa_api.modules.agents import routes as agents_routes
    from vsa_api.modules.sessions import routes as sessions_routes

    client = FakeAsyncRedis()
    monkeypatch.setattr(sessions_routes, "get_cache_redis", lambda: client)
    monkeypatch.setattr(agents_routes, "get_cache_redis", lambda: client)
    return client


@pytest_asyncio.fixture
async def make_org():
    """Insert an org (global, no RLS) and return its UUID."""

    async def _make(slug: str | None = None, name: str = "Org") -> uuid.UUID:
        slug = slug or f"org-{uuid.uuid4().hex[:8]}"
        async with get_sessionmaker()() as session, session.begin():
            row = await session.execute(
                text("INSERT INTO org (slug, name) VALUES (:slug, :name) RETURNING id"),
                {"slug": slug, "name": name},
            )
            return row.scalar_one()

    return _make
