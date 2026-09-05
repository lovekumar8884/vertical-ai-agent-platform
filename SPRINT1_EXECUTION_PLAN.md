# SPRINT 1 — EXECUTION PLAN

**Role:** Tech Lead. Architecture is frozen. This document converts [SPRINT1_FINAL_SCOPE.md](SPRINT1_FINAL_SCOPE.md) into an engineering execution plan. No new scope. No redesign.

**Inputs (only):** [ARCHITECTURE_FREEZE_V1.md](ARCHITECTURE_FREEZE_V1.md) · [SPRINT1_FINAL_SCOPE.md](SPRINT1_FINAL_SCOPE.md) · [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) · [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md).

**Optimized for:** one engineer, frequent commits, sub-20-minute reviews.

Effort unit: **dev-hours** (h). One engineer, focused. Estimates assume the pre-implementation checklist is already green (accounts created, keys captured, discovery calls done).

---

## Deliverable D1 — Repo scaffold + pre-commit + env + lint boundaries

**Objective:** A clonable monorepo with `uv` (Python) + `pnpm` (TS) workspaces, top-level `Makefile`, `.env.example`, `.gitignore`, pre-commit hooks (gitleaks, ruff, prettier, eslint), and an `import-linter` config declaring module boundaries.

**Files to create:**
- `README.md` (run-it section)
- `Makefile`
- `pyproject.toml` (uv workspace root)
- `package.json`, `pnpm-workspace.yaml`
- `.env.example`
- `.gitignore`, `.gitattributes`, `.editorconfig`
- `.pre-commit-config.yaml`
- `.importlinter` (module boundary contracts)
- `services/api/pyproject.toml` (placeholder package)
- `apps/console/package.json` (placeholder)

**Files to modify:** none (first commit set).

**Dependencies:** none. This is the root.

**Estimated effort:** 4h.

**Risks:**
- `uv` + `pnpm` workspace interplay in one repo — keep them independent, no shared tooling.
- Pre-commit hooks too strict on an empty repo (skip hooks that need source until D3/D4).

**Tests to write:** `make lint` runs clean on the empty scaffold. Pre-commit `--all-files` passes.

**Definition of Done:** Fresh clone → `make lint` green; `.env` is gitignored; gitleaks blocks a planted fake secret in a local test.

---

## Deliverable D2 — Docker Compose local stack + Neon compat check

**Objective:** `make dev` boots Postgres 16 (with `pgvector`), two Redis instances (session + cache), and Mailpit. A committed script verifies async SQLAlchemy works against a Neon-pooled endpoint (`statement_cache_size=0`).

**Files to create:**
- `docker-compose.yml`
- `infra/compose/docker-compose.dev.yml` (override)
- `infra/compose/docker-compose.ci.yml` (override)
- `services/api/scripts/verify_neon.py`

**Files to modify:**
- `Makefile` (add `dev`, `db-up`, `db-down`)
- `.env.example` (DB + two Redis URLs)

**Dependencies:** D1.

**Estimated effort:** 4h.

**Risks:**
- `pgvector/pgvector:pg16` image pin drift — pin an exact tag.
- Two Redis DBs locally = one container, two logical DBs (db 0 session, db 1 cache); mirror the Upstash split without two containers.
- asyncpg prepared-statement cache vs. pooled endpoint — the whole reason `verify_neon.py` exists.

**Tests to write:** `verify_neon.py` connects, runs `SELECT 1`, and a parameterized query twice (proves no prepared-statement error). CI job `compose-smoke` boots the stack and healthchecks.

**Definition of Done:** `make dev` brings all containers healthy in < 60s; `verify_neon.py` passes against a real Neon branch.

---

## Deliverable D3 — FastAPI skeleton (platform layer)

**Objective:** FastAPI app factory with `/healthz`, `/readyz`, structured JSON logs (`structlog`), Sentry init + PII scrubber, CORS, `request_id` middleware, async SQLAlchemy engine, `TenantScopedSession` wrapper, Redis clients, and the ULID↔UUID helper.

