# PRODUCT REQUIREMENTS

## 1. Personas

| Persona | Goal | Primary Surface |
|---------|------|-----------------|
| **Agent Builder** (non-technical ops) | Configure an AI Employee from a template | Console UI |
| **Developer** | Extend agents with custom tools, host on own infra | SDK + API |
| **Admin** | Manage tenants, users, roles, billing, compliance | Console UI |
| **Reviewer / QA** | Review conversations, label, run evals | Console UI |
| **End User** (caller/chatter) | Get their task done | Voice, Chat, WhatsApp, etc. |
| **Integrator** (ISV/SI) | White-label the platform | API + Multi-brand config |

## 2. Functional Requirements

### 2.1 Agent Design
- Visual **flow + prompt hybrid** designer (like Retell + Voiceflow).
- Version control for agents (git-like semantics; every change is a versioned artifact).
- Vertical **templates** (Support, Sales, Restaurant, Medical, RE, HR, Booking, Collections, Insurance, Manufacturing, Legal, Finance).
- **Persona config**: voice, language, tone, guardrails, refusal policies.
- **Knowledge**: upload PDFs, DOCX, URLs, Notion, Google Drive, Confluence; auto-chunk + index.
- **Tools**: HTTP, SQL, gRPC, Zapier, webhooks, MCP servers, custom Python/JS.
- **Guardrails**: PII redaction, topic allow/deny, output filters, safety classifiers.

### 2.2 Channels (all channels use same agent config)
| Channel | Latency Target | Notes |
|--------|---------------|------|
| Voice (SIP/PSTN) | < 700 ms p50 turn | Inbound + outbound |
| Voice (WebRTC) | < 500 ms p50 turn | For web/mobile SDK |
| Web Chat | < 1.5 s p50 | Embeddable widget + iframe |
| WhatsApp | < 3 s p50 | Meta Cloud API |
| SMS | < 5 s p50 | Twilio, MessageBird |
| Email | < 60 s p95 | IMAP/SMTP + SES/SendGrid |
| Slack | < 3 s | Slack bot |
| MS Teams | < 3 s | Bot framework |
| Public API | < 500 ms | REST + SSE + WS |

### 2.3 Conversation Engine
- **Streaming everywhere** (STT partials, LLM token stream, TTS chunked, tool results streamed back).
- **Interruption handling** (barge-in, backchanneling) on voice.
- **Multi-turn state** with typed variables and slot filling.
- **Handoff** to human (warm transfer for voice, thread claim for chat) with full context.
- **Multilingual**: auto-detect + translate; per-agent language whitelist.
- **Memory**: short-term (session), long-term (per end-user), episodic (per org).

### 2.4 Tool Calling
- OpenAPI import → auto-generate tools.
- **MCP (Model Context Protocol)** first-class support.
- Sandboxed execution (gVisor/Firecracker) for custom code.
- Per-tool auth vaults (OAuth, API keys, mTLS).
- Idempotency + retry policies.

### 2.5 Observability & Evals
- Full **distributed trace** per conversation turn (OpenTelemetry).
- Live transcript viewer with replay.
- **Eval harness**: golden set, LLM-as-judge, regression on every agent version.
- Sentiment, intent, resolution, containment metrics.
- Configurable **alerting** (PagerDuty, Slack, webhooks).

### 2.6 Admin & Governance
- Organizations → Workspaces → Projects → Agents.
- RBAC with fine-grained scopes; SSO (SAML 2.0, OIDC), SCIM provisioning.
- Audit log for every mutating action.
- **Data residency** selection (US, EU, IN) per workspace.
- Per-tenant encryption keys (BYOK via AWS KMS / GCP KMS / HSM).

### 2.7 Billing & Metering
- Usage-based: minutes (voice), messages (chat), tokens (LLM), tool calls, storage.
- Stripe billing; enterprise invoicing; prepaid credits; per-tenant quotas.
- Real-time usage dashboards; hard/soft caps.

## 3. Non-Functional Requirements

| Category | Target |
|---------|--------|
| **Availability** | 99.95% control plane, 99.99% data plane per region |
| **Latency (voice turn)** | p50 < 700 ms, p95 < 1200 ms, p99 < 2000 ms |
| **Latency (chat turn)** | p50 < 1.5 s, p95 < 3 s |
| **Throughput** | 10,000 concurrent voice sessions, 100,000 concurrent chat sessions per region |
| **Scale** | 100,000 tenants, 1B conversations/year |
| **Durability** | 11-nines for conversation records |
| **RPO / RTO** | RPO ≤ 5 min, RTO ≤ 30 min |
| **Security** | SOC2 Type II, HIPAA-ready, ISO 27001, GDPR, PCI SAQ-A |
| **Deployability** | Single-tenant VPC deploy in ≤ 1 day |
| **Local dev** | `docker compose up` boots full stack in < 5 min |

## 4. Constraints
- Must be **cloud-agnostic** (AWS/GCP/Azure/OCI).
- Must support **air-gapped / on-prem** for regulated buyers by year 2.
- Voice pipeline must not require any single proprietary vendor (STT/TTS/LLM interchangeable).
- Every feature must be **API-first** — console consumes public APIs only.

## 5. Out of Scope (for v1)
- Model training / fine-tuning UX (v2).
- Video agents (v3).
- Native mobile SDKs (community SDKs only in v1).
- Marketplace for third-party agents (v2).

## 6. Acceptance Criteria for MVP
- One customer can build a **Restaurant Ordering** agent, connect a Twilio phone number, and take real orders end-to-end within 1 hour of signup, with transcripts, evals, and billing working.
