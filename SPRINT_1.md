# SPRINT 1

**Duration:** 2 weeks (10 working days).
**Team:** 1 founder + 1 engineer.
**Goal:** By the end of Sprint 1, a logged-in user in their own organization can create an agent, send a message, and receive a **streamed LLM response** in the browser, backed by a real Postgres + Redis + FastAPI + Next.js stack, deployable to a preview environment on every PR.

**Explicit non-goals for Sprint 1 (do NOT build these):**
NO voice · NO WhatsApp · NO SMS · NO email channel (only transactional user emails via Clerk are OK) · NO Slack · NO Teams · NO billing / Stripe · NO enterprise SSO · NO SAML · NO SCIM · NO RBAC beyond owner/member · NO marketplace · NO Kubernetes · NO Prometheus/Grafana/Loki/Tempo · NO Qdrant · NO ClickHouse · NO Kafka · NO Temporal · NO multi-region · NO Vault · NO Istio · NO OPA · NO KB / RAG · NO tools / booking · NO widget · NO evals · NO analytics.

Sprint 2 adds knowledge/tools. Sprint 3 adds the widget. Sprint 4 adds bookings. This sprint just proves the spine works.

---

## Definition of Done (Sprint 1)

A cold laptop, after `git clone` + `cp .env.example .env` + `make dev`, must be able to:

1. Open `http://localhost:3000` and see the console.
2. Sign up via Clerk (email link).
3. Create an organization.
4. Land on the dashboard shell.
5. Create a new agent named "Hello Agent" (system prompt: "You are a helpful assistant.").
6. Open the Playground for that agent.
7. Type "Hi, who are you?" and see the response **stream token-by-token** in the UI.
8. Refresh the page and see the conversation in the history list.
9. Reopen it and see the prior turns.

A push to `main` (or a merge to a PR):
1. Triggers GitHub Actions: lint → typecheck → unit tests → build Docker images.
2. On PR: deploys a preview environment on Fly.io (or Render); comments the URL on the PR.

---

## Deliverables

### D1 — Repo scaffold (Day 1)
- Monorepo initialized with the layout defined in [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md).
- `uv` (Python) + `pnpm` (TS) workspaces configured.
- Top-level `Makefile`: `dev`, `test`, `lint`, `fmt`, `typecheck`, `openapi`.
- `README.md` with a 10-line "run it" section.
- `.env.example` documenting every var.
- `.editorconfig`, `.gitignore`, `.gitattributes`.

### D2 — Local dev with Docker Compose (Day 1)
- `docker-compose.yml` with:
  - `postgres:16` with `pgvector` extension pre-installed (image `pgvector/pgvector:pg16`) — we install the extension in Sprint 2, but the image is ready.
  - `redis:7`.
  - `mailpit` (for viewing Clerk-forwarded / dev emails locally).
- `make dev` starts compose + API (with `uvicorn --reload`) + Next.js (`pnpm dev`) in parallel, all hot-reloading.
- Healthchecks on all containers.

### D3 — FastAPI backend skeleton (Day 2)
- `services/api` with FastAPI, pydantic-settings config, structlog JSON logging, Sentry init (optional in dev).
- Middleware: request ID, exception → Problem+JSON, CORS (allow `http://localhost:3000`).
- Endpoints:
  - `GET /healthz` — liveness.
  - `GET /readyz` — checks DB + Redis connectivity.
  - `GET /v1/me` — returns the current user + org from the Clerk JWT (401 if unauth).
- Async SQLAlchemy engine + session dependency.
- Redis client dependency.
- Alembic set up with an initial empty migration.

### D4 — Next.js console skeleton (Day 2)
- `apps/console` with Next.js 15 (App Router), Tailwind, `shadcn/ui`, TypeScript strict.
- Clerk `@clerk/nextjs` wired: sign-in, sign-up, `<SignedIn>` gated shell.
- Basic layout: sidebar (Agents, Conversations, Settings), topbar with org switcher.
- `packages/shared-ts` scaffolded; contains a hand-written `apiClient` for now (openapi-typescript generation added in Sprint 2 when the API surface stabilizes).

### D5 — Authentication (end-to-end) (Day 3)
- Clerk configured (SaaS, free tier).
- Console: sign-up / sign-in / sign-out flows working, org creation via Clerk Organizations.
- API: verifies the Clerk-issued JWT (`clerk-sdk-python`), extracts `user_id` and `org_id`, exposes `current_user()` and `current_org()` FastAPI dependencies.
- On first sign-in, the API upserts the user + org into our Postgres via a Clerk webhook (`user.created`, `organization.created`, `organizationMembership.created`) — endpoint `POST /v1/webhooks/clerk` with Svix signature verification.

