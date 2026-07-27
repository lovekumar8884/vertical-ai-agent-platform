# AI EMPLOYEE FRAMEWORK

> The technical and product blueprint for **every AI Employee** ever created on this platform. The same components. The same lifecycle. The same evaluation. Only configuration changes.

If a decision violates this framework, either the framework is wrong or the decision is. There is no third option.

---

## 1. First Principle

An **AI Employee** is not a chatbot with a system prompt. It is a versioned, evaluated, deployable software artifact with an **identity, a mission, measurable outcomes, and a lifecycle** — modeled after a real employee, priced like one, and managed like one.

If a million AI Employees exist on this platform, every one must:

- Be **configurable** by a non-technical operator.
- Share **one runtime**, one memory, one knowledge system, one tool framework — no forked codepaths per vertical.
- Be **individually versioned, evaluated, and rolled back**.
- Emit the **same metrics** so verticals are comparable.
- Be **auditable end-to-end** for compliance and debugging.
- Cost less than the human alternative to run.

Anything that requires a per-vertical branch of the runtime is rejected by design.

---

## 2. The Canonical Model

Every AI Employee is a graph of eleven pillars. Every pillar has **defaults** (from the vertical template), **overrides** (per-employee), and **audit** (who changed what).

```
                          ┌──────────────────────┐
                          │       IDENTITY        │
                          │   (name, role, dept)  │
                          └──────────┬────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │       MISSION         │
                          │ (objectives, KPIs)    │
                          └──────────┬────────────┘
                                     │
        ┌────────────┬──────────────┼───────────────┬────────────┐
        │            │              │               │            │
   ┌────▼────┐  ┌────▼────┐   ┌─────▼─────┐   ┌────▼────┐   ┌───▼────┐
   │KNOWLEDGE│  │ MEMORY  │   │ SKILLS &  │   │  TOOLS  │   │ POLICY │
   │  (KB)   │  │(3 tiers)│   │ WORKFLOW  │   │  (typed)│   │ (rails)│
   └────┬────┘  └────┬────┘   └─────┬─────┘   └────┬────┘   └───┬────┘
        │            │              │              │            │
        └────────────┴──────────────┼──────────────┴────────────┘
                                    │
                          ┌─────────▼──────────┐
                          │     PERSONALITY    │
                          │ (voice, tone, lang)│
                          └─────────┬──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │    EVALUATION      │
                          │ (evals, judges)    │
                          └─────────┬──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │  VERSION + DEPLOY  │
                          │ (channels, limits) │
                          └─────────┬──────────┘
                                    │
                          ┌─────────▼──────────┐
                          │   OBSERVABILITY    │
                          │ (metrics, traces)  │
                          └────────────────────┘
```

---

## 3. Pillar Specification

Every AI Employee is fully described by the eleven pillars below. This is the **declarative contract** the runtime reads.

### 3.1 Identity
- `name` — human-friendly ("Amelia, Front Desk Assistant").
- `role` — normalized role from a controlled vocabulary (`receptionist`, `sales_sdr`, `support_agent`, `recruiter`, `debt_collector`, …).
- `department` — grouping within the org (`front_office`, `sales`, `hr`).
- `company_binding` — tenant / org / workspace / brand it represents.
- `avatar`, `pronouns`, `handle` — presentation.

### 3.2 Mission
- `mission_statement` — one sentence ("Answer patient inquiries and book appointments 24/7, so front desk can focus on in-person care").
- `objectives[]` — measurable goals ordered by priority.
- `kpis[]` — mapping of objectives → metrics (name, unit, target, weight).
- `success_definition` — the outcome that means the employee is working (e.g., "booking created in calendar").
- `constraints[]` — hard limits ("never quote prices for procedures without a human review").

### 3.3 Knowledge (see §7)
- `corpora[]` — bound knowledge corpora (website crawl, PDFs, FAQs, structured DB).
- `retrieval_strategy` — `hybrid | vector | keyword | none`.
- `top_k`, `reranker`, `citation_required`.
- `refresh_policy` per corpus.

