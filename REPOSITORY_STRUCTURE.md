# REPOSITORY STRUCTURE

> Designed for **one founder + one engineer** who need to move fast without repainting the codebase in 6 months. Monorepo, minimal services, boring tools, evolves cleanly toward the long-term architecture in [docs/](docs/).

## Guiding Rules

1. **One repo, one deploy pipeline, one CI.** No submodule sprawl.
2. **Monolith today, module boundaries drawn as if it were 6 services.** Every top-level Python package inside the API service is a candidate for future extraction — never import across boundaries except through explicit "ports."
3. **`apps/` = user-facing UIs. `services/` = backends. `packages/` = shared libs.** Never mix.
4. **Config, migrations, and env schemas live with the code they belong to.** No global `config/` dumping ground.
5. **Every folder has a `README.md`** (even 5 lines) explaining what it is and who owns it.
6. **The infra folder is code, not screenshots.** `infra/` is versioned Terraform + Fly.toml + Docker Compose.
7. **No `scripts/` cesspool.** Automation lives in `Makefile`s per package/service.

---

## Top-Level Layout

```
verticalsasai/
├── README.md                # Product overview + how to run
├── Makefile                 # Top-level: dev, test, lint, build, deploy
├── docker-compose.yml       # Local dev stack
├── pyproject.toml           # uv workspace root (Python)
├── package.json             # pnpm workspace root (JS/TS)
├── pnpm-workspace.yaml
├── uv.lock
├── pnpm-lock.yaml
├── .env.example             # Every required env var, documented
├── .github/
│   └── workflows/           # CI/CD (lint, test, deploy)
├── docs/                    # Long-term architecture (24 docs, from Phase 0)
│   ├── PROJECT_VISION.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── ... (all 24)
├── MVP_IMPLEMENTATION_PLAN.md
├── SPRINT_1.md
├── BACKLOG.md
├── FOUNDER_NOTES.md
│
├── apps/                    # User-facing UIs
│   ├── console/             # Next.js dashboard (paying customer's admin UI)
│   ├── widget/              # Embeddable chat widget (tiny bundle, iframe target)
│   └── landing/             # Marketing site + docs (optional; can be Vercel-hosted)
│
├── services/                # Backends
│   └── api/                 # THE monolith — FastAPI
│
├── packages/                # Shared libraries (versioned within the monorepo)
│   ├── shared-py/           # Python: types, ULID, tenant context, tracing helpers
│   ├── shared-ts/           # TS: types generated from OpenAPI, API client
│   └── sdk-python/          # (Sprint 6+) public Python SDK, generated from OpenAPI
│
├── infra/
│   ├── docker/              # Dockerfiles per app/service
│   ├── fly/                 # Fly.io app manifests (fly.api.toml, fly.console.toml)
│   ├── compose/             # Overrides for docker-compose (dev, ci)
│   └── terraform/           # Cloud infra (Cloudflare, R2, Neon config) — optional
│
└── tests/
    ├── e2e/                 # Playwright: console + widget flows
    └── load/                # k6 scripts (not run in CI; on demand)
```

---

## `apps/`

User-facing. Independently deployable. Do not import from `services/`.

### `apps/console/` — Next.js 15 dashboard
Owner: founder. **Why:** the customer-visible surface. Where they log in, build agents, upload KB, see conversations, install widget, connect calendar, pay.
```
apps/console/
├── app/                     # App Router
│   ├── (auth)/              # Sign-in, sign-up (Clerk)
│   ├── (app)/               # Authenticated shell
│   │   ├── agents/
│   │   ├── knowledge/
│   │   ├── conversations/
│   │   ├── connections/     # Calendar OAuth
│   │   ├── settings/
│   │   └── billing/
│   └── layout.tsx
├── components/              # shadcn/ui + our components
├── lib/                     # API client (from packages/shared-ts), auth helpers
├── styles/
├── public/
├── next.config.ts
├── package.json
└── README.md
```

### `apps/widget/` — Embeddable web chat
Owner: founder. **Why:** what ends up on the customer's website. Must load in < 30 KB gz. Deployed as static assets on Cloudflare R2 + CDN.
```
apps/widget/
├── src/
│   ├── loader.ts            # The <script> tag entry point — creates iframe
│   ├── iframe/              # React app inside the iframe
│   │   ├── App.tsx
│   │   ├── Chat.tsx         # SSE-streamed chat
│   │   └── theme.ts
│   └── config.ts
├── vite.config.ts           # Vite for tiny bundle
├── package.json
└── README.md
```