**Files to create:**
- `services/api/src/vsa_api/main.py`
- `services/api/src/vsa_api/config.py` (pydantic-settings)
- `services/api/src/vsa_api/platform/telemetry/logging.py`
- `services/api/src/vsa_api/platform/telemetry/sentry.py` (with `before_send` PII scrubber)
- `services/api/src/vsa_api/platform/db/engine.py`
- `services/api/src/vsa_api/platform/db/session.py` (`TenantScopedSession`)
- `services/api/src/vsa_api/platform/cache/redis.py`
- `services/api/src/vsa_api/platform/errors.py` (Problem+JSON, `DomainError`)
- `services/api/src/vsa_api/platform/ids.py` (ULID prefix table + UUID conversion)
- `services/api/src/vsa_api/platform/middleware.py` (request_id)
- `services/api/src/vsa_api/platform/pii.py` (regex scrubber)
- `services/api/Dockerfile` → `infra/docker/api.Dockerfile`
- `services/api/tests/unit/test_ids.py`
- `services/api/tests/unit/test_pii.py`

**Files to modify:**
- `services/api/pyproject.toml` (deps: fastapi, uvicorn, sqlalchemy, asyncpg, structlog, sentry-sdk, pydantic-settings, redis, python-ulid)
- `.importlinter` (add platform-layer contract)

**Dependencies:** D2 (needs DB + Redis to boot `/readyz`).

**Estimated effort:** 8h.

**Risks:**
- Sentry PII scrubber must catch nested breadcrumbs, not just top-level — test with a fixture.
- `TenantScopedSession` must set `SET LOCAL app.org_id` inside the transaction, not on the connection (pooled connections leak otherwise).
- structlog + uvicorn access-log double-logging — disable uvicorn access logger.

**Tests to write:** `test_ids` (round-trips every prefix), `test_pii` (email/phone/CC redaction incl. nested dict), integration `test_health` (`/healthz` 200, `/readyz` checks DB+Redis).

**Definition of Done:** API boots locally; `/readyz` green only when DB+Redis reachable; PII scrubber unit tests green; import-linter passes.

---

## Deliverable D4 — Next.js console skeleton

**Objective:** Next.js 15 App Router + Tailwind + shadcn/ui, HSTS + secure-cookie middleware, an app shell (sidebar: Agents, Conversations, Settings), and a hand-written typed API client under `apps/console/lib/api/`.

**Files to create:**
- `apps/console/package.json`, `next.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`
- `apps/console/app/layout.tsx`, `apps/console/app/page.tsx`
- `apps/console/app/(app)/layout.tsx` (shell)
- `apps/console/components/ui/*` (shadcn init)
- `apps/console/lib/api/client.ts`
- `apps/console/lib/api/types.ts`
- `apps/console/middleware.ts` (HSTS, secure cookies)
- `infra/docker/console.Dockerfile`

**Files to modify:**
- `package.json` (workspace scripts)
- `.env.example` (`NEXT_PUBLIC_*`)

**Dependencies:** D1 (parallelizable with D2/D3 — no runtime coupling yet).

**Estimated effort:** 6h.

**Risks:**
- shadcn/ui init writes many files — commit the init separately (see commits) to keep review small.
- App Router server/client component boundary confusion — keep the shell server-first.

**Tests to write:** Playwright smoke stub (loads `/`, sees the shell). Full auth e2e comes in D9.

**Definition of Done:** `pnpm dev` renders the shell; HSTS header present; `pnpm typecheck` + `pnpm lint` green.

---

## Deliverable D5 — Authentication end-to-end (Clerk)

**Objective:** Clerk sign-in/sign-up/org creation in the console; Clerk-JWT verification in the API; `POST /v1/webhooks/clerk` (Svix HMAC); lazy-upsert backstop on first authenticated request; `GET /v1/me`.

**Files to create:**
- `services/api/src/vsa_api/platform/auth/clerk.py` (JWT verify via JWKS)
- `services/api/src/vsa_api/platform/auth/deps.py` (`current_user`, `current_org`)
- `services/api/src/vsa_api/modules/iam/models.py` (user, org, membership)
- `services/api/src/vsa_api/modules/iam/service.py` (upsert logic)
- `services/api/src/vsa_api/modules/iam/routes.py` (`/me`, `/webhooks/clerk`, `/orgs/{id}/members`)
- `services/api/src/vsa_api/modules/iam/schemas.py`
- `services/api/tests/integration/test_clerk_webhook.py`
- `apps/console/app/(auth)/sign-in/[[...sign-in]]/page.tsx`
- `apps/console/app/(auth)/sign-up/[[...sign-up]]/page.tsx`

**Files to modify:**
- `apps/console/app/layout.tsx` (ClerkProvider)
- `apps/console/middleware.ts` (Clerk auth middleware)
- `services/api/src/vsa_api/main.py` (mount iam router)