### 3.4 Memory (see §8)
- `short_term.window_turns` (default 20).
- `long_term.enabled` + `subject_type` (`end_user` | `account` | `org`).
- `organizational_memory.enabled` (opt-in per org).
- `retention_policy` per tier.

### 3.5 Skills & Capabilities
Skills are **named capabilities** the employee is expected to perform. Skills compose from workflow nodes + tools + prompts.
- `skills[]` (e.g., `answer_faq`, `book_appointment`, `qualify_lead`, `escalate_to_human`).
- Each skill declares: `entry_condition`, `required_tools[]`, `required_slots[]`, `success_state`, `failure_state`.
- Skills are the unit reviewers see in the console ("This employee has 4 skills; 3 passed evals, 1 failed").

### 3.6 Workflow
- `graph` — LangGraph state machine (declarative YAML per [AGENT_ENGINE.md](docs/AGENT_ENGINE.md)).
- `nodes` from the standard library (`prompt`, `classify`, `slot_fill`, `tool_call`, `rag`, `condition`, `handoff`, `end`, `custom`).
- `entrypoint`, `terminal_nodes[]`, `max_turns`, `max_tool_calls_per_turn`.

### 3.7 Tools (see §9)
- `tools[]` — bindings (tool_id + config + connection_ref).
- `parallel_calls_max`.
- Per-tool: `rate_limit`, `timeout_ms`, `idempotency`, `retry_policy`, `observability`.

### 3.8 Policies · Compliance · Guardrails
- `input_guardrails[]` (prompt-injection classifier, PII detector, topic allow/deny).
- `output_guardrails[]` (safety classifier, refusal templates, citation enforcement, hallucination check).
- `pii_redaction` — fields to redact from logs/exports (`phone`, `email`, `dob`, `mrn`, …).
- `compliance_profile` — `standard | hipaa | pci | gdpr_strict | tcpa_outbound | eu_ai_act_high_risk`.
- `escalation_rules[]` — conditions that trigger human handoff.
- `refusal_policy` — how to decline out-of-scope requests.

### 3.9 Personality
- `voice_style` (spoken voice, TTS voice ID, speaking rate).
- `tone` (`warm-professional`, `formal`, `friendly-casual`).
- `language` (primary + whitelist for auto-switch).
- `conversation_style` (`concise` / `explanatory` / `sales-forward`).
- `formality`, `humor_level`, `emoji_policy`.
- `signature_phrases`, `forbidden_phrases`.

### 3.10 Reasoning · Decision Boundaries · Escalation
- `reasoning_strategy` — `direct | plan_then_act | react | reflective`.
- `decision_boundaries` — actions the AI can take autonomously vs. actions requiring approval (e.g., "confirm booking autonomously," "reschedule autonomously," "cancel > 24h with human review").
- `escalation_triggers` — sentiment breach, unrecognized intent, sensitive topic, N failed clarifications, explicit user request.
- `escalation_target` — human queue, another AI Employee, external ticketing.

### 3.11 Context · Learning · Evaluation · Version · Deployment
- `context_providers[]` — dynamic context injected per session (business_hours, weather, current_promotions).
- `learning_config` — feedback capture, prompt-suggestion loop, fine-tune eligibility (opt-in).
- `evaluation` — eval suite ID + blocking thresholds (see §6).
- `version` — semantic + immutable snapshot; publish workflow.
- `deployment` — bound channels + regions + limits + cost budget.
- `monitoring` — dashboards, alerts, review sampling %.
- `cost_budget` — hard/soft caps (tokens/mo, minutes/mo, tool$/mo).

---

## 4. Lifecycle

Every AI Employee follows the same lifecycle. States are strict; transitions are audited.

