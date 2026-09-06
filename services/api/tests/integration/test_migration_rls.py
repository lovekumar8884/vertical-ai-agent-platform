"""Commit 28 — migration/schema + RLS validation against real PostgreSQL.

Proves that Row-Level Security enforces cross-org isolation: Org A cannot read,
and cannot write into, Org B's tenant data — using the real ``TenantScopedSession``
the app uses in production, with FORCE RLS on so the table owner is not exempt.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from vsa_api.modules.agents.models import Agent
from vsa_api.platform.audit import write_audit
from vsa_api.platform.db.engine import get_engine
from vsa_api.platform.db.session import TenantScopedSession


async def test_schema_has_pgvector_partitioning_and_fk():
    async with get_engine().connect() as conn:
        vector = await conn.scalar(
            text("SELECT extversion FROM pg_extension WHERE extname='vector'")
        )
        assert vector is not None

        embedding_type = await conn.scalar(
            text(
                "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
                "WHERE attrelid='chunk'::regclass AND attname='embedding'"
            )
        )
        assert embedding_type == "vector(1536)"

        partstrat = await conn.scalar(
            text(
                "SELECT partstrat::text FROM pg_partitioned_table "
                "WHERE partrelid='audit_log'::regclass"
            )
        )
        assert partstrat == "r"  # RANGE

        fk = await conn.scalar(
            text(
                "SELECT conname FROM pg_constraint WHERE conrelid='turn'::regclass "
                "AND contype='f' AND confrelid='session'::regclass"
            )
        )
        assert fk is not None


async def test_rls_blocks_cross_org_reads(make_org):
    org_a = await make_org()
    org_b = await make_org()

    async with TenantScopedSession(str(org_a)) as session:
        session.add(Agent(org_id=org_a, slug="demo", name="A's agent", status="draft"))

    # Org B must not see Org A's agent.
    async with TenantScopedSession(str(org_b)) as session:
        visible = (await session.execute(select(Agent))).scalars().all()
        assert visible == []

    # Org A sees exactly its own.
    async with TenantScopedSession(str(org_a)) as session:
        visible = (await session.execute(select(Agent))).scalars().all()
        assert len(visible) == 1
        assert visible[0].name == "A's agent"


async def test_rls_with_check_blocks_writing_into_another_org(make_org):
    org_a = await make_org()
    org_b = await make_org()

    # Under Org A's scope, inserting a row tagged for Org B violates WITH CHECK.
    with pytest.raises(DBAPIError):
        async with TenantScopedSession(str(org_a)) as session:
            session.add(Agent(org_id=org_b, slug="x", name="wrong org", status="draft"))
            await session.flush()


async def test_audit_log_is_tenant_isolated(make_org):
    org_a = await make_org()
    org_b = await make_org()

    async with TenantScopedSession(str(org_a)) as session:
        await write_audit(
            session,
            org_id=org_a,
            actor_user_id=None,
            action="create",
            resource_type="agent",
            resource_id=uuid.uuid4(),
            after={"name": "A"},
        )

    async with TenantScopedSession(str(org_b)) as session:
        count_b = await session.scalar(text("SELECT count(*) FROM audit_log"))
        assert count_b == 0

    async with TenantScopedSession(str(org_a)) as session:
        count_a = await session.scalar(text("SELECT count(*) FROM audit_log"))
        assert count_a == 1


async def test_tenant_scoped_session_sets_org_guc(make_org):
    org_a = await make_org()
    async with TenantScopedSession(str(org_a)) as session:
        current = await session.scalar(text("SELECT current_setting('app.org_id', true)"))
        assert current == str(org_a)
