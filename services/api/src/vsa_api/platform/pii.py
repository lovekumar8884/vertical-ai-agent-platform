"""PII scrubbing for logs and Sentry events.

A single ``scrub`` walks arbitrary structures (strings, dicts, lists, tuples) so
it can sanitize both structlog event dicts and nested Sentry breadcrumbs.
"""

from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# 13-19 digits, optionally split by spaces or dashes (matched before phones).
_CREDIT_CARD = re.compile(r"(?<![\d-])(?:\d[ -]?){13,19}(?<!\s)(?![\d-])")
# +?, 9-15 digits with common separators; guarded so it does not eat plain ints.
_PHONE = re.compile(r"(?<![\w.])\+?\d[\d\s().-]{7,}\d(?![\w.])")


def scrub_text(value: str) -> str:
    value = _EMAIL.sub(REDACTED, value)
    value = _CREDIT_CARD.sub(REDACTED, value)
    value = _PHONE.sub(REDACTED, value)
    return value


def scrub(value: Any) -> Any:
    if isinstance(value, str):
        return scrub_text(value)
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return type(value)(scrub(item) for item in value)
    return value