```
      ┌────────┐          ┌─────────┐         ┌─────────┐
      │  DRAFT ├────────► │ TESTING ├───────► │ REVIEW  │
      └───┬────┘          └────┬────┘         └────┬────┘
          │                    │                   │
          │                    │                   ▼
          │                    │             ┌──────────┐
          │                    │             │ APPROVED │
          │                    │             └────┬─────┘
          │                    │                  ▼
          │                    │            ┌───────────┐
          │                    ◄────────────┤ PUBLISHED │◄──── rollback
          │                                 └────┬──────┘
          │                                      ▼
          ▼                                ┌────────────┐
     ARCHIVED ◄─────────────────────────── │ DEPRECATED │
                                           └────────────┘
```

### Transitions
| From → To | Trigger | Requires |
|---|---|---|
| Draft → Testing | Operator clicks "Test in Playground" | Valid config (schema validated) |
| Testing → Review | Operator submits for review | All required KPIs defined; guardrails set |
| Review → Approved | Reviewer approves | Eval suite passes ≥ thresholds; sign-off recorded |
| Approved → Published | Operator publishes | Deployment plan (channels + rollout %) selected |
| Published → Deprecated | Operator retires this version | Successor version bound to same channels |
| Deprecated → Archived | 30-day grace period | No active sessions using this version |
| Any state → Archived | Explicit delete (owner + step-up auth) | Data-retention policy enforced |
| Published → Published (rollback) | SLO breach or manual | Previous version rehydrated within seconds |

**Rules:**
- Only one **Published** version per channel binding at a time.
- Draft is mutable; every other state is immutable snapshot.
- Every transition writes to the audit log with actor, timestamp, diff, reason.

---

## 5. Versioning Strategy

- **Every save creates a Draft revision** (auto-versioned as `v{n}-draft.{k}`).
- **Publish** promotes a snapshot to `v{n}` — immutable forever.
- Semantic-version convention:
  - Major (`v1 → v2`): breaking prompt/skill changes or new hard workflow paths.
  - Minor: additive skills, tools, KB expansions.
  - Patch: prompt wording, tone, small guardrail tweaks.
- **Rollback** = re-publish an earlier snapshot. Zero data migration. Session state carries over safely because runtime is stateless.
- **Clone** = copy any snapshot into a new Draft (a new employee) — preserves nothing about sessions.
- **Template** = a snapshot marked `is_template=true`, `owner_scope='public'`. New employees can be scaffolded from any template.
- **Diff view** in console shows exactly what changed between any two versions (prompts, tools, guardrails, KB bindings).
- **A/B versioning** — two Published versions can serve traffic behind a split (Growth+ plan). Winner promoted via CLI or console.
- **Marketplace versions** — templates from the marketplace are pinned to a specific version; upgrades are opt-in with a diff review.

### Enterprise version management
- Multi-environment (dev / staging / prod) with **promotion workflow**: publish to dev → run evals → promote to staging → run canary → promote to prod.
- Signed publish artifacts (SBOM-like) for audit.
- CI-style **"agent PR review"** — a reviewer sees the diff, evals, and cost impact before approving.

---

## 6. Evaluation Framework

All AI Employees are evaluated on the same standard metric set. Verticals add domain-specific evals; the base is universal.

