# SCALING

## 1. Scaling Targets

| Dimension | MVP | Year 1 | Year 3 |
|-----------|-----|--------|--------|
| Tenants | 100 | 5,000 | 100,000+ |
| Concurrent voice calls | 100 | 2,000 | 10,000 |
| Concurrent chat sessions | 1,000 | 20,000 | 100,000 |
| Turns / sec (peak) | 100 | 5,000 | 50,000 |
| Conversations / year | 1M | 100M | 1B+ |
| Regions | 1 | 3 | 8 |
| Docs indexed | 1M | 100M | 5B |

## 2. Scale Principles

- **Stateless services** where possible; state in Redis / DB / Kafka.
- **Async everywhere** — never block a request on a downstream service that can be eventual.
- **Backpressure** — bounded queues, explicit shedding, no unbounded goroutines/tasks.
- **Partition early** — by `tenant_id` (Kafka, Postgres, ClickHouse, Redis Cluster).
- **Cache aggressively** — with tenant-scoped keys.
- **Autoscale on the right signal** — not just CPU (custom metrics: `active_sessions`, `queue_depth`).
- **Cell-based architecture** at large scale — bulkhead tenants into cells.

## 3. Horizontal Scaling per Service

| Service | Scale metric | Autoscaler |
|---------|-------------|-----------|
| gateway | RPS + p95 latency | HPA (KEDA on Prometheus) |
| realtime-gateway | Active calls per pod | KEDA custom metric |
| voice-agent-workers | Active workers per pod | KEDA |
| agent-runtime | Active turns / CPU | HPA |
| llm-router | Tokens/s + queue depth | KEDA |
| tool-executor | Queue depth | KEDA on Kafka lag |
| memory / knowledge | RPS + p95 | HPA |
| channels-* | Webhook queue depth | KEDA |
| analytics ingest | Kafka lag | KEDA |
| eval | Job queue | KEDA on Temporal task queue |

- **Pod Disruption Budgets** protect availability during rollouts / node drains.
- **Topology spread** across AZs.
- **Warm pools** for voice workers (cold start would ruin voice UX).

## 4. Database Scaling

### Postgres
- **Vertical first** — scale up to r7g.16xlarge; usually enough to 1B rows.
- **Read replicas** for read-heavy queries (analytics, console).
- **Partitioning** for time-series tables (already noted).
- **Citus** as future path for shard-by-tenant when single instance limits reached.
- **Connection pooling** via PgBouncer (transaction mode) at namespace level.

### Redis
- **Redis Cluster** for horizontal scale; keys hashed with `{tenant_id}` tag to co-locate tenant data.
- Separate clusters for: session state, cache, rate limits, pub/sub — different SLOs.

### Qdrant
- **Sharding** by collection; replicas for HA.
- Per-tenant collections at Dedicated tier avoid noisy-neighbor.
- Cold vectors → S3 offload (Qdrant on-disk index) for cost.

### ClickHouse
- **Distributed tables** with `tenant_id` in ORDER BY.
- Replicated `MergeTree` for HA; ZK/Keeper for coordination.
- Tiered storage: SSD (hot 30d) → S3 (cold).

### Kafka / Redpanda
- Partition by `tenant_id:aggregate_id`.
- Per-topic quotas per tenant; ACLs enforced.
- Redpanda for smaller footprints (no ZK); Kafka + KRaft for multi-region.

## 5. Multi-Region

### Control Plane
- **Primary + DR** (US-East + US-West or EU-West).
- Postgres logical replication for tenants/users/agents.
- Global DNS with health-check failover (Route53 / Cloudflare).

### Data Plane
- **Per-region**, self-contained (Postgres, Redis, Qdrant, Kafka, S3).
- Tenants **pinned** by data residency.
- Cross-region communication only for control plane sync.

### Voice Edge PoPs
- Media servers (LiveKit) deployed close to users (US, EU, IN, AP, LATAM, MEA — 15+ PoPs).
- SIP trunks per region.
- STT/TTS providers with regional endpoints.

## 6. Cell-Based Architecture (Year 2+)

- A **cell** = self-contained deployment serving a bounded set of tenants.
- Cells sized to ~10k tenants + 1k concurrent calls.
- Failure of one cell affects only its tenants.
- Cell control plane routes tenants to cells (sticky).
- Cell rebalance is offline (data migration workflow).

## 7. LLM Scaling & Cost Control

- **LiteLLM Router** with:
  - Multi-provider fallback (OpenAI → Anthropic → Groq → self-host)
  - Load-based routing
  - **Prompt caching** (Anthropic/OpenAI prefix caching + our own cache layer)
  - **Semantic cache** (query embedding → cached response) with tenant-scoped keys
- **Batching** for non-streaming tasks (fact extraction, KB summaries).
- **Small models first**, escalate on complexity heuristics.
- **Vertical fine-tunes** for hot verticals → 5–10x cheaper inference.
- **On-prem inference** (vLLM, TGI) for Enterprise volume where economics flip.

## 8. Cost Scaling Levers

| Lever | Impact |
|-------|-------|
| Prompt caching | 30–50% LLM cost reduction |
| Smaller models via router | 40–80% |
| Batch embeddings | 30% |
| Reserved / committed instances | 30–50% infra |
| Spot for stateless workers | 50–70% |
| Cold storage tiering | 60% storage |
| Contextual chunking + reranker (RAG) | Fewer LLM calls → 20% |

## 9. Load Testing

- **k6** for HTTP + WS; **Locust** for scenario mix.
- Custom **voice load generator** using LiveKit + synthetic audio.
- Weekly performance regression against staging.
- Chaos: LitmusChaos / Chaos Mesh — pod kill, network partition, latency injection.

## 10. Capacity Planning

- Track **utilization vs. headroom** dashboards; alert at 60% capacity → provision.
- Forecast growth from tenant onboarding + campaigns (outbound spikes).
- **Pre-scale** for known events (marketing campaigns, seasonal peaks).

## 11. Bottleneck Hypothesis (design-time)

| Bottleneck | Ceiling estimate | Mitigation |
|-----------|-----------------|-----------|
| Postgres single primary | ~20k WPS | Citus / cells |
| Redis single-key hotspot | ~100k ops/s | Sharding, tenant key tags |
| LiveKit room per pod | ~500 participants | Sharded rooms + PoP scaling |
| Qdrant single-node | ~1B vectors | Sharded collections |
| Kafka partition | ~10 MB/s per partition | Repartition by tenant |
| LLM provider rate limit | Provider-specific | Multi-provider fanout |

## 12. Anti-Patterns Rejected

- ❌ Scale via bigger boxes only.
- ❌ Cross-region synchronous calls.
- ❌ Global locks (Redlock etc.) in hot paths.
- ❌ Fan-out queries touching every tenant.
- ❌ Autoscaling on CPU alone for I/O-bound workloads.

## 13. Assumptions
- We adopt cells only when a single-region deploy can no longer meet SLOs.
- LLM provider concurrency limits are the tightest constraint until on-prem inference is viable.
- Voice concurrent capacity is the most expensive scaling axis and drives regional expansion decisions.
