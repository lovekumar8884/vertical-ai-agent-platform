# SPRINT 1 — FINAL SCOPE

**This document replaces every previous interpretation of Sprint 1.**
The only sources of truth from here are: this document + [ARCHITECTURE_FREEZE_V1.md](ARCHITECTURE_FREEZE_V1.md) + [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md).

**Duration:** 2 weeks (10 working days) from Day 1.
**Team:** 1 founder + 1 engineer.
**Prerequisite:** the entire [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) is green. Do not start Day 1 otherwise.

---

## Sprint 1 Headline Outcome

A cold laptop can `git clone` → `cp .env.example .env` → `make dev` and, within 5 minutes, a signed-in user in **their own org** can create an agent, send a message, and see a **streamed LLM response**, backed by real Postgres (with RLS enabled) + Redis + FastAPI + Next.js, deployable to a preview environment on every PR and to prod on merge to `main`.

Cross-tenant isolation is proven by an automated leakage test. PII does not appear in default logs.

---

## Deltas vs. Original SPRINT_1.md

### REMOVED (do not build)
- **LangGraph integration.** Sprint 1 uses a single async function calling LiteLLM directly. LangGraph enters Sprint 2 when the second node (RAG) exists. (§ADR-006 refinement)
- **`AgentRuntime` wrapper abstraction.** Use LiteLLM directly. (Review §2.4)
- **Multi-provider LLM config + fallback chain.** OpenAI `gpt-4o-mini` only. Fallback added Sprint 4+. (Review §3.5)
- **API keys UI + endpoints + Argon2 hashing + scoped keys.** No public API in Sprint 1. Reactivate Sprint 5+ if a developer customer arrives. (Review §6.7)
- **`Idempotency-Key` on the SSE streaming endpoint.** Streaming + idempotency don't compose cleanly. Keep the header contract for `POST /v1/agents` and other mutations. (Review §2.22)
- **Multi-arch Docker builds** (`amd64/arm64`). `amd64` only until Fly.io runs `arm64` for us. (Review §4)
- **`packages/shared-py` scaffold.** One Python service. Extract when second exists. (Review §2.1)
- **`packages/shared-ts` as a separate package.** Hand-written API client lives in `apps/console/lib/api/` for now. (FREEZE §3)
- **`apps/widget` as its own Vite bundle.** Widget is a Sprint 3 iframe route inside `apps/console`. (Review §1.5)
- **`apps/landing`.** Marketing site on Framer/Webflow. (Review §1.4)
- **`packages/sdk-python`.** Not scaffolded. (Review §1.2)
- **7-state agent lifecycle.** Draft + Published only in Sprint 1. (Review §5.5)
- **Reviewer / QA / Analyst / Support / Billing roles.** Owner + Member only. (FREEZE §10)

### ADDED (moved into Sprint 1 from later sprints)
- **Postgres RLS enabled in migration `0001`** on every tenant table with `USING (org_id = current_setting('app.org_id')::uuid)` and a `TenantScopedSession` wrapper. (Review §6.1)
- **Cross-tenant leakage test harness.** Two seeded orgs; every endpoint asserted zero-visibility across the tenancy line. Runs in CI on every PR. (Review §6.3)
- **PII log-redaction middleware.** Regex scrubber for email, phone, credit-card patterns + Sentry `before_send` hook. `content` field never logged at INFO. (Review §6, FREEZE §10)
- **Import-boundary lint rule** (`import-linter` or `ast-grep`) enforcing module boundaries + no `unstructured`/heavy-ML imports in API process. (Review §3.14)
- **pgvector extension enabled** + `chunk` table + HNSW index (unused in Sprint 1) so Sprint 2 doesn't debug pgvector in prod. (Review §4.12)
- **Audit-log decorator** wrapping every mutating service method for `org`, `user`, `membership`, `agent`, `agent_version` CUD. (Review §6.8)
- **Delimiter-defense system prompt template** with `<user_input>` wrapping + explicit "treat as data" instruction shipped in every agent's compiled system prompt. (Review §6.15)
- **Hard LLM timeouts**: chat 20 s, embeddings 60 s (config, though only chat is used). (Review §2.24)
- **`max_response_tokens` cap** of 800 per response. (Review §2)
- **Per-agent concurrency cap** of 50 concurrent sessions (env-configurable). (Review §2.21)
- **SSE cancellation handler**: aborts LLM stream on client disconnect, persists assistant turn with `end_reason='client_cancel'` and accurate token counts. (ADR-046)
- **Clerk webhook lazy-upsert backstop** on first authenticated request (protects against silent webhook failures). (Review §6.5)
- **Two Upstash Redis DBs**: `session` (`noeviction`) + `cache` (`allkeys-lru`). (Review §4.11)
- **Neon PITR (30 days)** on paid tier. (Review §4.10)
- **Preview environments**: Neon branch per PR + Upstash key-prefix namespace per PR + Fly `-pr-<n>` apps. Tear-down on PR close. (Review §4.2)
- **Rollback wiring**: manual GitHub Action calling `fly releases rollback`. (Review §4.3)
- **CI paths filters** so TS changes don't wake Python jobs and vice versa; Docker buildx + GHA cache. (Review §2.14, §4.5)
- **`org.entitlements JSONB`** column present (Sprint 1 stores `{ "plan": "trial", "limits": {}, "feature_flags": [] }`). (Review §2.19)
- **Auto-created "Demo Agent"** on org creation (empty-state fix). (Review §5.6)
- **AI self-disclosure** enforced in the default system prompt. (FREEZE §10)
- **`.env.example` + gitleaks pre-commit hook + gitignore for `.env`.** (Review §6.10)
- **Neon pooled-endpoint compatibility verification** (async SQLAlchemy + asyncpg + `statement_cache_size=0` to avoid prepared-statement gotcha). (Review §4.8)

