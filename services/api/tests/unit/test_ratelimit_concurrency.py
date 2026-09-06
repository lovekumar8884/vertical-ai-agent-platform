import pytest
from fakeredis import FakeAsyncRedis
from vsa_api.platform.concurrency import (
    AgentConcurrencyLimiter,
    ConcurrencyLimitError,
)
from vsa_api.platform.ratelimit import RateLimiter, RateLimitError


@pytest.fixture
def redis():
    return FakeAsyncRedis()


async def test_rate_limiter_allows_up_to_limit_then_blocks(redis):
    limiter = RateLimiter(redis, limit=3, window_seconds=60)
    for _ in range(3):
        await limiter.check("caller")
    with pytest.raises(RateLimitError):
        await limiter.check("caller")


async def test_rate_limiter_is_per_key(redis):
    limiter = RateLimiter(redis, limit=1, window_seconds=60)
    await limiter.check("a")
    await limiter.check("b")  # different key, still allowed


async def test_concurrency_cap_blocks_beyond_limit(redis):
    limiter = AgentConcurrencyLimiter(redis, limit=2)
    async with limiter.slot("agent"):
        async with limiter.slot("agent"):
            with pytest.raises(ConcurrencyLimitError):
                async with limiter.slot("agent"):
                    pass


async def test_concurrency_slot_released_on_exit(redis):
    limiter = AgentConcurrencyLimiter(redis, limit=1)
    async with limiter.slot("agent"):
        pass
    # Slot freed, so we can acquire again.
    async with limiter.slot("agent"):
        pass


async def test_concurrency_slot_released_on_exception(redis):
    limiter = AgentConcurrencyLimiter(redis, limit=1)
    with pytest.raises(ValueError):
        async with limiter.slot("agent"):
            raise ValueError("boom")
    assert await redis.get("concurrency:agent:agent") == b"0"
