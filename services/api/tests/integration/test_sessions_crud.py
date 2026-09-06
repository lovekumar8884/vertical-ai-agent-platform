"""Commit 32 — session CRUD against real PostgreSQL, end to end through auth+RLS."""

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
from vsa_api.platform.auth import clerk
from vsa_api.platform.db.session import TenantScopedSession


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def _stub_jwks(monkeypatch, rsa_key):
    public_key = rsa_key.public_key()
    fake = types.SimpleNamespace(
        get_signing_key_from_jwt=lambda _t: types.SimpleNamespace(key=public_key)
    )
    monkeypatch.setattr(clerk, "_jwk_client", lambda: fake)


def _token(rsa_key, *, org_slug: str) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    return jwt.encode(
        {
            "sub": "user_sessions",
            "iat": now,
            "exp": now + dt.timedelta(minutes=5),
            "org_slug": org_slug,
            "org_role": "org:admin",
        },
        rsa_key,
        algorithm="RS256",
    )


@pytest_asyncio.fixture
async def agent(make_org):
    org_id = await make_org(slug="acme-sessions")
    async with TenantScopedSession(str(org_id)) as db:
        agent_row = Agent(org_id=org_id, slug="demo", name="Demo", status="published")
        db.add(agent_row)
        await db.flush()
        db.add(
            AgentVersion(
                org_id=org_id,
                agent_id=agent_row.id,
                version=1,
                system_prompt="Be helpful.",
                is_published=True,
            )
        )
        agent_id = agent_row.id
    return org_id, agent_id


async def test_create_and_read_session(agent, rsa_key):
    _, agent_id = agent
    from vsa_api.platform.ids import IdType, from_uuid

    headers = {"Authorization": f"Bearer {_token(rsa_key, org_slug='acme-sessions')}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/v1/sessions",
            json={"agent_id": from_uuid(IdType.AGENT, agent_id)},
            headers=headers,
        )
        assert created.status_code == 201, created.text
        session_id = created.json()["id"]
        assert session_id.startswith("ses_")
        assert created.json()["agent_version_id"].startswith("agv_")

        listed = await client.get("/v1/sessions", headers=headers)
        assert listed.status_code == 200
        assert [s["id"] for s in listed.json()] == [session_id]

        fetched = await client.get(f"/v1/sessions/{session_id}", headers=headers)
        assert fetched.status_code == 200

        turns = await client.get(f"/v1/sessions/{session_id}/turns", headers=headers)
        assert turns.status_code == 200
        assert turns.json() == []


async def test_create_session_requires_auth(agent):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/v1/sessions", json={"agent_id": "agn_x"})
    assert resp.status_code == 401
