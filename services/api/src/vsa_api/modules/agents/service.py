"""Agent service operations, including the demo-agent provisioning hook."""

from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vsa_api.modules.agents.models import Agent, AgentVersion

_DEMO_SLUG = "demo"
_DEMO_PROMPT = (
    "You are a friendly, concise healthcare front-desk assistant. Help visitors "
    "with general questions and appointment requests. If you are unsure, say so."
)


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base or "agent"


async def create_agent(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    name: str,
    system_prompt: str,
    temperature: float = 0.7,
) -> Agent:
    """Create a published agent with its v1 version (frozen: Save = agent + v1)."""
    agent = Agent(
        org_id=org_id,
        slug=f"{_slugify(name)}-{uuid.uuid4().hex[:6]}",
        name=name,
        status="published",
    )
    db.add(agent)
    await db.flush()
    db.add(
        AgentVersion(
            org_id=org_id,
            agent_id=agent.id,
            version=1,
            system_prompt=system_prompt,
            is_published=True,
            spec={"temperature": temperature},
        )
    )
    await db.flush()
    return agent


async def list_agents(db: AsyncSession) -> list[Agent]:
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    return list(result.scalars())


async def ensure_demo_agent(session: AsyncSession, *, org_id: uuid.UUID) -> None:
    """Create a published Demo Agent (v1) for a new org, idempotently."""
    existing = await session.scalar(
        select(Agent.id).where(Agent.org_id == org_id, Agent.slug == _DEMO_SLUG)
    )
    if existing is not None:
        return

    agent = Agent(org_id=org_id, slug=_DEMO_SLUG, name="Demo Agent", status="published")
    session.add(agent)
    await session.flush()

    session.add(
        AgentVersion(
            org_id=org_id,
            agent_id=agent.id,
            version=1,
            system_prompt=_DEMO_PROMPT,
            is_published=True,
        )
    )
