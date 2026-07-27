# TECH STACK

Each decision below includes: **Why**, **Pros**, **Cons**, **Alternatives**, **Expected scale**, **Enterprise suitability**, **Maintenance cost**.

Legend: **Maintenance cost** — L (low), M (medium), H (high).

---

## 1. Realtime Media — **LiveKit**

- **Why**: Open-source, production-grade WebRTC SFU + SIP gateway + Python/Node **agents SDK** designed for AI voice. Cloud offering exists but self-hosting is battle-tested.
- **Pros**: Massive scale (LinkedIn/Spotify usage), permissive license, edge-friendly, SIP built in, active AI focus.
- **Cons**: Ops complexity (media servers, TURN, ports); requires WebRTC expertise.
- **Alternatives**: Daily.co (SaaS, lock-in), mediasoup (lower-level), Jitsi (SFU-first, less agent-oriented), Twilio Voice (SaaS, expensive at scale).
- **Expected scale**: 10k concurrent participants per SFU cluster; PoP shard for global.
- **Enterprise**: Excellent — self-host, on-prem viable.
- **Maintenance**: **M–H** (requires media/networking know-how).

## 2. Voice Pipeline Orchestration — **Pipecat**

- **Why**: Open-source Python framework for realtime voice+AI pipelines; composable processors; provider-agnostic.
- **Pros**: Purpose-built for voice AI; supports interruption, VAD, streaming end-to-end; growing community (Daily).
- **Cons**: Younger project; API still evolving; Python-only.
- **Alternatives**: LiveKit Agents (also excellent — often used together), Ultravox, custom.
- **Expected scale**: ~50 concurrent sessions per worker; horizontal scale.
- **Enterprise**: Good; MIT license.
- **Maintenance**: **M**.

## 3. Agent Orchestration — **LangGraph**

