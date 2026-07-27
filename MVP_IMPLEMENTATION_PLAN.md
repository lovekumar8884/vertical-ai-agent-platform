# MVP IMPLEMENTATION PLAN

> This plan reads the 24 architecture docs as the **long-term vision** and answers one question: **"What is the smallest thing a real customer will pay for in 8–10 weeks, built by one founder + one engineer, that evolves into that vision without being rewritten?"**

---

## Executive Summary

**What we're building (V1):** A hosted **AI Receptionist / Appointment Booker for small clinics and dental practices**, delivered as **web chat + embeddable widget** (not voice yet), with a simple dashboard where the practice owner uploads their info, connects a calendar, and gets a live agent that answers questions and books appointments.

**Why customers will pay:** Small clinics lose 20–40% of after-hours inquiries. Front-desk staff cost $15–25/hr, are overwhelmed during peak hours, and miss messages on their website. A $199–499/month AI that captures those leads and books appointments pays for itself in a single missed booking. This is a **known, quantifiable pain** — not a speculative "AI would be cool" pitch.

**Problem V1 solves:**
1. "I lose leads that come in on my website after 5pm."
2. "My front desk is on hold; the chat widget goes unanswered."
3. "I want a bot that knows my practice, not a generic FAQ."

**First customer profile:**
- Independent dental / physio / chiropractic / small medical clinic.
- US or Canada (English; TCPA/HIPAA-lite).
- 2–10 staff, active website, uses Google Calendar or Cal.com.
- Willing to pay $199–499/month.
- Already tried a generic chatbot and hated it.

**Why they choose us:**
1. **Vertical-tuned** (understands "impacted wisdom tooth", "invisalign consult", not just FAQs).
2. **Books appointments end-to-end** (not just "let me connect you to reception").
3. **Live in a day** — upload website URL + connect calendar → done.
4. **Actually gets it right** — measurable (booking rate, resolution rate).
5. **Priced for SMB** — no "contact sales."

**The bet:** We win by shipping a single vertical to real revenue in 10 weeks, then use that runtime to add the next vertical in 2 weeks. The 24-doc architecture is the destination; this is the on-ramp.

---

## Product Scope

### Must Have (blocking V1 launch)
- Sign up + org creation + invite one teammate.
- Create an "AI Employee" (agent) from a **Receptionist template**.
- Upload knowledge: website URL crawl + 1–3 PDFs.
- Streaming web chat (SSE) + embeddable JS widget (iframe or drop-in `<script>`).
- Google Calendar connection + booking tool (create/list/cancel event).
- Conversation history + transcript view in dashboard.
- Handoff to email/SMS notification to owner when AI can't handle it.
- Basic guardrails: refusal on off-topic, PII not stored in logs.
- Stripe checkout for the one paid plan.

### Nice to Have (add only if trivially cheap)
- WhatsApp channel (Meta Cloud — 1 week; add if a design partner asks).
- Human takeover in the dashboard (owner types → sent as message).
- Sentiment / intent tags on conversations.
- Weekly email summary of conversations.

### Future (post-first customer)
- Voice (phone number + PSTN inbound).
- More verticals (real estate, restaurants, recruiting).
- Advanced RAG (reranker, hybrid search, multi-hop).
- Team roles / RBAC beyond owner+member.
- Analytics dashboards.
- API + SDK for developers.
- Marketplace / template gallery.

### Removed (from V1 scope — architecture supports adding later)
- Voice / SIP / WebRTC / LiveKit / Pipecat.
- WhatsApp, SMS, Email, Slack, MS Teams channels (except the owner-notify email).
- Multi-tenant Silo/Dedicated/VPC tiers — one Shared tier only.
- Multi-region, edge PoPs, cell architecture.
- SSO / SAML / SCIM / enterprise IAM.
- Temporal, Kafka, Istio, service mesh, Argo Rollouts.
- Kubernetes — single VPS or Fly/Render for now.
- ClickHouse, Grafana/Loki/Tempo stack — Postgres + Sentry are enough.
- Qdrant self-host — use **pgvector** on the existing Postgres.
- Vault — use Fly/Render secrets or Doppler.
- Firecracker sandboxing — no custom code tools in V1.
- MCP server exposure.
- Sub-agents, handoff to human agents beyond email/SMS notification.
- Multi-provider LLM routing beyond LiteLLM's built-in fallback.
- Eval service, LLM-as-judge, golden set automation — spreadsheet + manual review for now.