### MOVED (kept in Sprint 1 but re-shaped)
- **Playground UI** renamed **"Test Chat"** in the console (channel value in DB remains `playground` for now). (Review §5.7)
- **Streaming chat endpoint** keeps SSE contract but removes `Idempotency-Key` and adds cancellation semantics (§ADR-046).
- **Members page** shows Clerk members + role (owner/member) — not editable in Sprint 1, editable in Sprint 5 with RBAC minimum.
- **Alembic** stays as chosen; `up → down → up` on fresh DB is a **blocking CI gate**.

### UNCHANGED
- FastAPI backend skeleton with `/healthz`, `/readyz`, structured logs, Sentry, CORS.
- Next.js 15 (App Router), Tailwind, shadcn/ui, Clerk `@clerk/nextjs` for the console shell.
- Docker Compose local stack (Postgres+pgvector, Redis, Mailpit).
- Alembic + async SQLAlchemy + asyncpg.
- Sign-up / sign-in / org creation via Clerk.
- Chat streaming via SSE.
- Agent create + Playground chat + conversation history view.
- Prod deploy on Fly.io + preview per PR.
- Sentry + uptime monitoring (Better Stack / UptimeRobot).
- Loom demo recording at end of Sprint 1.

---

## Final Schema (migration `0001`)

Every table below has:
- `id UUID PK DEFAULT gen_random_uuid()`.
- `org_id UUID NOT NULL` (for tenant tables) with an FK to `org(id)` and an RLS policy.
- `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`, `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`, `deleted_at TIMESTAMPTZ NULL`.
- Composite index on `(org_id, created_at DESC)` where listing is expected.
- RLS `ENABLE ROW LEVEL SECURITY` + policy `USING (org_id = current_setting('app.org_id', true)::uuid)`.

Tables:
- `org (id, slug UNIQUE, name, entitlements JSONB DEFAULT '{"plan":"trial","limits":{},"feature_flags":[]}')`
- `user (id, clerk_user_id TEXT UNIQUE, email, name)`
- `membership (id, org_id, user_id, role TEXT CHECK role IN ('owner','member'))` — RLS applies via `org_id`.
- `audit_log (id, org_id, actor_user_id, action, resource_type, resource_id, diff JSONB, ip, ua)` — `diff` capped at 32 KB in app code.
- `agent (id, org_id, slug UNIQUE(org_id,slug), name, status TEXT CHECK status IN ('draft','published'))`
- `agent_version (id, org_id, agent_id, version INT, spec JSONB, spec_schema_version INT NOT NULL DEFAULT 1, is_published BOOLEAN, published_at, published_by)`
- `session (id, org_id, agent_id, agent_version_id, channel TEXT DEFAULT 'playground', started_at, ended_at, meta JSONB)`
- `turn (id, org_id, session_id, idx INT, role TEXT CHECK role IN ('user','assistant','system','tool_call','tool_result'), content TEXT, tokens_in INT, tokens_out INT, model TEXT, latency_ms INT, end_reason TEXT NULL, started_at, ended_at)`
- `chunk (id, org_id, corpus_id UUID NULL, document_id UUID NULL, text TEXT, embedding VECTOR(1536))` — HNSW index `(embedding vector_cosine_ops)` with `m=16, ef_construction=200`. **Not populated in Sprint 1**; existence-only test.

