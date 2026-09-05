"""Clerk JWT verification via JWKS (RS256).

Manual JWKS verification (PyJWT) rather than the Clerk SDK: fewer moving parts,
offline-testable with a self-signed key, and no network dependency in the hot
path beyond the cached JWKS fetch.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient

from vsa_api.config import get_settings


class AuthError(Exception):
    """Raised when a token is missing, malformed, or fails verification."""


@lru_cache
def _jwk_client() -> PyJWKClient:
    return PyJWKClient(get_settings().clerk_jwks_url)


def verify_token(token: str) -> dict[str, Any]:
    """Verify a Clerk session JWT and return its claims."""
    settings = get_settings()
    try:
        signing_key = _jwk_client().get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer or None,
            options={"verify_aud": False, "require": ["exp", "sub"]},
        )
    except Exception as exc:
        raise AuthError(str(exc)) from exc
