"""Strict Jinja2 system-prompt composition with ``<user_input>`` delimiter defense.

The composer renders the static system prompt (persona, AI self-disclosure,
optional KB context) and wraps the untrusted user message in ``<user_input>``
delimiters after neutralizing any delimiter markers the user tried to inject.
``StrictUndefined`` makes a missing template variable fail loudly.
"""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from vsa_api.modules.runtime.ports import ChatMessage

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_SYSTEM_TEMPLATE = "system.jinja"
_USER_INPUT_OPEN = "<user_input>"
_USER_INPUT_CLOSE = "</user_input>"
_DELIMITER_RE = re.compile(r"</?\s*user_input\s*>", re.IGNORECASE)

# Autoescape stays off: this renders prompt text, not HTML. User content is
# defended by escaping delimiter markers, not by HTML escaping.
environment = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    undefined=StrictUndefined,
    autoescape=False,  # noqa: S701
    keep_trailing_newline=True,
)


def render_system(**context: str) -> str:
    return environment.get_template(_SYSTEM_TEMPLATE).render(**context)


def escape_user_input(text: str) -> str:
    """Neutralize any ``<user_input>``/``</user_input>`` markers in raw user text."""
    return _DELIMITER_RE.sub("[filtered]", text)


def compose_messages(
    *,
    agent_name: str,
    organization_name: str,
    instructions: str,
    user_input: str,
    kb_context: str = "",
) -> list[ChatMessage]:
    system = render_system(
        agent_name=agent_name,
        organization_name=organization_name,
        instructions=instructions,
        kb_context=kb_context,
    )
    safe_user_input = escape_user_input(user_input)
    user = f"{_USER_INPUT_OPEN}\n{safe_user_input}\n{_USER_INPUT_CLOSE}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