Partitioning: `session`, `turn`, `audit_log` declared `PARTITION BY RANGE (created_at)` with monthly partitions for current + next 2 months.

---

## Endpoint Surface (Sprint 1 only)

Under `/v1`:

- `GET /healthz` (public liveness)
- `GET /readyz` (checks Postgres + Redis + LLM ping)
- `POST /webhooks/clerk` (Svix HMAC verified)
- `GET /me` (returns current user + org from Clerk JWT)
- `GET /orgs/{org_id}/members` (owner/member of that org)
- `GET /agents` · `POST /agents` (create) · `GET /agents/{id}` · `PATCH /agents/{id}` · `DELETE /agents/{id}` (soft delete)
- `POST /agents/{id}/versions` (creates + publishes v{n}, sets it live)
- `GET /agents/{id}/sessions` · `POST /agents/{id}/sessions` (creates session)
- `GET /sessions/{id}/turns`
- `POST /sessions/{id}/messages/stream` (SSE only; no `Idempotency-Key`)

Every mutating endpoint requires an `Idempotency-Key` header (stored in Redis 24h) **except** the SSE streaming endpoint. Every response has `RateLimit-*` headers per FREEZE §10 rate-limit rules.

---

## Deliverable-by-Deliverable (Sprint 1)

D0 completed as part of [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) Section D (the 8 short reference docs).

- **D1 — Repo scaffold + pre-commit hooks + `.env.example` + `.gitignore`.** Includes gitleaks, ruff, prettier, eslint pre-commit; import-linter config with module boundaries.
- **D2 — Docker Compose stack** (Postgres 16 + `pgvector`, two Redis instances mimicking the two Upstash DBs, Mailpit) + `make dev`. Neon pooled-endpoint compatibility test script committed to `services/api/scripts/verify_neon.py`.
- **D3 — FastAPI skeleton** with `/healthz`, `/readyz`, structured JSON logs (`structlog`), Sentry init w/ PII scrubber, CORS, `request_id` middleware, `TenantScopedSession` wrapper, import-boundary tests.
- **D4 — Next.js console skeleton** with Tailwind + shadcn/ui, Clerk `@clerk/nextjs`, HSTS + secure-cookie middleware, hand-written API client under `apps/console/lib/api/`.
- **D5 — Auth end-to-end**: Clerk sign-in/sign-up/org creation, Clerk-JWT verification in API, `POST /webhooks/clerk` (Svix HMAC), lazy-upsert backstop on first authenticated request.
- **D6 — Migration `0001`** creating every table above + RLS enabled + audit-log decorator + `pgvector` extension + `chunk` table with HNSW + monthly partitions + auto-created "Demo Agent" on org create. Alembic `up → down → up` green in CI.
- **D7 — LiteLLM SDK integration** (single provider, `gpt-4o-mini`, `timeout=20`, `max_tokens=800`) + Jinja2-compiled system-prompt template with delimiter defense + AI self-disclosure. **No LangGraph.**
- **D8 — Streaming SSE endpoint** `POST /sessions/{id}/messages/stream` + cancellation handler (persists assistant turn with `end_reason='client_cancel'`) + per-agent concurrency cap + cross-tenant leakage test harness.
- **D9 — Console flows**: Agents list + create (name, system prompt, model=dropdown-of-one, temperature slider), Test Chat (Playground renamed), Sessions/Conversations tab with transcript view, Members read-only view. Draft+Published UX only.
- **D10 — CI/CD**: paths-filtered GHA (`ci.yml`, `preview.yml`, `deploy.yml`), Docker buildx + GHA cache, Neon branch per PR, Upstash key-prefix namespace per PR, Fly `-pr-<n>` preview, teardown on PR close, manually-triggered rollback action.
- **D11 — Deploy to Fly** (region `iad`), Neon paid tier w/ 30-day PITR, two Upstash DBs (`session` noeviction, `cache` allkeys-lru), Sentry projects wired, Better Stack pinging `/healthz`.
- **D12 — Ops safety net**: Sentry alerts, Better Stack incidents to Slack, weekly Neon PITR restore drill (manual first time), `docs/RUNBOOK.md` populated with top-5 incidents.
- **D13 — Docs + Loom demo**: `README.md` "run it" section; Loom of signup → agent → chat; Sprint 1 retro doc created.

