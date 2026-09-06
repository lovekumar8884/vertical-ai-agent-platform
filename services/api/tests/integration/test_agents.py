"""Agents API — create/list, idempotency, auth, tenant isolation (real Postgres)."""

from __future__ import annotations

import datetime as dt
import types

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from vsa_api.main import app
from vsa_api.platform.auth import clerk


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


async def test_create_and_list_agent(make_org, rsa_key):
    await make_org(slug="agents-org")
    headers = {
        "Authorization": f"Bearer {_token(rsa_key, 'agents-org')}",
        "Idempotency-Key": "agent-1",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/v1/agents",
            json={"name": "Front Desk", "system_prompt": "Be kind."},
            headers=headers,
        )
        assert created.status_code == 201, created.text
        assert created.json()["id"].startswith("agn_")
        assert created.json()["status"] == "published"

        # Idempotent replay -> same agent, no duplicate.
        replay = await client.post(
            "/v1/agents",
            json={"name": "Front Desk", "system_prompt": "Be kind."},
            headers=headers,
        )
        assert replay.json()["id"] == created.json()["id"]

        listed = await client.get("/v1/agents", headers={"Authorization": headers["Authorization"]})
        assert listed.status_code == 200
        assert created.json()["id"] in [a["id"] for a in listed.json()]


async def test_create_requires_idempotency_key(make_org, rsa_key):
    await make_org(slug="agents-org2")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/v1/agents",
            json={"name": "X", "system_prompt": "y"},
            headers={"Authorization": f"Bearer {_token(rsa_key, 'agents-org2')}"},
        )
    assert resp.status_code == 400


async def test_agents_require_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/v1/agents")).status_code == 401


async def test_agents_are_tenant_isolated(make_org, rsa_key):
    await make_org(slug="agents-a")
    await make_org(slug="agents-b")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/v1/agents",
            json={"name": "A only", "system_prompt": "p"},
            headers={
                "Authorization": f"Bearer {_token(rsa_key, 'agents-a')}",
                "Idempotency-Key": "a-1",
            },
        )
        listed_b = await client.get(
            "/v1/agents",
            headers={"Authorization": f"Bearer {_token(rsa_key, 'agents-b')}"},
        )
    assert listed_b.status_code == 200
    assert listed_b.json() == []
