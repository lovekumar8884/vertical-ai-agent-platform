"""Session HTTP routes: create a Test-Chat session and read its turns.

All endpoints require authentication and operate under the caller's org scope
(``TenantScopedSession``), so RLS guarantees tenant isolation.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from vsa_api.modules.sessions import service
from vsa_api.modules.sessions.models import Session
from vsa_api.modules.sessions.schemas import SessionCreate, SessionOut, TurnOut
from vsa_api.platform.auth.deps import require_org_id
from vsa_api.platform.db.session import TenantScopedSession
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
) -> SessionOut:
    async with TenantScopedSession(str(org_id)) as db:
        row = await service.create_session(db, org_id=org_id, agent_id=to_uuid(body.agent_id))
        return _to_out(row)


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
