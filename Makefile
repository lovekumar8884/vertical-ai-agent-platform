.DEFAULT_GOAL := help
.PHONY: help install dev dev-infra dev-api dev-console db-up db-down down lint fmt typecheck test migrate migrate-down

# Local dev stack = base compose + developer host-port overrides.
COMPOSE_DEV := docker compose -f docker-compose.yml -f infra/compose/docker-compose.dev.yml

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

install: ## Install Python (uv) and Node (pnpm) dependencies
	uv sync
	pnpm install

dev-infra: ## Start backing services (Postgres, Redis, Mailpit)
	$(COMPOSE_DEV) up -d --wait

db-up: ## Start Postgres + Redis and wait until healthy
	$(COMPOSE_DEV) up -d --wait postgres redis

db-down: ## Stop backing services and remove their volumes
	$(COMPOSE_DEV) down -v

dev-api: ## Run the FastAPI app with hot reload
	cd services/api && uv run uvicorn vsa_api.main:app --reload --port 8000

dev-console: ## Run the Next.js console with hot reload
	cd apps/console && pnpm dev

dev: dev-infra ## Start infra, then instruct how to run api + console
	@echo "Infra is up. In two terminals run:"
	@echo "  make dev-api"
	@echo "  make dev-console"

down: ## Stop backing services
	$(COMPOSE_DEV) down

lint: ## Lint Python and TypeScript
	uv run ruff check services
	pnpm -r lint

fmt: ## Format Python and TypeScript
	uv run ruff format services
	pnpm -r format

typecheck: ## Type-check Python and TypeScript
	uv run mypy services
	pnpm -r typecheck

test: ## Run Python and TypeScript tests
	uv run pytest services
	pnpm -r test

migrate: ## Apply database migrations
	cd services/api && uv run alembic upgrade head

migrate-down: ## Roll back the last database migration
	cd services/api && uv run alembic downgrade -1
