"""Commit 21 — Clerk webhook integration against real PostgreSQL.

Exercises the full path: raw-body Svix HMAC verification, event application, and
lazy upsert of user/org/membership rows. Requires ``VSA_DB_URL`` and
``CLERK_WEBHOOK_SIGNING_SECRET`` (set for the test run).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os

from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from vsa_api.main import app
from vsa_api.platform.db.engine import get_sessionmaker
from vsa_api.platform.db.session import TenantScopedSession

_SECRET = os.environ.get(
    "CLERK_WEBHOOK_SIGNING_SECRET",
    "whsec_" + base64.b64encode(b"webhook-test-secret").decode(),
)


def _headers(body: bytes, svix_id: str = "msg_1", ts: str = "1700000000") -> dict[str, str]:
    key = _SECRET.split("_", 1)[1]
    signed = f"{svix_id}.{ts}.".encode() + body
    digest = hmac.new(base64.b64decode(key), signed, hashlib.sha256).digest()
    return {
        "svix-id": svix_id,
        "svix-timestamp": ts,
        "svix-signature": f"v1,{base64.b64encode(digest).decode()}",
    }


def _event(event_type: str, data: dict) -> bytes:
    return json.dumps({"type": event_type, "data": data}).encode()


async def _post(client: AsyncClient, body: bytes, headers: dict[str, str]):
    return await client.post("/v1/webhooks/clerk", content=body, headers=headers)


async def _scalar(sql: str, params: dict | None = None):
    async with get_sessionmaker()() as session:
        return await session.scalar(text(sql), params or {})


async def test_webhook_lazy_upserts_user_org_and_membership():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_body = _event(
            "user.created",
            {
                "id": "user_a",
                "email_addresses": [{"email_address": "a@example.com"}],
                "first_name": "Ann",
                "last_name": "Lee",
            },
        )
        assert (await _post(client, user_body, _headers(user_body))).status_code == 204

        org_body = _event("organization.created", {"id": "org_a", "slug": "acme", "name": "Acme"})
        assert (await _post(client, org_body, _headers(org_body))).status_code == 204

        member_body = _event(
            "organizationMembership.created",
            {
                "role": "org:admin",
                "organization": {"id": "org_a", "slug": "acme", "name": "Acme"},
                "public_user_data": {"user_id": "user_a"},
            },
        )
        assert (await _post(client, member_body, _headers(member_body))).status_code == 204

    assert (
        await _scalar("SELECT email FROM \"user\" WHERE clerk_user_id = 'user_a'")
        == "a@example.com"
    )
    assert await _scalar("SELECT name FROM org WHERE slug = 'acme'") == "Acme"

    # Membership is RLS-protected: verify it within the org's scope.
    org_id = await _scalar("SELECT id FROM org WHERE slug = 'acme'")
    async with TenantScopedSession(str(org_id)) as session:
        role = await session.scalar(
            text(
                'SELECT role FROM membership m JOIN "user" u ON u.id = m.user_id '
                "WHERE u.clerk_user_id = 'user_a'"
            )
        )
    assert role == "owner"


async def test_webhook_upsert_is_idempotent():
    transport = ASGITransport(app=app)
    body = _event(
        "user.created",
        {"id": "user_b", "email_addresses": [{"email_address": "b@example.com"}]},
    )
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await _post(client, body, _headers(body))).status_code == 204
        assert (await _post(client, body, _headers(body))).status_code == 204

    assert await _scalar("SELECT count(*) FROM \"user\" WHERE clerk_user_id = 'user_b'") == 1


async def test_webhook_rejects_bad_signature():
    transport = ASGITransport(app=app)
    body = _event("user.created", {"id": "user_c"})
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/v1/webhooks/clerk",
            content=body,
            headers={"svix-id": "x", "svix-timestamp": "1", "svix-signature": "v1,bad"},
        )
    assert resp.status_code == 401
    assert await _scalar("SELECT count(*) FROM \"user\" WHERE clerk_user_id = 'user_c'") == 0


async def test_webhook_rejects_missing_signature():
    transport = ASGITransport(app=app)
    body = _event("user.created", {"id": "user_d"})
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/v1/webhooks/clerk", content=body)
    assert resp.status_code == 401
