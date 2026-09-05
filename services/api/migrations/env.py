"""Alembic environment.

The database URL and target metadata come from the application itself: all
model modules are imported so ``Base.metadata`` is complete, and the URL is read
from ``Settings`` (never hardcoded).
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

# Import every model module so Base.metadata is fully populated.
import vsa_api.modules.agents.models
import vsa_api.modules.iam.models
import vsa_api.modules.sessions.models  # noqa: F401
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from vsa_api.config import get_settings
from vsa_api.platform.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    return get_settings().db_url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    settings = get_settings()
    engine = create_async_engine(
        _database_url(),
        connect_args={"statement_cache_size": settings.db_statement_cache_size},
    )
    async with engine.connect() as connection:
        await connection.run_sync(_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
