# ROADMAP

Milestone-based, MVP → Enterprise Scale. Rough calendar quarters; sequence is the contract, dates flex.

Assumptions: ~10 engineers (mixed backend/AI/frontend/SRE) at start, growing to ~30 by end of Year 1.

---

## Phase 0 — Blueprint & Foundations (Weeks 1–4)

**Outcome**: Repo, CI, infra baseline, single "hello world" agent over web chat.

- [ ] Monorepo scaffold (`services/*`, `packages/*`, `apps/*`, `infra/*`).
- [ ] CI: lint, test, build, image sign, SBOM.
- [ ] Infra baseline (Terraform): VPC, EKS, RDS Postgres, ElastiCache Redis, S3, Vault, ArgoCD.
- [ ] Auth service (WorkOS integration) + tenant/user schema.
- [ ] API Gateway (Envoy) + gRPC scaffold with mTLS.
- [ ] OpenTelemetry Collector + Grafana/Tempo/Loki/Prometheus.
- [ ] Docs site + this documentation set published internally.
- [ ] Local dev experience (`make dev` boots stack < 5 min).

**Exit criteria**: `curl` a `POST /v1/agents/hello/chat` from a test tenant and see a streamed response from GPT-4o-mini, with a trace visible in Tempo.

---

## Phase 1 — MVP: One Vertical, Two Channels (Weeks 5–14)

**Outcome**: Real customer can build a **Restaurant Ordering** agent, deploy on **Web + Voice (WebRTC + PSTN)**, and take real orders.

### Workstreams
1. **Agent Runtime** (LangGraph): prompt/classify/slot_fill/tool_call/handoff nodes; streaming; state persistence.
2. **LLM Router** (LiteLLM proxy): OpenAI + Anthropic + Groq; fallbacks; per-tenant budgets.
3. **Tool Executor**: HTTP + builtin + OpenAPI import; Vault-based connections.
4. **Knowledge Service (RAG)**: file/URL ingest, chunk, embed (OpenAI 3-large), Qdrant, hybrid retrieval, reranker (Cohere).
5. **Memory**: short-term (Redis), long-term facts skeleton.
6. **Voice Pipeline**: LiveKit + Pipecat; Deepgram Nova STT; ElevenLabs Turbo TTS; barge-in; SIP inbound via LiveKit SIP; Twilio trunk.
7. **Web Chat Widget**: Embeddable JS, dark/light, transcripts, file upload.
8. **Console (Next.js)**: Agent designer (form + JSON), KB uploader, sessions viewer, live transcript.
9. **Billing skeleton**: Stripe subscription + usage metering (minutes, tokens).
10. **Analytics**: Kafka → ClickHouse; basic dashboards (sessions, latency, cost).
11. **Vertical template**: `restaurant_ordering` (agent YAML + tools + evals + prompts).

**Exit criteria**:
- Signup → first live voice call in **< 15 minutes**.
- p50 voice turn latency **< 900 ms**.
- Eval suite passes for restaurant_ordering (CSR > 80%).
- SOC 2 evidence collection started.

---

## Phase 2 — Multi-Channel + Multi-Vertical (Weeks 15–26)

**Outcome**: 5 verticals live; 6 channels (Voice, Web, WhatsApp, SMS, Email, Slack); reviewer console; evals in CI.

- [ ] Channel adapters: WhatsApp (Meta Cloud API), SMS (Twilio/MessageBird), Email (SES/SendGrid inbound+outbound), Slack (bot + Slash), MS Teams (deferred to Phase 3).
- [ ] Handoff service: warm transfer (voice), thread claim (chat).
- [ ] Reviewer console: transcript viewer, tag/annotate, escalate to eval set.
- [ ] Eval service: golden sets, LLM-judge, blocking on publish, regressions dashboard.
- [ ] Additional verticals: Support, Sales SDR, Medical Reception, Appointment Booking, Loan Collection.
- [ ] Long-term memory (facts extractor) + episodic (Qdrant).
- [ ] MCP support (client mode) — external MCP tools discoverable.
- [ ] Feature flags (OpenFeature) live per tenant.
- [ ] Backup + restore drills passing (Postgres, Qdrant, Redis).

**Exit criteria**:
- 3 paying customers live.
- 500 concurrent sessions sustained in load test.
- SOC 2 Type I audit report issued.

