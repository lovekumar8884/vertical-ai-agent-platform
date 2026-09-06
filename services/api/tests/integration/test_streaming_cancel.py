"""D8 cancellation contract (ADR-046): client disconnect mid-stream persists the
assistant turn with ``end_reason='client_cancel'`` and a truthful partial token
count. Real PostgreSQL; LLM + Redis stubbed.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import types

import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from vsa_api.main import app
from vsa_api.modules.agents.models import Agent, AgentVersion
from vsa_api.modules.runtime import llm
from vsa_api.modules.sessions import routes as sessions_routes
from vsa_api.modules.sessions.models import Session
from vsa_api.platform.auth import clerk
from vsa_api.platform.db.session import TenantScopedSession
from vsa_api.platform.ids import IdType, from_uuid

_ORG_SLUG = "acme-cancel"


def _chunk(content):
    delta = types.SimpleNamespace(content=content)
    return types.SimpleNamespace(choices=[types.SimpleNamespace(delta=delta)])


class _SlowStream:
    def __init__(self, contents):
        self._contents = contents

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for content in self._contents:
            yield _chunk(content)

    async def aclose(self):
        return None


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def _stubs(monkeypatch, rsa_key):
    public_key = rsa_key.public_key()
    monkeypatch.setattr(
        clerk,
        "_jwk_client",
        lambda: types.SimpleNamespace(
            get_signing_key_from_jwt=lambda _t: types.SimpleNamespace(key=public_key)
        ),
    )
    monkeypatch.setattr(sessions_routes, "get_cache_redis", FakeAsyncRedis)

    async def fake_acompletion(**_kwargs):
        return _SlowStream(["Hello", " world", " again"])

    monkeypatch.setattr(llm.litellm, "acompletion", fake_acompletion)

    # Simulate a client that disconnects after the first streamed token.
    calls = {"n": 0}

    async def fake_is_disconnected(_self):
        calls["n"] += 1
        return calls["n"] > 1

    monkeypatch.setattr("starlette.requests.Request.is_disconnected", fake_is_disconnected)


def _token(rsa_key) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    return jwt.encode(
        {
            "sub": "user_cancel",
            "iat": now,
            "exp": now + dt.timedelta(minutes=5),
            "org_slug": _ORG_SLUG,
            "org_role": "org:admin",
        },
        rsa_key,
        algorithm="RS256",
    )


@pytest_asyncio.fixture
async def session_ref(make_org):
    org_id = await make_org(slug=_ORG_SLUG)
    async with TenantScopedSession(str(org_id)) as db:
        agent = Agent(org_id=org_id, slug="demo", name="Ava", status="published")
        db.add(agent)
        await db.flush()
        version = AgentVersion(org_id=org_id, agent_id=agent.id, version=1, is_published=True)
        db.add(version)
        await db.flush()
        row = Session(org_id=org_id, agent_id=agent.id, agent_version_id=version.id)
        db.add(row)
        await db.flush()
        return org_id, row.id


async def _wait_for_assistant_turn(org_id, sid, max_wait=5.0):
    deadline = asyncio.get_event_loop().time() + max_wait
    while asyncio.get_event_loop().time() < deadline:
        async with TenantScopedSession(str(org_id)) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT content, tokens_out, end_reason FROM turn "
                        "WHERE session_id = :sid AND role = 'assistant'"
                    ),
                    {"sid": sid},
                )
            ).first()
        if row is not None:
            return row
        await asyncio.sleep(0.1)
    return None


async def test_disconnect_persists_partial_turn_as_client_cancel(session_ref, rsa_key):
    org_id, sid = session_ref
    headers = {"Authorization": f"Bearer {_token(rsa_key)}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST",
            f"/v1/sessions/{from_uuid(IdType.SESSION, sid)}/messages/stream",
            json={"content": "hi"},
            headers=headers,
        ) as resp:
            assert resp.status_code == 200
            async for _line in resp.aiter_lines():
                pass  # drain; the server cancels itself after the first token

    row = await _wait_for_assistant_turn(org_id, sid)
    assert row is not None, "assistant turn was not persisted after cancel"
    assert row.end_reason == "client_cancel"
    # Only the first token was collected before the simulated disconnect.
    assert row.tokens_out == 1
    assert row.content == "Hello"