---

## Vertical Selection

Scoring 1 (worst) → 5 (best). Higher total = better V1 target for a solo team.

| Vertical | Market size | Ease of dev | Competition | Rev potential (SMB ACV) | Time to MVP | Integration complexity | Sales cycle | **Total** |
|---|---|---|---|---|---|---|---|---|
| **Restaurant ordering** | 4 | 2 (needs POS, menu logic, voice ideal) | 3 | 3 ($100–300) | 2 | 4 (POS APIs vary wildly) | 4 (fast) | **22** |
| Healthcare / clinic receptionist | 5 | 4 (chat + calendar) | 3 | 4 ($199–499) | 4 | 3 (Google Cal is easy; EHR later) | 4 (fast; owner-decision) | **27** |
| Recruitment / AI recruiter | 3 | 3 | 3 | 4 | 3 | 3 (ATS APIs) | 2 (procurement) | 21 |
| Real estate | 4 | 3 (needs listings + scheduling) | 3 | 3 ($99–299) | 3 | 3 (MLS is hard) | 3 | 22 |
| Loan collection | 3 | 2 (voice-first, regulated) | 4 | 5 | 2 | 3 | 2 | 21 |
| Customer support | 5 | 3 (need integrations) | 1 (Intercom Fin, Ada, everyone) | 4 | 3 | 3 | 3 | 22 |
| Sales SDR | 4 | 3 (voice/email ideal, CRM) | 2 (Clay/11x/artisan) | 4 | 2 | 3 | 3 | 21 |
| Appointment booking (generic) | 4 | 5 (chat + calendar only) | 3 | 3 | 5 | 5 (just Cal/Google) | 4 | 29 |

**Winner: Healthcare Receptionist for small clinics, positioned as a specialized appointment-booking + FAQ agent.**

Why this wins for us specifically:
- **Chat-first is acceptable** (patients already use web chat / SMS). No voice required in V1 → we skip the hardest architecture chapter.
- **One integration matters**: Google Calendar / Cal.com. Anything more is upsell.
- **Single owner buys the decision** — no procurement, no legal review, credit card checkout.
- **Painful, measurable ROI** ("we booked 12 extra patients this month" → renewal).
- **Adjacent vertical adjacencies** (dental → physio → chiro → vet → aesthetics) share the same runtime with only template + tool changes.
- **HIPAA is a growth-tier concern**, not a launch blocker. We stay HIPAA-light (no PHI storage beyond appointment metadata; explicit consent; no diagnosis) and add BAA when a customer needs it.

If the founder has a warm-lead network in a different vertical, **restaurant ordering (chat, not voice)** or **appointment booking (multi-vertical)** are the acceptable pivots — same runtime, different template.

---

## Architecture Simplification

Ordered per [MICROSERVICE_ARCHITECTURE.md](docs/MICROSERVICE_ARCHITECTURE.md). Verdict is for **V1**. All the "postponed" items are compatible with the long-term docs — we just don't build them yet.

