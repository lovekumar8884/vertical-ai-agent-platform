# ARCHITECTURE DECISIONS

The official ADR (Architecture Decision Record) index. Every major decision made across all planning documents is captured here in a consistent shape.

**Statuses:** `Accepted` · `Accepted (MVP scope)` · `Deferred` · `Superseded` · `Under review`.

Ordering follows the natural stack (product / vertical → runtime → data → infra → operations).

---

## Index

| # | Decision | Status |
|---|---|---|
| ADR-001 | Vertical AI Platform, not general chatbot builder | Accepted |
| ADR-002 | Chat-first, voice deferred to Sprint 10 | Accepted (MVP scope) |
| ADR-003 | Healthcare / Dental Receptionist as launch vertical | Accepted (MVP scope) |
| ADR-004 | One runtime, N templates — never fork per vertical | Accepted |
| ADR-005 | AI Employee canonical model (11 pillars) | Accepted |
| ADR-006 | LangGraph as the runtime engine | Accepted |
| ADR-007 | LiteLLM as LLM router (SDK now, proxy later) | Accepted (MVP scope) |
| ADR-008 | Python + FastAPI for the backend, TypeScript + Next.js for the frontend | Accepted |
| ADR-009 | Monolith now, module boundaries drawn as future services | Accepted (MVP scope) |
| ADR-010 | Postgres as the single source of truth (OLTP) | Accepted |
| ADR-011 | pgvector for vector search in MVP; Qdrant later | Accepted (MVP scope) |
| ADR-012 | Redis for cache, sessions, rate limits, streams | Accepted |
| ADR-013 | ClickHouse for analytics — deferred; Postgres queries first | Deferred |
| ADR-014 | Kafka event bus — deferred; Postgres LISTEN/NOTIFY + Redis Streams in MVP | Deferred |
| ADR-015 | Temporal workflows — deferred; arq/RQ jobs in MVP | Deferred |
| ADR-016 | Fly.io for hosting, not Kubernetes | Accepted (MVP scope) |
| ADR-017 | Clerk for authentication; WorkOS/Ory later | Accepted (MVP scope) |
| ADR-018 | Stripe for billing; Metronome added at scale | Accepted |
| ADR-019 | Row-level tenancy via Postgres RLS; enforced from Sprint 5 | Accepted |
| ADR-020 | Firecrawl + `unstructured` + LlamaParse for KB ingestion | Accepted |
| ADR-021 | OpenAI embeddings (`text-embedding-3-small`); BGE-M3 for self-host | Accepted |
| ADR-022 | Cohere Rerank added in Sprint 15, not before | Deferred |
| ADR-023 | LiveKit + Pipecat for voice pipeline (when we add voice) | Accepted |
| ADR-024 | Deepgram STT + ElevenLabs TTS as V1 voice providers | Accepted |
| ADR-025 | Twilio + Telnyx + Plivo as telephony providers (multi-provider) | Accepted |
| ADR-026 | MCP first-class in tool framework | Accepted |
| ADR-027 | Firecracker sandbox for custom-code tools; deferred until custom tools ship | Deferred |
| ADR-028 | OpenTelemetry from Day 1; full Grafana stack deferred | Accepted (MVP scope) |
| ADR-029 | Sentry + PostHog + Axiom as MVP observability stack | Accepted (MVP scope) |
| ADR-030 | Langfuse (free tier) for LLM tracing and evals | Accepted (MVP scope) |
| ADR-031 | Cloudflare R2 for object storage; egress-free advantage | Accepted (MVP scope) |
| ADR-032 | HashiCorp Vault deferred; Fly/Render secrets + Doppler for MVP | Deferred |
| ADR-033 | Istio / service mesh deferred until multi-service | Deferred |
| ADR-034 | OpenAPI 3.1 + Protobuf as contract sources of truth | Accepted |
| ADR-035 | Cell-based multi-region architecture — deferred to Year 2 | Deferred |
| ADR-036 | Cloud-agnostic architecture; AWS-first for infra defaults | Accepted |
| ADR-037 | Compliance-ready architecture from Day 1; certification pursued only when a customer requires it | Accepted |
| ADR-038 | ULID identifiers with type prefixes | Accepted |
| ADR-039 | Deterministic replay of conversations from event log | Accepted |
| ADR-040 | Card-required 14-day trial, no forever-free tier | Accepted |

