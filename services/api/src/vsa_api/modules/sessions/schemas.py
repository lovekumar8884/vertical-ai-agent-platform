"""API schemas for sessions and turns (ULID-prefixed ids)."""

from __future__ import annotations

from pydantic import BaseModel


class SessionCreate(BaseModel):
    agent_id: str


class SessionOut(BaseModel):
    id: str
    agent_id: str
    agent_version_id: str
    channel: str


class TurnOut(BaseModel):
    id: str
    idx: int
    role: str
    content: str
