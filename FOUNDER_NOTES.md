# FOUNDER NOTES

Direct, unvarnished advice from your CTO / VC-side co-thinker. Read this once at the start of every sprint.

---

## The 5 Biggest Risks (ranked)

1. **You build something no one is desperate for.** Nine of ten "AI platform" startups fail here, not in engineering. Book **10 clinic demos before writing Sprint 2**. If those demos are hard to book, your vertical is wrong — pivot before writing more code.
2. **You out-engineer your revenue.** With 1 founder + 1 engineer, every hour on Kubernetes/Kafka/OTel is an hour not on the widget UX or the sales call. The long-term architecture in `docs/` is a **map**, not a **schedule**.
3. **LLM quality degrades in the wild** compared to your demo. What works on 20 example questions fails on the 200th real one. Sprint 5's eval loop is not optional.
4. **Solo on-call burnout.** You will get paged at 2 AM. Ship uptime monitoring in Sprint 8 and set a **no-fix-after-11pm-except-outage** rule now.
5. **Compliance surprises.** A hospital / large clinic will ask for a BAA or SOC 2 report in month 3 and you'll panic. Say "we're SOC 2 in-progress; happy to sign an NDA and share our security policy" — draft that policy in Sprint 7, not Sprint 19.

---

## Most Likely Engineering Mistakes

- **Premature microservices.** Do NOT split the API monolith until a specific service has a different scaling profile that actually hurts you (voice is the canonical example, ~Sprint 10). Every early split doubles your ops toil.
- **Choosing a "cool" vector DB early.** pgvector will carry you to millions of chunks. Migrating to Qdrant later is a script, not a rewrite.
- **Writing your own PDF parser.** You will lose 4 weeks. Use `unstructured` + LlamaParse.
- **Building auth from scratch.** Clerk (or Supabase Auth) saves 3 weeks. Migrate to WorkOS/Ory the day a customer asks for SAML, not before.
- **Reinventing rate limiting / retries / idempotency.** Use `slowapi`, `tenacity`, standard patterns.
- **Skipping RLS "just for now."** OK for Sprint 1–4 (one dev, one tenant per test). Enforce it in Sprint 5 **before** you hire or open beta widely. Retrofitting RLS post-scale is painful.
- **Logging PII.** By default, redact `email`, `phone`, `content` from logs. Add explicit `pii-logs` stream if you need it. This is the #1 SOC 2 gotcha.
- **No cost dashboards.** Track LLM spend per org from Day 1 (Sprint 2). A single runaway prompt from an abusive widget visitor can burn $500 overnight. Add per-session token caps + per-visitor rate limits.
- **Streaming half-done.** Streaming is either end-to-end or worthless. Test with a slow-network throttle from Day 1.
- **Using Kubernetes.** Just don't. Fly.io scales cleanly to thousands of tenants. Add K8s when you have a full-time SRE.
- **Ignoring migrations discipline.** Every schema change reversible. Test `up → down → up` in CI from Sprint 1.

---

## Most Likely Product Mistakes

- **Building a "chatbot builder."** You are not competing with Chatbase. You are shipping **a vertical AI employee**. The product is the outcome (bookings placed, questions answered), not the tool. Keep the language crisp everywhere: "AI Receptionist that books appointments."
- **Adding features design partners ask for one-off.** For every 3 requests, hard-say "not yet." Only build a feature when a **third customer** asks and it's on your critical path.
- **Skipping the onboarding wizard.** A 15-minute self-serve activation flow is worth 10 sprint items. Do it in Sprint 6, not later.
- **Overcomplicated pricing on Day 1.** Two plans — `starter` and `growth`. Add `scale` after 50 customers.
- **Perfect docs before customers.** Loom videos beat docs at your stage. Ship the video, iterate the docs.
- **Building for enterprise before SMB traction.** Enterprise sales cycles will drown you. Get 100 SMB customers first, THEN raise your seed / Series A and hire enterprise sales.
- **Adding voice too early.** Voice UX is the hardest thing on the roadmap. Sprint 10 is aggressive; don't move it earlier unless customers refuse to buy without it.
- **Falling in love with your architecture.** The 24 docs are a destination. Every week, re-ask: "does this ship revenue faster?"

---

## What NOT To Build (right now)