---

## ADR-001 — Vertical AI Platform, not general chatbot builder

- **Decision:** Position and build the product as an **AI Employee platform for specific verticals**, not a generic "AI chatbot builder."
- **Why:** Generic chatbot builders (Chatbase, Voiceflow, Botpress) are commoditized. Vertical depth compounds via templates, tools, evals, integrations, case studies. Enterprises pay for outcomes, not for "AI."
- **Alternatives:** Horizontal builder (Chatbase-like); LLM API reseller; developer-only agent framework.
- **Trade-offs:** Slower TAM appearance vs. horizontal, faster real revenue and moat compounding per vertical.
- **When to revisit:** After 5 verticals shipped + $10M ARR; then evaluate whether a marketplace/horizontal layer is warranted.
- **Migration path:** Templates are already the abstraction; a horizontal "build your own" surface can sit on top later.
- **Risk:** Low. This is a positioning bet more than a technical bet.
- **Status:** Accepted.

## ADR-002 — Chat-first, voice deferred to Sprint 10

- **Decision:** Ship the MVP as web chat + widget. Voice pipeline is Sprint 10 (~week 20+).
- **Why:** Voice is the most complex, expensive, and latency-sensitive channel. Building it before PMF is the #1 way to burn 6 weeks pre-revenue. Chat proves the runtime and unblocks revenue.
- **Alternatives:** Voice-first (Retell/Vapi model); simultaneous chat + voice.
- **Trade-offs:** Slightly less marketing wow, dramatically faster revenue.
- **When to revisit:** If ≥ 3 paying customers block on voice before Sprint 10.
- **Migration path:** LiveKit + Pipecat plug into the same runtime; the runtime is already channel-agnostic ([AI_EMPLOYEE_FRAMEWORK.md §11](AI_EMPLOYEE_FRAMEWORK.md)).
- **Risk:** Medium. A voice-first competitor may out-market us; we counter with outcomes, integrations, and vertical depth.
- **Status:** Accepted (MVP scope).

## ADR-003 — Healthcare / Dental Receptionist as launch vertical

- **Decision:** Launch with the AI Receptionist for small clinics + dental practices ([PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md)).
- **Why:** Highest weighted score (pain × buy-speed × ACV × ease-of-MVP × expansion adjacency). Owner-decision buyer. HIPAA is manageable at MVP (no PHI stored).
- **Alternatives:** Restaurant, real estate, legal intake, generic appointment booking.
- **Trade-offs:** Regulated content requires care; upside is highest-quality customer + adjacent vertical expansion.
- **When to revisit:** If clinic demo booking rate < 30% after 40 attempts, pivot to Legal Intake or generic Appointment Booking. Runtime unchanged.
- **Migration path:** New template ships in ≤ 1 week using existing runtime + template framework.
- **Risk:** Medium. Mitigated by vertical scoring rigor + explicit pivot trigger.
- **Status:** Accepted (MVP scope).

## ADR-004 — One runtime, N templates — never fork per vertical

- **Decision:** All verticals share the same Agent Runtime, Memory, Knowledge, Tool Framework, Channel adapters, Console. Vertical differences live in declarative templates ([AI_EMPLOYEE_FRAMEWORK.md §7](AI_EMPLOYEE_FRAMEWORK.md)).
- **Why:** Forking per vertical explodes maintenance, blocks eval/observability standardization, kills marketplace potential.
- **Alternatives:** Per-vertical service branches; parallel product lines.
- **Trade-offs:** More upfront rigor in configuration boundaries; enormous downstream leverage.
- **When to revisit:** Never — if we violate this, we've become a services company.
- **Migration path:** Not applicable.
- **Risk:** Low if enforced from Sprint 1. High if violated once (precedent effect).
- **Status:** Accepted.

## ADR-005 — AI Employee canonical model (11 pillars)

