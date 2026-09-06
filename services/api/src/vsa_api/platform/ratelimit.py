"""Redis fixed-window rate limiter.

A minimal counter-per-window limiter: the first request in a window sets the
key's TTL; requests beyond ``limit`` within the window are rejected.
"""

from __future__ import annotations

from redis.asyncio import Redis


class RateLimitError(Exception):
    """Raised when a caller exceeds the configured request rate."""


class RateLimiter:
    def __init__(self, redis: Redis, *, limit: int, window_seconds: int) -> None:
        self._redis = redis
        self._limit = limit
        self._window = window_seconds

    async def check(self, key: str) -> None:
        redis_key = f"ratelimit:{key}"
        count = await self._redis.incr(redis_key)
        if count == 1:
            await self._redis.expire(redis_key, self._window)
        if count > self._limit:
            raise RateLimitError(f"Rate limit of {self._limit} exceeded.")
