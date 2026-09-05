# syntax=docker/dockerfile:1
#
# API image. Build context = repository root (needs root pyproject.toml + uv.lock
# for the uv workspace). Built with:
#   docker build -f infra/docker/api.Dockerfile -t vsa-api .
FROM python:3.12-slim

# uv provides fast, fully-locked installs.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY services/api services/api

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package vsa-api

# Drop privileges for the runtime.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request as u, sys; sys.exit(0 if u.urlopen('http://localhost:8000/healthz').status == 200 else 1)"

CMD ["uvicorn", "vsa_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