- **Decision:** Every AI Employee is fully described by 11 pillars (Identity, Mission, Knowledge, Memory, Skills, Workflow, Tools, Policy, Personality, Reasoning/Escalation, Version/Deployment). Full spec in [AI_EMPLOYEE_FRAMEWORK.md §3](AI_EMPLOYEE_FRAMEWORK.md).
- **Why:** A canonical model makes templates portable, evals uniform, marketplace publishable, RBAC coherent, migrations clean.
- **Alternatives:** Ad-hoc per-agent config; framework-only (LangGraph raw); free-form JSON.
- **Trade-offs:** Slight upfront rigidity; long-term the only path to a durable ecosystem.
- **When to revisit:** After 5 verticals; evaluate whether a 12th pillar is needed (unlikely).
- **Risk:** Low if enforced from Sprint 5 template.
- **Status:** Accepted.

## ADR-006 — LangGraph as the runtime engine

- **Decision:** LangGraph for the agent state machine. Wrapped behind our own `AgentRuntime` abstraction so it is swappable.
- **Why:** Explicit state; streaming; persistence; human-in-the-loop; production references; MIT-licensed core.
- **Alternatives:** OpenAI Agents SDK (newer, less battle-tested for complex flows); LlamaIndex Workflows (elegant, smaller ecosystem); CrewAI/AutoGen (too non-deterministic for regulated verticals); custom state machine.
- **Trade-offs:** Python-centric; some inherited LangChain flavor; version churn.
- **When to revisit:** If LangGraph's release cadence or licensing changes materially, or if OpenAI Agents SDK matures enough to matter.
- **Migration path:** `AgentRuntime` port isolates the choice. Node types map cleanly; migration is weeks, not months.
- **Risk:** Low-medium.
- **Status:** Accepted.

## ADR-007 — LiteLLM as LLM router (SDK now, proxy later)

- **Decision:** LiteLLM used as an in-process SDK in MVP. Upgrade to LiteLLM proxy sidecar in Sprint 5 when per-tenant quotas + centralized fallback become necessary.
- **Why:** Instant provider portability; no lock-in; supports 100+ providers; strong fallback semantics.
- **Alternatives:** Direct OpenAI/Anthropic SDKs; Portkey (SaaS); OpenRouter (SaaS); custom router.
- **Trade-offs:** Occasional lag on bleeding-edge features per provider.
- **When to revisit:** When we need per-tenant budgets, semantic cache, or multi-model A/B routing at scale.
- **Migration path:** From SDK → proxy sidecar → dedicated `llm-router` service. Interface unchanged at call sites.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-008 — Python + FastAPI (backend), TypeScript + Next.js (frontend)

- **Decision:** FastAPI for all AI-heavy backends. Next.js 15 (App Router) for the console. Fastify/NestJS for channel-webhook-heavy services when they appear.
- **Why:** Best-in-class ecosystems (Python for AI, TypeScript for React). Async-first, typed, OpenAPI-native.
- **Alternatives:** Go backend (worse AI ecosystem), Django (too batteries-included), Remix (smaller ecosystem than Next.js).
- **Trade-offs:** Two languages in the monorepo; mitigated by clear service ownership.
- **When to revisit:** Never for FastAPI/Next.js; revisit for Node channel adapters case-by-case.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-009 — Monolith now, module boundaries drawn as future services

- **Decision:** Ship the MVP as a **modular monolith** (`services/api`). Modules internally are shaped like the future services documented in [docs/MICROSERVICE_ARCHITECTURE.md](docs/MICROSERVICE_ARCHITECTURE.md). Extractions happen only when a service has a genuinely different scaling profile.
- **Why:** 1 team; complexity kills speed. Premature microservices doubles ops toil.
- **Alternatives:** Microservices from Day 1 (rejected); classic monolith (rejected — no module boundaries).
- **Trade-offs:** Discipline required to keep imports clean (enforced by lint).
- **When to revisit:** When voice ships (extract `realtime-gateway` + `voice-agent-workers`); when KB scale demands (extract `knowledge`); when > 200 tenants.
- **Migration path:** Every module has `ports.py`; extraction is a Dockerfile + new deploy target, not a refactor.
- **Risk:** Medium if module discipline slips; enforced by CI lint rules from Sprint 1.
- **Status:** Accepted (MVP scope).

## ADR-010 — Postgres as the single source of truth (OLTP)

