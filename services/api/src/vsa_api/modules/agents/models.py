"""ORM models for agents and agent versions.

Lifecycle is ``draft`` / ``published`` (ADR). A session pins the
``agent_version_id`` it started on (ADR-045); publishing a new version never
mutates an existing one.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from vsa_api.platform.db.base import (
    Base,
    TenantMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "agent"
    __table_args__ = (
        UniqueConstraint("org_id", "slug", name="uq_agent_org_slug"),
        CheckConstraint("status IN ('draft', 'published')", name="ck_agent_status"),
    )

    slug: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="draft", server_default="draft"
    )


class AgentVersion(UUIDPrimaryKeyMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "agent_version"
    __table_args__ = (
        UniqueConstraint("agent_id", "version", name="uq_agent_version_agent_version"),
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("agent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    spec_schema_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