### 6.1 Universal metrics (every employee, every version)
| Metric | Definition | Judge type | Notes |
|---|---|---|---|
| **Booking / Outcome rate** | % of sessions ending in the defined success outcome | Deterministic | Vertical-defined outcome (booking, ticket-close, lead-qualified) |
| **Containment rate** | % of sessions resolved without human handoff | Deterministic | Excludes user-abandoned |
| **Resolution rate** | % of sessions where user's intent was addressed | LLM judge | Rubric versioned |
| **Escalation appropriateness** | % of handoffs that were the right call | LLM judge | Sampled |
| **Customer satisfaction (CSAT)** | Post-session rating (optional prompt) | Direct | Opt-in per vertical |
| **Response accuracy / faithfulness** | Claims supported by KB citations | LLM judge + citation check | Zero-tolerance for hallucinated numeric facts |
| **Hallucination rate** | % of turns with unsupported claims | LLM judge | Target < 2% |
| **Tool success rate** | Tool calls succeeding first attempt | Deterministic | Per-tool breakdown |
| **Latency p50 / p95 / p99** | End-to-end turn latency | Deterministic | Channel-specific thresholds |
| **Cost per resolved conversation** | Fully-allocated LLM + tool + infra $ / resolved conv | Deterministic | The unit-economics metric |
| **Safety compliance rate** | % of outputs passing guardrails | Deterministic | Per-guardrail attribution |
| **Refusal appropriateness** | Correct refusal vs. over-refusal balance | LLM judge | Prevents unhelpful defensiveness |

### 6.2 Vertical KPIs (composed on top)
- Receptionist: bookings/week, no-shows-prevented, insurance questions answered.
- Sales SDR: qualified-leads/week, meetings-booked, MQL→SQL rate.
- Debt Collector: promise-to-pay rate, RPCs, compliance flags/1000 calls.
- Recruiter: candidates-screened, screening→interview conversion.

### 6.3 Eval loop
- **Golden set** per employee (curated, versioned; grows over time; seeded from template).
- **CI evals**: on every publish, block if any threshold regresses.
- **Nightly evals**: full suite, results dashboarded.
- **Prod sampling**: 5% of live sessions auto-judged; anomalies alerted.
- **Human review**: reviewers tag issues → promote to golden set → runs on next publish.
- **A/B evals**: split-test two versions; statistical significance tracked.

### 6.4 Success definition (single line per employee)
- "This employee is successful when **booking rate ≥ 15%**, **containment ≥ 70%**, **hallucination < 2%**, and **cost per resolved conversation ≤ $0.10**."
- Reviewer console shows a **traffic-light status** for each employee against its success definition.

---

## 7. Template Framework

### 7.1 What a template is
A **Template** is a fully specified AI Employee (all 11 pillars filled) plus:
- A **starter KB** (sample FAQ document, sample prompts).
- A **starter eval suite** (10–50 golden conversations).
- A **default persona** (voice, tone, language).
- **Recommended tools** (with connectors marked required/optional).
- A **compliance profile**.
- A **cost budget** appropriate for the vertical.

### 7.2 What changes per vertical vs. what stays platform-shared

**Changes per vertical (template):**
- System prompts + persona + tone.
- Workflow graph (which nodes, which order).
- Skills list.
- Recommended tool bindings.
- Vertical KPIs added on top of universal metrics.
- Golden eval set.
- Compliance profile defaults (HIPAA for medical, PCI for finance).

**Stays identical (platform):**
- The Agent Runtime executing the graph.
- The Memory system (all 3 tiers).
- The Knowledge system (ingest → embed → retrieve).
- The Tool Framework (registry, execution, sandbox, MCP).
- The Channel adapters (web widget, WhatsApp, SMS, email, Slack, Teams, voice, API).
- The Observability + Eval pipelines.
- The Deployment + Version + RBAC + Billing systems.
- The Console UX.

**No vertical is ever a fork of the codebase.**

### 7.3 Template catalog (V1 → V2 rollout)
| Template | Priority | Ships |
|---|---|---|
| `clinic_receptionist` | 1 | Sprint 5 |
| `dental_receptionist` (specialization) | 2 | Sprint 9 |
| `appointment_booker_generic` | 3 | Sprint 4 (base) |
| `real_estate_lead_qualifier` | 4 | Sprint 9 |
| `restaurant_ordering_assistant` | 5 | V1.1 |
| `sales_sdr` | 6 | V1.1 |
| `support_agent` | 7 | V1.1 |
| `recruiter` | 8 | V1.2 |
| `debt_collector` | 9 | V2 (regulated) |
| `insurance_intake` | 10 | V2 |
| `legal_intake` | 11 | V1.2 |
| `finance_assistant` | 12 | V2 |