| Long-term service | V1 verdict | How it's handled in V1 |
|---|---|---|
| `gateway` | **MERGE into monolith** | FastAPI app handles auth + rate limit + routing. No Envoy. |
| `realtime-gateway` | **POSTPONE** | No voice. SSE + WebSocket served from the FastAPI monolith. |
| `orchestrator` | **MERGE** | A `sessions` module inside the monolith. |
| `agent-runtime` | **KEEP (as module)** | LangGraph state machine as a Python package inside the monolith. Same code we'd extract to a service later. |
| `llm-router` | **KEEP (as LiteLLM proxy or SDK)** | Use LiteLLM as a **library** in-process. Upgrade to proxy service in Sprint 5+. |
| `tool-executor` | **MERGE + simplify** | In-process tool calls (HTTP + built-ins). No sandbox, no custom code, no Firecracker. |
| `memory` | **SIMPLIFY** | Short-term in Redis (session state); "long-term facts" = a `contacts` table. No Qdrant-based episodic memory. |
| `knowledge` | **MERGE + simplify** | In-process ingestion: URL + PDF → chunk → embed (OpenAI) → **pgvector**. No Qdrant, no reranker, no contextual chunking. |
| `channels-*` | **REMOVE except web-widget** | Only the web widget channel. WhatsApp/etc. as Sprint 3+ additions. |
| `billing` | **SIMPLIFY** | Stripe Checkout + webhook → set `plan` on org. No metering. |
| `analytics` | **REMOVE** | Postgres queries for a "conversations" list. No ClickHouse. |
| `eval` | **REMOVE** | Manual review in a spreadsheet. Golden set as a folder of JSON. |
| `admin/iam` | **MERGE + simplify** | Users, orgs, memberships, API keys in Postgres. Roles = owner/member. |
| `notifier` | **SIMPLIFY** | Resend/Postmark for transactional email. No worker service. |
| `connector-mgr` | **SIMPLIFY** | Google OAuth flow directly; tokens in Postgres (encrypted column). |

**Deleted infra:**
- Kubernetes, Istio, Argo CD, Argo Rollouts, KEDA, Karpenter, Vault, Kafka/Redpanda, Temporal, Prometheus/Grafana/Tempo/Loki stack, ClickHouse, Qdrant, MinIO (use S3), OPA sidecars.
- Multi-region, cells, edge PoPs.

**V1 runtime footprint:**
- **1 FastAPI monolith** (`services/api`) doing gateway + auth + orchestrator + runtime + tools + KB + memory + billing hooks.
- **1 Next.js app** (`apps/console`).
- **Postgres** (with `pgvector`).
- **Redis** (sessions, rate limits, SSE fanout).
- **S3** (KB file storage; can use Cloudflare R2 for zero egress).
- Deployed on **Fly.io** or **Render** or a single VPS (Docker Compose behind Caddy). No Kubernetes.
- **Sentry** for errors. **PostHog** for product analytics. **Logtail/Axiom** for logs.

---

## Technology Decisions

