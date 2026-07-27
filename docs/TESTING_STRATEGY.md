# TESTING STRATEGY

## 1. Testing Pyramid (Adapted for AI Systems)

```
                ┌──────────────────────────┐
                │   Human review + red team │   (weekly, sampled)
                ├──────────────────────────┤
                │  Live prod eval (5%)      │  (continuous)
                ├──────────────────────────┤
                │  Full agent eval suites   │  (nightly + on publish)
                ├──────────────────────────┤
                │  E2E scenarios (Playwright + voice sim)  │
                ├──────────────────────────┤
                │  Contract tests (OpenAPI + proto)         │
                ├──────────────────────────┤
                │  Integration tests (real deps in docker)  │
                ├──────────────────────────┤
                │  Unit tests (fast, deterministic)         │  (foundation)
                └──────────────────────────────────────────┘
```

## 2. Unit Tests

- Framework: **pytest** (Python), **Vitest** (TS), **testing** (Go).
- Coverage floor **80% branch** on new/changed code (enforced on PR).
- Property-based (`hypothesis`, `fast-check`) for parsers/validators.
- Snapshot tests for prompt composers + guardrail outputs.
- Time frozen (`freezegun`, `sinon.useFakeTimers`).
- Random seeded.

## 3. Integration Tests

- Real Postgres/Redis/Qdrant/Redpanda/Temporal via **testcontainers** (Python + TS).
- Wiremock for HTTP providers (LLM, STT, TTS, Twilio, WhatsApp) with recorded fixtures.
- Migration replay tested (`up`, `down`, `up`).
- Multi-tenant leakage tests (create 2 tenants; assert isolation across every endpoint).
- RLS regression: attempt query without `SET app.tenant_id` → must fail.

## 4. Contract Tests

- **OpenAPI**: `schemathesis` fuzzes every endpoint against spec.
- **gRPC**: **buf breaking** vs. main branch; blocked if breaking without major version bump.
- **Events**: schema registry (Buf/Confluent) with compat mode BACKWARD; producer tests confirm event shapes.

## 5. End-to-End (E2E)

- **Web**: Playwright (widget + console flows).
- **Voice**: custom load-gen using LiveKit + synthetic audio (or `sipp` for pure SIP).
- **Channels**: sandbox numbers/accounts (Twilio test creds, WhatsApp Cloud sandbox).
- Runs against ephemeral preview environments (per PR).

## 6. AI-Specific Testing (Evals)

### 6.1 Golden Set Evals
- Per agent: 50–500 canonical conversations with expected outputs / decision points.
- Formats:
  - **Turn-level**: given prior context + user input, expected intent + slot values + tool call.
  - **Session-level**: multi-turn scripts with checkpoints.
- Run: nightly + on every agent version publish (blocking).

### 6.2 LLM-as-Judge Rubrics
- Judged dimensions (per vertical):
  - Correctness / task completion
  - Groundedness (RAG citations supported)
  - Tone / persona adherence
  - Safety (no PII leak, no policy violation)
  - Refusal appropriateness
- Judge model: stronger than production model (e.g., GPT-4o or Claude Sonnet).
- **Prompt for judge is versioned** — same rubric across time enables trend analysis.

### 6.3 Classifier Judges
- Cheap deterministic checks: intent-correct, entity extraction accuracy, PII redaction rate.
- Ideal for regressions.

### 6.4 Prod Sampling
- 5% of prod sessions auto-scored.
- Deltas vs. golden-set signals drift (data or model).

### 6.5 Red-Teaming
- Prompt-injection suite: gadgets from OWASP LLM Top-10 + adversarial datasets.
- Jailbreak attempts library maintained; run before every model swap.
- Human red-team: quarterly focused campaigns.

### 6.6 Voice-Specific Evals
- **WER (Word Error Rate)** on curated audio.
- **Barge-in accuracy** (true-positive / false-positive).
- **MOS estimate** on TTS.
- **Latency percentiles** enforced in load tests.

## 7. Performance Tests

- **k6** for HTTP/WS; **Locust** for scenario mixes; **wrk2** for tight latency benchmarks.
- Voice load: synthetic caller pool at target concurrency; measure turn latency p50/p95/p99.
- Weekly regression against staging; results archived.
- **Load profiles**:
  - Steady-state (baseline capacity)
  - Spike (2x sudden burst)
  - Soak (24h sustained)
  - Chaos (with pod kills + network delays)

## 8. Chaos & Resilience

- **Chaos Mesh / LitmusChaos** experiments:
  - Kill pods (each service)
  - Add network latency (100–500 ms)
  - Partition AZs
  - Fill Redis memory
  - Kill Kafka broker
- Assertions: SLIs remain within tolerance; alerts fire correctly.
- Quarterly game days.

## 9. Security Tests

- **SAST**: Semgrep, Bandit, ESLint security, gosec on every PR.
- **SCA**: Trivy / Snyk on deps + images; block High/Critical.
- **Secret scan**: gitleaks pre-commit + CI.
- **DAST**: OWASP ZAP baseline weekly on staging.
- **Fuzzing**: parsers (KB ingestion, webhook payloads).
- **Auth tests**: attempt cross-tenant, missing scope, expired token, replay.
- **Prompt injection tests**: run before every prompt/model change (part of evals).

## 10. Data Quality Tests

- KB ingestion: schema validation, checksum idempotency, unicode/RTL/emojis, malformed docs.
- Analytics events: consumer contract tests; missing-field detection; late-arrival tolerance.

## 11. Compliance / Audit Tests

- Data residency: attempt to write EU tenant data outside EU region → must fail.
- PII redaction: audit logs contain no raw PII (grep in CI).
- Deletion cascade: after "forget me", assert no traces in PG / Qdrant / S3 within SLA.

## 12. Test Data

- Synthetic data generators per vertical (e.g., faker + industry catalog).
- No prod PII in dev/staging; anonymization pipeline for staging refresh.
- Recorded fixtures for LLM/STT/TTS responses (VCR-style) — deterministic replays.

## 13. Local Test UX

- `make test` runs unit + integration in < 3 min on laptop.
- `make eval agent=agn_...` runs agent's golden set locally.
- `make load` runs a small local voice load test.

## 14. CI Gates

| Gate | Blocking? |
|------|-----------|
| Lint / format | ✅ |
| Unit tests | ✅ |
| Integration tests | ✅ |
| Coverage floor | ✅ (on changed files) |
| Contract compatibility | ✅ |
| Security scans | ✅ (High+ blocking) |
| E2E smoke (preview env) | ✅ |
| Full E2E suite | ✅ on main, non-blocking on PR |
| Golden-set evals | ✅ on agent version publish |
| Load tests | ⏱ scheduled, non-blocking to PR |

## 15. Anti-Patterns Rejected

- ❌ Mocking your own code exhaustively (mock external boundaries, use real internal code).
- ❌ Tests that require exact LLM outputs (use judges/rubrics).
- ❌ Flaky tests tolerated in main.
- ❌ E2E as the only safety net (feedback loop too slow).
- ❌ Coverage as a vanity metric without meaningful assertions.

## 16. Assumptions
- LLM outputs will always vary; we test **behavior** not **exact tokens**.
- Judges add latency + cost; sample judiciously in prod.
- Voice testing infrastructure requires investment early — otherwise voice UX regressions go unnoticed until a customer call.
