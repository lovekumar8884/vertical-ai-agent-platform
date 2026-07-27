# BACKLOG (Sprint 2 → V1.0)

Rules:
- Every sprint = 2 weeks, ships something demoable, has a **single headline outcome**.
- Sprints are ordered by learning value + revenue proximity, not by technical elegance.
- Anything not listed here is out of scope until V1.1.
- Move items **up** only if a paying customer blocks on it.

---

## Sprint 2 — Knowledge Base (RAG v1)
**Headline:** An agent answers questions grounded in files and website content the user uploaded.

- KB schema: `corpus`, `document`, `chunk (pgvector)`.
- Ingestion worker (arq/RQ on Redis): URL crawl via **Firecrawl**, PDF/DOCX via **`unstructured`** (fallback **LlamaParse** for scanned).
- Recursive char chunker (1000 tokens, 100 overlap); title/heading metadata captured.
- Embeddings via OpenAI `text-embedding-3-small` (batch).
- Retrieval: pgvector top-K (k=6) with `org_id` filter.
- RAG node in LangGraph: retrieve → assemble prompt with citations `[1] [2]` → answer.
- Console: **Knowledge** tab (upload files, add URLs, list/delete/reindex; per-doc status).
- Playground shows retrieved snippets used per turn (for debugging).
- OpenAPI generation pipeline live; `packages/shared-ts` regenerates types on `make openapi`.

**Exit:** Upload a PDF and a URL → ask a question → grounded answer with citations.

---

## Sprint 3 — Public Web Widget
**Headline:** Paste one `<script>` tag on any site → live streaming chat with the agent.

- `apps/widget` built with Vite → tiny loader `.js` + iframe React app.
- Public API `POST /v1/public/widget/{agent_id}/chat/stream` (SSE, unauthenticated, per-agent CORS whitelist, per-IP rate limit).
- Anonymous **end-user** identity: signed cookie with rotating ID (fingerprint fallback).
- Widget config in console: primary color, greeting, position, avatar, allowed domains.
- Install instructions page with copy-paste snippet + Wordpress/Shopify tips.
- Session-level guardrails: max turns, max tokens, refusal on off-topic per system prompt.
- Sentry + PostHog on widget bundle.

**Exit:** Founder installs the widget on their landing page; a stranger has a real chat.

---

## Sprint 4 — Tools + Calendar Booking
**Headline:** Agent books a real Google Calendar event during a chat.

- Tool framework:
  - Declarative YAML tool spec (JSON Schema params, HTTP kind).
  - Runtime validation, retries (tenacity), circuit breaker per tool.
  - Tool trace in session view.
- Google OAuth via `authlib`; store refresh token encrypted at rest.
- Built-in tools:
  - `list_availability(date_range)`
  - `create_booking(datetime, name, email, reason)`
  - `cancel_booking(booking_id)`
  - `send_email(to, subject, body)` via Resend
  - `notify_owner(message)` — email/SMS placeholder (email only in this sprint)
- Slot-fill node for gathering booking fields.
- Console: **Connections** page (connect Google Calendar); **Tools** panel per agent (enable/disable).
- Vertical template `appointment_booking` (generic) shipped.

**Exit:** Real appointment placed on a real Google Calendar via chat.

---

## Sprint 5 — First Vertical + Multi-Tenant Correctness
**Headline:** `clinic_receptionist` template used by 3 design-partner clinics; app is provably tenant-safe.

- Vertical `clinic_receptionist`:
  - Persona + system prompts (per language).
  - Preloaded FAQ prompts (insurance, hours, address, cancellation policy).
  - Tools: booking, FAQ retrieval, handoff-to-owner.
  - Seeded eval set (10 golden conversations).
- Template gallery in console (choose template on agent create).
- **Postgres RLS enabled** on `org_id` for all tenant tables.
- `TenantScopedSession` wrapper enforced; lint rule bans raw connections.
- Cross-tenant leakage test added to CI (create 2 orgs, run every endpoint as A, assert zero visibility into B).
- LLM router upgraded: LiteLLM proxy sidecar in the API pod with per-org token quotas + fallback chain.
- Session state persisted to Postgres after every turn (not just Redis).

**Exit:** 3 clinics have widgets live. Automated leakage tests pass. RLS enforced.

---

## Sprint 6 — Billing + Onboarding
**Headline:** A stranger goes from `signup → paid` with zero human involvement.

- Stripe Checkout + Billing Portal + customer-portal link.
- Webhook: `checkout.session.completed`, `customer.subscription.updated`, `invoice.paid`, `invoice.payment_failed` → set org `plan` + `stripe_customer_id`.
- Plans: `free (trial, 14d)`, `starter ($199)`, `growth ($499)` — differ by message quota + KB size + agents.
- Quota enforcement at chat endpoints with soft/hard caps.
- Onboarding wizard: create org → pick template → upload KB → install widget → connect calendar → book demo call slot with founder.
- Basic transactional emails (Resend): welcome, trial ending, payment failed.
- Landing + pricing pages (`apps/landing`).

