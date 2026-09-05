"""Sentry initialization with a PII-scrubbing ``before_send`` hook.

The hook runs ``scrub`` over the whole event, so nested breadcrumbs and request
data are sanitized, not just top-level fields.
"""

from __future__ import annotations

from typing import Any

import sentry_sdk

from vsa_api.platform.pii import scrub


def _before_send(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    return scrub(event)


def init_sentry(dsn: str, environment: str) -> None:
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        send_default_pii=False,
        before_send=_before_send,
        traces_sample_rate=0.0,
    )
