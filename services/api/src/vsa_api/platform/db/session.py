"""Tenant-scoped database session — the only sanctioned way to touch Postgres.

Opens a transaction and issues ``set_config('app.org_id', <org_id>, true)``
inside it. Row-Level Security policies read that setting via
``current_setting('app.org_id', true)::uuid`` to scope every statement to one
org. Because the setting is transaction-local (``is_local=true``, the SET LOCAL
equivalent), a pooled connection cannot leak the value to the next checkout.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from vsa_api.platform.db.engine import get_sessionmaker

_SET_ORG = text("SELECT set_config('app.org_id', :org_id, true)")


class TenantScopedSession:
    """Async context manager yielding an ``AsyncSession`` bound to one org.

    Usage::

        async with TenantScopedSession(org_id) as session:
            ...
    """

    def __init__(self, org_id: str) -> None:
        self._org_id = org_id
        self._ctx = self._open()

    @asynccontextmanager
    async def _open(self) -> AsyncIterator[AsyncSession]:
        async with get_sessionmaker()() as session, session.begin():
            await session.execute(_SET_ORG, {"org_id": self._org_id})
            yield session

    async def __aenter__(self) -> AsyncSession:
        return await self._ctx.__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._ctx.__aexit__(exc_type, exc, tb)
