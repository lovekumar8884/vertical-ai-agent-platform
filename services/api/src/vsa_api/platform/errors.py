"""RFC 7807 Problem+JSON errors and the ``DomainError`` base.

Domain code raises ``DomainError`` (or a subclass); the registered handlers
render it as ``application/problem+json``. Unhandled exceptions become an opaque
500 so internals never leak to clients.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

PROBLEM_MEDIA_TYPE = "application/problem+json"


class DomainError(Exception):
    """Base for expected, client-facing errors."""

    status_code: int = 400
    title: str = "Bad Request"
    type: str = "about:blank"

    def __init__(self, detail: str, *, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.code = code


class NotFoundError(DomainError):
    status_code = 404
    title = "Not Found"


class ForbiddenError(DomainError):
    status_code = 403
    title = "Forbidden"


class ConflictError(DomainError):
    status_code = 409
    title = "Conflict"


def _problem(
    *,
    status_code: int,
    title: str,
    detail: str,
    type_: str,
    instance: str,
    code: str | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }
    if code is not None:
        body["code"] = code
    return JSONResponse(status_code=status_code, content=body, media_type=PROBLEM_MEDIA_TYPE)


async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return _problem(
        status_code=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        type_=exc.type,
        instance=request.url.path,
        code=exc.code,
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return _problem(
        status_code=500,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
        type_="about:blank",
        instance=request.url.path,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