- **Decision:** Postgres 16 (managed: Neon for MVP; RDS for scale) for all transactional data with mandatory `org_id` and Row-Level Security.
- **Why:** Mature; JSONB; RLS; partitioning; extensions (pgvector, pg_partman); managed everywhere; boring in the best sense.
- **Alternatives:** MySQL (weaker RLS); CockroachDB (great for global, higher latency); YugabyteDB.
- **Trade-offs:** Vertical scaling ceiling; Citus for horizontal at scale.
- **When to revisit:** When single-instance ceiling hit (~20k WPS). Then Citus + shard-by-tenant.
- **Migration path:** Documented in [docs/SCALING.md](docs/SCALING.md).
- **Risk:** Low.
- **Status:** Accepted.

## ADR-011 — pgvector for vector search in MVP; Qdrant later

- **Decision:** Use `pgvector` extension on the primary Postgres for vector storage in MVP. Migrate to Qdrant when hybrid retrieval + reranker + billion-scale demand it.
- **Why:** Zero additional ops; same DB; sufficient to millions of chunks.
- **Alternatives:** Qdrant from Day 1 (extra service); Weaviate/Milvus (heavier); Pinecone (SaaS lock-in).
- **Trade-offs:** Weaker hybrid + payload filter ergonomics than Qdrant; acceptable at MVP scale.
- **When to revisit:** At ~10M chunks OR when advanced RAG (Sprint 15) requires Qdrant's payload filters and hybrid.
- **Migration path:** Same chunk model; move data via ETL; embedding format unchanged. 1–2 sprints.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-012 — Redis for cache, sessions, rate limits, streams

- **Decision:** Redis (Upstash managed for MVP; Redis Cluster later) for cache, session state, rate limits, pub/sub, streams.
- **Why:** Sub-ms latency; ubiquitous; every scale tier supported.
- **Alternatives:** Valkey (Redis OSS fork; monitor licensing evolution); Dragonfly (higher single-node throughput); Memcached (cache-only).
- **Trade-offs:** Post-BSL licensing; Valkey is the fallback if licensing worsens.
- **When to revisit:** Migrate to Valkey if Redis licensing conflicts with our distribution model.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-013 — ClickHouse for analytics — deferred; Postgres queries first

- **Decision:** No ClickHouse in MVP. Postgres queries + basic materialized views serve analytics through Sprint 12+. ClickHouse arrives only when Postgres analytics hurt.
- **Why:** ClickHouse is powerful but not free operationally; premature at < 1M sessions.
- **Alternatives:** BigQuery (SaaS $$$); Snowflake; DuckDB for local analytics.
- **When to revisit:** When session count / analytics query latency > acceptable threshold in Postgres.
- **Migration path:** Kafka → ClickHouse ingest pipeline in [docs/DATABASE_DESIGN.md §6](docs/DATABASE_DESIGN.md).
- **Risk:** Low.
- **Status:** Deferred.

## ADR-014 — Kafka event bus — deferred; Postgres LISTEN/NOTIFY + Redis Streams in MVP

- **Decision:** No Kafka/Redpanda in MVP. Use Postgres LISTEN/NOTIFY for low-volume cross-module events; Redis Streams for high-throughput. Kafka only when durable, replayable, ordered cross-service event flow is required.
- **Why:** Kafka is a significant operational burden; unnecessary until services are split.
- **Alternatives:** NATS JetStream (simpler); Pulsar (heavier).
- **When to revisit:** When cross-service async volume or replay/audit needs justify it.
- **Migration path:** Event contracts (Buf/Protobuf) are already the plan; wiring changes without touching producers/consumers semantically.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-015 — Temporal workflows — deferred; arq/RQ jobs in MVP

- **Decision:** No Temporal in MVP. Use `arq` (or `RQ`) Redis-backed job workers for background ingestion, billing sync, notifications. Temporal arrives when multi-step compensating workflows appear.
- **Why:** Temporal is excellent but heavy for a solo team.
- **Alternatives:** Airflow (batch, wrong fit); Prefect (lighter); Cadence.
- **When to revisit:** When we need durable, compensating workflows (tenant provisioning, outbound voice campaigns, complex billing runs).
- **Migration path:** Job interfaces designed to be replaced with Temporal activities.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-016 — Fly.io for hosting, not Kubernetes