| Area | V1 decision | Why | Long-term (per TECH_STACK) | When to move |
|---|---|---|---|---|
| App framework (backend) | **FastAPI** (Python 3.12) | Best AI ecosystem, async, OpenAPI free | Same | — |
| Frontend | **Next.js 15 + shadcn/ui + Tailwind** | Fast build, hire-friendly | Same | — |
| Agent runtime | **LangGraph** (library) | Matches long-term choice | Same | — |
| LLM router | **LiteLLM as SDK** | 30 min to integrate; provider portability | LiteLLM proxy | Sprint 6+ or when you need per-tenant budgets |
| Primary LLMs | **GPT-4o-mini + Claude 3.5 Haiku fallback** | Cheap, fast, capable enough | Multi-provider with fine-tunes | After 100 customers |
| Embeddings | **OpenAI text-embedding-3-small** | Cheap, good, one API | 3-large / BGE-M3 | Sprint 6 or when quality bites |
| Vector store | **pgvector on Postgres** | Zero ops; one DB for everything | Qdrant | Move at ~10M chunks or when hybrid+reranker becomes bottleneck |
| OLTP | **Postgres (managed: Neon or Supabase or Render PG)** | One click; branching; backups | Same | — |
| Cache/queues | **Redis (Upstash or Render Redis)** | Sessions, SSE fanout, rate limits | Redis Cluster | Sprint 8+ |
| Object storage | **Cloudflare R2** (or S3) | R2 = no egress fees for KB downloads | S3 | — |
| Auth | **Clerk** (or Supabase Auth) | Save 3 weeks; SSO+SCIM ready later | WorkOS / Ory | Move to WorkOS when a customer demands SAML |
| Payments | **Stripe** (Checkout + Billing) | Universal | Stripe + Metronome | Add Metronome at 100+ customers with usage-based |
| Emails | **Resend** or **Postmark** | Deliverability + DX | SES/SendGrid | — |
| Calendars | **Google Calendar API + Cal.com API** | Covers 80% of SMBs | Add Outlook | Sprint 3 |
| Telephony (later) | **Twilio** | Ubiquity | Twilio + Telnyx + Plivo | Sprint 8 |
| Voice pipeline (later) | **LiveKit + Pipecat** | Matches long-term | Same | Sprint 8 |
| Error tracking | **Sentry** | Standard | Same | — |
| Product analytics | **PostHog Cloud** | Free tier; funnels | Same | — |
| Log aggregation | **Axiom** or **Better Stack** | Cheap; queryable | Loki | Sprint 8 |
| CI/CD | **GitHub Actions** | Standard | Same | — |
| Deployment | **Fly.io** (primary) or **Render** | One command; global; sane pricing | Kubernetes | Sprint 10+ or when 500+ tenants |
| Feature flags | **Env vars + Postgres row** | Overkill to run Unleash | OpenFeature/Unleash | Sprint 6 |
| Secrets | **Fly/Render secrets** + **Doppler** if needed | No Vault ops | Vault | Sprint 8 |
| Observability | **Sentry + Axiom + PostHog** | 3 SaaS beats 6 open-source | OTel + Prom + Grafana | Sprint 8 |
| Message bus | **Postgres LISTEN/NOTIFY** or **Redis Streams** | Zero-ops | Kafka | When cross-service async justifies it |
| Workflows | **arq** or **RQ** (Redis-backed) | KB ingestion + notifications | Temporal | When multi-step compensating workflows appear |
| Container orchestration | **Fly.io machines** or Docker Compose on VPS | Zero K8s ops | Kubernetes | 500+ tenants or enterprise on-prem |

---

## Build vs Buy

Rule: **Buy anything a customer never sees.** Build only the differentiators (the agent runtime, the vertical templates, the KB pipeline, the console UX).

| Component | Build / Buy | Choice | Rationale |
|---|---|---|---|
| Authentication | **Buy** | Clerk | 3 weeks saved; free tier fits; SAML/SCIM available when needed |
| Payments / billing | **Buy** | Stripe (Checkout + Billing Portal) | Table stakes; never build |
| Email transactional | **Buy** | Resend | Deliverability we cannot beat |
| Vector DB | **Buy (as pgvector)** | Postgres extension | Zero ops; same DB |
| Monitoring / errors | **Buy** | Sentry | Weekend integration, high value |
| Product analytics | **Buy** | PostHog | Funnels, session replay |
| Logs | **Buy** | Axiom | Cheap, fast |
| KB parsing | **Mostly buy** | `unstructured` (OSS library) + LlamaParse/Reducto **API** for hard PDFs | Do not build a PDF parser |
| Web scraping / URL crawling | **Buy** | Firecrawl or Jina Reader | Robots.txt, JS rendering, dedup — hard to reimplement |
| Embeddings | **Buy** | OpenAI API | Cheap; batch |
| LLM routing | **Buy (as lib)** | LiteLLM | Community-maintained provider adapters |
| Voice STT | **Buy (later)** | Deepgram | Best latency/accuracy |
| Voice TTS | **Buy (later)** | ElevenLabs / Cartesia | Same |
| Telephony (later) | **Buy** | Twilio | Never build a carrier |
| Scheduling (booking logic) | **Buy** | Cal.com API + Google Calendar API | Never rebuild availability math |
| CRM integrations | **Buy later** | Merge.dev or Nango | Unified API when demand shows |
| Calendar OAuth flows | **Buy the primitive, own the UX** | `authlib` + our OAuth code; consider Nango when >3 providers | — |
| Sandbox for user code | **Postpone** | — | No custom-code tools in V1 |
| Search relevance / reranker | **Postpone** | — | Add Cohere Rerank in Sprint 5 |
| Agent runtime | **Build** | LangGraph-based | This is our product |
| Vertical templates | **Build** | Ours | Differentiator |
| Console UX | **Build** | Ours | Differentiator |
| Embed widget | **Build** | Ours | Differentiator |
| Prompt versioning | **Build (thin)** | Postgres rows | 100 lines of code |
| Eval harness | **Buy or DIY minimal** | Braintrust / Langfuse (free tier) | Do not build our own |