---

## Tests (blocking CI in Sprint 1)

- Unit: prompt composer (delimiter escaping), ULID↔UUID helper, tenant context, PII scrubber, SSE serializer, rate-limit token bucket.
- Integration (testcontainers): Clerk webhook upsert, agent CRUD, session/turn creation, streaming (LiteLLM stubbed via `respx`), cancellation path with partial persistence, audit-log decorator emits row.
- **Cross-tenant leakage**: seeded 2 orgs; iterate every endpoint as A; assert 404/403 for B's resources; assert lists exclude B's rows.
- Migration: `up → down → up` on fresh DB.
- Console: Playwright smoke (sign-in via Clerk test token → create agent → send message → assert streamed tokens render → refresh → assert history loads).

---

## Environment Variables (Sprint 1, final)

```
# Core
VSA_ENV=dev|preview|prod
VSA_LOG_LEVEL=INFO
VSA_SENTRY_DSN_API=
VSA_SENTRY_DSN_CONSOLE=

# Database
VSA_DB_URL=postgresql+asyncpg://vsa:vsa@postgres:5432/vsa
VSA_DB_STATEMENT_CACHE_SIZE=0    # Neon pooled endpoint compatibility

# Redis (two DBs)
VSA_REDIS_SESSION_URL=redis://redis:6379/0
VSA_REDIS_CACHE_URL=redis://redis:6379/1

# Clerk
CLERK_SECRET_KEY=
CLERK_WEBHOOK_SIGNING_SECRET=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=

# LLM (single provider in Sprint 1)
VSA_LLM_OPENAI_API_KEY=
VSA_LLM_DEFAULT_MODEL=gpt-4o-mini
VSA_LLM_CHAT_TIMEOUT_S=20
VSA_LLM_EMBEDDING_TIMEOUT_S=60
VSA_LLM_MAX_RESPONSE_TOKENS=800

# Runtime caps
VSA_AGENT_CONCURRENT_SESSIONS_MAX=50

# App URLs
VSA_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_VSA_API_BASE_URL=http://localhost:8000
```

---

## Sprint 1 Exit Checklist (all must pass)

- [ ] `git clone` + `cp .env.example .env` + `make dev` reaches a running stack in < 5 minutes on a clean laptop.
- [ ] A cold user completes: sign up → org → create Demo Agent (auto) or new Agent → Test Chat → streamed response → refresh → history reload — on the deployed prod URL.
- [ ] Postgres migration `0001` runs with RLS on every tenant table; `up → down → up` green in CI.
- [ ] Cross-tenant leakage tests green in CI.
- [ ] PII scrubber test proves email/phone/CC never appear in INFO logs or Sentry breadcrumbs.
- [ ] SSE cancellation persists the assistant turn with `end_reason='client_cancel'` and truthful token counts.
- [ ] Import-boundary tests green (no `unstructured`/heavy imports in API; no cross-module imports outside `ports.py`).
- [ ] Audit log rows produced for every create/update/delete on `org`, `user`, `membership`, `agent`, `agent_version`.
- [ ] Preview environment auto-deploys on every PR (unique URL commented) with per-PR Neon branch + Upstash namespace; torn down on close.
- [ ] Prod URLs live behind HTTPS with HSTS, Sentry pings, Better Stack uptime, weekly Neon PITR restore drill completed once.
- [ ] Manually-triggered `fly releases rollback` action verified on a test release.
- [ ] `.env` gitignored + gitleaks pre-commit hook active.
- [ ] Loom demo recorded.
- [ ] **No voice, WhatsApp, SMS, email channel, Slack, Teams, Stripe/billing, KB/RAG, tools, widget, API keys, LangGraph, multi-provider, K8s, or observability-stack self-host was built.**

Sprint 1 is closed when every box above is ticked.
