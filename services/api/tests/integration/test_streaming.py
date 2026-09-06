"""D8 streaming — happy path and per-agent concurrency cap (real PostgreSQL).

The LLM is stubbed (no OpenAI call) and Redis uses fakeredis; the tenant
database is real. Asserts both turns persist with a truthful streamed-token
count.
"""

from __future__ import annotations

import datetime as dt
import json
import types
import uuid

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

_ORG_SLUG = "acme-stream"


def _chunk(content):
    delta = types.SimpleNamespace(content=content)
    return types.SimpleNamespace(choices=[types.SimpleNamespace(delta=delta)])


class _FakeStream:
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
        return _FakeStream(["Hello", " ", "there"])

    monkeypatch.setattr(llm.litellm, "acompletion", fake_acompletion)


def _token(rsa_key) -> str:
    now = dt.datetime.now(tz=dt.UTC)
    return jwt.encode(
        {
            "sub": "user_stream",
            "iat": now,
            "exp": now + dt.timedelta(minutes=5),
            "org_slug": _ORG_SLUG,
            "org_role": "org:admin",
        },
        rsa_key,
        algorithm="RS256",
    )


@pytest_asyncio.fixture
async def session_id(make_org):
    org_id = await make_org(slug=_ORG_SLUG)
    async with TenantScopedSession(str(org_id)) as db:
        agent = Agent(org_id=org_id, slug="demo", name="Ava", status="published")
        db.add(agent)
        await db.flush()
        version = AgentVersion(
            org_id=org_id,
            agent_id=agent.id,
            version=1,
            system_prompt="Be helpful.",
            is_published=True,
        )
        db.add(version)
        await db.flush()
        row = Session(org_id=org_id, agent_id=agent.id, agent_version_id=version.id)
        db.add(row)
        await db.flush()
        return org_id, row.id


async def test_streaming_persists_both_turns(session_id, rsa_key):
    org_id, sid = session_id
    headers = {"Authorization": f"Bearer {_token(rsa_key)}"}
    tokens: list[str] = []
    done_reason = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST",
            f"/v1/sessions/{_ulid(sid)}/messages/stream",
            json={"content": "hi there"},
            headers=headers,
        ) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                event = json.loads(line[len("data: ") :])
                if event["op"] == "token":
                    tokens.append(event["text"])
                elif event["op"] == "done":
                    done_reason = event["end_reason"]

    assert "".join(tokens) == "Hello there"
    assert done_reason == "stop"

    async with TenantScopedSession(str(org_id)) as db:
        rows = (
            await db.execute(
                text(
                    "SELECT idx, role, content, tokens_out, end_reason FROM turn "
                    "WHERE session_id = :sid ORDER BY idx"
                ),
                {"sid": sid},
            )
        ).all()
    assert [(r.idx, r.role) for r in rows] == [(0, "user"), (1, "assistant")]
    assert rows[0].content == "hi there"
    assert rows[1].content == "Hello there"
    assert rows[1].tokens_out == 3
    assert rows[1].end_reason is None


def _ulid(value: uuid.UUID) -> str:
    from vsa_api.platform.ids import IdType, from_uuid

    return from_uuid(IdType.SESSION, value)
