"""Async Redis clients.

Two logical DBs on one instance, mirroring the Upstash split:
  * session store -> db 0 (``VSA_REDIS_SESSION_URL``)
  * cache         -> db 1 (``VSA_REDIS_CACHE_URL``)

Clients are process singletons and decode responses to ``str``.
"""

from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis
from redis.asyncio import from_url as redis_from_url

from vsa_api.config import get_settings


@lru_cache
def get_session_redis() -> Redis:
    return redis_from_url(get_settings().redis_session_url, decode_responses=True)


@lru_cache
def get_cache_redis() -> Redis:
    return redis_from_url(get_settings().redis_cache_url, decode_responses=True)