---

## Weekly Roadmap (10 weeks)

Assumes 1 founder + 1 engineer, working full-time. Every week ships something demoable.

### Week 1 — Foundations
**Deliverable:** Monorepo boots locally with `make dev`; anyone can sign up and see an empty dashboard; deploy pipeline lands preview URL on every PR.
- Monorepo scaffold (`services/api`, `apps/console`, `packages/shared`).
- Docker Compose (Postgres + pgvector, Redis, MinIO/R2 local, MailPit).
- Clerk auth wired end-to-end.
- FastAPI + Next.js skeleton with health checks, logging, Sentry.
- GitHub Actions: lint, test, build, Fly.io preview deploy per PR.
- Postgres schema v1: `orgs, users, memberships, api_keys, audit_log`.

### Week 2 — Hello Agent
**Deliverable:** Logged-in user creates an agent and has a streaming chat with it in the dashboard.
- Schema: `agents, agent_versions, sessions, turns`.
- LangGraph runtime with one node (prompt → LLM streaming).
- LiteLLM SDK wired to OpenAI + Anthropic (env keys).
- SSE endpoint `POST /v1/agents/{id}/chat/stream`.
- Console: "Playground" tab with streaming chat UI (shadcn `chat` primitives).
- Prompt editor (system prompt textarea + versioning on save).

### Week 3 — Knowledge (RAG v1)
**Deliverable:** Upload a PDF and paste a website URL; ask a question; answer cites the source.
- Schema: `corpora, documents, chunks (pgvector)`.
- Ingestion: URL via Firecrawl → chunk → embed → pgvector; PDF via `unstructured` (LlamaParse fallback for scanned).
- RAG node in LangGraph (retrieve top-K + prompt template with citations).
- Console: KB tab (upload, list, delete, reindex button).

### Week 4 — Tools + Booking
**Deliverable:** Agent books a real Google Calendar event through natural language.
- Tool framework (JSON-schema, in-process, HTTP + built-ins).
- Google OAuth + `calendar.readonly` + `calendar.events` scopes.
- Built-in tools: `list_availability(date_range)`, `create_booking(...)`, `cancel_booking(...)`, `send_email(...)` (Resend).
- Slot-fill node for gathering name/email/reason.
- Guardrails: max_turns, refusal on off-topic, PII redaction in logs.

### Week 5 — Embeddable Widget + First Vertical Template
**Deliverable:** Paste a snippet on a website; live chat appears; the "Clinic Receptionist" template just works.
- Public web widget (`apps/widget`) — tiny React bundle, iframe-embedded, streaming SSE.
- Public unauthenticated endpoint `POST /v1/public/widget/{agent_id}/chat/stream` with per-agent CORS + rate limits.
- Widget config: color, greeting, position, avatar.
- **Vertical template**: `clinic_receptionist` (YAML agent spec + starter prompts + FAQ template + booking tool + evals seed).
- Owner-notify email when agent triggers handoff.

### Week 6 — Billing + Onboarding
**Deliverable:** A stranger can sign up, install, connect calendar, and pay us — with zero human involvement.
- Stripe Checkout + Billing Portal + webhook → set `plan` + `stripe_customer_id`.
- Trial (14 days) → convert flow.
- Onboarding wizard: create org → pick template → upload KB → connect calendar → install widget → done.
- Basic quotas (messages/month) enforced at chat endpoint.

### Week 7 — Design-Partner Polish
**Deliverable:** 3 design-partner clinics live; conversations flowing; issues logged.
- Conversations tab: list, filter, view transcript, listen to owner-notify log.
- Handoff tab: pending items owner needs to respond to.
- Manual "take over" (owner types a reply → shown as agent message).
- Small eval loop: Langfuse traces + a Notion-based golden-set doc.
- Fix top 10 things design partners complain about.

