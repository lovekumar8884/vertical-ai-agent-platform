"""FastAPI application factory and process entrypoint.

Cross-cutting wiring (logging, Sentry, DB, Redis, error handling) is layered on
in later commits. This commit establishes the factory and the liveness/readiness
probes that Fly.io and the compose healthchecks call.
"""

from __future__ import annotations

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from vsa_api.config import Settings, get_settings
from vsa_api.modules.iam.routes import router as iam_router
from vsa_api.platform.cache.redis import get_cache_redis, get_session_redis
from vsa_api.platform.db.engine import get_engine
from vsa_api.platform.errors import register_error_handlers
from vsa_api.platform.middleware import request_id_middleware
from vsa_api.platform.telemetry.logging import configure_logging
from vsa_api.platform.telemetry.sentry import init_sentry


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    configure_logging(settings.log_level)
    init_sentry(settings.sentry_dsn_api, settings.env)

    app = FastAPI(
        title="Vertical AI Agent Platform API",
        version="0.1.0",
        docs_url="/docs" if settings.env != "prod" else None,
        redoc_url=None,
    )
    app.state.settings = settings

    app.middleware("http")(request_id_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)

    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        """Liveness: the process is up. No dependency checks."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["health"])
    async def readyz(response: Response) -> dict[str, object]:
        """Readiness: 200 only when Postgres and both Redis DBs are reachable."""
        checks: dict[str, str] = {}
        ready = True

        try:
            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["db"] = "ok"
        except Exception:
            checks["db"] = "error"
            ready = False

        for name, client in (
            ("redis_session", get_session_redis()),
            ("redis_cache", get_cache_redis()),
        ):
            try:
                await client.ping()
                checks[name] = "ok"
            except Exception:
                checks[name] = "error"
                ready = False

        response.status_code = 200 if ready else 503
        return {"status": "ready" if ready else "not_ready", "checks": checks}

    app.include_router(iam_router)

    return app


app = create_app()
