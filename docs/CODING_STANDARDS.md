# CODING STANDARDS

## 1. Guiding Principles

- **Boring code, exciting product.** Prefer well-known patterns over cleverness.
- **Explicit over implicit.** Types, contracts, errors, side effects — all named.
- **Small units, sharp boundaries.** SRP + hexagonal ports/adapters.
- **Fail fast, fail loud.** No silent errors; no bare `except`.
- **Async-first** for I/O; sync only where semantics require it.
- **API-first**: every service defines its contract before implementation.

## 2. Repo Layout Rules

- Monorepo (Turborepo/Nx for JS, uv workspaces for Python).
- No cross-service imports outside `packages/shared/*` (enforced by lint).
- No shared database schemas across services (see [MICROSERVICE_ARCHITECTURE.md](MICROSERVICE_ARCHITECTURE.md)).
- Every service has: `README.md`, `Makefile`, `Dockerfile`, `Chart.yaml`, `openapi.yaml` or `*.proto`.

## 3. Python

- **Version**: 3.12+.
- **Formatter**: `ruff format` (Black-compatible).
- **Linter**: `ruff` with rules: `E, F, I, N, UP, B, ANN, S, ASYNC, PTH, PL, RUF`.
- **Types**: `mypy --strict` (or `pyright strict`). No `Any` without justification comment.
- **Deps**: `uv` (or Poetry) with `pyproject.toml`; lockfile committed.
- **Style**:
  - `snake_case` variables/functions; `PascalCase` classes; `UPPER_SNAKE` constants.
  - Modules per bounded concept; avoid god modules.
  - Prefer pydantic v2 models for data at boundaries.
  - Prefer dataclasses / frozen models for internal DTOs.
  - `typing.Protocol` for structural typing at ports.
- **Async**:
  - `async def` for all I/O.
  - Use `anyio` primitives; avoid mixing `asyncio` and `trio`.
  - Cancellation-safe: use `async with` for resources; propagate cancellation.
- **Errors**:
  - Define a `DomainError` base; specific subclasses per bounded context.
  - Never swallow exceptions; log with context or re-raise.
  - Convert to HTTP problem+json only at edge.
- **Logging**: `structlog` with JSON renderer + OTel trace context binding.
- **Testing**: `pytest`, `pytest-asyncio`, `hypothesis` for properties, `pytest-benchmark` for hot paths.

## 4. TypeScript

- **Version**: TypeScript 5.5+, Node 22 LTS.
- **Runtime**: Bun for scripts/tools; Node for services.
- **Formatter**: `biome` or `prettier`.
- **Linter**: `biome` or `eslint` w/ `@typescript-eslint`, `security`, `sonarjs`.
- **Config**:
  - `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`.
  - Path aliases via `tsconfig.paths`; no relative `../..` chains.
- **Style**:
  - `camelCase`, `PascalCase`, `UPPER_SNAKE` per JS convention.
  - Prefer functions over classes; classes for stateful adapters.
  - `zod` for runtime validation of external inputs.
- **Framework**:
  - **Fastify** or **NestJS** for services (choose per service, not per week).
  - **Next.js 15 App Router** for console.
- **Testing**: Vitest / Jest, Playwright for e2e.

## 5. Go (for infra tooling & selected services)

- `gofmt` + `staticcheck` + `golangci-lint`.
- Clear package boundaries; small interfaces at consumer side.
- Context-first APIs (`ctx context.Context` always first arg).
- Errors wrapped with `%w`; sentinel errors sparingly.

## 6. API Design

- OpenAPI 3.1 spec is source of truth for REST.
- Protobuf (Buf) source of truth for gRPC.
- Breaking changes fail CI (Buf breaking, oas-diff).
- Errors always Problem+JSON (RFC 7807).
- Pagination cursor-based (never offset).
- IDs are ULID with type prefix (`ses_...`, `agn_...`).
- Times RFC 3339 UTC.

## 7. Database

