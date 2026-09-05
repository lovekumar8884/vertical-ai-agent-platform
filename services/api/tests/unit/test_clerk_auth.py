import datetime as dt
import types

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from vsa_api.platform.auth import clerk
from vsa_api.platform.auth.clerk import AuthError, verify_token
from vsa_api.platform.auth.deps import Principal, UnauthorizedError, require_principal


@pytest.fixture
def rsa_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def _stub_jwks(monkeypatch, rsa_key):
    public_key = rsa_key.public_key()
    fake_client = types.SimpleNamespace(
        get_signing_key_from_jwt=lambda _token: types.SimpleNamespace(key=public_key)
    )
    monkeypatch.setattr(clerk, "_jwk_client", lambda: fake_client)


def _make_token(rsa_key, **overrides):
    now = dt.datetime.now(tz=dt.UTC)
    payload = {"sub": "user_123", "iat": now, "exp": now + dt.timedelta(minutes=5)}
    payload.update(overrides)
    return jwt.encode(payload, rsa_key, algorithm="RS256")


def test_valid_token_returns_claims(rsa_key):
    token = _make_token(rsa_key, org_id="org_abc", org_role="admin")
    claims = verify_token(token)
    assert claims["sub"] == "user_123"
    assert claims["org_id"] == "org_abc"


def test_expired_token_raises(rsa_key):
    now = dt.datetime.now(tz=dt.UTC)
    token = _make_token(rsa_key, exp=now - dt.timedelta(minutes=1))
    with pytest.raises(AuthError):
        verify_token(token)


def test_missing_sub_raises(rsa_key):
    now = dt.datetime.now(tz=dt.UTC)
    token = jwt.encode({"exp": now + dt.timedelta(minutes=5)}, rsa_key, algorithm="RS256")
    with pytest.raises(AuthError):
        verify_token(token)


async def test_require_principal_parses_org_context(rsa_key):
    token = _make_token(rsa_key, org_id="org_abc", org_role="admin")
    principal = await require_principal(authorization=f"Bearer {token}")
    assert isinstance(principal, Principal)
    assert principal.user_id == "user_123"
    assert principal.org_id == "org_abc"
    assert principal.org_role == "admin"


async def test_require_principal_rejects_missing_header():
    with pytest.raises(UnauthorizedError):
        await require_principal(authorization=None)


async def test_require_principal_rejects_non_bearer():
    with pytest.raises(UnauthorizedError):
        await require_principal(authorization="Basic xyz")