### `apps/landing/` — Marketing + docs (optional)
Owner: founder. **Why:** SEO + convert cold traffic. Can be built later; if built, use Next.js/Astro; deploy to Vercel. Not strictly required for MVP.

---

## `services/`

Only backends. Every service must expose `/healthz`, structured logs, Sentry, OpenAPI spec.

### `services/api/` — The Monolith
Owner: engineer. **Why:** V1 has one backend. Modules inside are designed so any can be lifted into its own service later without renames or import surgery.

```
services/api/
├── pyproject.toml
├── Dockerfile
├── Makefile
├── README.md
├── alembic.ini              # Postgres migrations
├── migrations/              # Alembic versions
│   └── versions/
├── src/
│   └── vsa_api/
│       ├── main.py          # FastAPI app factory + middleware
│       ├── config.py        # pydantic-settings (typed env)
│       ├── deps.py          # dependency-injection wiring
│       │
│       ├── platform/        # Cross-cutting; no domain logic
│       │   ├── auth/        # Clerk JWT verification, API key auth
│       │   ├── db/          # Async SQLAlchemy engine + session
│       │   ├── cache/       # Redis client
│       │   ├── storage/     # S3/R2 client
│       │   ├── telemetry/   # OTel + Sentry init + structlog config
│       │   ├── errors.py    # Problem+JSON, DomainError base
│       │   ├── ids.py       # ULID helpers, type prefixes
│       │   ├── ratelimit.py
│       │   └── tenant.py    # `current_org()` context var
│       │
│       ├── modules/         # Bounded contexts — each = future service
│       │   ├── iam/         # Orgs, users, memberships, api_keys, audit
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── service.py
│       │   │   ├── routes.py
│       │   │   └── ports.py
│       │   ├── agents/      # Agents, versions, prompts
│       │   ├── knowledge/   # Corpora, documents, chunks, retrieval
│       │   ├── tools/       # Tool registry + built-ins (calendar, email)
│       │   ├── runtime/     # LangGraph agent runtime + prompt composer
│       │   ├── sessions/    # Sessions, turns, streaming chat endpoints
│       │   ├── channels/    # Channel adapters (widget only in V1)
│       │   │   └── widget/  # Public widget endpoint + CORS + rate limit
│       │   ├── memory/      # Short-term (Redis), long-term facts (PG)
│       │   ├── connections/ # OAuth (Google Calendar) + token store
│       │   ├── billing/     # Stripe checkout, webhook, plan enforcement
│       │   └── notifier/    # Transactional email via Resend
│       │
│       ├── verticals/       # Agent templates + starter prompts + evals
│       │   ├── _base/
│       │   ├── clinic_receptionist/
│       │   │   ├── agent.yaml
│       │   │   ├── prompts/
│       │   │   ├── tools.yaml
│       │   │   └── evals.jsonl
│       │   └── ... (add per new vertical)
│       │
│       └── workers/         # Background jobs (arq/RQ)
│           ├── ingest.py    # KB URL/PDF ingestion
│           ├── billing_sync.py
│           └── notify.py
└── tests/
    ├── unit/
    ├── integration/         # Testcontainers-based
    └── contract/            # Schemathesis on OpenAPI
```

**Module rules (enforced by lint):**
- `modules/*` may import from `platform/*` and `packages/shared-py`.
- `modules/*` may not import from other `modules/*` **except through a `ports.py`** interface (dependency-inverted). This is what allows painless service extraction later.
- `verticals/*` may only import from `modules/agents`, `modules/tools`, `modules/knowledge` via ports.
- `workers/*` may import from `modules/*` freely (they are batch jobs owned by the same monolith).

---

## `packages/`

Shared code. Versioned within the workspace; never published externally in V1.

### `packages/shared-py/`
Owner: engineer. **Why:** types + helpers used across `services/api` and (later) other services or SDKs.
```
packages/shared-py/
├── src/vsa_shared/
│   ├── ids.py              # ULID + prefixes
│   ├── types.py            # Message, Turn, Session pydantic models (schema-mirrored)
│   ├── errors.py
│   ├── time.py
│   └── logging.py
└── pyproject.toml
```

