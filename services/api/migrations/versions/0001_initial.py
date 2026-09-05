"""initial schema: core tables + RLS + pgvector

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-05

NOTE ON PARTITIONING: SPRINT1_FINAL_SCOPE declares session/turn/audit_log
``PARTITION BY RANGE (created_at)``. Postgres cannot enforce a foreign key that
references a partitioned table on a non-partition-key column (e.g.
``turn.session_id -> session.id``), and a partitioned table's primary key must
include the partition key. To keep referential integrity intact at MVP volume,
these tables are created non-partitioned here; monthly RANGE partitioning is a
follow-up migration to add once volume warrants and the FK strategy is settled.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMPS = (
    "created_at TIMESTAMPTZ NOT NULL DEFAULT now(), "
    "updated_at TIMESTAMPTZ NOT NULL DEFAULT now(), "
    "deleted_at TIMESTAMPTZ"
)

# Tenant tables carry org_id and are protected by Row-Level Security.
_TENANT_TABLES = (
    "membership",
    "agent",
    "agent_version",
    "session",
    "turn",
    "audit_log",
    "chunk",
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        f"""
        CREATE TABLE org (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            slug TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            entitlements JSONB NOT NULL
                DEFAULT '{{"plan":"trial","limits":{{}},"feature_flags":[]}}',
            {_TIMESTAMPS}
        )
        """
    )

    op.execute(
        f"""
        CREATE TABLE "user" (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            clerk_user_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            name TEXT,
            {_TIMESTAMPS}
        )
        """
    )

    op.execute(
        f"""
        CREATE TABLE membership (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK (role IN ('owner', 'member')),
            {_TIMESTAMPS},
            CONSTRAINT uq_membership_org_user UNIQUE (org_id, user_id)
        )
        """
    )
    op.execute("CREATE INDEX ix_membership_org_id ON membership(org_id)")

    op.execute(
        f"""
        CREATE TABLE agent (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            slug TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'published')),
            {_TIMESTAMPS},
            CONSTRAINT uq_agent_org_slug UNIQUE (org_id, slug)
        )
        """
    )
    op.execute("CREATE INDEX ix_agent_org_created ON agent(org_id, created_at DESC)")

    op.execute(
        f"""
        CREATE TABLE agent_version (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            agent_id UUID NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
            version INT NOT NULL,
            system_prompt TEXT NOT NULL DEFAULT '',
            spec JSONB NOT NULL DEFAULT '{{}}',
            spec_schema_version INT NOT NULL DEFAULT 1,
            is_published BOOLEAN NOT NULL DEFAULT false,
            published_at TIMESTAMPTZ,
            published_by UUID,
            {_TIMESTAMPS},
            CONSTRAINT uq_agent_version_agent_version UNIQUE (agent_id, version)
        )
        """
    )
    op.execute("CREATE INDEX ix_agent_version_org_id ON agent_version(org_id)")
    op.execute("CREATE INDEX ix_agent_version_agent_id ON agent_version(agent_id)")

    op.execute(
        f"""
        CREATE TABLE session (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            agent_id UUID NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
            agent_version_id UUID NOT NULL
                REFERENCES agent_version(id) ON DELETE RESTRICT,
            channel TEXT NOT NULL DEFAULT 'playground',
            started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            ended_at TIMESTAMPTZ,
            meta JSONB NOT NULL DEFAULT '{{}}',
            {_TIMESTAMPS}
        )
        """
    )
    op.execute("CREATE INDEX ix_session_org_created ON session(org_id, created_at DESC)")
    op.execute("CREATE INDEX ix_session_agent_id ON session(agent_id)")

    op.execute(
        f"""
        CREATE TABLE turn (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            session_id UUID NOT NULL REFERENCES session(id) ON DELETE CASCADE,
            idx INT NOT NULL,
            role TEXT NOT NULL CHECK (
                role IN ('user', 'assistant', 'system', 'tool_call', 'tool_result')
            ),
            content TEXT NOT NULL DEFAULT '',
            tokens_in INT,
            tokens_out INT,
            model TEXT,
            latency_ms INT,
            end_reason TEXT,
            started_at TIMESTAMPTZ,
            ended_at TIMESTAMPTZ,
            {_TIMESTAMPS},
            CONSTRAINT uq_turn_session_idx UNIQUE (session_id, idx)
        )
        """
    )
    op.execute("CREATE INDEX ix_turn_org_created ON turn(org_id, created_at DESC)")
    op.execute("CREATE INDEX ix_turn_session_id ON turn(session_id)")

    op.execute(
        f"""
        CREATE TABLE audit_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            actor_user_id UUID,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id UUID,
            diff JSONB,
            ip TEXT,
            ua TEXT,
            {_TIMESTAMPS}
        )
        """
    )
    op.execute("CREATE INDEX ix_audit_log_org_created ON audit_log(org_id, created_at DESC)")

    # chunk exists for schema completeness; not populated in Sprint 1.
    op.execute(
        f"""
        CREATE TABLE chunk (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id UUID NOT NULL REFERENCES org(id) ON DELETE CASCADE,
            corpus_id UUID,
            document_id UUID,
            text TEXT,
            embedding vector(1536),
            {_TIMESTAMPS}
        )
        """
    )
    op.execute(
        "CREATE INDEX ix_chunk_embedding ON chunk "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 200)"
    )

    for table in _TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_isolation ON {table} "
            "USING (org_id = current_setting('app.org_id', true)::uuid) "
            "WITH CHECK (org_id = current_setting('app.org_id', true)::uuid)"
        )


def downgrade() -> None:
    for table in (
        "chunk",
        "audit_log",
        "turn",
        "session",
        "agent_version",
        "agent",
        "membership",
        "user",
        "org",
    ):
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
