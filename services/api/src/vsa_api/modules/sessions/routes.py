"""Session HTTP routes: create a Test-Chat session and read its turns.

All endpoints require authentication and operate under the caller's org scope
(``TenantScopedSession``), so RLS guarantees tenant isolation.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import text

from vsa_api.config import get_settings
from vsa_api.modules.agents.models import Agent, AgentVersion
from vsa_api.modules.runtime.llm import LLMError, stream_chat
from vsa_api.modules.runtime.prompt import compose_messages
from vsa_api.modules.sessions import service
from vsa_api.modules.sessions.models import Session
from vsa_api.modules.sessions.schemas import (
    MessageCreate,
    SessionCreate,
    SessionOut,
    TurnOut,
)
from vsa_api.modules.sessions.sse import sse_event
from vsa_api.platform.auth.deps import require_org_id
from vsa_api.platform.cache.redis import get_cache_redis
from vsa_api.platform.concurrency import AgentConcurrencyLimiter, ConcurrencyLimitError
from vsa_api.platform.db.session import TenantScopedSession
from vsa_api.platform.errors import DomainError, TooManyRequestsError
from vsa_api.platform.idempotency import run_idempotent
from vsa_api.platform.ids import IdType, from_uuid, to_uuid

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


def _to_out(session_row: Session) -> SessionOut:
    return SessionOut(
        id=from_uuid(IdType.SESSION, session_row.id),
        agent_id=from_uuid(IdType.AGENT, session_row.agent_id),
        agent_version_id=from_uuid(IdType.AGENT_VERSION, session_row.agent_version_id),
        channel=session_row.channel,
    )


@router.post("", response_model=SessionOut, status_code=201)
async def create_session(
    body: SessionCreate,
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> SessionOut:
    if not idempotency_key:
        raise DomainError("Idempotency-Key header is required.")

    async def produce() -> dict:
        async with TenantScopedSession(str(org_id)) as db:
            row = await service.create_session(db, org_id=org_id, agent_id=to_uuid(body.agent_id))
            return _to_out(row).model_dump()

    result, _replayed = await run_idempotent(
        get_cache_redis(),
        org_id=str(org_id),
        idempotency_key=idempotency_key,
        produce=produce,
    )
    return SessionOut(**result)


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
) -> list[SessionOut]:
    async with TenantScopedSession(str(org_id)) as db:
        return [_to_out(row) for row in await service.list_sessions(db)]


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: str,
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
) -> SessionOut:
    async with TenantScopedSession(str(org_id)) as db:
        row = await service.get_session(db, session_id=to_uuid(session_id))
        return _to_out(row)


@router.get("/{session_id}/turns", response_model=list[TurnOut])
async def list_turns(
    session_id: str,
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
) -> list[TurnOut]:
    async with TenantScopedSession(str(org_id)) as db:
        await service.get_session(db, session_id=to_uuid(session_id))
        turns = await service.list_turns(db, session_id=to_uuid(session_id))
        return [
            TurnOut(
                id=from_uuid(IdType.TURN, turn.id),
                idx=turn.idx,
                role=turn.role,
                content=turn.content,
            )
            for turn in turns
        ]


@router.post("/{session_id}/messages/stream")
async def stream_message(
    session_id: str,
    body: MessageCreate,
    request: Request,
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
) -> StreamingResponse:
    settings = get_settings()
    sid = to_uuid(session_id)

    # Load context and persist the user turn immediately (RLS-scoped).
    async with TenantScopedSession(str(org_id)) as db:
        session_row = await service.get_session(db, session_id=sid)
        version = await db.get(AgentVersion, session_row.agent_version_id)
        agent = await db.get(Agent, session_row.agent_id)
        org_name = await db.scalar(text("SELECT name FROM org WHERE id = :id"), {"id": org_id})
        user_idx = await service.next_turn_index(db, session_id=sid)
        await service.append_turn(
            db,
            org_id=org_id,
            session_id=sid,
            idx=user_idx,
            role="user",
            content=body.content,
        )
        agent_id = session_row.agent_id

    messages = compose_messages(
        agent_name=agent.name,
        organization_name=org_name or "",
        instructions=version.system_prompt,
        user_input=body.content,
    )

    # Reserve a per-agent concurrency slot before streaming so we can return 429.
    limiter = AgentConcurrencyLimiter(
        get_cache_redis(), limit=settings.agent_concurrent_sessions_max
    )
    slot = limiter.slot(str(agent_id))
    try:
        await slot.__aenter__()
    except ConcurrencyLimitError as exc:
        raise TooManyRequestsError("Agent is at capacity; retry shortly.") from exc

    async def event_stream() -> AsyncIterator[str]:
        collected: list[str] = []
        end_reason: str | None = None
        try:
            stream = stream_chat(messages)
            try:
                async for delta in stream:
                    if await request.is_disconnected():
                        end_reason = "client_cancel"
                        break
                    collected.append(delta)
                    yield sse_event("token", text=delta)
            except LLMError:
                end_reason = "error"
                yield sse_event("error", message="The assistant failed to respond.")
            finally:
                await stream.aclose()
            yield sse_event("done", end_reason=end_reason or "stop")
        finally:
            await slot.__aexit__(None, None, None)
            # Persist the assistant turn on every exit path (done, error, cancel)
            # with a truthful streamed-token count (ADR-046).
            async with TenantScopedSession(str(org_id)) as db:
                await service.append_turn(
                    db,
                    org_id=org_id,
                    session_id=sid,
                    idx=user_idx + 1,
                    role="assistant",
                    content="".join(collected),
                    tokens_out=len(collected),
                    model=settings.llm_default_model,
                    end_reason=end_reason,
                )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
