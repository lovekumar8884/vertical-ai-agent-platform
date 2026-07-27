# DATABASE DESIGN

## 1. Datastore Choices

| Store | Purpose | Why |
|-------|---------|-----|
| **PostgreSQL 16** | Transactional truth (tenants, agents, sessions, billing) | Mature, JSONB, RLS, extensions (pg_partman, pg_stat_statements), managed everywhere |
| **Redis 7 (Cluster)** | Session state, cache, rate limits, pub/sub | Sub-ms, streams, TTLs |
| **Qdrant** | Vector search for KB + episodic memory | Rust, filters, gRPC, HNSW, self-hostable, mature |
| **ClickHouse** | Analytics, conversation search, evals | Best-in-class OLAP, cheap storage, materialized views |
| **S3 / MinIO** | Blob (audio, transcripts, docs, exports) | Object durability + WORM for compliance |
| **Kafka (Redpanda)** | Event backbone | Ordered, replayable, high-throughput |
| **HashiCorp Vault** | Secrets, per-tenant KEKs | Transit, dynamic secrets |

## 2. Multi-Tenancy Strategy

- **Row-level tenancy** in Postgres via mandatory `tenant_id` column + **Row-Level Security (RLS)** policies.
- **Schema-per-tenant** offered for Enterprise Dedicated tier.
- **Cluster-per-tenant** for VPC/on-prem Enterprise Plus.
- Redis: key prefix `t:{tenant_id}:...`; ACL user per tenant in dedicated tier.
- Qdrant: **payload filter** on `tenant_id`; dedicated collection per corpus with `tenant_id` payload.
- ClickHouse: `tenant_id` low-cardinality column, ORDER BY includes it.
- S3: bucket-per-region, prefix `t/{tenant_id}/...`; SSE-KMS with per-tenant CMK.

## 3. Core Tables (Postgres — Control Plane)

```sql
-- All tables include: id (ULID), tenant_id, created_at, updated_at, deleted_at
-- All tables enable RLS: USING (tenant_id = current_setting('app.tenant_id')::uuid)

tenants(id, name, plan, region, data_residency, encryption_key_ref, status)
users(id, tenant_id, email, name, sso_subject, mfa_enabled, status)
roles(id, tenant_id, name, scopes jsonb)
user_roles(user_id, role_id)
api_keys(id, tenant_id, prefix, hash, scopes jsonb, expires_at, last_used_at)
audit_log(id, tenant_id, actor_id, action, resource_type, resource_id, diff jsonb, ip, ua, at)

-- Agent Design
agents(id, tenant_id, slug, name, vertical, status)
agent_versions(id, agent_id, tenant_id, version, spec jsonb, published_at, published_by)
prompts(id, agent_version_id, tenant_id, role, template, variables jsonb)
tool_bindings(id, agent_version_id, tool_id, config jsonb)
kb_bindings(id, agent_version_id, corpus_id)

-- Channels
channel_accounts(id, tenant_id, kind, provider, external_id, credentials_ref, status)
phone_numbers(id, tenant_id, e164, provider, capabilities, agent_binding jsonb)

-- Tools & Connectors
tools(id, tenant_id, name, kind, spec jsonb, sandbox_profile)
connections(id, tenant_id, provider, oauth_ref, scopes, status)

-- Knowledge
corpora(id, tenant_id, name, embedding_model, chunker jsonb)
documents(id, corpus_id, tenant_id, source, uri, checksum, status, meta jsonb)
chunks(id, document_id, tenant_id, ord, text, tokens, vector_ref) -- vector_ref points to Qdrant

-- Sessions & Turns (partitioned by month)
sessions(id, tenant_id, agent_version_id, channel, external_ref, started_at, ended_at,
         end_reason, user_ref, metadata jsonb) PARTITION BY RANGE (started_at);
turns(id, session_id, tenant_id, idx, role, content, tool_calls jsonb, latency_ms,
      tokens_in, tokens_out, model, cost_micros, started_at, ended_at)
      PARTITION BY RANGE (started_at);

-- Memory (long-term)
memory_facts(id, tenant_id, subject_ref, key, value jsonb, confidence, source_turn_id,
             valid_from, valid_to)

-- Billing
subscriptions(id, tenant_id, plan, status, current_period_start, current_period_end)
usage_records(id, tenant_id, meter, quantity, unit, at, session_id, agent_version_id)
   PARTITION BY RANGE (at);
invoices(id, tenant_id, period_start, period_end, subtotal, tax, total, status, pdf_ref)

-- Eval
eval_suites(id, tenant_id, agent_id, name, spec jsonb)
eval_runs(id, suite_id, tenant_id, agent_version_id, status, summary jsonb, started_at, ended_at)
eval_cases(id, run_id, tenant_id, input jsonb, expected jsonb, actual jsonb, verdict, judge_meta jsonb)
```