### Week 8 — Reliability + Small-Ops
**Deliverable:** Runs unattended for 72h without an owner complaint.
- Uptime monitoring (Better Stack / UptimeRobot).
- Sentry alerts + PagerDuty (or Slack alerts on-call).
- Backups + weekly restore drill (script + confirmation email).
- Read-only status page.
- Rate limits + abuse guardrails on public widget endpoint.
- Basic runbook doc (5 pages).

### Week 9 — First Paying Customers
**Deliverable:** 3–5 paid customers at $199–$499/mo. First $1k MRR.
- Landing page + pricing page + docs (Docusaurus or Mintlify).
- Convert design partners to paid.
- Cold outreach + community posts to book 15 clinic demos.
- Two-vertical proof: spin up `dental_receptionist` template in one day using existing runtime.

### Week 10 — Prove Repeatability + Roadmap
**Deliverable:** 5–10 paying customers; second vertical template shipped; investor-ready data room.
- Add second vertical (physio or aesthetics clinic template).
- Basic analytics for owner: bookings/week, top questions, containment %.
- Metrics dashboard for us: MRR, activation rate, D7 retention, CSR.
- One-page metrics summary + technical postmortem of what broke.

Slippage rule: **if any week slips, cut scope from that week — never push next week's Deliverable back.**

---

## Risks

### Technical
- **RAG quality** on messy clinic websites → mitigation: reranker (Cohere) in Sprint 5 if needed; template-first FAQ over pure RAG.
- **Tool-call flakiness** (Google Calendar edge cases) → mitigation: idempotency keys, dry-run mode, thorough error messages.
- **LangGraph learning curve** in Week 2 → mitigation: keep the graph tiny (3 nodes) until Sprint 3.
- **pgvector scale** — fine to millions of chunks; plan Qdrant migration when needed.
- **Prompt injection** in KB content — spotlight untrusted content; safety classifier before response.

### Business
- **Vertical mis-pick.** If clinic demos are hard to book, pivot to appointment-booking-for-services within 2 weeks. Runtime is unchanged.
- **Undifferentiated vs. Intercom Fin / Chatbase.** Counter: vertical depth + booking + priced for SMB + human onboarding.
- **Churn from underwhelming quality.** Enforce a personal onboarding call for the first 20 customers; use those to build the golden set.

### Product
- **Feature creep** from every design partner. Rule: 1 hard "no" for every 3 "not yet".
- **Widget UX misses.** Copy the best patterns from Intercom / Crisp; don't invent.

### Operational
- **Solo on-call** = burnout risk. Mitigation: uptime monitoring, deep sleep hours documented, non-critical alerts suppressed.
- **Data loss.** Backups + weekly restore drill from Sprint 8.

### Financial
- **LLM cost overrun** by chatty widget visitors. Mitigation: token caps per session, per-visitor rate limits, cheap model default.
- **Stripe fraud on trials.** Require card upfront after trial; abuse monitor on session volume.

### Legal / Compliance
- **HIPAA** — do NOT store PHI in V1. TOS explicitly excludes it. Ship BAA when a first paying customer requires it.
- **TCPA / call recording** — N/A in V1 (no voice).
- **DPA / GDPR** — publish a DPA template; use EU region only when a customer needs it.
- **AI disclosure** laws (e.g., California, EU AI Act) — bot self-identifies as AI on first message.

---

## Technical Debt (intentional shortcuts)

