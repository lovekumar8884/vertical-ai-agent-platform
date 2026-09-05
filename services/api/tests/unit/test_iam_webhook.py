import base64
import hashlib
import hmac

import pytest
from starlette.testclient import TestClient
from vsa_api.main import app
from vsa_api.modules.iam.service import (
    WebhookVerificationError,
    verify_webhook_signature,
)

_SECRET_B64 = base64.b64encode(b"super-secret-signing-key").decode()


def _sign(svix_id: str, svix_ts: str, payload: bytes) -> str:
    signed = f"{svix_id}.{svix_ts}.".encode() + payload
    digest = hmac.new(base64.b64decode(_SECRET_B64), signed, hashlib.sha256).digest()
    return f"v1,{base64.b64encode(digest).decode()}"


def test_valid_signature_passes():
    payload = b'{"type":"user.created"}'
    header = _sign("msg_1", "1700000000", payload)
    verify_webhook_signature(
        payload=payload,
        svix_id="msg_1",
        svix_timestamp="1700000000",
        svix_signature=header,
        secret="whsec_" + _SECRET_B64,
    )


def test_tampered_payload_fails():
    header = _sign("msg_1", "1700000000", b'{"type":"user.created"}')
    with pytest.raises(WebhookVerificationError):
        verify_webhook_signature(
            payload=b'{"type":"user.deleted"}',
            svix_id="msg_1",
            svix_timestamp="1700000000",
            svix_signature=header,
            secret="whsec_" + _SECRET_B64,
        )


def test_missing_headers_raise():
    with pytest.raises(WebhookVerificationError):
        verify_webhook_signature(
            payload=b"{}",
            svix_id=None,
            svix_timestamp=None,
            svix_signature=None,
            secret="whsec_" + _SECRET_B64,
        )


def test_me_without_auth_returns_401():
    client = TestClient(app)
    assert client.get("/v1/me").status_code == 401


def test_webhook_bad_signature_returns_401():
    client = TestClient(app)
    response = client.post(
        "/v1/webhooks/clerk",
        content=b"{}",
        headers={"svix-id": "x", "svix-timestamp": "1", "svix-signature": "v1,bad"},
    )
    assert response.status_code == 401