**Exit:** First self-serve paid customer (cold traffic → subscribed).

---

## Sprint 7 — Reviewer Console + Basic Evals
**Headline:** Founder can review conversations, tag problems, and see quality trends per agent version.

- Conversations tab v2: filters (date, channel, contained/handoff), search, sentiment tag.
- Transcript viewer: prompt state per turn, retrieved snippets, tool calls, model, tokens, latency.
- Tag conversations (good/bad/needs-fix); promote to golden set.
- **Langfuse** (free tier) wired for LLM tracing.
- Eval runner: on agent version publish, run the golden set through the new prompt → block publish if regression on containment/faithfulness thresholds.
- Weekly quality email to org owners: "X conversations, Y bookings, Z containment %".

**Exit:** Every published agent version passed evals; reviewer console reduces "why did it say that?" debug time to seconds.

---

## Sprint 8 — WhatsApp Channel + Reliability Basics
**Headline:** Same agent, now on WhatsApp.

- Meta WhatsApp Cloud API adapter:
  - Inbound webhook → session mapping by phone → same runtime.
  - Outbound message sender (respect 24h session window; template messages).
  - Template management UI (start with 2 canonical templates).
- Owner-facing "Send this agent to WhatsApp" flow (connect a phone number).
- Message quota per WhatsApp conversation (Meta pricing awareness).
- Reliability:
  - Uptime + Sentry alerts wired to PagerDuty (or founder phone).
  - Backups: nightly Neon backup verified by automated restore-to-branch test.
  - Read-only status page (Better Stack).
  - Basic runbook (5 pages): common incidents + rollback playbook.
- Log aggregation via **Axiom**.

**Exit:** A clinic's WhatsApp Business Number replies via the agent. Runbook exists.

---

## Sprint 9 — Second Vertical + Templates Library
**Headline:** Adding a new vertical takes ≤ 1 week using the runtime; two templates ship in production.

- Vertical `dental_receptionist` (specialization of clinic).
- Vertical `real_estate_lead_qualifier` (chat-only for now).
- Template config extraction: verticals defined declaratively (`verticals/*/agent.yaml`) with prompts, tools, evals.
- Template versioning + upgrade prompts for existing tenants.
- Onboarding wizard picks up new templates automatically.
- Copy improvements to landing (per-vertical pages, SEO-oriented).

**Exit:** 2 verticals live with paying customers. Sales cycle from demo → paid < 7 days average.

---

## Sprint 10 — Voice v1 (Inbound Only, One Number)
**Headline:** A clinic can point a phone number at us; caller talks to the same agent that runs their chat.

- LiveKit self-hosted (or LiveKit Cloud) + LiveKit SIP.
- Twilio Elastic SIP trunk (US-only for now).
- Pipecat voice worker: Silero VAD + Deepgram STT + ElevenLabs TTS + our LangGraph runtime.
- Barge-in support.
- Same agent config as chat; voice-specific overrides (voice model, tone).
- Recording (optional per tenant) → R2 encrypted.
- Consent prompt on inbound (jurisdiction-aware later; hardcoded US-safe copy for now).
- Console: **Numbers** page (purchase/port, bind to agent).

**Exit:** Founder calls a US phone number, agent answers, books an appointment.

---

## Sprint 11 — Voice Polish + Outbound Campaigns (opt-in)
**Headline:** Voice quality good enough that a clinic replaces after-hours voicemail with our agent; simple outbound reminders.

- Provider fallback (Deepgram → AssemblyAI; ElevenLabs → Cartesia).
- Semantic turn detector to cut false interruptions.
- Warm transfer via SIP REFER + whisper announce.
- Basic outbound: "reminder call" tool that dials a number at a scheduled time using LiveKit outbound.
- TCPA/DNC scrubbing before dial (US-only).
- Recording UI + auto PII redaction on transcripts.
- Per-agent voice + tone + speaking rate controls.

**Exit:** A clinic uses inbound + reminder-call outbound in production. Turn latency p50 < 1 s.

---

## Sprint 12 — Analytics + Tenant-Facing Metrics
**Headline:** Owners see, in the console, what the agent is doing for them (and why they should keep paying).

- Owner analytics: bookings/week, top questions, containment rate, handoff reasons, missed opportunities.
- Basic funnels (widget-shown → chat-started → question-answered → booked).
- Materialized views in Postgres (defer ClickHouse; add only when Postgres hurts).
- Weekly email digest.
- Internal ops dashboard: MRR, activation, retention, per-agent CSR, cost per tenant (LLM + infra allocation).

**Exit:** Owners have a "renew" story they can screenshot. We can compute per-tenant unit economics.

---

## Sprint 13 — Developer API + Public SDK (v0.1)
**Headline:** A developer can build a custom widget or integrate the agent into their app via the API.