- Postgres migrations via **Alembic** (Python) / **Kysely+dbmate** (TS) / **atlas**.
- Every migration reversible.
- Every table has `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`.
- Every table with `tenant_id` has RLS policy.
- Indexes measured before adding; documented in migration comment.
- No cross-service joins.

## 8. Configuration

- 12-factor env vars, typed schema (pydantic-settings / zod).
- No hardcoded URLs, credentials, or magic numbers.
- Secrets only via Vault Agent (Python: `hvac`; TS: `node-vault`).
- Feature flags via OpenFeature client.

## 9. Concurrency & Time

- All time comparisons UTC.
- Never `sleep()` in prod code; use timers/backoff with jitter.
- Bounded queues; explicit backpressure signals.
- Idempotency keys for all mutating operations.

## 10. Errors, Retries, Idempotency

- Retryable errors classified in a small enum (`TRANSIENT`, `RATE_LIMITED`, `TIMEOUT`, `UPSTREAM`, `PERMANENT`).
- Retry policy centralized (`tenacity` in Python, `p-retry` in TS).
- Idempotency-Key stored in Redis with response digest, 24h TTL.

## 11. Logging Conventions

- One JSON object per line.
- Required fields: `ts`, `level`, `service`, `msg`, `trace_id`, `tenant_id`, `session_id?`, `turn_id?`.
- No PII by default; use `pii=` field only in `pii-logs` stream.
- No `print()` / `console.log()` in committed code (lint rule).

## 12. Comments & Docs

- Code comments explain **why**, not **what**.
- Module docstring at top of every file (purpose + owner tag).
- Public functions have docstrings with `Args/Returns/Raises`.
- Architecture Decision Records (ADRs) in `docs/adr/NNNN-title.md`.

## 13. Git & Reviews

- **Trunk-based**, short-lived branches, small PRs (< 400 lines diff ideal).
- Conventional Commits (`feat:`, `fix:`, `chore:`, etc.).
- PR template: motivation, screenshots (UI), test coverage, migrations, rollout plan.
- 1+ code reviewer required; 2 for security/data model changes.
- CODEOWNERS per service.
- Squash-merge default.

## 14. Security in Code

- No secrets in code (gitleaks in CI).
- No `eval`, `exec`, unrestricted shell, unrestricted SQL string concat.
- Parameterized queries only.
- Sanitize/validate all external input with pydantic/zod.
- URL/HTML/SQL escapers used explicitly.
- Random via cryptographic RNG (`secrets` / `crypto`) not `random`.

## 15. Performance

- Profile before optimizing (`py-spy`, `clinic.js`, `pprof`).
- Set explicit timeouts on every I/O call.
- Batch DB writes where possible.
- Prefer streaming over buffering for large payloads.
- Cache with tenant-scoped keys + explicit TTLs.

## 16. Tests

- See [TESTING_STRATEGY.md](TESTING_STRATEGY.md).
- Coverage floor: 80% branch on new code (blocking CI check for changed files).
- Contract tests for every public API.
- Deterministic tests (freeze time via `freezegun`/`sinon`).

## 17. Dependencies

- Prefer stdlib + a small, stable set of libraries.
- New dep requires PR justification (weekly downloads, maintainers, license).
- Pin versions; renovate/dependabot for updates.
- License allowlist enforced (`fossa`, `scancode`).

## 18. Anti-Patterns Rejected

- ❌ Catch-all exceptions with silent pass.
- ❌ Singletons for stateful services.
- ❌ Business logic in controllers/handlers.
- ❌ Business logic in migrations.
- ❌ Manual retry loops without backoff.
- ❌ String-typed enums when a class enum would do.
- ❌ Long function chains for trivial data mapping.
- ❌ "Just this once" TODOs that live forever.

## 19. Definition of Done

- Feature works with tests, docs, metrics, alerts.
- Runbook updated if new failure modes introduced.
- Migration reversible + tested on staging.
- Feature flag defined (default off) for user-visible behavior.
- Release notes drafted.
- Owner tagged in CODEOWNERS.