### D6 — Initial database schema (Day 3–4)
Alembic migration `0001_initial.sql`:
```
org              (id, slug, name, plan_default 'free', created_at, updated_at)
user             (id, clerk_user_id UNIQUE, email, name, created_at, updated_at)
membership       (id, org_id, user_id, role 'owner'|'member', created_at)
api_key          (id, org_id, prefix, hash, name, scopes JSONB, last_used_at,
                  expires_at, created_by, created_at, revoked_at)
audit_log        (id, org_id, actor_user_id, action, resource_type, resource_id,
                  diff JSONB, ip, ua, at)
agent            (id, org_id, slug UNIQUE(org_id,slug), name, status 'draft'|'active',
                  created_at, updated_at, deleted_at)
agent_version    (id, agent_id, org_id, version INT, spec JSONB, system_prompt TEXT,
                  model TEXT, temperature FLOAT, is_published BOOLEAN,
                  published_at, published_by, created_at)
session          (id, org_id, agent_id, agent_version_id, channel 'playground',
                  started_at, ended_at, meta JSONB)
turn             (id, session_id, org_id, idx INT, role 'user'|'assistant'|'system',
                  content TEXT, tokens_in INT, tokens_out INT, model TEXT,
                  latency_ms INT, started_at, ended_at)
```
- Every table has `id ULID PK`, `org_id` where applicable, timestamps.
- Indexes: `(org_id, created_at)` on `agent`, `session`, `turn`; unique `(org_id, slug)` on `agent`; unique `clerk_user_id` on `user`.
- **RLS is NOT enabled yet** (single dev, careful queries; Sprint 5 adds RLS). All queries scope by `org_id` from `current_org()` — enforce via a code-review checklist.
- Seed: `make seed` creates a demo org + user (dev only).

### D7 — LiteLLM + LangGraph integration (Day 4–5)
- `services/api/src/vsa_api/modules/runtime/` module:
  - `llm.py` — LiteLLM client wrapper. Env-configured: `VSA_LLM_OPENAI_API_KEY`, `VSA_LLM_ANTHROPIC_API_KEY` (optional). Exposes an `async def stream_chat(messages, model, temperature)` returning an async iterator of token deltas.
  - `graph.py` — the smallest possible LangGraph: one node that composes `[system, ...history, user]`, calls `stream_chat`, and yields deltas. State type is a pydantic `RuntimeState`.
  - `prompt.py` — trivial composer (system prompt + last N=20 messages).
- Configured models: default `openai/gpt-4o-mini`. Fallback list can be empty; add in Sprint 2.

### D8 — Streaming chat API (Day 5–6)
- `POST /v1/agents/{agent_id}/sessions` → creates a session, returns `session_id`.
- `GET /v1/agents/{agent_id}/sessions` → paginated list for the org.
- `GET /v1/sessions/{session_id}/turns` → returns ordered turns.
- `POST /v1/sessions/{session_id}/messages/stream` — SSE.
  - Body: `{ "content": "..." }`.
  - Persists the user turn immediately.
  - Streams events:
    - `event: token\ndata: {"delta":"..."}\n\n`
    - `event: done\ndata: {"turn_id":"tur_...","tokens_in":123,"tokens_out":45,"latency_ms":812}\n\n`
    - `event: error\ndata: {"code":"...","message":"..."}\n\n`
  - Persists the assistant turn on `done`.
  - Uses `RedisPubSub` internally so a future websocket fan-out is a small change (do NOT build the fan-out now; just structure the code).
- Rate limit: 60 req/min per user via a Redis token bucket.
- Idempotency: accept `Idempotency-Key` header; store response digest in Redis for 24h.

### D9 — Console flows (Day 6–7)
- **Agents page**:
  - List agents in the current org.
  - "New Agent" modal: name + system prompt (single textarea) + model dropdown (`gpt-4o-mini`, `claude-3-5-haiku-latest`) + temperature slider (0–1).
  - Save → creates `agent` + `agent_version` (v1, published).
- **Agent detail → Playground tab**:
  - Left: message list (auto-scroll).
  - Bottom: input box + Send.
  - On Send: create session if needed, then open SSE to `/v1/sessions/{id}/messages/stream`, render tokens as they arrive, append assistant turn on `done`.
  - "New conversation" button.
- **Agent detail → Conversations tab**:
  - Paginated list of past sessions (Playground channel).
  - Click → transcript view with role bubbles and metadata (model, tokens, latency).
- **Settings → Members**:
  - Read-only for now: shows current org's members (from Clerk).
