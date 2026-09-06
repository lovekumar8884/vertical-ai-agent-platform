"""D8 tenant-leakage harness — Org B must not reach Org A's data on ANY endpoint.

Proves isolation at the HTTP layer (auth + RLS together), not just the DB layer.
"""

from __future__ import annotations

import datetime as dt
import types

import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from vsa_api.main import app
from vsa_api.modules.agents.models import Agent, AgentVersion
from vsa_api.modules.sessions.models import Session
from vsa_api.platform.auth import clerk
from vsa_api.platform.db.session import TenantScopedSession
from vsa_api.platform.ids import IdType, from_uuid


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def _stub_jwks(monkeypatch, rsa_key):
    public_key = rsa_key.public_key()
    monkeypatch.setattr(
        clerk,
        "_jwk_client",
        lambda: types.SimpleNamespace(
            get_signing_key_from_jwt=lambda _t: types.SimpleNamespace(key=public_key)
        ),
    )


def _token(rsa_key, org_slug: str) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    return jwt.encode(
        {
            "sub": f"user_{org_slug}",
            "iat": now,
            "exp": now + dt.timedelta(minutes=5),
            "org_slug": org_slug,
            "org_role": "org:admin",
        },
        rsa_key,
        algorithm="RS256",
    )


@pytest_asyncio.fixture
async def org_a_session(make_org):
    org_id = await make_org(slug="tenant-a")
    async with TenantScopedSession(str(org_id)) as db:
        agent = Agent(org_id=org_id, slug="demo", name="A", status="published")
        db.add(agent)
        await db.flush()
        version = AgentVersion(org_id=org_id, agent_id=agent.id, version=1, is_published=True)
        db.add(version)
        await db.flush()
        row = Session(org_id=org_id, agent_id=agent.id, agent_version_id=version.id)
        db.add(row)
        await db.flush()
        return from_uuid(IdType.SESSION, row.id), from_uuid(IdType.AGENT, agent.id)


async def test_org_b_cannot_reach_org_a_data(make_org, org_a_session, rsa_key):
    a_session_id, a_agent_id = org_a_session
    await make_org(slug="tenant-b")  # provision B so require_org_id resolves
    b_headers = {"Authorization": f"Bearer {_token(rsa_key, 'tenant-b')}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List is filtered to B (empty).
        listed = await client.get("/v1/sessions", headers=b_headers)
        assert listed.status_code == 200
        assert listed.json() == []

        # Direct fetch of A's session -> 404 (RLS hides it).
        assert (
            await client.get(f"/v1/sessions/{a_session_id}", headers=b_headers)
        ).status_code == 404

        # A's turns -> 404.
        assert (
            await client.get(f"/v1/sessions/{a_session_id}/turns", headers=b_headers)
        ).status_code == 404

        # Streaming into A's session -> 404 before any streaming starts.
        assert (
            await client.post(
                f"/v1/sessions/{a_session_id}/messages/stream",
                json={"content": "leak?"},
                headers=b_headers,
            )
        ).status_code == 404

        # Creating a session with A's agent -> 409 (agent not visible to B).
        assert (
            await client.post("/v1/sessions", json={"agent_id": a_agent_id}, headers=b_headers)
        ).status_code == 409


async def test_every_session_endpoint_requires_auth(org_a_session):
    a_session_id, a_agent_id = org_a_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/v1/sessions")).status_code == 401
        assert (await client.get(f"/v1/sessions/{a_session_id}")).status_code == 401
        assert (await client.get(f"/v1/sessions/{a_session_id}/turns")).status_code == 401
        assert (
            await client.post(
                f"/v1/sessions/{a_session_id}/messages/stream",
                json={"content": "x"},
            )
        ).status_code == 401
        assert (await client.post("/v1/sessions", json={"agent_id": a_agent_id})).status_code == 401