- API keys already exist (Sprint 1); document them.
- Public REST endpoints: agents (list/create/publish), sessions (create, list, get), messages (stream), knowledge (upload/list/delete).
- OpenAPI docs served via Redocly or Mintlify.
- `packages/sdk-python` v0.1 (generated + hand-polished).
- Rate limits and quotas exposed via `RateLimit-*` headers.
- Sandbox environment (`sandbox.` subdomain) with test tenants.

**Exit:** A design-partner developer builds something with the SDK end-to-end.

---

## Sprint 14 — Second Channel Pack (SMS + Email)
**Headline:** Same agent now on SMS and threaded email.

- SMS via Twilio (US inbound + outbound). Session mapping by phone.
- Email adapter (Resend inbound routing → session per thread; outbound via Resend).
- Both channels reuse existing runtime; owner enables per-agent.
- Delivery/handling metrics per channel.

**Exit:** A clinic runs one agent across web widget + WhatsApp + SMS + email.

---

## Sprint 15 — Advanced RAG + Reranking
**Headline:** Answer quality visibly improves; retrieval hit@5 > 90% on our eval set.

- Hybrid retrieval: pgvector + Postgres `tsvector` BM25 with RRF fusion.
- **Cohere Rerank v3** on top-30 → top-6.
- Contextual chunk enrichment (LLM-generated chunk summaries) for professional corpora.
- Multi-query rewrite for ambiguous questions.
- Grounding check post-generation; refuse if not supported.
- Per-vertical retrieval tuning saved in template.

**Exit:** Eval hit@5 crosses target; owner reports fewer wrong-answer complaints.

---

## Sprint 16 — Team Roles + Basic RBAC + Audit
**Headline:** Multi-user orgs work like customers expect; every mutating action is auditable.

- Roles: owner, admin, developer, reviewer, member.
- Scopes wired at API layer (simple decorator; upgrade to OPA later).
- Audit log surfaced in console (settings → activity).
- Member invitation flow (Clerk Organizations).
- Per-agent permissions (who can publish).

**Exit:** A 5-person clinic team uses roles correctly; audit satisfies mid-market sales conversations.

---

## Sprint 17 — Reliability + Load + Ops Maturity
**Headline:** We can sustain 200 concurrent conversations + 50 concurrent calls without a founder-in-the-loop.

- k6 load harness (chat) + voice load-gen (LiveKit + synthetic audio).
- Autoscaling on Fly (or migration to Render autoscale groups).
- Redis Streams for message fan-out (upgrade path from LISTEN/NOTIFY).
- Postgres partitioning on `session`, `turn` by month (pg_partman).
- Runbooks expanded (SEV1–SEV4); PagerDuty on-call.
- Chaos experiment: kill API pod during live chat; verify graceful degradation.

**Exit:** Load target sustained for 24h in staging. Two SEV3+ incidents resolved from runbooks.

---

## Sprint 18 — Long-term Memory + Contact Profiles
**Headline:** Returning end-users are recognized; agent remembers what matters.

- Contact profiles (per end-user, per org): normalized identity (phone/email hash).
- Long-term fact extractor (async job after session close; strict JSON schema).
- Console: contact profile view + editable facts + "forget me" API.
- Episodic memory later (only if needed): postpone Qdrant migration to V1.1.

**Exit:** Returning caller in a demo is recognized by name and past bookings.

---

## Sprint 19 — Compliance Foundation (SOC 2 Type I prep)
**Headline:** We can start SOC 2 fieldwork; enterprise conversations are unblocked.

- Vanta or Drata connected; evidence collection automated.
- Security policies documented (access, incident response, change management).
- Access review process (monthly).
- Backup restore drill formalized (monthly).
- Sub-processor list + DPA template published.
- BAA offering (HIPAA-light) drafted for healthcare vertical.

**Exit:** SOC 2 Type I fieldwork scheduled; first BAA signed.

---

## Sprint 20 — V1.0 Release
**Headline:** Public launch. 50+ paying customers. 2 verticals dominant.

- Marketing site polished; case studies (3+).
- Public pricing (starter / growth / scale).
- Referral program.
- Product Hunt / HN launch.
- Docs, SDK, and API stable v1.
- Internal metrics dashboard shows MRR, churn, CSR trending healthy.
- Postmortem: what we cut, what we regret cutting, what we won't build.

**Exit:** V1.0 tagged. Fundraise-ready metrics deck exists.

---

## Post-V1 (deferred, in priority order)

- Voice edge PoPs (multi-region voice).
- MS Teams + Slack channels.
- MCP server exposure.
- Enterprise SSO (WorkOS SAML/OIDC + SCIM).
- Dedicated tier provisioning (Temporal workflow).
- Multi-region data plane + data residency (EU, IN).
- Qdrant migration + advanced RAG (GraphRAG, agentic).
- Custom-code tools (Firecracker sandbox).
- Fine-tuning per vertical (LoRA on hosted vLLM).
- Marketplace (third-party templates + tools).
- Mobile SDKs.
- Kubernetes migration (only when Fly.io hurts).

Each of these is already blueprinted in [docs/](docs/) — the runtime and data model do not need to be rewritten to add them.