### Indexing Rules
- Every FK indexed.
- All `tenant_id` columns lead composite indexes: `(tenant_id, ...)`.
- Hot query paths get partial + covering indexes; measured via `pg_stat_statements`.
- BRIN on time-partitioned columns.

### Partitioning
- `sessions`, `turns`, `usage_records`, `audit_log`, `eval_cases` → monthly range partitions via `pg_partman`.
- Auto-detach + move to S3 (via `pg_dump` + parquet export) after 90 days; queryable via ClickHouse.

## 4. Redis Keyspaces

| Pattern | TTL | Purpose |
|---------|-----|---------|
| `t:{tid}:sess:{sid}:state` (hash) | 24h sliding | Live conversation state |
| `t:{tid}:sess:{sid}:history` (list) | 24h | Rolling window messages |
| `t:{tid}:rl:{key}` (token bucket) | 60s | Rate limits |
| `t:{tid}:idem:{key}` | 24h | Idempotency responses |
| `stream:conv.turns` | 7d | Realtime tail for dashboards |
| `t:{tid}:cache:llm:{hash}` | 1h | Prompt+response cache |
| `t:{tid}:presence:{agent}` (set) | 30s | Active sessions per agent |

## 5. Qdrant Layout

- **Collection per (tenant, corpus)** for large tenants; **shared collection with `tenant_id` payload filter** for SMB tier.
- Vector size: 1024 (default: BGE-M3 or text-embedding-3-large).
- HNSW: `m=16, ef_construct=200, ef=128`.
- Payload: `tenant_id`, `corpus_id`, `document_id`, `chunk_id`, `title`, `source`, `updated_at`, `acl_tags[]`.
- **ACL filter** applied on every query (defense-in-depth vs. RLS).

## 6. ClickHouse Schema (Analytics Plane)

```sql
CREATE TABLE turns_analytics (
  ts             DateTime64(3, 'UTC'),
  tenant_id      LowCardinality(String),
  agent_id       LowCardinality(String),
  agent_version  LowCardinality(String),
  channel        LowCardinality(String),
  session_id     String,
  turn_id        String,
  role           LowCardinality(String),
  model          LowCardinality(String),
  tokens_in      UInt32,
  tokens_out     UInt32,
  latency_ms     UInt32,
  cost_micros    UInt64,
  tool_names     Array(LowCardinality(String)),
  had_error      UInt8,
  sentiment      Float32,
  intent         LowCardinality(String)
) ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, agent_id, ts)
TTL ts + INTERVAL 730 DAY;
```

Materialized views:
- `mv_daily_usage_by_tenant`
- `mv_agent_success_rate_hourly`
- `mv_model_cost_by_tenant_daily`

## 7. S3 Layout

```
s3://vsa-{env}-{region}/
  t/{tenant_id}/
    sessions/{yyyy}/{mm}/{dd}/{session_id}/
      audio.opus            # full call recording
      transcript.jsonl
      trace.json            # OTEL trace snapshot
    kb/{corpus_id}/documents/{doc_id}/{filename}
    exports/{export_id}.zip
    invoices/{invoice_id}.pdf
```

WORM (Object Lock) enabled on `sessions/` for compliance tenants.

## 8. Data Retention (default; tenant-configurable)

| Data | Default | Configurable |
|------|--------|--------------|
| Transcripts | 90 days | 7 days → 7 years |
| Audio recordings | 30 days | 0 → 7 years |
| Long-term memory | Forever (until revoked) | Yes |
| Traces | 14 days | 3 → 90 days |
| Metrics | 400 days (Prometheus + Thanos) | Fixed |
| Audit log | 7 years | Fixed (compliance) |
| Billing | 10 years | Fixed |

## 9. Migrations
- **Alembic** for Postgres. Every migration reversible.
- Zero-downtime rules: expand → migrate → contract. Never rename in a single deploy.
- `ghost` / `pg-osc` for large table changes.

## 10. Backups & DR
- Postgres: continuous WAL to S3 (via `wal-g`); nightly base backup; PITR 35 days.
- Redis: AOF + RDB snapshots every 15 min to S3.
- Qdrant: snapshot API nightly to S3.
- ClickHouse: `BACKUP` to S3 daily; incremental hourly.
- Cross-region replication for control plane.
- Quarterly restore drill (mandatory).
