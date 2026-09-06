"""LiteLLM streaming chat wrapper.

Single provider in Sprint 1 (OpenAI ``gpt-4o-mini``), no LangGraph, no
multi-provider fallback. Enforces the configured request timeout and a hard
response-token ceiling, and surfaces provider failures as ``LLMError``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import litellm

from vsa_api.config import get_settings
from vsa_api.modules.runtime.ports import ChatMessage


class LLMError(Exception):
    """Raised when the LLM provider call or stream fails."""


async def stream_chat(
    messages: list[ChatMessage],
    *,
    model: str | None = None,
    timeout_s: float | None = None,
    max_tokens: int | None = None,
) -> AsyncIterator[str]:
    """Yield assistant token deltas for ``messages`` from the configured model."""
    settings = get_settings()

    token_ceiling = settings.llm_max_response_tokens
    effective_max_tokens = (
        min(max_tokens, token_ceiling) if max_tokens is not None else token_ceiling
    )

    try:
        stream = await litellm.acompletion(
            model=model or settings.llm_default_model,
            messages=messages,
            api_key=settings.llm_openai_api_key.get_secret_value(),
            stream=True,
            timeout=timeout_s if timeout_s is not None else settings.llm_chat_timeout_s,
            max_tokens=effective_max_tokens,
        )
    except Exception as exc:
        raise LLMError(str(exc)) from exc

    try:
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    finally:
        # Abort the provider stream on completion OR caller cancellation (aclose).
        aclose = getattr(stream, "aclose", None)
        if aclose is not None:
            await aclose()