- ❌ Voice pipeline (until Sprint 10, and only if chat customers demand it).
- ❌ WhatsApp/SMS/Email/Slack/Teams channels (until Sprint 8/14).
- ❌ Marketplace, template gallery for third parties (V1.1+).
- ❌ Enterprise SSO / SAML / SCIM (until a paying customer asks).
- ❌ Multi-region (until an EU or APAC customer asks).
- ❌ Kubernetes, Istio, Argo, Kafka, Temporal, ClickHouse, Vault, OPA, KEDA, service mesh (all later).
- ❌ Custom fine-tuned models (until 100+ customers of a vertical + volume justifies it).
- ❌ Video agents.
- ❌ Native mobile SDKs.
- ❌ Your own eval framework — use Langfuse / Braintrust.
- ❌ Your own vector DB.
- ❌ Your own PDF parser.
- ❌ Your own auth.
- ❌ Your own metrics/logs/traces stack — use Sentry + Axiom + PostHog.

---

## Where Competitors Waste Time (learn from them)

- **Retell/Vapi/Bland:** amazing voice; weak console; weak channel unification; enterprise controls late. **Don't out-voice them — out-vertical them.**
- **Chatbase/Voiceflow/Botpress:** great builders; shallow outcomes. Their agents chat; ours **book, close, escalate, transact**. Ship the outcome loop, not the design surface.
- **Intercom Fin / Ada:** heavy enterprise sales; overkill and pricing for SMB clinics. Slot in below them with a self-serve, vertical-tuned product.
- **Autonomous multi-agent frameworks (CrewAI/AutoGen):** endless demos, few production deploys. Deterministic vertical workflows win.
- **Big-model-worship:** teams over-index on GPT-4o vs. Claude vs. Gemini benchmarks. Your win is prompts + tools + data — not the model.

---

## How to Reach First Revenue Quickly

1. **Book 15 demos before Sprint 5.** Cold outreach + community posts + your personal network. Every demo is a de-risking event.
2. **Charge from Day 1.** Even $199/mo. Free pilots become forever pilots.
3. **Personal onboarding for the first 20 customers.** 45-minute call, install the widget with them, watch them use it. Every call is a Sprint 6 backlog input.
4. **Say the price in the first email.** No "get in touch" theatre.
5. **A single case study beats a landing page.** Get one clinic to say "we booked X extra appointments" and put their logo everywhere.
6. **Do outbound yourself for the first 6 months.** Founders sell better than reps at this stage.
7. **When in doubt, do the unscalable thing.** Manually curate the KB for the first 10 customers. It buys learning + retention.

---

## How to Validate Product-Market Fit

You have PMF **when at least half your customers would be very disappointed if the product went away**. Until then:

- Track weekly: demo-booked → demo-showed-up → trial-started → activated (widget installed + calendar connected) → paid → D30-retained.
- Read every conversation in the first 60 days. Yourself.
- Interview every churned customer within 48h.
- If **retention D30 > 85%** and **word-of-mouth signups appear**, you have signal.
- If you're pushing water uphill on every renewal, the vertical or the product is wrong — **do not scale marketing to fix a product problem**.

---

## Which Metrics Matter (weekly review)

- **Demos booked** (leading indicator of pipeline).
- **Trial → paid conversion** (target ≥ 25%).
- **Activation rate within 24h** (target ≥ 60%).
- **Containment rate** per agent (target ≥ 70%): % of conversations resolved with no handoff.
- **Outcome rate** per agent: for clinics, % of chat sessions ending in a booked appointment.
- **D30 retention** (target ≥ 85%).
- **Gross MRR + Net MRR churn**.
- **Cost per resolved conversation** (from Sprint 6 onward).

## Which Metrics DO NOT Matter (yet)

- GitHub stars, Twitter followers, HN karma.
- Model benchmark scores (MMLU/HumanEval, etc.).
- API endpoint p99 latency below 200 ms on chat (nobody notices under 1.5 s).
- Number of integrations built (breadth is a trap; depth wins).
- Feature parity with Retell/Vapi/Chatbase feature lists.
- Any vanity dashboard your investors don't ask about (they will ask about MRR, retention, containment).
- Code coverage % (aim for good enough, not perfect).

---

## How to Avoid Overengineering

Ask three questions before starting any technical work:

1. **What breaks if we don't build this until we have 10 more customers?** If the answer is "nothing," postpone.
2. **Would a paying customer notice the difference?** If not, postpone.
3. **Can we do this later without a rewrite?** If yes, postpone.

Additional rules:
- **The smallest change that ships the outcome wins.** A 1-file solution beats a 12-file "framework."
- **You are allowed to write hacky code as long as it has a test and a TODO with a specific trigger** (e.g., "TODO: extract to service when we have >200 tenants").
- **Delete more code than you write when possible.** Nothing accelerates a startup like removing weight.
- **Sprint retros end with a "what did we build that no one used?" list.** Delete or de-prioritize immediately.
- **The 24 docs are your safety net, not your to-do list.** Refer to them when you finally need to solve the problem they solve. Not before.

---

## Weekly Founder Rhythm (protect this)

- **Mon:** review last week's metrics, plan the week (max 3 outcomes), record any pivots.
- **Tue–Thu:** deep work + customer calls. No meetings mornings.
- **Fri:** ship the week; write the 5-line update ("shipped X, learned Y, decided Z"); send to advisors + design partners.
- **Sat/Sun:** one afternoon of "read + think," rest of the weekend off. Burnout kills startups faster than competitors.

---

## The One Thing to Remember

> **You are not building a platform. You are building the smallest useful AI employee for one specific vertical, and letting the platform emerge from a second vertical, then a third.**
>
> The platform is the *result* of shipping 5 verticals well — not the *cause* of shipping the first one.

Print this. Tape it to your monitor.

---

## Recommended Next Prompt

Paste the prompt below into Claude Code (or any coding agent) to begin **Sprint 1 only**. Do not modify it to include Sprint 2 items.

```
You are the sole engineer implementing Sprint 1 of the Vertical AI Agent Platform.

Your source of truth is:
- SPRINT_1.md (the exact scope; do not exceed it)
- REPOSITORY_STRUCTURE.md (the monorepo layout you must follow)
- MVP_IMPLEMENTATION_PLAN.md (the "why" behind the tech choices; consult when a tradeoff appears)

Constraints:
- Do ONLY the work described in SPRINT_1.md. If a change is tempting but not in SPRINT_1.md, add it to BACKLOG.md instead — do not implement it.
- Follow the repo layout in REPOSITORY_STRUCTURE.md exactly (names, folders, ownership).
- Stack: Python 3.12 + FastAPI + SQLAlchemy async + Alembic + pgvector-ready Postgres image + Redis + LangGraph + LiteLLM (as SDK) + Clerk (auth) + Next.js 15 (App Router) + Tailwind + shadcn/ui + Docker Compose + GitHub Actions + Fly.io (preview + prod).
- No Kubernetes, no Qdrant, no ClickHouse, no Kafka, no Temporal, no service mesh, no observability stack beyond Sentry.
- No voice, no WhatsApp, no SMS, no email channel, no Slack, no Teams, no billing, no widget, no KB/RAG, no tools/calendar. Those are later sprints.

Deliverable definition:
- A cold laptop can run `git clone` + `cp .env.example .env` + `make dev` and reach the running app within 5 minutes.
- A signed-in user in their own org can create an agent, chat with it via streaming SSE, refresh, and see history — end to end, backed by real Postgres + Redis + FastAPI + Next.js.
- Every PR gets a preview deploy on Fly.io; main auto-deploys to prod.
- All items in SPRINT_1.md's "Exit Checklist" pass.

How to work:
1. Start by reading SPRINT_1.md end to end. Ask me any clarifying question BEFORE writing code.
2. Propose the first 3 commits (scaffold, docker-compose, FastAPI skeleton) as a plan with file lists. Wait for my "go" before creating files.
3. After each Deliverable (D1–D13), stop, summarize what changed, and request my review.
4. When the Exit Checklist is fully green, stop. Do not begin Sprint 2 work under any circumstances.

Rules:
- Prefer boring, well-known code over clever code.
- No premature abstractions. No microservice extraction.
- Every migration must be reversible; include an Alembic downgrade.
- Every new endpoint must have an integration test using testcontainers.
- Never commit secrets; use .env.example only.
- Ask before adding any dependency not already implied by SPRINT_1.md.

Begin by reading SPRINT_1.md and confirming your understanding of the Exit Checklist.
```