**Dependencies:** D3 (API platform), D4 (console shell), and **D6 is co-dependent** — iam models need the migration. Sequence: write models in D5, migration in D6; or fold iam tables into D6's `0001`. **Decision: iam models defined in D5, all DDL emitted in D6's single `0001` migration.**

**Estimated effort:** 10h.

**Risks:**
- `clerk-sdk-python` maintenance — fall back to manual JWKS verification (~100 LOC) if flaky. Budget for the fallback.
- Webhook signature (Svix) must be verified on raw body, before JSON parsing.
- Lazy-upsert race: two concurrent first-requests → use `INSERT ... ON CONFLICT DO NOTHING` then read.

**Tests to write:** webhook HMAC valid/invalid; `user.created`/`organization.created` upsert; lazy-upsert on first `/me` when webhook was missed; unauthorized `/me` → 401.

**Definition of Done:** Console login works; `/me` returns the DB-backed user+org; webhook upserts; missing-webhook backstop upserts on first call.

---

## Deliverable D6 — Migration 0001 (schema + RLS + pgvector + audit + demo agent)

**Objective:** One Alembic migration creating every Sprint 1 table with RLS enabled, the `pgvector` extension + `chunk` table + HNSW index, monthly partitions on `session`/`turn`/`audit_log`, the audit-log decorator, and auto-creation of a "Demo Agent" on org creation.

**Files to create:**
- `services/api/alembic.ini`
- `services/api/migrations/env.py`
- `services/api/migrations/versions/0001_initial.py`
- `services/api/src/vsa_api/modules/agents/models.py` (agent, agent_version)
- `services/api/src/vsa_api/modules/sessions/models.py` (session, turn)
- `services/api/src/vsa_api/platform/audit.py` (decorator)
- `services/api/src/vsa_api/modules/agents/service.py` (create Demo Agent hook)
- `services/api/tests/integration/test_migration_roundtrip.py`
- `services/api/tests/integration/test_rls.py`
- `services/api/tests/integration/test_audit_decorator.py`

**Files to modify:**
- `services/api/src/vsa_api/modules/iam/service.py` (call Demo Agent creation on org upsert)
- `Makefile` (`migrate`, `migrate-down`)

**Dependencies:** D3 (engine), D5 (iam models).

**Estimated effort:** 10h.

**Risks:**
- RLS policy using `current_setting('app.org_id', true)` must handle the unset case (return no rows, not error) — the `true` flag matters.
- HNSW index creation on an empty table is fine but must be in the migration, not lazy.
- Partition creation in Alembic — write explicit `CREATE TABLE ... PARTITION OF` for current + next 2 months.
- Audit decorator must not swallow the wrapped exception.

**Tests to write:** `up → down → up` on fresh DB; RLS blocks cross-org reads (set `app.org_id` to A, query B → empty); audit decorator writes a row on create/update/delete; Demo Agent exists after org upsert.

**Definition of Done:** Migration round-trips in CI; RLS test green; audit rows produced; Demo Agent auto-created.

---

## Deliverable D7 — LLM integration + system-prompt template

**Objective:** LiteLLM SDK wrapper (single provider `gpt-4o-mini`, `timeout=20`, `max_tokens=800`), a Jinja2-compiled system-prompt template with delimiter defense (`<user_input>`, `<kb_context>` placeholders) and AI self-disclosure, and a prompt composer with the fixed composition order.

**Files to create:**
- `services/api/src/vsa_api/modules/runtime/llm.py` (`stream_chat`)
- `services/api/src/vsa_api/modules/runtime/prompt.py` (Jinja2 composer)
- `services/api/src/vsa_api/modules/runtime/templates/system.jinja`
- `services/api/src/vsa_api/modules/runtime/ports.py` (interface for future extraction)
- `services/api/tests/unit/test_prompt_composer.py`
- `services/api/tests/integration/test_llm_stream.py` (respx-stubbed)

**Files to modify:**
- `services/api/pyproject.toml` (litellm, jinja2)
- `.env.example` (model, timeouts, max tokens)
- `.importlinter` (runtime module contract)

**Dependencies:** D3 (config, platform).

**Estimated effort:** 8h.

**Risks:**
- LiteLLM streaming abort API — confirm `.aclose()`/cancellation works with the OpenAI provider (needed for D8).
- Jinja2 `StrictUndefined` will raise on any missing var — test the happy path thoroughly.
- Delimiter escaping: user input containing `</user_input>` must be neutralized (escape or strip).