### 7.4 Template versioning
- Templates are versioned independently from customer employees.
- Customers who scaffolded from a template are notified on major template updates ("New v2 available; here's the diff").
- Upgrade is **opt-in** — customer explicitly promotes; their previous version is retained as a rollback point.

---

## 8. Knowledge Strategy

### 8.1 Sources (unified ingestion pipeline)
| Source | Ingestion method |
|---|---|
| Website URL / sitemap | Firecrawl or Jina Reader → cleaned HTML → chunks |
| PDF, DOCX, PPTX, XLSX | `unstructured` (fallback LlamaParse for scanned) |
| Markdown / plain text | Native parser |
| Notion / Google Drive / Confluence / SharePoint | OAuth + delta sync |
| Structured DB / API / CRM | SQL/HTTP tool at query time (**not** pre-ingested) |
| FAQ (structured) | Native FAQ import; each Q/A becomes a chunk with high weight |
| Zendesk / Intercom / Freshdesk (past tickets) | API sync |
| Audio recordings | Whisper transcription → text |

### 8.2 How employees consume knowledge
- Two modes:
  1. **RAG-first** — retrieve top-K chunks per turn; ground answers with citations. Default for FAQ / policy content.
  2. **Tool-first** — invoke a live tool (SQL query, CRM lookup) for real-time data. Default for inventory, prices, availability, order status.
- **Hybrid** by default: RAG for narrative content, tools for live data.
- Every KB answer includes citations; every ungrounded numeric claim triggers refusal.
- **Freshness policy** per corpus: `immediate | hourly | daily | weekly | manual`.
- **Access control** — chunks carry ACL tags; retrieval filters by end-user role (RBAC-aware retrieval).

### 8.3 Governance
- Every document has status (`pending`, `indexed`, `stale`, `failed`, `deleted`) visible in console.
- PII detection during ingestion; sensitive chunks encrypted with tenant CMK.
- Deletion cascades within 30 days with certificate.
- No cross-tenant KB ever.

---

## 9. Memory Strategy

Three tiers, each with clear scope and retention. Never blur boundaries.

| Tier | Scope | Store | Purpose | Retention |
|---|---|---|---|---|
| **Session (short-term)** | One conversation | Redis (hot) + Postgres (durable) | Rolling window + slot values + tool results | Session + 24h |
| **Contact (long-term facts)** | Per end-user, per tenant | Postgres (`memory_facts`) | Structured facts ("prefers evening appointments", "peanut allergy") | Configurable (default forever until user revokes) |
| **Episodic** | Per end-user, per tenant | Qdrant (post-migration; pgvector V1) | Semantic recall of past conversations | Configurable |
| **Organizational (opt-in)** | Per tenant | Qdrant + Postgres | Aggregated patterns across all users, anonymized | Curated |
| **Global** | ❌ Never | — | Cross-tenant sharing is **prohibited** by architecture | — |

### Responsibilities
- **Session memory** is the AI's working state. Fast, ephemeral.
- **Contact memory** is what a returning caller "remembers about themselves" — human-editable in the console, revocable.
- **Episodic memory** improves resolution on returning users (opt-in per tenant).
- **Organizational memory** is where learning compounds — top failure modes, best responses, effective patterns — anonymized and reused per tenant only.

### Rules
- Prompt composer injects memory in a strict priority order (long-term facts → episodic → organizational → RAG snippets → rolling window → user input).
- **No fact is added silently** — the console shows exactly what the agent knew per turn.
- **"Forget me"** API cascades across all tiers within 30 days.

---

## 10. Tool Strategy

Tools are **the only way** an AI Employee affects the world.

