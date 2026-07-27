# MULTI-TENANCY

## 1. Tenancy Tiers

We offer **four physical isolation tiers**, chosen by plan:

| Tier | Compute | Database | Vector DB | Storage | Buyer |
|------|---------|----------|-----------|---------|-------|
| **Shared** | Shared pods (namespace: `tenants-shared`) | Shared PG, RLS | Shared collection, filtered | Shared bucket, prefixed | SMB / self-serve |
| **Silo** | Shared cluster, per-tenant deployments | Shared PG cluster, schema-per-tenant | Dedicated collection | Dedicated bucket | Mid-market |
| **Dedicated** | Dedicated node pool, per-tenant namespace | Dedicated PG instance | Dedicated Qdrant instance | Dedicated bucket + KMS CMK | Enterprise |
| **VPC / On-Prem** | Customer VPC or air-gapped cluster | Customer-owned | Customer-owned | Customer-owned | Regulated enterprise |

Upgrade path: **Shared → Silo → Dedicated → VPC** is a supported migration (documented runbook + tooling).

## 2. Logical Isolation (applies to all tiers)

- **Mandatory `tenant_id`** column on every table + **Row-Level Security** enforced by policy.
- Every query sets `SET LOCAL app.tenant_id = '<uuid>'`; RLS uses `current_setting`.
- ORMs must go through a `TenantScopedSession` wrapper — direct connections forbidden by lint rule.
- Redis keys prefixed `t:{tenant_id}:...`; ACL user per silo/dedicated tenant.
- Qdrant queries carry `must` filter on `tenant_id`; enforced by SDK wrapper — no raw client calls.
- S3 prefix per tenant; IAM policies deny cross-prefix access; presigned URLs scoped narrowly.
- Kafka: topic namespacing `<tenant_id>.<topic>` for dedicated tier; ACLs enforced.
- ClickHouse: `tenant_id` in ORDER BY + `settings row_policy` per role for extra defense.

## 3. Noisy-Neighbor Protection

- Per-tenant **quotas** enforced at gateway: RPS, concurrent sessions, tokens/min, minutes/day.
- Per-tenant **priority classes** on K8s (Guaranteed for Enterprise, Burstable for Shared).
- LLM Router enforces **per-tenant token buckets**; overage → soft-throttle → hard-throttle → 429.
- Voice: **max concurrent calls** enforced at Realtime Gateway; new calls parked with polite retry.
- Kafka: quotas on producer/consumer throughput per tenant.

## 4. Data Residency

- Tenant selects primary region at creation (US, EU, IN, AP; growing).
- **All customer data pinned to region** — control plane (billing/admin) may replicate globally with **no** conversation payloads.
- Cross-region access blocked by network policies + KMS key scoping (keys don't leave region).
- Console detects user region and routes to nearest data plane.

## 5. Encryption Per Tenant

- **SSE-KMS** on S3 with per-tenant CMK (Dedicated+).
- **Postgres**: TDE via disk encryption; column-level encryption for PII fields using per-tenant DEK wrapped by tenant KEK in Vault (Transit engine).
- **BYOK**: Enterprise can supply CMK (AWS KMS, GCP KMS, Azure Key Vault, or on-prem HSM).
- **Envelope encryption** for large blobs; keys rotated annually or on demand.

## 6. Tenant Provisioning Workflow (Temporal)

```
provision_tenant(input):
  1. Create tenant row (status=provisioning)
  2. Create KMS CMK (if Dedicated+)
  3. Create Postgres schema/DB (Silo+) or ensure RLS setup (Shared)
  4. Create Qdrant collection (Silo+)
  5. Create S3 prefix + bucket policy
  6. Create Kafka topics (Dedicated)
  7. Seed default roles + owner user
  8. Configure billing (Stripe customer)
  9. Emit tenant.provisioned event
  10. Send welcome email + provisioning report
  ROLLBACK on failure (compensating activities)
```

## 7. Tenant Lifecycle

| State | Meaning |
|-------|--------|
| `provisioning` | Setup in progress |
| `active` | Normal |
| `suspended` | Read-only; no new sessions; billing paused per policy |
| `frozen` | Compliance freeze; no writes, no reads except by authorized ops |
| `deleting` | Data destruction in progress |
| `deleted` | Tombstone; hard-delete after retention window |

**Deletion**: soft-delete + 30-day recovery, then hard-delete across all datastores + backups (compliance-scheduled purge). Deletion certificate issued.

## 8. Tenant Data Export

- Full export bundle (Parquet + JSONL + audio) via async job → signed S3 URL.
- Includes: agents, versions, tools, KB, sessions, transcripts, audio (if retained), usage.
- On-demand + automatic on tenant deletion.
- Portable schema documented in `docs/EXPORT_SCHEMA.md` (created when feature ships).

## 9. Cost Attribution

- Every event carries `tenant_id`.
- `usage_records` table + ClickHouse aggregate produce per-tenant unit economics.
- Internal infra cost allocated via K8s namespace tags + Kubecost → per-tenant COGS.

## 10. Testing Multi-Tenancy (mandatory)

- **Tenant leakage tests** in CI:
  - Create 2 tenants; run all endpoints as A; assert zero visibility into B (data, metrics, traces, logs).
  - Fuzz `tenant_id` in every request.
- RLS regression tests: drop `SET app.tenant_id` and assert queries fail.
- Chaos test: revoke tenant KMS key → assert graceful denial, no data leak.

## 11. Anti-Patterns Rejected

- ❌ Global caches keyed by non-tenant keys.
- ❌ Shared LLM prompt caches across tenants.
- ❌ Metrics labels without `tenant_id`.
- ❌ Logs missing `tenant_id` correlation.
- ❌ Any admin backdoor that bypasses RLS without audit.

## 12. Assumptions
- We commit to Postgres RLS as the primary isolation mechanism — trust its correctness, but verify via automated tests.
- Dedicated tier's operational overhead is amortized over Enterprise price points.
- On-prem/VPC tier requires SRE-consulting revenue; not intended for scale by count.