**Tests to write:** composer output ordering + delimiter escaping of hostile input; AI-disclosure line present; streamed deltas concatenate to full text (respx stub).

**Definition of Done:** `stream_chat` yields token deltas from a stubbed provider; composer renders the contract order; hostile `</user_input>` cannot break out.

---

## Deliverable D8 — Streaming SSE endpoint + cancellation + leakage harness

**Objective:** `POST /v1/sessions/{id}/messages/stream` (SSE), persisting the user turn immediately and the assistant turn on `done`/cancel, with the ADR-046 cancellation contract, per-agent concurrency cap, rate limits, and the cross-tenant leakage test harness.

**Files to create:**
- `services/api/src/vsa_api/modules/sessions/service.py`
- `services/api/src/vsa_api/modules/sessions/routes.py` (sessions CRUD + stream)
- `services/api/src/vsa_api/modules/sessions/sse.py` (event serializer)
- `services/api/src/vsa_api/platform/ratelimit.py` (Redis token bucket)
- `services/api/src/vsa_api/platform/concurrency.py` (per-agent cap)
- `services/api/tests/integration/test_streaming.py`
- `services/api/tests/integration/test_streaming_cancel.py`
- `services/api/tests/integration/test_tenant_leakage.py`

**Files to modify:**
- `services/api/src/vsa_api/main.py` (mount sessions router)
- `services/api/src/vsa_api/modules/runtime/llm.py` (support abort signal)

**Dependencies:** D6 (session/turn tables), D7 (LLM + composer).

**Estimated effort:** 12h. **(Largest deliverable — the critical-path peak.)**

**Risks:**
- Client-disconnect detection in Starlette SSE (`await request.is_disconnected()`) must actually cancel the LLM task — wire an `asyncio.Task` + cancel.
- Partial-turn persistence must record truthful `tokens_out` (count streamed tokens, don't trust the provider's final usage on cancel).
- Concurrency cap must decrement on every exit path (success, error, cancel) — use `try/finally`.
- Leakage harness is the security keystone — it must hit **every** endpoint, not a sample.

**Tests to write:** happy-path stream persists both turns; disconnect mid-stream persists assistant turn with `end_reason='client_cancel'` + correct token count; concurrency cap returns 429 at limit and recovers; leakage test iterates all endpoints for org B as org A → 403/404 + filtered lists.

**Definition of Done:** streaming works end to end (stubbed LLM); cancellation contract verified; concurrency cap enforced; leakage tests green across all endpoints.

---

## Deliverable D9 — Console flows (Agents, Test Chat, Conversations, Members)

**Objective:** Agents list + create form (name, system prompt, single-model dropdown, temperature slider), Test Chat (renamed Playground) with live SSE rendering, Conversations tab with transcript view, read-only Members view. Draft+Published only.

**Files to create:**
- `apps/console/app/(app)/agents/page.tsx` (list)
- `apps/console/app/(app)/agents/new/page.tsx` (create)
- `apps/console/app/(app)/agents/[id]/page.tsx` (detail + tabs)
- `apps/console/app/(app)/agents/[id]/test-chat.tsx`
- `apps/console/app/(app)/agents/[id]/conversations.tsx`
- `apps/console/app/(app)/settings/members/page.tsx`
- `apps/console/components/chat/*` (message list, input, streaming hook)
- `apps/console/lib/api/agents.ts`, `sessions.ts`
- `apps/console/lib/sse.ts` (EventSource/fetch-stream parser)
- `apps/console/e2e/agent-chat.spec.ts` (Playwright)

**Files to modify:**
- `apps/console/lib/api/client.ts` (auth header injection)
- `apps/console/app/(app)/layout.tsx` (nav links)

**Dependencies:** D5 (auth), D8 (endpoints).

**Estimated effort:** 12h.

**Risks:**
- SSE from the browser with auth headers — `EventSource` can't set headers; use `fetch` + `ReadableStream` parser.
- Streaming render jank — append deltas via a ref, not per-token React state churn.
- Optimistic user message + reconciliation on `done`.

**Tests to write:** Playwright e2e — sign-in (Clerk test token) → create agent → send message → assert streamed tokens render → refresh → assert history loads.

**Definition of Done:** Full cold-user flow works on `localhost` and prod URL; e2e smoke green.

---

## Deliverable D10 — CI/CD + preview environments

**Objective:** GitHub Actions with per-language path filters, Docker buildx + GHA cache, Neon branch per PR, Upstash key-prefix namespace per PR, Fly `-pr-<n>` preview deploy, teardown on PR close, and a manual rollback action.

