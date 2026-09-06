"""Per-agent concurrency cap backed by Redis.

Bounds concurrent live streams for a single agent. The counter is incremented on
entry and decremented on every exit path (success, error, cancel) via the async
context manager's ``finally``. A safety TTL prevents a crashed holder from
leaking a slot forever.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis

_SLOT_TTL_SECONDS = 300


class ConcurrencyLimitError(Exception):
    """Raised when an agent is already at its concurrent-stream cap."""


class AgentConcurrencyLimiter:
    def __init__(self, redis: Redis, *, limit: int) -> None:
        self._redis = redis
        self._limit = limit

    @asynccontextmanager
    async def slot(self, agent_id: str) -> AsyncIterator[None]:
        key = f"concurrency:agent:{agent_id}"
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, _SLOT_TTL_SECONDS)
        if current > self._limit:
            await self._redis.decr(key)
            raise ConcurrencyLimitError(f"Agent is at its concurrency cap of {self._limit}.")
        try:
            yield
        finally:
            await self._redis.decr(key)
