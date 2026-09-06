"""Session/turn service operations.

All queries run inside a ``TenantScopedSession`` so Row-Level Security scopes
them to the caller's org — cross-tenant access is impossible by construction. A
session pins the agent's currently-published version at creation (ADR-045).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vsa_api.modules.agents.models import AgentVersion
from vsa_api.modules.sessions.models import Session, Turn
from vsa_api.platform.errors import ConflictError, NotFoundError


async def create_session(db: AsyncSession, *, org_id: uuid.UUID, agent_id: uuid.UUID) -> Session:
    version_id = await db.scalar(
        select(AgentVersion.id)
        .where(AgentVersion.agent_id == agent_id, AgentVersion.is_published.is_(True))
        .order_by(AgentVersion.version.desc())
        .limit(1)
    )
    if version_id is None:
        raise ConflictError("Agent has no published version to chat with.")

    session_row = Session(org_id=org_id, agent_id=agent_id, agent_version_id=version_id)
    db.add(session_row)
    await db.flush()
    return session_row


async def get_session(db: AsyncSession, *, session_id: uuid.UUID) -> Session:
    row = await db.get(Session, session_id)
    if row is None:
        raise NotFoundError("Session not found.")
    return row


async def list_sessions(db: AsyncSession) -> list[Session]:
    result = await db.execute(select(Session).order_by(Session.created_at.desc()))
    return list(result.scalars())


async def list_turns(db: AsyncSession, *, session_id: uuid.UUID) -> list[Turn]:
    result = await db.execute(select(Turn).where(Turn.session_id == session_id).order_by(Turn.idx))
    return list(result.scalars())


async def next_turn_index(db: AsyncSession, *, session_id: uuid.UUID) -> int:
    current_max = await db.scalar(
        select(Turn.idx).where(Turn.session_id == session_id).order_by(Turn.idx.desc()).limit(1)
    )
    return 0 if current_max is None else current_max + 1


async def append_turn(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    session_id: uuid.UUID,
    idx: int,
    role: str,
    content: str,
    tokens_out: int | None = None,
    model: str | None = None,
    end_reason: str | None = None,
) -> Turn:
    turn = Turn(
        org_id=org_id,
        session_id=session_id,
        idx=idx,
        role=role,
        content=content,
        tokens_out=tokens_out,
        model=model,
        end_reason=end_reason,
    )
    db.add(turn)
    await db.flush()
    return turn