**Files to create:**
- `.github/workflows/ci.yml`
- `.github/workflows/preview.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/rollback.yml`
- `.github/actions/neon-branch/action.yml`
- `infra/fly/fly.api.toml`, `fly.console.toml`, `fly.worker.toml`

**Files to modify:**
- `Makefile` (`ci`, `build`)
- `infra/docker/*` (buildx cache mounts)

**Dependencies:** D3, D4 (buildable images), D6 (migrations to run as release_command).

**Estimated effort:** 10h.

**Risks:**
- Neon branch API + teardown lifecycle tied to PR events — leaked branches cost money; ensure `pull_request: closed` cleanup runs even on force-close.
- Fly preview app naming collisions — use `vsa-api-pr-<number>`.
- Secrets in Actions — least-privilege tokens; never echo.
- Path filters must not skip a needed job (e.g., a shared `.env.example` change).

**Tests to write:** a throwaway PR proves preview URL is commented; closing it tears down the Neon branch + Fly apps; `up→down→up` migration gate runs in CI.

**Definition of Done:** PR → preview URL commented; merge → prod deploy + migration; rollback action reverts a test release; CI path filters verified.

---

## Deliverable D11 — Deploy to Fly (prod infra)

**Objective:** Prod running in `iad`: Neon paid tier (30-day PITR), two Upstash DBs (`session` noeviction, `cache` allkeys-lru), Sentry projects, Better Stack uptime on `/healthz`.

**Files to create:**
- `infra/fly/README.md` (region + secrets runbook)

**Files to modify:**
- `infra/fly/fly.api.toml`, `fly.console.toml` (primary_region=iad, health checks)
- `.env.example` (prod notes)

**Dependencies:** D10 (deploy workflow).

**Estimated effort:** 6h.

**Risks:**
- Neon region must equal Fly region — verify both `us-east`.
- Upstash eviction policy set per DB (easy to forget on the cache DB).
- Fly health-check path + grace period tuning (avoid killing during migration).

**Tests to write:** post-deploy smoke (curl prod `/healthz`, `/readyz`); a real sign-up on prod URL.

**Definition of Done:** Prod URLs live over HTTPS+HSTS; Sentry receives events; Better Stack pings green; a real cold sign-up + chat works on prod.

---

## Deliverable D12 — Ops safety net

**Objective:** Sentry alerts, Better Stack incidents → Slack, one completed Neon PITR restore drill, and a `docs/RUNBOOK.md` populated with the top-5 incidents.

**Files to create:**
- `docs/RUNBOOK.md` (LLM down, PG pool exhausted, Fly crash, Clerk webhook failure, widget/endpoint flood)
- `services/api/scripts/restore_drill.md` (steps + evidence)

**Files to modify:**
- `services/api/src/vsa_api/platform/telemetry/sentry.py` (alert tags)

**Dependencies:** D11 (prod exists to monitor).

**Estimated effort:** 4h.

**Risks:**
- Restore drill on Neon must target a **branch**, never prod.
- Alert fatigue — page only on `/healthz` down + error-rate spike; everything else to Slack.

**Tests to write:** trigger a synthetic Sentry error and confirm alert routing; execute the restore drill once and record evidence.

**Definition of Done:** Alerts route correctly; restore drill completed with written evidence; runbook covers the 5 incidents.

---

## Deliverable D13 — Docs + Loom demo + retro

**Objective:** `README.md` "run it" section finalized, a 2-minute Loom (signup → agent → chat), and a Sprint 1 retro doc.

**Files to create:**
- `notes/sprint1_retro.md`

**Files to modify:**
- `README.md` (finalize run-it + prod URL + demo link)

**Dependencies:** D9 (working flow), D11 (prod URL).

**Estimated effort:** 2h.

**Risks:** none material.

**Tests to write:** none (documentation deliverable). Verify README steps on a truly clean clone.

**Definition of Done:** A stranger following README reaches a running app; Loom recorded; retro written.

---

## Dependency Graph

