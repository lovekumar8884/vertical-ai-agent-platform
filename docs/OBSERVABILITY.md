# OBSERVABILITY

## 1. Pillars

1. **Traces** — every conversation turn is a distributed trace (OpenTelemetry).
2. **Metrics** — SLIs at every layer (Prometheus + OpenMetrics).
3. **Logs** — structured JSON, correlated by IDs (Loki/Elasticsearch).
4. **Events** — business events on Kafka → ClickHouse for analytics.
5. **Evals** — quality signals produced by automated + human review.
6. **Session Replay** — reconstruct any conversation deterministically.

## 2. OpenTelemetry Standard

- All services auto-instrumented via OTel SDKs (Python, Node, Go).
- Custom spans for domain operations: `agent.turn`, `llm.call`, `tool.invoke`, `kb.retrieve`, `stt.stream`, `tts.stream`.
- **Semantic conventions** followed; extensions under `vsa.*` namespace.
- Propagation via W3C `traceparent` across HTTP/gRPC/Kafka (header injected in Kafka message headers).
- **Sampling**: head-based 10% + tail-based (always sample errors, slow spans, PII refusals).
- Exporter → OTel Collector → Tempo/Jaeger (traces), Loki (logs), Prometheus (metrics).

### Standard span attributes
```
vsa.tenant_id
vsa.workspace_id
vsa.agent_id
vsa.agent_version
vsa.session_id
vsa.turn_id
vsa.channel
vsa.model
vsa.tokens_in / vsa.tokens_out
vsa.cost_micros
vsa.latency_bucket
```

## 3. Metrics (SLIs)

### 3.1 Platform SLIs
| Metric | Target |
|--------|--------|
| Voice turn latency p50 / p95 / p99 | 700 / 1200 / 2000 ms |
| Chat turn latency p50 / p95 | 1.5 / 3 s |
| Session start success | > 99.9% |
| LLM call success (post-fallback) | > 99.5% |
| Tool call success | > 98% |
| STT WER (sampled) | < 8% English |
| RAG retrieval hit@5 | > 85% on eval set |
| Uptime (control plane) | 99.95% |
| Uptime (data plane per region) | 99.99% |

### 3.2 Business Metrics
- Concurrent sessions (by channel, tenant, region)
- Turns per minute
- Conversation Success Rate (CSR) per agent per day
- Handoff rate + reason distribution
- Cost per resolved conversation

## 4. Logging

- **Structured JSON**; one line per event.
- Required fields: `ts, level, service, message, tenant_id, session_id?, turn_id?, trace_id, span_id`.
- No PII in default log stream — dedicated `pii-logs` stream with restricted access + short TTL.
- Log levels: `DEBUG` (dev only), `INFO`, `WARN`, `ERROR`, `CRITICAL`.
- Dynamic log level per service via config (feature flag).

## 5. Session Replay & Debugging

- **Trace-first debugging**: click a session → see full waterfall (audio, transcript, prompts, LLM tokens, tool calls, DB queries).
- **Time-travel**: scrub through turns; see prompt state at each step.
- **Prompt diff**: compare prompts across turns or agent versions.
- **LLM raw view**: request/response payloads (redacted per policy) accessible to authorized roles.
- **Replay run**: re-execute a session against a new agent version → diff outputs.

## 6. Alerts

- **Golden signals** alerts per service: latency, traffic, errors, saturation.
- **Multi-window multi-burn** SLO alerts (Google SRE style).
- **Anomaly detection** on business metrics (Sudden CSR drop → page on-call).
- Delivered via: PagerDuty (P1/P2), Slack (P3/P4), email (informational).
- **Runbook link** attached to every alert (mandatory).

## 7. Dashboards

Built in Grafana; per-tenant + platform-wide:

- **Ops Dashboard**: SLIs, error rates, saturation.
- **Voice Dashboard**: concurrent calls, turn latency histogram, barge-in rate, provider health.
- **LLM Dashboard**: TPS per model, cost per tenant, fallback frequency.
- **KB Dashboard**: retrieval quality, ingestion queue depth.
- **Tenant-facing Dashboard**: sessions, minutes, tokens, spend, CSR — self-serve.
- **Cost Dashboard**: Kubecost + LLM spend allocated per tenant.

## 8. Eval Pipeline (Quality Observability)

- **Golden set** per agent (curated conversations with expected outputs).
- **LLM-as-judge** for open-ended metrics (helpfulness, faithfulness, tone).
- **Classifier judges** for closed metrics (intent correct, PII refused).
- **Continuous evals**:
  - Nightly full suite per agent
  - On every agent version publish (blocking check)
  - Random sample from prod (5%) with judge scoring
- Results in `eval_runs` table → dashboards + regression alerts.
- **Human-in-the-loop**: reviewer console for tagging + escalating.

## 9. Correlation IDs

- **`request_id`** — HTTP request unique.
- **`session_id`** — one conversation.
- **`turn_id`** — one turn.
- **`trace_id`** — OTel trace = usually 1:1 with turn.
- **`end_user_ref`** — hashed if PII.
- All logged + returned in response headers for user-side correlation.

## 10. Tooling Stack

| Layer | Primary | Fallback |
|-------|---------|---------|
| Traces | Tempo / Jaeger | Datadog APM |
| Metrics | Prometheus + Thanos | Datadog / New Relic |
| Logs | Loki (small) → Elasticsearch/OpenSearch (large) | Datadog Logs |
| Analytics events | Kafka → ClickHouse | Snowflake |
| Error tracking | Sentry | Rollbar |
| Uptime | Grafana Synthetic Monitoring + StatusCake | UptimeRobot |
| Product analytics (console) | PostHog (self-host) | Amplitude |

## 11. Retention

| Type | Retention |
|------|----------|
| Traces (sampled) | 14 days |
| Traces (error/PII refusal) | 90 days |
| Metrics (1m resolution) | 15 days |
| Metrics (5m + 1h rollups) | 400 days |
| Logs (INFO) | 14 days |
| Logs (ERROR/audit) | 400 days |
| Events (hot) | 90 days ClickHouse |
| Events (cold) | 2 years S3 (Iceberg / Parquet) |

## 12. Privacy in Observability

- PII scrubbing at the collector level (OTel processors).
- Sensitive attributes hashed with tenant salt before leaving service boundary.
- Access to raw transcripts/traces restricted by RBAC + step-up auth.
- All access to production observability tools is audited.

## 13. Anti-Patterns Rejected

- ❌ Logging entire LLM prompts by default.
- ❌ Alert fatigue (page on symptoms, not causes).
- ❌ Metrics without `tenant_id` label (blind to noisy neighbors).
- ❌ Sampling errors away.
- ❌ Custom logging format per service.

## 14. Assumptions
- OpenTelemetry ecosystem maturity is sufficient (Python voice pipeline instrumentation is the weakest link — we contribute back).
- Loki cost/perf holds up to ~1 TB/day; migrate to Elastic beyond that.
- Tail-based sampling (via Grafana Agent / OTel Collector) required for cost control.