---

## Phase 3 — Enterprise Readiness (Weeks 27–40)

**Outcome**: Enterprise contracts closable; MS Teams; SSO/SCIM; audit; HIPAA-ready; data residency; Dedicated tier.

- [ ] SSO (SAML + OIDC) + SCIM 2.0.
- [ ] Comprehensive audit log + SIEM export.
- [ ] Data residency (US, EU, IN).
- [ ] Dedicated tier: per-tenant DB/Qdrant/S3 provisioning workflow (Temporal).
- [ ] BYOK (customer-supplied KMS keys).
- [ ] HIPAA BAA offering; PHI-safe defaults; PII redaction defaults on.
- [ ] MS Teams adapter.
- [ ] Advanced RAG: contextual chunking, GraphRAG (opt-in), agentic retrieval.
- [ ] Human-in-the-loop moderation for regulated verticals.
- [ ] Enterprise console: workspaces, projects, granular RBAC, quotas UI.
- [ ] Public SDKs (Python, Node) v1.0 stable.
- [ ] Public MCP server (agents as MCP endpoints).

**Exit criteria**:
- 1 enterprise (>$100k ARR) signed.
- SOC 2 Type II fieldwork started.
- 2k concurrent voice + 20k chat sustained.

---

## Phase 4 — Scale, Multi-Region, Cost (Weeks 41–52)

**Outcome**: 3 regions live; blended cost per resolved conversation cut in half; auto-scaling proven.

- [ ] Multi-region deployment (US-East, US-West, EU-West).
- [ ] Regional voice PoPs (5+).
- [ ] Prompt caching + semantic cache across LLM Router.
- [ ] Vertical fine-tunes for top 3 verticals (5–10x cost cut).
- [ ] Optional on-prem inference (vLLM) for Enterprise volume.
- [ ] KEDA-driven autoscaling everywhere.
- [ ] Cell-based architecture design (implementation in Phase 5).
- [ ] Chaos engineering practice established.
- [ ] Cost dashboards per tenant; unit economics tracked.

**Exit criteria**:
- Cost per resolved conversation ≤ target for support vertical.
- 99.99% data-plane uptime last quarter.
- 10 enterprise customers.

---

## Phase 5 — Ecosystem & Advanced (Year 2)

- [ ] Marketplace: third-party agent templates, tools, voices.
- [ ] Agent Studio v2 (visual flow editor).
- [ ] Fine-tuning UX (customer datasets → hosted LoRA per vertical).
- [ ] Native mobile SDKs.
- [ ] On-prem / air-gapped tier GA.
- [ ] Additional languages (15+).
- [ ] Cell-based architecture in prod.
- [ ] ISO 27001 certified.
- [ ] FedRAMP Moderate work started (if federal pipeline exists).

---

## Phase 6 — Vertical Depth & Platform Effects (Year 3)

- [ ] Deep integrations per vertical (Epic/Cerner for medical, Salesforce Health Cloud, POS ecosystem for restaurants, LOS/BPMS for finance).
- [ ] Agent-to-agent protocols (A2A) mature.
- [ ] Real-time analytics products (co-pilot for reviewers).
- [ ] Video agent (v1).
- [ ] Auto-improvement: agents that suggest their own prompt/tool improvements from eval failures.
- [ ] $100M+ ARR trajectory.

---

## Hiring Milestone Guide

| Phase | Team size | Key hires |
|-------|-----------|----------|
| 0 | 8 | Founding backend x2, AI x2, frontend, SRE, PM, design |
| 1 | 14 | +Voice specialist, +Data eng, +Enterprise BE, +QA, +Growth eng, +SecEng |
| 2 | 22 | +Channels team (3), +Reviewer/Eval team (2), +Onboarding, +Docs |
| 3 | 30 | +Enterprise SRE, +Compliance PM, +TAM x2, +Support |
| 4 | 45 | Regional SRE, LLM infra team, cost/perf team |

## De-risking (order matters)
1. **Voice latency at p50** — attack first; kills UX if wrong.
2. **Multi-tenancy correctness** — earliest, hardest to retrofit.
3. **Eval quality** — build the ratchet before you have a mess.
4. **Cost model** — track from Day 1 (unit economics = fundraising credibility).
5. **Deployment reproducibility** — every release regressions-tested; drift kills.
