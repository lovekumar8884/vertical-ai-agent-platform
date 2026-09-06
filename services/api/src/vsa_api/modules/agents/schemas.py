"""API schemas for agents (ULID-prefixed ids)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    system_prompt: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AgentOut(BaseModel):
    id: str
    slug: str
    name: str
    status: str