- **Why**: Graph-based state machine for LLM apps; persistence, streaming, human-in-the-loop, checkpoints. Production-grade compared to LangChain's abstractions.
- **Pros**: Explicit state; deterministic where possible; battle-tested by many prod deployments; LangSmith integration.
- **Cons**: Python-centric; some inherited "LangChain flavor"; version churn.
- **Alternatives**:
  - **OpenAI Agents SDK** (great DX, but newer, less battle-tested for complex flows).
  - **LlamaIndex Workflows** (event-driven, elegant, but smaller ecosystem).
  - **CrewAI / AutoGen** (autonomous multi-agent — too non-deterministic for prod verticals).
  - **Custom state machine** (we've considered; deferred pending scale reasons).
- **Expected scale**: State machines are cheap; bottleneck is downstream LLM/tools.
- **Enterprise**: Good; MIT-licensed core.
- **Maintenance**: **M**.

## 4. LLM Gateway — **LiteLLM**

- **Why**: Unified OpenAI-compatible interface to 100+ providers; retries, fallbacks, budgets, caching, key management.
- **Pros**: Provider-agnostic; drop-in swap; observability hooks; self-hostable proxy.
- **Cons**: Occasional lag in supporting bleeding-edge features per provider.
- **Alternatives**: Portkey (SaaS), OpenRouter (SaaS), custom router.
- **Expected scale**: Stateless; scales horizontally.
- **Enterprise**: Excellent.
- **Maintenance**: **L**.

## 5. Vector DB — **Qdrant**

- **Why**: Rust-based, high performance, hybrid search (dense+sparse), rich filtering, gRPC, easy to operate.
- **Pros**: Payload filters + tenant isolation; snapshots; well-documented; strong SDK story.
- **Cons**: Younger than Elasticsearch; managing large clusters requires care.
- **Alternatives**:
  - **Weaviate** — great features, heavier ops.
  - **Milvus** — mature, complex.
  - **pgvector** — simple, but limits at scale; considered for Shared tier if we consolidate.
  - **Pinecone** — SaaS, expensive, lock-in.
  - **Elastic / OpenSearch** — good hybrid; heavier for pure vector.
- **Expected scale**: 1B+ vectors per cluster.
- **Enterprise**: Excellent (Apache 2 self-host).
- **Maintenance**: **M**.

## 6. Backend Framework — **FastAPI** (Python) + **Fastify/NestJS** (TS)

- **Why**: FastAPI for AI-heavy services (best ecosystem); Fastify/NestJS for the console BFF + channel webhooks where Node ecosystem wins.
- **Pros**: Async, typed (pydantic/zod), OpenAPI-native, huge community.
- **Cons**: FastAPI's tooling for large services requires discipline; NestJS is opinionated (mostly good).
- **Alternatives**: Django (too batteries-included), Litestar, Go (Gin/Echo — used sparingly for infra services).
- **Expected scale**: Both proven at internet scale.
- **Enterprise**: Excellent.
- **Maintenance**: **L**.

## 7. Frontend — **Next.js 15 + React 19**

- **Why**: Best-in-class SSR/SSG, App Router, server components, Vercel-honed DX.
- **Pros**: Ecosystem, hiring, ergonomics; supports the console + docs + widget landing.
- **Cons**: Framework churn; overkill for tiny widgets (use plain React for embed).
- **Alternatives**: Remix, SvelteKit (smaller ecosystem).
- **Expected scale**: Fine; console is not a bottleneck.
- **Enterprise**: Excellent.
- **Maintenance**: **L**.

## 8. Workflow Engine — **Temporal**

- **Why**: Durable, retryable workflows: KB ingestion, outbound campaigns, billing runs, provisioning, handoff SLAs.
- **Pros**: Reliability primitive; code-first workflows; strong observability.
- **Cons**: Operational cost (server + workers + DB); learning curve.
- **Alternatives**: Airflow (batch, not real-time), Prefect (lighter), Cadence, DBOS, custom sagas.
- **Expected scale**: Millions of executions/day per cluster.
- **Enterprise**: Excellent; Temporal Cloud available for offload.
- **Maintenance**: **M–H**.

## 9. Cache / State — **Redis 7 (Cluster)**

- **Why**: Sub-ms latency; streams, pub/sub, structures, TTL — everything we need.
- **Pros**: Ubiquitous; managed everywhere; simple mental model.
- **Cons**: Licensing (post-BSL); use OSS Valkey fork if concerned.
- **Alternatives**: **Valkey** (Linux Foundation fork), KeyDB, Memcached (cache-only), Dragonfly (single-node throughput).
- **Enterprise**: Excellent.
- **Maintenance**: **L–M**.

## 10. OLTP — **PostgreSQL 16**

- **Why**: Most trusted OLTP; JSONB, RLS, partitioning, extensions.
- **Pros**: Boring, reliable, everywhere; RLS = multi-tenancy sweet spot.
- **Cons**: Vertical scaling ceiling; Citus for horizontal at scale.
- **Alternatives**: MySQL (fine, but weaker RLS), CockroachDB (great for global, higher latency), YugabyteDB.
- **Enterprise**: Excellent.
- **Maintenance**: **L–M**.

## 11. OLAP — **ClickHouse**

- **Why**: Analytics + conversation search at billion-row scale, cheap storage, fast aggregates.
- **Pros**: Extreme performance-per-dollar; materialized views; S3 tiering.
- **Cons**: Ops (Keeper/ZK, replication) if self-hosted.
- **Alternatives**: BigQuery (SaaS), Snowflake (SaaS $$$), Druid, Pinot.
- **Enterprise**: Excellent.
- **Maintenance**: **M–H** (or use ClickHouse Cloud).

## 12. Event Backbone — **Kafka (Redpanda for small footprint)**

- **Why**: Standard for event-driven; ordered, replayable, high throughput.
- **Pros**: Ecosystem, exactly-once semantics, connect ecosystem.
- **Cons**: JVM ops (Kafka) or vendor lock (Confluent). Redpanda simpler but single-vendor.
- **Alternatives**: NATS JetStream (simpler, less ecosystem), Pulsar (feature-rich, heavier), RabbitMQ (not stream-native).
- **Enterprise**: Excellent.
- **Maintenance**: **M–H**.

## 13. Object Store — **S3 / MinIO / GCS / Azure Blob**

- **Why**: Durable, cheap, ubiquitous; MinIO for on-prem.
- **Pros**: 11-nines, lifecycle, WORM (Object Lock).
- **Cons**: Egress fees; latency for small objects (use CDN or local cache).
- **Alternatives**: Cloudflare R2 (no egress fees), Backblaze B2.
- **Enterprise**: Excellent.
- **Maintenance**: **L** (SaaS) / M (MinIO self-host).

## 14. Container Orchestration — **Kubernetes (EKS/GKE/AKS)**

- **Why**: Portability across clouds and on-prem; broad ecosystem (Argo, KEDA, Istio, cert-manager).
- **Pros**: Everything integrates; hiring pool.
- **Cons**: Operational complexity; over-engineering risk for small teams.
- **Alternatives**: ECS (AWS only), Nomad (simpler), Fly.io (edge), Cloud Run (managed).
- **Enterprise**: Standard.
- **Maintenance**: **H** (mitigated by managed control plane).

## 15. Service Mesh — **Istio (or Linkerd)**

- **Why**: mTLS everywhere, traffic policies, observability, canary.
- **Pros**: Zero-code security; rich policy.
- **Cons**: Istio is complex; Linkerd simpler but fewer features.
- **Alternatives**: Consul Connect, Cilium Service Mesh, no mesh (defer).
- **Enterprise**: Yes; needed for zero-trust posture.
- **Maintenance**: **M–H**.

## 16. Observability — **OpenTelemetry + Prometheus + Grafana + Tempo + Loki + Sentry**

- **Why**: Open standard, portable, best-of-breed OSS stack; can swap to Datadog if enterprise-managed preferred.
- **Pros**: No lock-in; vendor-neutral.
- **Cons**: You operate it (or pay Grafana Cloud).
- **Alternatives**: Datadog (best UX, expensive), New Relic, Honeycomb (best trace UX), Elastic.
- **Enterprise**: Excellent.
- **Maintenance**: **M–H**.

## 17. Secrets — **HashiCorp Vault**

- **Why**: Dynamic secrets, transit engine, PKI, gold standard for zero-trust secret management.
- **Pros**: Universal; on-prem friendly.
- **Cons**: Ops-heavy; licensing changes to BUSL (OSS is still functional for us).
- **Alternatives**: Cloud SM (AWS/GCP), Infisical (OSS), Doppler.
- **Enterprise**: Excellent.
- **Maintenance**: **M**.

## 18. Auth (Console) — **WorkOS (build) / Ory (buy-vs-build)**

- **Why**: WorkOS = fastest to enterprise SSO/SCIM (time-to-market); Ory = self-hostable OSS if BYOC/on-prem required later.
- **Pros / Cons**: WorkOS SaaS lock-in vs Ory ops overhead. Decision: **WorkOS Day 1, migrate to Ory for on-prem tier**.
- **Alternatives**: Auth0 (mature, expensive), Keycloak (heavy), Clerk (SaaS, less enterprise).
- **Enterprise**: Yes.
- **Maintenance**: **L** (WorkOS) / M–H (Ory).

## 19. Billing — **Stripe** + **Metronome (usage-based)**

- **Why**: Stripe for CC + invoicing; Metronome for complex usage metering + rating.
- **Pros**: Battle-tested; enterprise invoicing.
- **Cons**: Metronome cost; Stripe fees.
- **Alternatives**: Orb, Lago (OSS, alternative to Metronome), custom.
- **Enterprise**: Yes.
- **Maintenance**: **L**.

## 20. Error Tracking — **Sentry**

- Standard. Self-hostable. Great DX. **L** maintenance.

## 21. Feature Flags — **OpenFeature spec + Unleash / Flagsmith**

- Vendor-neutral spec; self-hostable; per-tenant targeting supported.

## 22. Sandboxing — **Firecracker (primary) / gVisor (fallback)**

- **Why**: Strong isolation for customer code tools; used by AWS Lambda + Fly.
- **Cons**: KVM required; complex; gVisor is the pragmatic alternative.

## 23. CDN / Edge / WAF — **Cloudflare**

- CDN + WAF + Turnstile + R2 + Workers for edge logic. **L** maintenance.

## 24. CI/CD — **GitHub Actions + Argo CD + Argo Rollouts**

- Standard, portable. **L–M**.

## 25. Package Manager (Python) — **uv** (or Poetry)

- **uv** for speed; **Poetry** if we need broader tooling. Both fine.

---

## Language Choice Summary

| Service | Language |
|---------|---------|
| Agent Runtime, Voice, Memory, Knowledge, LLM Router, Tool Executor, Eval | **Python 3.12** |
| Console, Widget, Docs | **TypeScript / Next.js** |
| Channel adapters (webhook-heavy) | **TypeScript (Fastify)** |
| Gateway (Envoy config) + infra tooling | **Go** where useful |
| Shared proto/OpenAPI | **Protobuf + OpenAPI 3.1** |

---

## Explicit Rejections (with reason)

- **Autonomous agent frameworks (CrewAI, AutoGen)** — too non-deterministic for regulated verticals.
- **Serverless-only (Lambda-only)** — cold starts hostile to voice; vendor lock; local dev harder.
- **Single-vendor voice SaaS (Vapi/Bland/Retell)** — great products, but building a *platform* on them = wrong bet.
- **NoSQL as primary store** — RLS + strong consistency needed for tenants/billing; use Redis/Qdrant/ClickHouse alongside.
- **Full Datadog stack** — great, but cost + lock-in unappealing until we have revenue to justify.
- **Ruby / Rails** — no compelling reason vs. Python for AI stack.

---

## Cloud Choice
- **Cloud-agnostic** — architecture ports to AWS / GCP / Azure / OCI.
- **AWS default** for MVP (best breadth + SOC/HIPAA tooling); prove GCP and Azure by year 2.
- Managed services chosen only when replaceable (RDS, EKS, S3-compatible).