```
D1  (repo scaffold)
├── D2  (docker compose + neon check)
│    └── D3  (fastapi platform)
│         ├── D5  (auth end-to-end) ──────────┐
│         │    └── D6  (migration 0001) ◄──────┘  (D6 needs iam models from D5)
│         │         ├── D7  (llm + prompt)
│         │         │    └── D8  (SSE stream + cancel + leakage) ◄── needs D7
│         │         └── D8  (also needs D6 tables)
│         └── D7  (llm can start after D3, parallel to D5/D6)
├── D4  (next.js console)  ── parallel to D2/D3
│    └── D9  (console flows) ◄── needs D5 (auth) + D8 (endpoints)
├── D10 (CI/CD + preview) ◄── needs D3, D4 (images), D6 (migrations)
│    └── D11 (deploy to fly) ◄── needs D10
│         └── D12 (ops safety net) ◄── needs D11
└── D13 (docs + loom + retro) ◄── needs D9 + D11
```

Textual precedence (must-happen-before):
- D1 → everything.
- D2 → D3.
- D3 → D5, D7, D10.
- D4 → D9, D10.
- D5 → D6, D9.
- D6 → D8, D10.
- D7 → D8.
- D8 → D9.
- D10 → D11.
- D11 → D12, D13.
- D9 → D13.

Parallelizable pairs for a single engineer (context-switch, not true parallel): **D4 while D2/D3 compile**; **D7 right after D3, before D5 lands**.

---

## Critical Path

```
D1 → D2 → D3 → D5 → D6 → D7 → D8 → D9 → D13
```

with **D10 → D11 → D12** as a parallel infra track that must finish before D13's prod URL step.

**Critical-path effort:** D1(4) + D2(4) + D3(8) + D5(10) + D6(10) + D7(8) + D8(12) + D9(12) + D13(2) = **70h**.
Infra track D10(10) + D11(6) + D12(4) = **20h**, overlaps with the tail of the critical path.

**Peak-risk deliverable:** **D8** (streaming + cancellation + leakage harness). Front-load nothing else during D8.

**Total Sprint 1 effort:** ~90 dev-hours ≈ 10–11 focused days for one engineer. Matches the 2-week window with buffer.

---

## Atomic Commit Decomposition

Each commit ≤ its Max LOC, reviewable in < 20 minutes. Titles are Conventional Commits.

### D1 — Repo scaffold

**Commit 01 — chore: initialize monorepo workspaces**
- Purpose: root workspace config for uv + pnpm.
- Files: `pyproject.toml`, `package.json`, `pnpm-workspace.yaml`, `.gitignore`, `.gitattributes`, `.editorconfig`
- Expected review: 120 LOC · Max: 150

**Commit 02 — chore: add Makefile and README run-it section**
- Purpose: top-level task runner + onboarding.
- Files: `Makefile`, `README.md`
- Expected review: 100 LOC · Max: 150

**Commit 03 — chore: add .env.example and secret hygiene**
- Purpose: documented env surface + gitleaks.
- Files: `.env.example`, `.pre-commit-config.yaml`
- Expected review: 90 LOC · Max: 120

**Commit 04 — chore: declare module import boundaries**
- Purpose: `import-linter` contracts + placeholder package manifests.
- Files: `.importlinter`, `services/api/pyproject.toml`, `apps/console/package.json`
- Expected review: 110 LOC · Max: 150

### D2 — Docker Compose

**Commit 05 — chore: docker-compose dev stack**
- Purpose: Postgres+pgvector, Redis, Mailpit.
- Files: `docker-compose.yml`, `infra/compose/docker-compose.dev.yml`
- Expected review: 130 LOC · Max: 160

**Commit 06 — chore: CI compose override + make dev targets**
- Files: `infra/compose/docker-compose.ci.yml`, `Makefile` (edit)
- Expected review: 70 LOC · Max: 100

**Commit 07 — feat(db): Neon pooled-endpoint compatibility script**
- Files: `services/api/scripts/verify_neon.py`
- Expected review: 90 LOC · Max: 120

### D3 — FastAPI platform

**Commit 08 — feat(api): app factory, config, health endpoints**
- Files: `main.py`, `config.py` (+ mount health)
- Expected review: 150 LOC · Max: 180

**Commit 09 — feat(api): structured logging + Sentry PII scrubber**
- Files: `platform/telemetry/logging.py`, `platform/telemetry/sentry.py`, `platform/pii.py`, `tests/unit/test_pii.py`
- Expected review: 160 LOC · Max: 200

**Commit 10 — feat(api): async DB engine + TenantScopedSession**
- Files: `platform/db/engine.py`, `platform/db/session.py`
- Expected review: 140 LOC · Max: 180

**Commit 11 — feat(api): Redis clients + Problem+JSON errors + request_id**
- Files: `platform/cache/redis.py`, `platform/errors.py`, `platform/middleware.py`
- Expected review: 150 LOC · Max: 180

