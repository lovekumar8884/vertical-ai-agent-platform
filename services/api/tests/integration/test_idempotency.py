"""Idempotency-Key on POST /v1/sessions (real PostgreSQL, shared fakeredis)."""

from __future__ import annotations

import datetime as dt
import types

import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from vsa_api.main import app
from vsa_api.modules.agents.models import Agent, AgentVersion
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


async def _provision(make_org, slug: str):
    org_id = await make_org(slug=slug)
    async with TenantScopedSession(str(org_id)) as db:
        agent = Agent(org_id=org_id, slug="demo", name="A", status="published")
        db.add(agent)
        await db.flush()
        db.add(AgentVersion(org_id=org_id, agent_id=agent.id, version=1, is_published=True))
        agent_ulid = from_uuid(IdType.AGENT, agent.id)
    return org_id, agent_ulid


@pytest_asyncio.fixture
async def agent(make_org):
    return await _provision(make_org, "acme-idem")


async def test_duplicate_key_creates_one_session(agent, rsa_key):
    org_id, agent_ulid = agent
    headers = {
        "Authorization": f"Bearer {_token(rsa_key, 'acme-idem')}",
        "Idempotency-Key": "k1",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post("/v1/sessions", json={"agent_id": agent_ulid}, headers=headers)
        r2 = await client.post("/v1/sessions", json={"agent_id": agent_ulid}, headers=headers)

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] == r2.json()["id"]  # replayed, same session

    async with TenantScopedSession(str(org_id)) as db:
        count = await db.scalar(text("SELECT count(*) FROM session"))
    assert count == 1


async def test_missing_idempotency_key_is_rejected(agent, rsa_key):
    _, agent_ulid = agent
    headers = {"Authorization": f"Bearer {_token(rsa_key, 'acme-idem')}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/v1/sessions", json={"agent_id": agent_ulid}, headers=headers)
    assert resp.status_code == 400


async def test_in_flight_duplicate_returns_409(agent, rsa_key, fake_redis):
    org_id, agent_ulid = agent
    await fake_redis.set(f"t:{org_id}:idem:k2", "__processing__")
    headers = {
        "Authorization": f"Bearer {_token(rsa_key, 'acme-idem')}",
        "Idempotency-Key": "k2",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/v1/sessions", json={"agent_id": agent_ulid}, headers=headers)
    assert resp.status_code == 409


async def test_same_key_is_isolated_per_org(make_org, rsa_key):
    _, agent_a = await _provision(make_org, "idem-a")
    _, agent_b = await _provision(make_org, "idem-b")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ra = await client.post(
            "/v1/sessions",
            json={"agent_id": agent_a},
            headers={
                "Authorization": f"Bearer {_token(rsa_key, 'idem-a')}",
                "Idempotency-Key": "shared",
            },
        )
        rb = await client.post(
            "/v1/sessions",
            json={"agent_id": agent_b},
            headers={
                "Authorization": f"Bearer {_token(rsa_key, 'idem-b')}",
                "Idempotency-Key": "shared",
            },
        )
    assert ra.status_code == 201
    assert rb.status_code == 201
    assert ra.json()["id"] != rb.json()["id"]  # same key, different org -> distinct