### 10.1 Built-in tool categories
| Category | Examples |
|---|---|
| Scheduling | Google Calendar, Outlook, Cal.com, Calendly |
| CRM | Salesforce, HubSpot, Zoho, Pipedrive |
| Messaging | Email (Resend/SES), SMS (Twilio), WhatsApp, Slack |
| Payments | Stripe, Razorpay (payment links, subscription, refund) |
| ERP / Vertical | Dentrix, Epic (later), NetSuite, Zoho Books |
| Data | SQL query (read-only, allowlisted), HTTP API (typed) |
| Storage | Document generate (PDF/DOCX), file upload |
| Handoff | Zendesk, Intercom, Freshdesk, warm-transfer (voice) |
| Utility | Web search, web scrape, code interpreter, translate, sentiment |
| MCP | Any MCP server (client mode) |

### 10.2 Governance
- All tools **typed** (JSON Schema for args + returns).
- **Idempotency required** for state-changing tools.
- **Retries + circuit breaker** per tool per tenant.
- **Rate limits** per tool per tenant.
- **Cost budgets** per tool (some tools cost money — e.g., web search API).
- **Per-tool approval flow** for high-risk actions (transactions > threshold, sensitive data writes) — human-in-the-loop toggle.
- **Sandboxed execution** for custom-code tools (Firecracker / gVisor).
- **Audit** — every tool call is logged with args (redacted per policy), result digest, latency, cost.
- **Version pinning** — an employee is pinned to a tool version; upgrades are explicit.
- **MCP first-class** — external MCP servers register once; their tools appear as native tools with the same governance.

### 10.3 Tool lifecycle
1. Register (from OpenAPI import, MCP server, or manual spec).
2. Test in Playground (dry-run mode).
3. Bind to employee.
4. Publish employee.
5. Monitor in observability.
6. Deprecate (grace period; employees warned).
7. Delete.

---

## 11. Multi-Channel Strategy

**One AI Employee. Many transports.** The channel is a **thin adapter** that speaks the runtime's I/O protocol — nothing else.

### 11.1 Channels
| Channel | Adapter role |
|---|---|
| Web widget | Widget bundle + public SSE endpoint |
| Voice (PSTN + WebRTC) | LiveKit + Pipecat worker (STT/TTS bridging) |
| WhatsApp | Meta Cloud API webhook + template messaging |
| SMS | Twilio / MessageBird webhook + segmentation |
| Email | Resend/SES inbound routing + threaded outbound |
| Slack | Slack bot + slash commands |
| MS Teams | Bot framework |
| Public API | REST + SSE + WebSocket + SDKs |

### 11.2 Why channels never affect the Agent Runtime

The runtime consumes a **normalized session message**:
```
{
  role: "user",
  content: "..." | [{type:"text",text:"..."} , {type:"image",url:"..."}],
  attachments: [...],
  channel: "voice" | "widget" | "whatsapp" | ...,   # metadata only
  locale: "en-US",
  end_user_ref: "..."
}
```

The runtime emits a **normalized session event**:
```
{ event: "token" | "tool_call" | "tool_result" | "final" | "handoff",
  payload: {...} }
```

Adapters translate to/from channel-specific formats (audio frames, WhatsApp templates, email MIME). They do **not**:
- Change the state machine.
- Add channel-specific tools inside the runtime.
- Bypass guardrails or memory.
- Directly call LLMs.

**Benefits:**
1. A new channel = 1 adapter, 0 runtime changes.
2. All evals + observability + memory work identically per channel.
3. Customers configure once, deploy N channels.
4. The runtime scales independently of channel-specific bottlenecks (voice concurrency, WhatsApp template limits).

### 11.3 Channel-specific overrides (only at the persona layer)
- Voice: TTS voice, speaking rate, barge-in threshold.
- WhatsApp: template messages (for outside-24h-window messaging).
- Email: signature, threading behavior.
- All overrides are configuration; no code branches.

---

## 12. Marketplace Strategy

The marketplace is how the platform becomes an **ecosystem** — the Shopify of AI Employees.

