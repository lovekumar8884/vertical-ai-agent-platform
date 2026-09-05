"""FastAPI application factory and process entrypoint.

Cross-cutting wiring (logging, Sentry, DB, Redis, error handling) is layered on
in later commits. This commit establishes the factory and the liveness/readiness
probes that Fly.io and the compose healthchecks call.
"""

from __future__ import annotations

from fastapi import FastAPI

from vsa_api.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="Vertical AI Agent Platform API",
        version="0.1.0",
        docs_url="/docs" if settings.env != "prod" else None,
        redoc_url=None,
    )
    app.state.settings = settings

    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        """Liveness: the process is up. No dependency checks."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["health"])
    async def readyz() -> dict[str, str]:
        """Readiness: dependency checks (DB + Redis) are wired in a later commit."""
        return {"status": "ready"}

    return app


app = create_app()
