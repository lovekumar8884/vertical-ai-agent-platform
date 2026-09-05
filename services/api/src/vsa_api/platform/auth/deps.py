"""FastAPI auth dependencies.

Extracts and verifies the bearer token, exposing a ``Principal`` (Clerk user +
optional org context) that route handlers depend on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Header

from vsa_api.platform.auth.clerk import AuthError, verify_token
from vsa_api.platform.errors import DomainError


class UnauthorizedError(DomainError):
    status_code = 401
    title = "Unauthorized"


@dataclass(frozen=True)
class Principal:
    user_id: str
    org_id: str | None
    org_role: str | None
    claims: dict[str, Any]


async def require_principal(
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token.")

    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = verify_token(token)
    except AuthError as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc

    return Principal(
        user_id=claims["sub"],
        org_id=claims.get("org_id"),
        org_role=claims.get("org_role"),
        claims=claims,
    )