- **Decision:** Deploy on Fly.io (primary) or Render (fallback) for MVP. Kubernetes only when scale/enterprise demands it.
- **Why:** One-command deploys; global anycast; sane pricing; zero K8s ops.
- **Alternatives:** EKS/GKE (too much for solo team); Cloud Run (managed, GCP-only); ECS.
- **Trade-offs:** Fly.io is opinionated; we accept it for speed.
- **When to revisit:** When Fly.io no longer fits (multi-region complex networking; enterprise on-prem; > 1000 tenants).
- **Migration path:** Docker images + Helm charts already the plan for the long-term architecture. K8s is a lift-and-shift when needed.
- **Risk:** Low-medium.
- **Status:** Accepted (MVP scope).

## ADR-017 — Clerk for authentication; WorkOS/Ory later

- **Decision:** Clerk for MVP (sign-in, sign-up, orgs, MFA, JWT verification). Migrate to WorkOS (or Ory for on-prem) when a paying customer requires SAML/SCIM.
- **Why:** 3 weeks saved. Excellent DX. Free tier fits.
- **Alternatives:** WorkOS (better enterprise, more setup time), Auth0 (expensive), Keycloak (heavy), custom (never).
- **Trade-offs:** SaaS lock-in; mitigated by the Clerk → WorkOS migration being well-trodden and stateless.
- **When to revisit:** First enterprise SAML/SCIM request.
- **Migration path:** JWT verification stays the same shape; user table already normalized.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-018 — Stripe for billing; Metronome added at scale

- **Decision:** Stripe (Checkout + Billing Portal + webhooks) for subscriptions in MVP. Add Metronome for enterprise metered plans at ~100 customers.
- **Why:** Stripe is standard; Metronome fills the usage-metering gap when we need it.
- **Alternatives:** Orb, Lago (OSS), custom metering.
- **Trade-offs:** Stripe fees.
- **When to revisit:** When enterprise usage-based pricing gets complex.
- **Risk:** Very low.
- **Status:** Accepted.

## ADR-019 — Row-level tenancy via Postgres RLS; enforced from Sprint 5

- **Decision:** Every tenant table has `org_id` and RLS policies. In Sprint 1–4, single-dev discipline enforces scoping in code; RLS policies enabled + verified from Sprint 5 with automated cross-tenant leakage tests.
- **Why:** Row-level tenancy is the sweet spot for SMB tier; strong isolation without dedicated infra per tenant.
- **Alternatives:** Schema-per-tenant (Silo tier, later); dedicated DB per tenant (Enterprise, later); no isolation (rejected).
- **Trade-offs:** Requires code discipline until RLS enabled; leakage tests catch violations from Sprint 5.
- **When to revisit:** When first enterprise requests Silo tier.
- **Migration path:** Silo tier = schema-per-tenant; Dedicated = DB-per-tenant. Documented in [docs/MULTI_TENANCY.md](docs/MULTI_TENANCY.md).
- **Risk:** High if delayed past Sprint 5.
- **Status:** Accepted.

## ADR-020 — Firecrawl + `unstructured` + LlamaParse for KB ingestion

- **Decision:** URL crawling via Firecrawl (or Jina Reader); documents via `unstructured` OSS with LlamaParse as fallback for hard PDFs.
- **Why:** Do not build a PDF parser. Do not build a crawler. Both are quality moats owned by dedicated teams.
- **Alternatives:** Custom Playwright crawler; PyMuPDF only; Reducto; Marker.
- **Trade-offs:** Third-party dependencies and cost.
- **When to revisit:** If KB ingestion cost becomes material or quality issues persist.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-021 — OpenAI embeddings (`text-embedding-3-small`); BGE-M3 for self-host

- **Decision:** OpenAI `text-embedding-3-small` for MVP embeddings; switch to `text-embedding-3-large` when quality demands; BGE-M3 for on-prem/self-host scenarios.
- **Why:** Cheap, good, one API. Matryoshka reduction available if storage matters.
- **Alternatives:** Voyage, Cohere multilingual, BGE-M3 self-host.
- **When to revisit:** Sprint 15 (advanced RAG) or when enterprise on-prem lands.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-022 — Cohere Rerank added in Sprint 15, not before

