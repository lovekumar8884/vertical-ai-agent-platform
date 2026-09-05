"""ORM models for orgs, users, and memberships."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from vsa_api.platform.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

_DEFAULT_ENTITLEMENTS: dict[str, Any] = {
    "plan": "trial",
    "limits": {},
    "feature_flags": [],
}


class Org(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "org"

    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    entitlements: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=lambda: dict(_DEFAULT_ENTITLEMENTS)
    )


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user"

    clerk_user_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "membership"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uq_membership_org_user"),
        CheckConstraint("role IN ('owner', 'member')", name="ck_membership_role"),
    )

    # org_id is declared here (not via TenantMixin) so membership can be looked
    # up before an org scope is established, e.g. during Clerk webhook upsert.
    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("org.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
