"""API schemas for the IAM surface (ULID-prefixed ids, ADR-042/043)."""

from __future__ import annotations

from pydantic import BaseModel


class OrgOut(BaseModel):
    id: str
    slug: str
    name: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str | None = None


class MembershipOut(BaseModel):
    id: str
    role: str
    org: OrgOut


class MemberOut(BaseModel):
    id: str
    role: str
    user: UserOut


class MeResponse(BaseModel):
    user: UserOut
    memberships: list[MembershipOut]
