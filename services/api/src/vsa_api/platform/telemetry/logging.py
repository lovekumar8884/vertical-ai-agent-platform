"""Structured JSON logging via structlog.

Emits one JSON object per line to stdout, scrubs PII from every event, and
silences uvicorn's access logger so requests are logged once (by our own
middleware) instead of twice.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from vsa_api.platform.pii import scrub


def _scrub_processor(_logger: Any, _method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    return scrub(event_dict)


def configure_logging(level: str = "INFO") -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)

    # uvicorn logs each request on its access logger; we log requests in our
    # own middleware, so disable uvicorn's to avoid double logging.
    access = logging.getLogger("uvicorn.access")
    access.handlers = []
    access.propagate = False

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _scrub_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