**Commit 12 — feat(api): ULID/UUID id helpers + tests**
- Files: `platform/ids.py`, `tests/unit/test_ids.py`
- Expected review: 130 LOC · Max: 160

**Commit 13 — chore(api): Dockerfile + readyz dependency checks**
- Files: `infra/docker/api.Dockerfile`, `main.py` (edit readyz)
- Expected review: 90 LOC · Max: 120

### D4 — Console skeleton

**Commit 14 — chore(console): Next.js + Tailwind bootstrap**
- Files: `package.json`, `next.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`, `app/layout.tsx`, `app/page.tsx`
- Expected review: 150 LOC · Max: 190

**Commit 15 — chore(console): shadcn/ui init**
- Purpose: generated primitives (isolated for easy review).
- Files: `components/ui/*`, config
- Expected review: generated — review config only · Max: 250 (generated exempt)

**Commit 16 — feat(console): app shell + security middleware**
- Files: `app/(app)/layout.tsx`, `middleware.ts`, `infra/docker/console.Dockerfile`
- Expected review: 150 LOC · Max: 180

**Commit 17 — feat(console): typed API client skeleton**
- Files: `lib/api/client.ts`, `lib/api/types.ts`
- Expected review: 120 LOC · Max: 150

### D5 — Auth

**Commit 18 — feat(iam): user/org/membership models**
- Files: `modules/iam/models.py`, `modules/iam/schemas.py`
- Expected review: 150 LOC · Max: 180

**Commit 19 — feat(api): Clerk JWT verification + auth deps**
- Files: `platform/auth/clerk.py`, `platform/auth/deps.py`
- Expected review: 160 LOC · Max: 200

**Commit 20 — feat(iam): webhook + lazy-upsert service**
- Files: `modules/iam/service.py`, `modules/iam/routes.py` (webhook + /me + members)
- Expected review: 180 LOC · Max: 200

**Commit 21 — test(iam): webhook + upsert integration tests**
- Files: `tests/integration/test_clerk_webhook.py`
- Expected review: 150 LOC · Max: 190

**Commit 22 — feat(console): Clerk auth pages + provider wiring**
- Files: `app/(auth)/sign-in/...`, `app/(auth)/sign-up/...`, `app/layout.tsx` (edit), `middleware.ts` (edit)
- Expected review: 120 LOC · Max: 160

### D6 — Migration 0001

**Commit 23 — feat(agents): agent + agent_version models**
- Files: `modules/agents/models.py`
- Expected review: 130 LOC · Max: 160

**Commit 24 — feat(sessions): session + turn models**
- Files: `modules/sessions/models.py`
- Expected review: 130 LOC · Max: 160

**Commit 25 — feat(db): Alembic setup + env**
- Files: `alembic.ini`, `migrations/env.py`, `Makefile` (migrate targets)
- Expected review: 120 LOC · Max: 150

**Commit 26 — feat(db): migration 0001 tables + RLS + pgvector**
- Files: `migrations/versions/0001_initial.py`
- Expected review: 200 LOC · Max: 240 (single migration; allow slightly larger)

**Commit 27 — feat(api): audit-log decorator + demo-agent hook**
- Files: `platform/audit.py`, `modules/agents/service.py`, `modules/iam/service.py` (edit)
- Expected review: 150 LOC · Max: 190

**Commit 28 — test(db): migration round-trip + RLS + audit tests**
- Files: `tests/integration/test_migration_roundtrip.py`, `test_rls.py`, `test_audit_decorator.py`
- Expected review: 190 LOC · Max: 220

### D7 — LLM + prompt

**Commit 29 — feat(runtime): LiteLLM streaming wrapper + timeouts**
- Files: `modules/runtime/llm.py`, `modules/runtime/ports.py`, `.env.example` (edit)
- Expected review: 150 LOC · Max: 180

**Commit 30 — feat(runtime): system prompt template + composer**
- Files: `modules/runtime/prompt.py`, `modules/runtime/templates/system.jinja`
- Expected review: 160 LOC · Max: 190

**Commit 31 — test(runtime): composer + streaming (respx) tests**
- Files: `tests/unit/test_prompt_composer.py`, `tests/integration/test_llm_stream.py`
- Expected review: 170 LOC · Max: 200

### D8 — Streaming + cancellation + leakage

**Commit 32 — feat(sessions): session CRUD + service**
- Files: `modules/sessions/service.py`, `modules/sessions/routes.py` (CRUD only)
- Expected review: 170 LOC · Max: 200

