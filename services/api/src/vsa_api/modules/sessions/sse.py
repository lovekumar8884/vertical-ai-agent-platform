"""Server-Sent Events serialization for the streaming chat endpoint.

Sprint 1 ops: ``token`` (a text delta), ``error``, and ``done`` (terminal, with
``end_reason``). Each event is a single ``data:`` line with a JSON payload.
"""

from __future__ import annotations

import json
from typing import Any


def sse_event(op: str, **data: Any) -> str:
    return f"data: {json.dumps({'op': op, **data})}\n\n"