| Shortcut | Why acceptable now | When to fix |
|---|---|---|
| Monolith instead of microservices | 1 team; complexity kills speed | Extract voice + KB when they need independent scaling (Sprint 8+) |
| pgvector instead of Qdrant | Fine to ~10M chunks; one DB | Migrate at 10M+ chunks or when hybrid/reranker demand it |
| LiteLLM as SDK (not proxy) | Simpler ops; still portable | Move to proxy when per-tenant budgets/limits needed (~100 customers) |
| No Temporal | KB ingestion works with arq/RQ jobs | When compensating workflows or multi-hour flows appear |
| No Kafka | Postgres + Redis suffice at 1M events | When cross-service async or replay matters |
| No K8s | Fly.io scales fine to 1000s of tenants | When enterprise on-prem/VPC demanded |
| Clerk instead of WorkOS/Ory | 2 sprints saved | When SSO/SCIM required by enterprise |
| Postgres RLS not enforced in V1 (single-tenant queries via `org_id` filter) | 1 dev, careful code review | Enforce RLS by Sprint 5 — do it before growing the team |
| No sandbox for custom tools | Tools are built-in only | Add Firecracker/gVisor when we allow customer code |
| No dedicated eval service | Langfuse traces + Notion golden set | Sprint 6 when we have 100+ conversations to score |
| No multi-region | US-only | When first EU/APAC customer demands it |
| Session state in Redis only (not persisted per turn to PG) | Sessions are short; loss acceptable | Persist to PG in Sprint 4 |
| Feature flags via env + DB row | 5 flags total; overkill to add tool | Unleash when >20 flags |
| No RBAC beyond owner/member | Solo owner buyer | Add roles when a mid-market customer asks |
| Audit log logs to Postgres only | Fine for now | Immutable + hash-chain when SOC 2 fieldwork starts |

Every entry above is compatible with the long-term architecture — **no rewrites required**, just extractions.

---

## Cost Estimate (V1, monthly)

Assumes 20 paying customers × ~5k messages each = ~100k LLM calls, ~2k widget page loads/day.

| Line | V1 monthly ($) |
|---|---|
| Fly.io (2 machines api + 1 worker + 1 console) | 60 |
| Postgres (Neon Pro or Render 2GB) | 40 |
| Redis (Upstash pay-as-you-go) | 15 |
| Cloudflare R2 (KB blobs, 50GB) | 5 |
| Domain + email domain | 5 |
| **OpenAI + Anthropic** (GPT-4o-mini + Haiku, 30M in / 6M out, 100k embeddings) | 60–120 |
| Firecrawl (KB URL crawls) | 20 |
| LlamaParse (hard PDFs, 500 pages) | 5 |
| Clerk (Pro when >5k MAU) | 25 |
| Stripe fees | ~3% of MRR |
| Sentry (Team) | 26 |
| PostHog (self-serve) | 0–20 |
| Axiom / Better Stack logs | 25 |
| Resend | 20 |
| Langfuse (free tier) | 0 |
| GitHub Team | 4 |
| Google Workspace (biz email) | 12 |
| Vercel (docs site, if used) | 20 |
| Misc (Notion, Linear, 1Password) | 40 |
| **Total** | **~$400–500/mo + LLM overage** |

At $199–499 ACV × 20 customers, MRR = $4k–10k. **Gross margin 85–90% at this size.** Break-even is 3–5 customers.

---

## Success Metrics

| Milestone | Definition | Target date |
|---|---|---|
| **First working demo** | Founder demos live agent booking an appointment on a screen-share | End of Week 5 |
| **First beta customer** | Real clinic uses widget on their real site | Week 6 |
| **First paying customer** | Card charged, on paid plan post-trial | Week 8 |
| **10 paying customers** | Same | Week 12 |
| **100 paying customers** | Same | Month 8 |
| **$10k MRR** | Trailing | Month 4 |
| **$50k MRR** | Trailing | Month 9 |
| **$100k MRR** | Trailing | Month 12 |

**Leading indicators (weekly review):**
- Demos booked / week (target ≥ 8 by Week 8)
- Demo → trial conversion (target ≥ 40%)
- Trial → paid conversion (target ≥ 25%)
- Activation rate (widget installed + calendar connected within 24h) (target ≥ 60%)
- **Containment rate** (% conversations resolved without owner intervention) (target ≥ 70%)
- **Booking rate** (% chat sessions ending in a scheduled event) (target ≥ 15%)
- D30 retention (target ≥ 85%)

**Vanity metrics we ignore:** GitHub stars, Twitter followers, "AI" mentions in trade press, LLM latency below 300 ms (chat is not voice), model benchmarks.
