.DEFAULT_GOAL := help
.PHONY: help install dev dev-infra dev-api dev-console down lint fmt typecheck test migrate migrate-down

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

install: ## Install Python (uv) and Node (pnpm) dependencies
	uv sync
	pnpm install

dev-infra: ## Start backing services (Postgres, Redis, Mailpit)
	docker compose up -d

dev-api: ## Run the FastAPI app with hot reload
	cd services/api && uv run uvicorn vsa_api.main:app --reload --port 8000

dev-console: ## Run the Next.js console with hot reload
	cd apps/console && pnpm dev

dev: dev-infra ## Start infra, then instruct how to run api + console
	@echo "Infra is up. In two terminals run:"
	@echo "  make dev-api"
	@echo "  make dev-console"

down: ## Stop backing services
	docker compose down

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
