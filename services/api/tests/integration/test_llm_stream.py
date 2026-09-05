import types

import pytest
from vsa_api.modules.runtime import llm
from vsa_api.modules.runtime.llm import LLMError, stream_chat

_MESSAGES = [{"role": "user", "content": "hi"}]


def _chunk(content):
    delta = types.SimpleNamespace(content=content)
    choice = types.SimpleNamespace(delta=delta)
    return types.SimpleNamespace(choices=[choice])


class _FakeStream:
    def __init__(self, contents):
        self._contents = contents

    def __aiter__(self):
        return self._generate()

    async def _generate(self):
        for content in self._contents:
            yield _chunk(content)


def _stub_acompletion(monkeypatch, *, contents=None, calls=None, error=None):
    async def fake_acompletion(**kwargs):
        if calls is not None:
            calls.update(kwargs)
        if error is not None:
            raise error
        return _FakeStream(contents or [])

    monkeypatch.setattr(llm.litellm, "acompletion", fake_acompletion)


async def test_stream_concatenates_deltas(monkeypatch):
    _stub_acompletion(monkeypatch, contents=["Hello", ", ", "world"])
    out = [delta async for delta in stream_chat(_MESSAGES)]
    assert "".join(out) == "Hello, world"


async def test_uses_configured_model_and_streams(monkeypatch):
    calls: dict = {}
    _stub_acompletion(monkeypatch, contents=["x"], calls=calls)
    _ = [d async for d in stream_chat(_MESSAGES)]
    assert calls["model"] == "gpt-4o-mini"
    assert calls["stream"] is True
    assert calls["messages"] == _MESSAGES


async def test_response_token_limit_is_capped(monkeypatch):
    calls: dict = {}
    _stub_acompletion(monkeypatch, contents=["x"], calls=calls)
    _ = [d async for d in stream_chat(_MESSAGES, max_tokens=5000)]
    assert calls["max_tokens"] == 800


async def test_timeout_is_passed_through(monkeypatch):
    calls: dict = {}
    _stub_acompletion(monkeypatch, contents=["x"], calls=calls)
    _ = [d async for d in stream_chat(_MESSAGES, timeout_s=12.5)]
    assert calls["timeout"] == 12.5


async def test_empty_deltas_are_skipped(monkeypatch):
    _stub_acompletion(monkeypatch, contents=["a", None, "", "b"])
    out = [delta async for delta in stream_chat(_MESSAGES)]
    assert out == ["a", "b"]


async def test_provider_error_is_wrapped(monkeypatch):
    _stub_acompletion(monkeypatch, error=RuntimeError("boom"))
    with pytest.raises(LLMError):
        _ = [d async for d in stream_chat(_MESSAGES)]