- **Settings → API Keys**:
  - Create key (name + copy-once secret; store `argon2id(hash)` + prefix).
  - Revoke key.
  - (Keys are functional but no public endpoints require them yet; wired up so Sprint 2's KB APIs can use them.)

### D10 — CI/CD + preview environments (Day 8)
- `.github/workflows/ci.yml`:
  - Triggers on PR and push to `main`.
  - Jobs (parallel matrix):
    - `python`: `ruff format --check`, `ruff check`, `mypy`, `pytest` (unit + integration via testcontainers).
    - `node`: `pnpm lint`, `pnpm typecheck`, `pnpm test` (Vitest).
    - `docker`: build multi-arch images (`amd64` only for now to save time), tag `vsa-api`, `vsa-console`.
- `.github/workflows/preview.yml`:
  - On PR opened/updated: `flyctl deploy` with app name `vsa-api-pr-<n>` and `vsa-console-pr-<n>` to a **Fly.io preview org**.
  - Uses a **shared preview Postgres** (Neon branching preferred: 1 DB branch per PR) and a shared **preview Redis**.
  - Comments the two URLs on the PR.
  - On PR closed: destroys the preview apps and DB branch.
- `.github/workflows/deploy.yml`:
  - On push to `main` after CI passes: `flyctl deploy` to `vsa-api` + `vsa-console` (single prod region, `iad` or `ord`).
  - Runs Alembic migrations as a release command inside the API container.

### D11 — Deploy to Fly (Day 9)
- `infra/fly/fly.api.toml`, `fly.console.toml` written.
- Postgres: **Neon** free tier (managed; branchable) — chosen over Fly Postgres for backups + branching.
- Redis: **Upstash** free tier — chosen for zero ops + serverless pricing.
- Secrets set via `flyctl secrets set`.
- Deployed prod URLs live: `https://app.vsa.local` (placeholder domain; buy real one in Sprint 2).

### D12 — Basic ops safety net (Day 9)
- Sentry projects for `api` and `console`; DSNs in env.
- Better Stack / UptimeRobot pinging `/healthz` every minute; alert to founder's phone.
- Weekly Neon backup verified once (manual).

### D13 — Docs + first internal demo (Day 10)
- `README.md`: how to run, deploy, and the "book a demo" copy paragraph.
- Loom video (2 min): founder signs up → creates agent → chats. This is the artifact for Sprint 2's design-partner outreach.
- Sprint 1 retro doc created (blockers, cuts, learnings).

---

## Tests to Write

- **API unit**: prompt composer, ULID generator, tenant context, rate limiter, SSE serializer.
- **API integration** (testcontainers): user upsert from Clerk webhook, create agent, create session, stream a message with LLM stubbed via `respx` — asserts DB rows and event sequence.
- **Console e2e (Playwright)**: sign-in stub (Clerk test token) → create agent → send message → assert streamed response appears → refresh → assert history loads.
- **CI check**: `alembic upgrade head && alembic downgrade base && alembic upgrade head` runs clean on a fresh DB.

---

## Environment Variables (Sprint 1)

```
# Core
VSA_ENV=dev|preview|prod
VSA_LOG_LEVEL=INFO
VSA_SENTRY_DSN_API=
VSA_SENTRY_DSN_CONSOLE=

# Database
VSA_DB_URL=postgresql+asyncpg://vsa:vsa@postgres:5432/vsa

# Redis
VSA_REDIS_URL=redis://redis:6379/0

# Clerk
CLERK_SECRET_KEY=
CLERK_WEBHOOK_SIGNING_SECRET=
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=

# LLMs
VSA_LLM_OPENAI_API_KEY=
VSA_LLM_ANTHROPIC_API_KEY=

# App URLs
VSA_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_VSA_API_BASE_URL=http://localhost:8000
```

---

## What Sprint 1 Deliberately Skips (so no scope creep)

- **RAG / knowledge upload** — Sprint 2.
- **Tools / booking / calendar** — Sprint 4.
- **Public widget** — Sprint 3.
- **Stripe billing** — Sprint 6.
- **RLS enforcement** — Sprint 5.
- **Multi-model routing / fallback config** — Sprint 5.
- **Evals** — Sprint 6.
- **Backups automation** — Sprint 8.
- **Vertical templates** — Sprint 5 (once runtime is proven).

If any of the above starts sneaking into Sprint 1, cut it. This sprint is the **spine**; every subsequent sprint is a limb attached to it.

---

## Exit Checklist (must all pass to close Sprint 1)

- [ ] `git clone` + `make dev` boots the full stack in < 5 minutes on a clean laptop.
- [ ] A cold user completes: sign up → org → agent → streamed chat → history reload — in the deployed preview URL.
- [ ] CI: lint + typecheck + tests + docker build all green on `main`.
- [ ] Preview environment auto-deploys on every PR and gets torn down on close.
- [ ] Prod URLs live behind HTTPS with Sentry + uptime pings.
- [ ] Alembic up + down + up cycles cleanly.
- [ ] Loom demo recorded.
- [ ] No voice, WhatsApp, SMS, email channel, Slack, Teams, Stripe, K8s, or observability stack was built.