### 12.1 What gets published
- **Templates** — verified AI Employees for a vertical.
- **Tool packs** — bundles of tools (e.g., "Dental practice pack: Dentrix + Weave + Adit").
- **Voice/persona packs** — voice + tone bundles.
- **Eval suites** — golden sets contributed by domain experts.
- **Prompt libraries** — vertical-specific prompt snippets.

### 12.2 Lifecycle
```
CREATE → SUBMIT → REVIEW (automated + human) → APPROVED → LISTED → INSTALLED → RATED → UPDATED → DEPRECATED
```
- **Automated checks**: schema validation, eval suite runs, cost estimate, PII scan.
- **Human review**: content appropriateness, vertical fit, legal/compliance surface.
- **Publisher identity verified** (Stripe Connect + KYB for paid templates).
- **Signed manifests** so installs are tamper-evident.

### 12.3 Monetization
- **Free templates** by us to seed the market.
- **Free community templates** with reputation reviews.
- **Paid templates** (Year 2+): one-time or subscription; 80/20 revenue split favoring the creator.
- **Enterprise-only templates** (private listings for a specific tenant or industry group).

### 12.4 Governance
- **Ratings** (1–5) + written reviews from actual installs.
- **Analytics per template** (installs, retention, avg CSR).
- **Deprecation policy** — creator can deprecate; installs get 90-day notice.
- **Fork policy** — installed templates can be cloned into private edits without affecting the source.

---

## 13. Future Vision — 1 Million AI Employees

If a million AI Employees run on this platform, the system must operate more like a global compute + labor market than a SaaS app.

### Operating model
- **Multi-region cells**, each ~10k tenants / 100k employees / 5k concurrent voice sessions.
- **Tenant-cell routing** at DNS/gateway based on data residency + capacity.
- **Template installations dominate creation** — 90%+ of employees are marketplace-scaffolded, not hand-built.
- **Fine-tuned small models per top vertical** (5–10x cheaper inference) hosted on our GPUs (vLLM).
- **Federated evals** — templates run continuous evals across all their installs, and update recommendations back to the creator.
- **Prompt / skill improvements propagate** as optional upgrades — install owners can accept in one click with diff preview.

### Marketplace scale
- 10,000+ published templates.
- Vertical sub-marketplaces (dental, restaurant, real-estate, legal, …) each with 500–1,000 templates.
- Creator earnings dashboards; automated payouts (Stripe Connect).
- ISVs (independent software vendors) launching entire product lines on top of our runtime.

### Enterprise mode
- On-prem / VPC deployments with feature parity except marketplace access (which becomes curated private mirrors).
- Federated identity (SPIFFE) across customer VPC and our multi-region control plane.
- Air-gapped mode with offline model inference.

### Governance at scale
- Every AI Employee auditable to a signed workflow trace.
- **AI Employee registry per tenant** — like an org chart, but for AI.
- **Compliance profiles** enforced by policy engine (OPA) at every runtime step.
- **Regulatory reporting** (EU AI Act high-risk classification workflows) built-in per template.

### Economic implications
- Verticalized labor pricing: per outcome, per resolved conversation, per booking, per closed loop — not per token.
- **Outcome-based SLAs** ("we guarantee ≥ 15% booking rate or the month is free") for opinionated verticals.
- **Employee-of-the-year metrics** — top templates per vertical ranked publicly, creating an incentive flywheel.

### Product implications
- The console evolves into an **AI Employee HR system** — hiring, onboarding, KPIs, performance reviews, promotions (version upgrades), retirement (archives).
- Business owners think in terms of "workforce planning" for their AI.
- Every action a human ops person can do, an AI can do; every action an AI can do, a human ops person can review.

**In short:** the platform stops looking like a "SaaS product" and starts looking like an **operating system for how businesses hire, deploy, and manage software labor**. That is the endgame the entire 24-doc architecture is engineered to reach — and the MVP is the first step onto it.