### `packages/shared-ts/`
Owner: founder. **Why:** typed API client for the console + widget, generated from the API's OpenAPI spec.
```
packages/shared-ts/
├── src/
│   ├── generated/          # openapi-typescript output (git-ignored + regenerated)
│   ├── client.ts           # Thin fetch wrapper w/ auth
│   ├── types.ts            # Re-exports
│   └── events.ts           # SSE + WS event parsers
├── openapi.json            # Snapshot pulled from API on build
└── package.json
```

### `packages/sdk-python/` (Sprint 6+)
Public SDK — same generation pipeline. Add only when a developer customer asks.

---

## `infra/`

Everything code-controlled that isn't application code.

### `infra/docker/`
Dockerfiles kept small, one per deployable.
```
infra/docker/
├── api.Dockerfile
├── console.Dockerfile
├── widget.Dockerfile
└── worker.Dockerfile
```

### `infra/fly/`
Deployment manifests. Fly is the V1 host; swap to Kubernetes only when justified.
```
infra/fly/
├── fly.api.toml
├── fly.console.toml
├── fly.worker.toml
└── README.md
```

### `infra/compose/`
Docker-compose overrides for dev/ci/prod-like local. Base file is `docker-compose.yml` at repo root.

### `infra/terraform/` (optional in V1)
Cloudflare R2 bucket, DNS, IAM. Add only when you need reproducibility.

---

## `docs/`

Long-term architecture set (already exists — 24 documents). Read-only reference. Any changes flow through ADRs.

Add over time:
- `docs/adr/NNNN-title.md` — Architecture Decision Records.
- `docs/runbooks/` — SRE runbooks (start with 5 pages by Sprint 8).

---

## Top-Level Files

- **`README.md`** — 2-minute overview + `make dev` instructions.
- **`Makefile`** — top-level orchestration:
  - `make dev` — boots docker-compose + api + console with hot reload.
  - `make test` — unit + integration.
  - `make lint`, `make fmt`, `make typecheck`.
  - `make openapi` — pulls API spec into `packages/shared-ts/openapi.json` and regenerates types.
  - `make deploy-preview` — CI uses this.
- **`docker-compose.yml`** — postgres (with `pgvector`), redis, minio (or R2 emulator), mailpit, api, worker, console.
- **`.env.example`** — every required var, grouped by service.
- **`.github/workflows/`** — one workflow per: `ci.yml`, `preview.yml`, `deploy.yml`.

---

## Ownership Map

| Area | Primary owner | Why |
|---|---|---|
| `apps/console`, `apps/widget`, `apps/landing` | Founder | Customer-facing UX, positioning, copy |
| `services/api/modules/runtime`, `verticals/` | Engineer + Founder together | Product differentiator |
| `services/api/modules/knowledge`, `tools`, `sessions`, `memory` | Engineer | Core infra |
| `services/api/modules/iam`, `billing`, `connections`, `channels/widget` | Engineer | Backbone |
| `packages/shared-*` | Engineer | Cross-cutting types |
| `infra/*`, `.github/workflows/*` | Engineer | Deploy pipeline |
| `docs/`, plan docs | Founder | Vision + roadmap |
| Runbooks (later) | Engineer | Operations |

---

## Naming Conventions

- **Repo**: `verticalsasai` (matches this workspace).
- **Docker images**: `vsa-api`, `vsa-console`, `vsa-widget`, `vsa-worker`.
- **Fly app names**: `vsa-api`, `vsa-console-prod`, `vsa-console-preview-<pr>`.
- **DB naming**: singular tables → `agent`, `session`, `turn`. Every table has `id ULID, org_id ULID, created_at, updated_at, deleted_at`.
- **ID prefixes**: `org_`, `usr_`, `mem_`, `key_`, `agn_`, `ver_`, `cor_`, `doc_`, `chk_`, `ses_`, `tur_`, `tol_`, `con_`, `inv_`.
- **Env vars**: `VSA_<SUBSYSTEM>_<KEY>` (e.g., `VSA_DB_URL`, `VSA_LLM_OPENAI_API_KEY`).

---

## What This Structure Buys You

1. **Day 1 productivity**: `make dev` → running app in one command.
2. **Refactor-free growth**: every module has clean seams; extracting `runtime` or `voice` into its own service later is a `git mv` + Dockerfile.
3. **Hire-friendly**: any Python/TS dev recognizes the layout in 15 minutes.
4. **CI stays fast**: one repo, one CI, parallel matrix per package.
5. **Preserves the long-term architecture** in `docs/` without letting it dictate MVP complexity.
