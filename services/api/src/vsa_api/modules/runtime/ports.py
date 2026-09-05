"""Runtime ports — the stable seam other modules depend on.

Other bounded contexts import from here, never from the runtime's private
implementation (``prompt``, ``llm``), so the module stays independently
extractable.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Literal, Protocol, TypedDict

Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    role: Role
    content: str


class ChatStreamer(Protocol):
    """Streams assistant token deltas for a list of chat messages."""

    def __call__(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        timeout_s: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]: ...
