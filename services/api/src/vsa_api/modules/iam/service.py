"""IAM service: Clerk webhook verification, event application, and lazy upsert.

Clerk is authoritative for identity/membership (ADR-044). The webhook keeps our
copies in sync; ``lazy_upsert_principal`` is the backstop that materializes rows
on the first authenticated request if a webhook was missed.

``org`` and ``user`` are global (no RLS); ``membership`` is RLS-scoped by
``org_id``, so membership writes run with ``app.org_id`` set to the org.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from vsa_api.modules.iam.models import Membership, Org, User
from vsa_api.modules.iam.schemas import MembershipOut, MeResponse, OrgOut, UserOut
from vsa_api.platform.ids import IdType, from_uuid


class WebhookVerificationError(Exception):
    """Raised when a Clerk/Svix webhook signature fails verification."""


def verify_webhook_signature(
    *,
    payload: bytes,
    svix_id: str | None,
    svix_timestamp: str | None,
    svix_signature: str | None,
    secret: str,
) -> None:
    """Verify a Svix HMAC signature over the raw body. Raises on failure."""
    if not (svix_id and svix_timestamp and svix_signature and secret):
        raise WebhookVerificationError("Missing signature material.")

    key = secret.split("_", 1)[1] if secret.startswith("whsec_") else secret
    secret_bytes = base64.b64decode(key)
    signed = f"{svix_id}.{svix_timestamp}.".encode() + payload
    expected = base64.b64encode(hmac.new(secret_bytes, signed, hashlib.sha256).digest()).decode()

    # svix-signature is a space-separated list of "v1,<sig>" entries.
    candidates = [part.partition(",")[2] for part in svix_signature.split()]
    if not any(hmac.compare_digest(expected, candidate) for candidate in candidates):
        raise WebhookVerificationError("Signature mismatch.")


async def _set_org_scope(session: AsyncSession, org_id: str) -> None:
    await session.execute(
        text("SELECT set_config('app.org_id', :org_id, true)"), {"org_id": org_id}
    )


async def _upsert_user(
    session: AsyncSession, *, clerk_user_id: str, email: str, name: str | None
) -> User:
    stmt = pg_insert(User).values(clerk_user_id=clerk_user_id, email=email, name=name)
    stmt = stmt.on_conflict_do_update(
        index_elements=["clerk_user_id"],
        set_={"email": stmt.excluded.email, "name": stmt.excluded.name, "updated_at": func.now()},
    )
    await session.execute(stmt)
    return (
        await session.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    ).scalar_one()


async def _upsert_org(session: AsyncSession, *, slug: str, name: str) -> Org:
    stmt = pg_insert(Org).values(slug=slug, name=name)
    stmt = stmt.on_conflict_do_update(
        index_elements=["slug"],
        set_={"name": stmt.excluded.name, "updated_at": func.now()},
    )
    await session.execute(stmt)
    return (await session.execute(select(Org).where(Org.slug == slug))).scalar_one()


async def _upsert_membership(session: AsyncSession, *, org_id, user_id, role: str) -> None:
    await _set_org_scope(session, str(org_id))
    stmt = pg_insert(Membership).values(org_id=org_id, user_id=user_id, role=role)
    stmt = stmt.on_conflict_do_update(
        index_elements=["org_id", "user_id"],
        set_={"role": stmt.excluded.role, "updated_at": func.now()},
    )
    await session.execute(stmt)


def _clerk_email(data: dict[str, Any]) -> str:
    emails = data.get("email_addresses") or []
    return emails[0].get("email_address", "") if emails else data.get("email", "")


def _clerk_name(data: dict[str, Any]) -> str | None:
    parts = [data.get("first_name"), data.get("last_name")]
    joined = " ".join(p for p in parts if p)
    return joined or None


async def apply_clerk_event(session: AsyncSession, event: dict[str, Any]) -> None:
    """Apply a Clerk webhook event to our tables."""
    event_type = event.get("type", "")
    data = event.get("data", {})

    if event_type in ("user.created", "user.updated"):
        await _upsert_user(
            session,
            clerk_user_id=data["id"],
            email=_clerk_email(data),
            name=_clerk_name(data),
        )
    elif event_type in ("organization.created", "organization.updated"):
        await _upsert_org(session, slug=data["slug"], name=data.get("name", data["slug"]))
    elif event_type in (
        "organizationMembership.created",
        "organizationMembership.updated",
    ):
        organization = data.get("organization", {})
        user_data = data.get("public_user_data", {})
        org = await _upsert_org(
            session,
            slug=organization["slug"],
            name=organization.get("name", organization["slug"]),
        )
        user = (
            await session.execute(select(User).where(User.clerk_user_id == user_data["user_id"]))
        ).scalar_one()
        role = "owner" if "admin" in data.get("role", "") else "member"
        await _upsert_membership(session, org_id=org.id, user_id=user.id, role=role)


async def lazy_upsert_principal(
    session: AsyncSession,
    *,
    clerk_user_id: str,
    email: str,
    org_slug: str | None,
    org_name: str | None,
    org_role: str | None,
) -> User:
    """Materialize the user (and current org membership) on first authenticated call."""
    user = await _upsert_user(session, clerk_user_id=clerk_user_id, email=email, name=None)
    if org_slug:
        org = await _upsert_org(session, slug=org_slug, name=org_name or org_slug)
        role = "owner" if org_role and "admin" in org_role else "member"
        await _upsert_membership(session, org_id=org.id, user_id=user.id, role=role)
    return user


async def load_me(session: AsyncSession, *, clerk_user_id: str) -> MeResponse:
    user = (
        await session.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    ).scalar_one()

    rows = (
        await session.execute(
            select(Membership, Org)
            .join(Org, Org.id == Membership.org_id)
            .where(Membership.user_id == user.id)
        )
    ).all()

    memberships = [
        MembershipOut(
            id=from_uuid(IdType.MEMBERSHIP, membership.id),
            role=membership.role,
            org=OrgOut(id=from_uuid(IdType.ORG, org.id), slug=org.slug, name=org.name),
        )
        for membership, org in rows
    ]
    return MeResponse(
        user=UserOut(id=from_uuid(IdType.USER, user.id), email=user.email, name=user.name),
        memberships=memberships,
    )