- **Decision:** No reranker in MVP. Add Cohere Rerank v3 (or BGE-reranker-v2-m3 self-host) in Sprint 15 when retrieval quality plateaus.
- **Why:** Reranker adds latency + cost. Measured value only appears when the base retrieval is proven to be the bottleneck.
- **When to revisit:** When faithfulness eval scores plateau below target.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-023 — LiveKit + Pipecat for voice pipeline (when we add voice)

- **Decision:** When voice ships (Sprint 10), use LiveKit (WebRTC SFU + SIP gateway) + Pipecat (voice orchestration).
- **Why:** Both are OSS, purpose-built for AI voice, active communities, no lock-in.
- **Alternatives:** Daily.co (SaaS), Twilio Voice (SaaS expensive), Vapi/Bland (SaaS lock-in), custom.
- **When to revisit:** If LiveKit or Pipecat OSS trajectory stalls.
- **Risk:** Medium; voice ops is the hardest ops in the platform.
- **Status:** Accepted.

## ADR-024 — Deepgram STT + ElevenLabs TTS as V1 voice providers

- **Decision:** Deepgram Nova as primary STT; ElevenLabs Turbo as primary TTS. Multi-provider fallback (AssemblyAI, Cartesia) added same sprint.
- **Why:** Best latency/quality on both.
- **When to revisit:** When on-prem tier requires (Whisper + XTTS-v2 fallback).
- **Risk:** Low.
- **Status:** Accepted.

## ADR-025 — Twilio + Telnyx + Plivo as telephony providers

- **Decision:** Multi-provider telephony from Sprint 10 for reliability + coverage.
- **Why:** Single-provider telephony is a business risk. Multi-provider trunking is table stakes.
- **When to revisit:** Rebalance based on cost / reliability.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-026 — MCP first-class in tool framework

- **Decision:** Support Model Context Protocol as both a client (external MCP servers appear as tools) and a server (our agents exposed as MCP endpoints for external clients like Claude Desktop / IDEs).
- **Why:** MCP is trending to become the de facto standard for AI tool interop. First-class support is a leverage bet.
- **Alternatives:** Custom protocol; OpenAPI-only.
- **When to revisit:** If MCP adoption stalls after 12 months.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-027 — Firecracker sandbox for custom-code tools — deferred

- **Decision:** No custom-code tools in MVP. When we allow customer code, use Firecracker microVMs (or gVisor fallback) for isolation.
- **Why:** Custom code is a big attack surface; ship it only when demand justifies the ops investment.
- **When to revisit:** When first paying customer requests custom Python/JS tools.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-028 — OpenTelemetry from Day 1; full Grafana stack deferred

- **Decision:** OTel SDKs and semantic conventions from Sprint 1. Full self-hosted Prometheus + Tempo + Loki stack deferred to Sprint 17+.
- **Why:** Instrumentation is cheap when done early, expensive when retrofitted. Backend storage can be swapped later without touching call sites.
- **Alternatives:** Vendor-specific SDKs (locks in observability vendor).
- **When to revisit:** When Axiom/Sentry costs or capabilities become limiting.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-029 — Sentry + PostHog + Axiom as MVP observability stack

- **Decision:** Sentry (errors), PostHog (product analytics), Axiom (logs) for MVP. Grafana stack later.
- **Why:** Three SaaS tools beat six OSS ops burdens at this stage.
- **When to revisit:** When cost or data-residency requires self-hosting.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-030 — Langfuse (free tier) for LLM tracing and evals

- **Decision:** Langfuse for LLM traces, prompt versioning, and eval runs in MVP. Own eval service considered only if Langfuse constraints bite.
- **Alternatives:** Braintrust, Helicone, own build.
- **When to revisit:** Sprint 15+ when eval volume/features exceed Langfuse's free tier or fit.
- **Risk:** Low.
- **Status:** Accepted (MVP scope).

## ADR-031 — Cloudflare R2 for object storage

- **Decision:** Cloudflare R2 for KB blobs, transcripts, exports. S3-compatible so switch to AWS S3 is trivial.
- **Why:** Zero egress fees + S3 compatibility.
- **When to revisit:** For enterprise BYOC (bring-your-own-cloud) tenants.
- **Risk:** Very low.
- **Status:** Accepted (MVP scope).