**Commit 33 — feat(platform): Redis rate limiter + per-agent concurrency cap**
- Files: `platform/ratelimit.py`, `platform/concurrency.py`
- Expected review: 150 LOC · Max: 180

**Commit 34 — feat(sessions): SSE serializer + streaming endpoint**
- Files: `modules/sessions/sse.py`, `modules/sessions/routes.py` (edit: stream), `modules/runtime/llm.py` (edit: abort)
- Expected review: 190 LOC · Max: 220

**Commit 35 — test(sessions): streaming happy-path + cancellation**
- Files: `tests/integration/test_streaming.py`, `test_streaming_cancel.py`
- Expected review: 180 LOC · Max: 210

**Commit 36 — test(security): cross-tenant leakage harness**
- Files: `tests/integration/test_tenant_leakage.py`
- Expected review: 170 LOC · Max: 200

### D9 — Console flows

**Commit 37 — feat(console): agents list + create form**
- Files: `app/(app)/agents/page.tsx`, `agents/new/page.tsx`, `lib/api/agents.ts`
- Expected review: 180 LOC · Max: 210

**Commit 38 — feat(console): SSE parser + streaming chat hook**
- Files: `lib/sse.ts`, `components/chat/*`
- Expected review: 170 LOC · Max: 200

**Commit 39 — feat(console): agent detail + Test Chat tab**
- Files: `app/(app)/agents/[id]/page.tsx`, `test-chat.tsx`, `lib/api/sessions.ts`
- Expected review: 180 LOC · Max: 210

**Commit 40 — feat(console): Conversations transcript + Members view**
- Files: `agents/[id]/conversations.tsx`, `app/(app)/settings/members/page.tsx`
- Expected review: 160 LOC · Max: 190

**Commit 41 — test(console): agent-chat e2e (Playwright)**
- Files: `e2e/agent-chat.spec.ts`
- Expected review: 130 LOC · Max: 160

### D10 — CI/CD

**Commit 42 — ci: lint/test/build with per-language path filters**
- Files: `.github/workflows/ci.yml`
- Expected review: 160 LOC · Max: 190

**Commit 43 — ci: PR preview (Neon branch + Upstash namespace + Fly)**
- Files: `.github/workflows/preview.yml`, `.github/actions/neon-branch/action.yml`
- Expected review: 180 LOC · Max: 210

**Commit 44 — ci: prod deploy + migration release command**
- Files: `.github/workflows/deploy.yml`, `infra/fly/fly.api.toml`, `fly.console.toml`, `fly.worker.toml`
- Expected review: 170 LOC · Max: 200

**Commit 45 — ci: manual rollback action**
- Files: `.github/workflows/rollback.yml`
- Expected review: 70 LOC · Max: 100

### D11 — Deploy to Fly

**Commit 46 — chore(infra): Fly region + health-check config + secrets runbook**
- Files: `infra/fly/*.toml` (edit), `infra/fly/README.md`
- Expected review: 120 LOC · Max: 150

### D12 — Ops safety net

**Commit 47 — docs(ops): runbook + restore drill + Sentry alert tags**
- Files: `docs/RUNBOOK.md`, `services/api/scripts/restore_drill.md`, `platform/telemetry/sentry.py` (edit)
- Expected review: 150 LOC · Max: 190

### D13 — Docs + demo

**Commit 48 — docs: finalize README + Sprint 1 retro**
- Files: `README.md` (edit), `notes/sprint1_retro.md`
- Expected review: 100 LOC · Max: 140

**Total: 48 commits.** Every non-generated commit ≤ 220 LOC, reviewable in < 20 minutes.

---

## Effort Rollup

| Deliverable | Effort (h) | Commits |
|---|---|---|
| D1 | 4 | 01–04 |
| D2 | 4 | 05–07 |
| D3 | 8 | 08–13 |
| D4 | 6 | 14–17 |
| D5 | 10 | 18–22 |
| D6 | 10 | 23–28 |
| D7 | 8 | 29–31 |
| D8 | 12 | 32–36 |
| D9 | 12 | 37–41 |
| D10 | 10 | 42–45 |
| D11 | 6 | 46 |
| D12 | 4 | 47 |
| D13 | 2 | 48 |
| **Total** | **96** | **48** |

See [IMPLEMENTATION_ORDER.md](IMPLEMENTATION_ORDER.md) for the day-by-day sequence and [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md) for the per-PR gate.
