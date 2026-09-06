"""Agent HTTP routes: list agents and create an agent (published v1).

Authenticated, org-scoped (``TenantScopedSession`` + RLS). Creation is a
mutation and requires an ``Idempotency-Key`` header.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header

from vsa_api.modules.agents import service
from vsa_api.modules.agents.models import Agent
from vsa_api.modules.agents.schemas import AgentCreate, AgentOut
from vsa_api.platform.auth.deps import require_org_id
from vsa_api.platform.cache.redis import get_cache_redis
from vsa_api.platform.db.session import TenantScopedSession
from vsa_api.platform.errors import DomainError
from vsa_api.platform.idempotency import run_idempotent
from vsa_api.platform.ids import IdType, from_uuid

router = APIRouter(prefix="/v1/agents", tags=["agents"])


def _to_out(agent: Agent) -> AgentOut:
    return AgentOut(
        id=from_uuid(IdType.AGENT, agent.id),
        slug=agent.slug,
        name=agent.name,
        status=agent.status,
    )


@router.get("", response_model=list[AgentOut])
async def list_agents(
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
) -> list[AgentOut]:
    async with TenantScopedSession(str(org_id)) as db:
        return [_to_out(agent) for agent in await service.list_agents(db)]


@router.post("", response_model=AgentOut, status_code=201)
async def create_agent(
    body: AgentCreate,
    org_id: Annotated[uuid.UUID, Depends(require_org_id)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> AgentOut:
    if not idempotency_key:
        raise DomainError("Idempotency-Key header is required.")

    async def produce() -> dict:
        async with TenantScopedSession(str(org_id)) as db:
            agent = await service.create_agent(
                db,
                org_id=org_id,
                name=body.name,
                system_prompt=body.system_prompt,
                temperature=body.temperature,
            )
            return _to_out(agent).model_dump()

    result, _replayed = await run_idempotent(
        get_cache_redis(),
        org_id=str(org_id),
        idempotency_key=idempotency_key,
        produce=produce,
    )
    return AgentOut(**result)
