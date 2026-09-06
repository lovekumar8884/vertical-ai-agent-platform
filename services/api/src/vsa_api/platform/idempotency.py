"""Idempotency-Key support for mutating endpoints (Redis-backed).

Per ARCHITECTURE_FREEZE §10, every mutating endpoint requires an
``Idempotency-Key`` (except SSE streams). The first request reserves a
tenant-scoped key and stores its JSON response for 24h; a replay with the same
key returns that response without re-running the mutation, and a concurrent
duplicate that is still in flight gets a 409.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from redis.asyncio import Redis

from vsa_api.platform.errors import ConflictError

_TTL_SECONDS = 24 * 60 * 60
_LOCK_TTL_SECONDS = 60
_PROCESSING = "__processing__"


def _redis_key(org_id: str, idempotency_key: str) -> str:
    return f"t:{org_id}:idem:{idempotency_key}"


def _decode(value: Any) -> str:
    return value.decode() if isinstance(value, bytes | bytearray) else value


async def run_idempotent(
    redis: Redis,
    *,
    org_id: str,
    idempotency_key: str,
    produce: Callable[[], Awaitable[dict[str, Any]]],
) -> tuple[dict[str, Any], bool]:
    """Run ``produce`` once per (org, key); return ``(response, replayed)``."""
    key = _redis_key(org_id, idempotency_key)

    # Reserve atomically: only the first caller runs the mutation.
    acquired = await redis.set(key, _PROCESSING, nx=True, ex=_LOCK_TTL_SECONDS)
    if not acquired:
        stored = _decode(await redis.get(key))
        if stored is None or stored == _PROCESSING:
            raise ConflictError("A request with this Idempotency-Key is in progress.")
        return json.loads(stored), True

    result = await produce()
    await redis.set(key, json.dumps(result), ex=_TTL_SECONDS)
    return result, False