## ADR-032 — HashiCorp Vault deferred; Fly/Render secrets + Doppler for MVP

- **Decision:** Use platform-native secret stores for MVP. Vault when compliance/BYOK demands it.
- **When to revisit:** Enterprise BYOK / on-prem tier.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-033 — Istio / service mesh deferred until multi-service

- **Decision:** No service mesh in MVP monolith. Add Istio/Linkerd when we have ≥ 3 services and need mTLS + policy.
- **Risk:** Low.
- **Status:** Deferred.

## ADR-034 — OpenAPI 3.1 + Protobuf as contract sources of truth

- **Decision:** Every public REST surface has an OpenAPI 3.1 spec; every internal gRPC has a `.proto`. Both check for breaking changes in CI (`buf breaking`, `oasdiff`).
- **Why:** API-first is the only sustainable path to SDKs, docs, contract tests.
- **When to revisit:** Never.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-035 — Cell-based multi-region architecture — deferred to Year 2

- **Decision:** Single region for MVP. Multi-region added when first EU/APAC customer demands data residency. Cells (tenant-bulkheads) added at Year 2 scale.
- **When to revisit:** First data-residency-blocked deal or > 5,000 tenants.
- **Migration path:** Documented in [docs/SCALING.md](docs/SCALING.md) and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
- **Risk:** Medium if delayed past first enterprise regional requirement.
- **Status:** Deferred.

## ADR-036 — Cloud-agnostic architecture; AWS-first for infra defaults

- **Decision:** Portable to AWS/GCP/Azure/OCI via Kubernetes + open standards. AWS is our default cloud for the first year.
- **Why:** Portability preserves optionality (enterprise BYOC) without slowing us down day-to-day.
- **When to revisit:** If a strategic enterprise deal requires GCP/Azure primary.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-037 — Compliance-ready architecture from Day 1; certification pursued only when a customer requires it

- **Decision:** Every architectural choice is compatible with SOC 2, HIPAA, GDPR, PCI SAQ-A from Day 1. Formal certification (SOC 2 Type I, HIPAA BAA, ISO 27001) is pursued only when a paying customer requires it.
- **Why:** Retrofitting compliance is 10x more expensive than baking it in. Certifying prematurely is unnecessary spend.
- **When to revisit:** Every new enterprise deal.
- **Risk:** Low if architecture is disciplined; high if any pattern violates the plan (e.g., PII in logs).
- **Status:** Accepted.

## ADR-038 — ULID identifiers with type prefixes

- **Decision:** All IDs are ULIDs with type prefixes (`org_`, `usr_`, `agn_`, `ses_`, `tur_`, ...).
- **Why:** Sortable, unique, human-readable, cross-system portable, no coordination.
- **Alternatives:** UUIDv4 (unsortable), auto-increment integers (tenant leakage risk).
- **Risk:** Very low.
- **Status:** Accepted.

## ADR-039 — Deterministic replay of conversations from event log

- **Decision:** Every non-deterministic input (LLM output, tool result, current time, random) is captured to an event log; a "replay" mode reproduces the conversation exactly. Used for evals, debugging, regression.
- **Why:** The single biggest debuggability multiplier for AI systems.
- **When to revisit:** Never.
- **Risk:** Low.
- **Status:** Accepted.

## ADR-040 — Card-required 14-day trial, no forever-free tier

- **Decision:** Trials require card upfront; auto-convert to paid at day 14 (Stripe). No forever-free tier.
- **Why:** Forever-free tiers cost money and produce weak signal; card-required trials filter for intent and dramatically raise conversion.
- **Alternatives:** Free tier (rejected); no trial (rejected).
- **When to revisit:** If cold-traffic conversion is too low; consider "free tier for education/nonprofit" only.
- **Risk:** Low.
- **Status:** Accepted.

---

## Reserved for future ADRs

- ADR-041 — Voice pipeline provider tiers per region.
- ADR-042 — Fine-tune vs. RAG cost boundary.
- ADR-043 — On-prem tier packaging.
- ADR-044 — Marketplace publisher KYB + payouts.
- ADR-045 — MCP server exposure of our agents (Year 2).

New ADRs are added by PR; the index above is updated in the same PR. Every ADR must include the eight fields above.
