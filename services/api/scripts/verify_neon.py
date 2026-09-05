"""Neon pooled-endpoint compatibility check for async SQLAlchemy + asyncpg.

Neon's pooled endpoint (PgBouncer in transaction mode) does not support
server-side prepared statements. asyncpg caches prepared statements by default,
which breaks on a pooled connection. We disable that cache
(``statement_cache_size=0``) and prove a parameterized query can run twice
without a ``DuplicatePreparedStatementError``.

Usage:
    VSA_DB_URL=postgresql+asyncpg://user:pass@host/db \\
        uv run python services/api/scripts/verify_neon.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import create_async_engine


def _database_url() -> str:
    url = os.environ.get("VSA_DB_URL")
    if not url:
        sys.stderr.write("VSA_DB_URL is not set.\n")
        raise SystemExit(2)
    return url


async def _run() -> None:
    url = _database_url()
    # statement_cache_size=0 is mandatory for Neon's pooled (PgBouncer) endpoint.
    engine = create_async_engine(
        url,
        connect_args={"statement_cache_size": 0},
        pool_pre_ping=True,
    )
    try:
        async with engine.connect() as conn:
            one = await conn.scalar(text("SELECT 1"))
            if one != 1:
                raise RuntimeError(f"SELECT 1 returned {one!r}, expected 1")

            # Run the same parameterized statement twice. On a pooled endpoint
            # with prepared-statement caching left on, the second call raises.
            stmt = text("SELECT :v").bindparams(bindparam("v"))
            for value in (41, 42):
                echoed = await conn.scalar(stmt, {"v": value})
                if echoed != value:
                    raise RuntimeError(f"parameterized echo returned {echoed!r}, expected {value}")
    finally:
        await engine.dispose()

    sys.stdout.write("Neon pooled-endpoint compatibility: OK\n")


if __name__ == "__main__":
    asyncio.run(_run())
