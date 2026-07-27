# INDEPENDENT PRE-IMPLEMENTATION REVIEW

**Reviewer role:** Independent Principal Engineer + Staff Architect + startup CTO + VC technical DD.
**Author of the plan:** Not me.
**Bias:** Deliberately unforgiving. The goal is to catch expensive mistakes now, when they're cheap.

---

## 0. Executive Judgment Up Front

The planning corpus is well-written, internally consistent, and shows unusual maturity for a pre-code project. It is also **over-scoped for a two-person team and dangerously optimistic about the founder's ability to sell into healthcare from cold**. There is more architecture here than an early-stage company should carry, and the "MVP" is at least 30% wider than what a single engineer can ship in 10 weeks at production quality.

The bones are right. The weight is wrong. The vertical bet is fragile. Fix a handful of specific things and this is buildable. Do not fix them and the founder will burn 4–6 weeks re-cutting scope after Sprint 3.

**Verdict:** **B — Needs Minor Fixes** (see §12). Not "A — Ready to Build."

The delta between B and A is a small number of decisions the founder must sign off on **before Sprint 1 starts**. Those decisions are in [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md).

---

## 1. Startup Founder Perspective

### Overbuilt
- **Ten sprints of pre-planning documents**. This is the first smell. Real early-stage teams write < 30 pages of docs and start building. You have ~180 pages of docs and no `git init`. Time-to-first-customer is not "10 weeks" — it's "however-long-planning-takes-plus-10-weeks." That is already 2–3 weeks lost.
- **11 pillars in the AI Employee model**. Impressive framework. Wrong stage. In Sprint 1–5 you have prompt + tools + KB + memory. The other 7 pillars ship as they're needed. Publishing them as a canonical model *before* first customer risks over-designing versioning, marketplace, and lifecycle for a product no one has bought yet.
- **Marketplace strategy documented at pre-Sprint-1**. Zero people will publish to it. Delete this from active thinking; keep the doc for Y2.
- **11 verticals scored and 12 templates roadmapped**. You will ship ≤ 3 verticals in Year 1. Delete the extra 9 from any docs that inform scope.
- **Custom eval framework language ("universal metrics", "vertical KPIs", "reusable evaluation standards")** — this is architecturally correct but psychologically dangerous for a solo team. It invites over-engineering. Ship a Google Sheet + Langfuse for the first 50 conversations, not a framework.
- **BACKLOG Sprints 13–20**. You will not follow this roadmap. Real backlogs are re-cut monthly. Presenting a 40-week roadmap as if it's a plan is fiction that pretends to be certainty.

### Underbuilt
- **Sales/onboarding tooling is 0% built out**. Where is the discovery-call script? The demo checklist? The "install widget on their site" wizard walkthrough? These are the actual moat vs. Chatbase — and they're not mentioned until Sprint 6.
- **No customer research done**. The persona (Dr. Sarah Patel) is invented, not interviewed. You have not talked to a single dentist yet. Everything downstream — pricing, positioning, MVP scope — is guesswork calibrated to internally consistent theory. **This is the single largest risk in the entire project.**
- **No pilot design partner secured**. You cannot design a "Sprint 7 = Design-partner polish" if you don't have design partners identified in Sprint 1.
- **No pricing tested with a human**. $199/$499 is a reasonable guess. It is still a guess.
- **No "day in the life"** of the office manager mapped. Where does the AI live in Maria's day? What existing tool does it replace? What system does it push data into that Maria trusts?

### What will delay revenue
1. **The 3-week gap between "Sprint 8 owner-facing analytics" and actual weekly digest email**. Ship the digest in Sprint 6. It is the single strongest retention lever.
2. **Voice deferral is right, but not sold to prospects.** If your first 30 calls with dentists reveal that voice is table-stakes for their receptionist, you have a positioning problem. Solve during discovery, not during Sprint 10.
3. **Multi-model LLM router configured in Sprint 1**. Delete. Ship OpenAI + one fallback and move on.
4. **Sprint 3 embeddable widget being its own React app in `apps/widget`**. A first-cut widget is a `<script>` tag + iframe pointing to an existing Next.js route. The bundle size story is a Sprint 12 problem.
5. **Building `apps/landing`** — delete. Use Framer/Webflow. Never maintain two Next.js apps at 2 engineers.

### Delete immediately
- `apps/landing` — use Framer/Webflow.
- `apps/widget` as its own Vite bundle in MVP — inline into console for now, extract later.
- Public API + SDK plan (Sprint 13) — remove from BACKLOG until a developer asks.
- Long-term memory / episodic memory / organizational memory (Sprints 18+) — remove until data shows repeat users are a top-3 request.
- MCP server exposure — Y2 problem.
- MS Teams + Slack channels — Y1 unlikely.
- Multi-region planning — Y2 problem.
- Cell-based architecture references — YAGNI at your stage.
- Every ADR marked "Deferred" is fine — but stop naming them like they're on a roadmap.

---

## 2. Principal Software Architect Perspective

### Wrong abstractions
- **`packages/shared-py` is premature**. There is one Python service. Extracting shared code before it's shared duplicates thinking. Delete for MVP; add when the second Python service exists (Sprint 10+).
- **`packages/sdk-python` in the roadmap** — see above.
- **Module `ports.py` per bounded context**. Correct pattern for a real microservices future. Overhead for the current reality (one dev, one service). Draw the seam only when the module actually needs an interface (KB, runtime). For `iam`, `billing`, `notifier` — skip ports; use direct imports until proven wrong.
- **`AgentRuntime` abstraction over LangGraph** in Sprint 1. Wrapping LangGraph for future-swappability is a leaky, expensive abstraction. LangGraph's API is intrusive; a thin wrapper won't help you swap frameworks anyway. Use LangGraph directly. If you ever need to swap, you're rewriting the graph regardless.
- **"11-pillar" AI Employee model as the canonical schema in Sprint 1**. Ship the fields you actually need per sprint. A `spec JSONB` column + a Pydantic model that grows is fine. Canonizing the 11 pillars now will drive you to build screens for pillars nobody uses (Personality, Reasoning strategy, Decision boundaries) in months 3–4.

### Hidden coupling
- **Single Postgres for OLTP + pgvector + BM25 + LISTEN/NOTIFY + Redis-Stream-equivalent**. Nice for MVP simplicity. When one of those workloads becomes hot (pgvector on a 10M-chunk corpus, or LISTEN/NOTIFY under load), all four suffer. Add a **capacity plan trigger** ("split pgvector to its own Neon branch or Qdrant when > 2M chunks per tenant or > 200ms p95 vector search") — currently missing.
- **Clerk owns the org model.** Your `org` table's authoritative fields duplicate Clerk's. If Clerk's Organization semantics diverge from yours (e.g., roles, invitations), you'll have drift bugs. Decide now: **Clerk is source of truth for identity + membership, ours is source of truth for entitlement + billing**. Document who owns what field. Currently ambiguous.
- **Session state in Redis with "durable write on turn-end to Postgres"** — race conditions if the Redis write fires and the Postgres write fails. What's the reconciliation? Not specified.
- **Widget uses `agent_id` unauthenticated with CORS whitelist + rate limit.** An `agent_id` leaks the moment it's on a customer's site (it's in the DOM). Anyone can scrape it and pound your endpoint from their own domain if CORS is enforced client-side. **CORS is not a security boundary.** You need a signed embed token (short-lived, origin-bound, issued by the customer's site or by our loader with domain verification) — not documented anywhere yet.

### Future migration pain
- **`org_id` naming everywhere but `tenant_id` in the long-term docs.** Pick one now. Migrations across 200 tables to rename a column later will hurt.
- **ULID with type prefix**: great. But how is the type prefix computed? Is `agn_` for `agent`, `agv_` or `ver_` for `agent_version`? Document the full prefix table now (in one file), or you'll invent inconsistent prefixes and never migrate them.
- **`spec JSONB` on `agent_version`** — the schema of this field will evolve rapidly and you have no plan for typed versioning of it. Either: (a) validate with a versioned Pydantic model where each version knows how to migrate from the last, or (b) store the raw + a normalized shadow. Not specified.
- **Two languages, one repo, both must build in CI on every PR**. This burns CI minutes and slows the loop. Only wake up TS CI when TS files change; only wake up Python CI when Python files change. `turbo` / `pnpm --filter` + `paths:` filters in Actions. Not specified in Sprint 1.

### Data model mistakes
- **`turn.role IN ('user','assistant','system')`** — no `tool` role. LangGraph will need tool call + result turns. Add `tool_call` and `tool_result` (or store them as structured content on the assistant turn — pick one convention now).
- **`session.agent_version_id`** captured — good. But once a session starts on v3 and the agent gets republished to v4 mid-conversation, what happens? Not specified. Recommended: sessions are pinned to the version they started on; document this explicitly.
- **`memory_facts` table** planned for Sprint 18 — but if you invent it later without care, you'll re-invent it wrong. Add a placeholder table + comment now; do not build UX around it.
- **No `end_user` / `contact` table in V1**. Sessions are anonymous. That's fine, but the moment WhatsApp/SMS arrive, you need contact identity (phone-hashed). Reserve the shape now.
- **`audit_log.diff JSONB`** — for large diffs this bloats. Cap payload size; store large diffs in R2 with pointer.
- **No `feature_flag` table nor an `entitlement` table.** Plan says "env + Postgres row." You will need a real entitlements model by Sprint 6 (billing). Design the shape now (org × feature × value) or you'll bolt something bad on.

### Runtime mistakes
- **No cancellation contract in the SSE endpoint spec.** When the browser closes the tab mid-stream, does the LLM call get aborted? Does the DB write happen for the partial assistant turn? Not defined. This will show up as billing anomalies and orphan spans within a week of prod.
- **No back-pressure story.** If a widget goes viral (5,000 visitors talking at once), what happens? "Rate limit at 60 req/min per user" doesn't help if it's 5,000 different users. There's no per-agent concurrency cap defined.
- **Idempotency-Key on `/messages/stream`** is called out but streaming + idempotency is subtle. Returning a cached response digest for a POST that returned an SSE stream last time is a **replay problem**, not a cache-hit. Delete Idempotency-Key for streams; keep it only for tool-invoke and admin mutations.
- **Prompt caching not planned.** Every LLM call re-sends the full system prompt. OpenAI + Anthropic both have prefix caching that cuts costs 40–90%. Even in Sprint 2 you should structure the system prompt with the stable part first.
- **No provider-side timeouts.** LiteLLM has defaults but they are too generous. Set a hard 20s timeout on chat and 60s on embeddings from Day 1.

---

## 3. Staff AI Engineer Perspective

### LangGraph
- **Wrong choice for Sprint 1.** You are shipping a **single-node** LangGraph in Sprint 1. That is `openai.chat.completions.create` with 4x the abstraction. LangGraph earns its complexity at nodes ≥ 3 with real branching and persistence needs. Ship Sprint 1 with a plain function; introduce LangGraph in Sprint 2 or 3 when you actually branch (RAG node, tool node). This will halve Sprint 1's cognitive load.
- **LangGraph is a moving target.** API churn in 2025 was material. Pin to a specific minor version and read release notes before every upgrade.
- **LangGraph persistence** (checkpointers) will interact awkwardly with your custom Redis session state. Choose one:
  - Use LangGraph's checkpointer (PostgresSaver) and skip the custom short-term store, OR
  - Do not use LangGraph's checkpointer and manage state yourself.
  - **Doing both is a race-condition factory.** Not decided in the docs.

### LiteLLM
- **Right choice. Wrong integration mode.** Using LiteLLM as an SDK in-process for MVP is fine; but the doc waffles between "SDK" and "proxy" for Sprint 5+ without a hard trigger. Set the trigger explicitly: "switch to proxy when we need per-tenant cost caps, semantic cache, or observability of a request we didn't originate."
- **LiteLLM's OpenAI-compat surface has edge cases**, especially around tool calling parity across providers. Do not assume Anthropic/Groq/Llama behave identically with the same graph. Add per-provider integration tests early.
- **Do not enable fallback in Sprint 1.** Fallback masks broken code as "provider issue." Ship single-provider until you've seen prod traffic for a month.

### Prompt architecture
- **No prompt registry planned.** Prompts are just strings in `agent_version.system_prompt`. This is the single most-changed artifact and you have zero version diffing, zero A/B, zero rollback UX planned for it. Even minimal: a `prompt_template` table with `(id, agent_version_id, role, template_text, variables)` and a diff view. Missing.
- **No structured prompt composition primitives.** You will end up with 3,000-token system prompts assembled by string concatenation. Adopt a **template rendering library** (Jinja2 with strict undefined + safelist) and a **composition order contract** (system → memory → KB → tools → history → user). Codify in Sprint 2, not Sprint 15.
- **No prompt cache strategy** (see §2).
- **No output-format contract.** Voice vs. chat need different formats (voice hates markdown). Add a `channel` variable in every prompt and branch output style.

### Evaluation strategy
- **Golden set as JSONL files in `verticals/*/evals.jsonl` is right for MVP.** Do not build an eval service. Do not build "universal judges" until you have 100+ conversations to score.
- **LLM-as-judge in CI blocks publish** — this is aspirational and will bite you when a judge is flaky and blocks legit releases. Make it advisory in Sprint 5–7; blocking only after 3 months of judge stability.
- **No "trace-diff" tool** planned. When agent v3 → v4 changes behavior, being able to replay 20 golden conversations through both and diff outputs is invaluable. Should be a Sprint 6 tool, not Sprint 12+.
- **Faithfulness eval assumes citations.** Your Sprint 2 RAG plan already says "citations required." Make sure the eval judge is calibrated against your citation format, not a generic one.

### Memory strategy
- **Three memory tiers documented; MVP has one (Redis short-term).** Fine. But the doc-vs-code gap is confusing. Say clearly in the Sprint plan: "memory in MVP = Redis rolling window + `contact` table (deferred)."
- **"Organizational memory (opt-in)"** — nice concept. Never build until asked by a paying customer. Even then, hard privacy problem (cross-user learning inside a tenant). Legal review required before shipping. Not flagged.

### Knowledge architecture
- **Firecrawl for URLs is a good call.** But: Firecrawl on a 5,000-page dental group website costs money and takes time. Add a **corpus size cap** in Sprint 2 (e.g., 200 pages / 100 MB on Starter). Missing.
- **Chunking strategy documented (1000 tokens ± 100 overlap)** — fine for MVP. But recursive character splitting on medical/legal content is known to be poor. For Sprint 5 (clinic template), plan a **header-aware chunker** (splits on `<h1>/<h2>` and preserves parent context). Currently not scoped.
- **`unstructured` library** is heavy (multi-GB Docker image, slow cold starts). Fine on a worker; deadly if you accidentally import it into the API. Add a hard import boundary.
- **Embedding model choice (`text-embedding-3-small` @ 1536d) with pgvector**: HNSW indexing on 1536d gets slow past ~1M rows. Plan the migration to Qdrant at **~500k chunks per tenant**, not the "10M chunks" the doc claims. Test this empirically in Sprint 3.
- **No reranker in MVP** is the right call, but you should be **measuring hit@k** from Sprint 3. Otherwise you'll add a reranker in Sprint 15 with no baseline to compare against.

### Tool framework
- **Declarative YAML + JSON Schema is right.** But the plan skips the hardest part: **how does the LLM choose the right tool when there are 15+ tools defined?** Tool selection accuracy degrades sharply past ~10 tools. Plan a **tool routing** step (per-turn shortlist) by Sprint 7 or you'll hit a quality cliff at the "Business plan" tier.
- **Google Calendar edge cases**: timezone, recurring events, all-day events, participant cascades, conflicts. These are the most common source of "the AI booked wrong" complaints. Sprint 4 needs a **written checklist of Google Calendar edge cases** and integration tests for each. Currently not scoped.
- **Idempotency on `create_booking`** — mentioned. But the actual pattern is subtle: retry a booking with the same idempotency key must return the previously created event, not a duplicate. Requires the tool to also *read back* on retry.
- **No dry-run mode** on tools — critical for eval and safe rollout. Add.

---

## 4. Infrastructure Engineer Perspective

### Deployment
- **Fly.io is a fine MVP host, but the plan understates its footguns.** Neon + Upstash + Fly across three vendors means three failure domains, three billing dashboards, three status pages. That's normal — but plan a single **incident notification aggregator** (statuspage.io or a Slack webhook that hits all three).
- **Preview environments per PR using Fly.io + Neon branching + Upstash preview**: Neon branching works well; Upstash "preview" is unclear (do you spin a new Upstash DB per PR? Or share?). Not documented. If shared, PR tests pollute each other's Redis keys. Namespacing per PR is required.
- **`fly deploy` from GitHub Actions is fine**, but no rollback strategy is defined. Fly supports `fly releases rollback`; wire it into the deploy workflow with a manual button.
- **Zero-downtime**: for the Postgres migration model (`alembic upgrade head` as release command), you must guarantee **backward-compatible migrations**. Rename columns via expand → migrate → contract. This is in `CODING_STANDARDS.md`; needs a **CI check** (`pgroll` or `atlas`), not just a policy.

### Docker
- **Multi-arch build in CI (`amd64/arm64`)** is planned. Sprint 1 note says "amd64 only for now." Good. Do not enable arm64 until Fly.io machines actually run arm64 for you.
- **`unstructured` Docker image size** (see §3). Worker container will be 3–5 GB. Consider a separate lighter API container.
- **Base image choice not specified.** Use `python:3.12-slim-bookworm` + `uv`. Do not use `alpine` (musl breaks a lot of ML wheels).
- **No layer caching strategy** documented. Multi-stage builds with `uv sync --no-install-project` before copying source. Save 60% of CI time.

### CI/CD
- **`docker build` in CI on every PR without cache is slow.** Enable `docker buildx` with GHA cache backend. Missing.
- **No test parallelism strategy**. `pytest-xdist` + shared testcontainers is subtle (each worker needs its own PG). Plan or you'll ship with 20-minute PR feedback loops.
- **Playwright e2e in CI on every PR** — flaky by nature. Run smoke in every PR, full suite nightly.
- **No visual regression** for the console. Not required in MVP; noting for BACKLOG.

### Fly.io specifics
- **Sticky sessions for SSE**. Fly's global load balancer does not do sticky routing on POST → response. If you have multiple machines, an SSE connection will land on the machine that started the stream (because it's one HTTP request), but a reconnect might land elsewhere. If you plan to add WebSocket in Sprint 3, this becomes a routing problem — plan `fly-replay` or single-region pinning.
- **Fly Postgres vs. Neon** — plan says Neon. Fine. Confirm Neon's connection pooler mode works with your async SQLAlchemy engine (asyncpg + pgbouncer transaction mode requires care around prepared statements). Test this in Sprint 1 or expect a nasty prod bug.
- **Regional strategy** — Sprint 1 says "US-East single region." Set `primary_region` in `fly.toml` explicitly. Neon is region-pinned; make sure it matches.

### Postgres
- **`pgvector` on Neon**: supported. HNSW index requires manual creation post-table-creation; put it in the migration, not "we'll add it later."
- **Connection limits**: Neon free tier caps concurrent connections. Async SQLAlchemy pool + Fly's multiple machines can blow this. Use Neon's pooled endpoint (not direct) and set `pool_size` conservatively.
- **`org_id UUID` vs. `ULID` as a string**: pick one. ULIDs stored as `TEXT` are slower to index than `UUID`. Store as `UUID` on-disk + present as ULID string in the API. Not decided.
- **Backup strategy**: "Neon PITR for 7 days on free tier" is not documented. Confirm the plan actually gets you 30-day PITR before customers arrive; may require paid tier from Day 1.

### Redis
- **Upstash serverless pricing** is per-request. For a chat workload this is fine. For voice (Sprint 10) with 100 req/s per call, this pricing will surprise you. Plan the pricing threshold now.
- **No eviction policy** documented. Session state must not be evicted; rate-limit buckets must be. Two different Redis usages → probably two different DBs or keyspace prefixes + eviction rules per db.

### Scaling
- **HNSW pgvector on a single machine** will be your first ceiling. Load-test it in Sprint 3 with a realistic corpus.
- **`asyncio` in FastAPI with sync database calls** is a classic footgun. Confirm every DB call is async (`sqlalchemy.ext.asyncio`).
- **SSE fan-out at scale** requires either (a) sticky routing, or (b) a shared bus (Redis Pub/Sub) — plan (b) if you plan to run > 1 machine.

### Security
- **Secrets in Fly**: fine, but no rotation policy exists. Add a Sprint 1 rule: "no secret > 90 days old; rotate on off-boarding."
- **No SBOM / image signing**. `cosign` planned for the long-term but skipped for MVP. Acceptable, but add a note in FINAL_PRE_IMPLEMENTATION_CHECKLIST.
- **CORS-based widget security is broken** (see §2 again — this is important enough to repeat).
- **Clerk webhook signature verification via Svix** — mentioned. Confirm HMAC secret is stored in secret manager not env.
- **Rate limit key**: per-IP is easily defeated with mobile carrier NAT. Per-`(agent_id, IP)` at widget layer + per-`(user_id)` at API layer.

---

## 5. Product Manager Perspective

### Missing user flows
- **Onboarding wizard**: currently punted to Sprint 6. Prospects will churn in Sprint 2 previews if the flow is "log in → blank dashboard → figure it out." Ship the wizard skeleton in Sprint 3 (post-KB).
- **Install flow for the widget**: no plan for what happens between "here's your snippet" and "installed successfully on your site." Need a **verification ping** (widget on load calls back with the origin; console shows green check) — missing.
- **Handoff / owner-notify UX**: what does the owner see when the agent escalates? Email + link to conversation? Slack? Dashboard notification? Not designed.
- **"Test the agent before going live"** playground has no clear separation from prod chat. Owners will accidentally publish an untested version. Need a **staging vs. published** distinction in the UX from Sprint 2.
- **Agent versions UX**: the plan versions everything, but doesn't say how the owner sees or reverts them. Draft → Publish → Draft is confusing without a visible "current live version" indicator.
- **Empty states**: no dashboard, no first-run experience, no sample data / demo agent. Every customer's first minute is empty and confusing. Plan **an auto-created "Demo Agent"** on org creation.

### Missing retention features
- **Weekly digest email is the #1 retention lever** and it's in Sprint 12. Pull to Sprint 6.
- **In-app "here's what the AI did this week"** widget. 60 seconds of dev work in Sprint 7; huge felt value.
- **Owner Slack notifications** for handoffs — table stakes for owners who use Slack. Sprint 8-ish.
- **"Missed booking alert"** when a conversation stalls without a booking — proactive intervention prompt. High-value; not planned.

### Confusing UX (design smells)
- **"Agents" as top-level** vs. "AI Employees" branding — you use both. Pick one word. If the product is "AI Employees," the console noun should be "Employees" — otherwise you're selling one thing and shipping another.
- **`playground` as a channel value** is developer-flavored. Owners will not understand. Rename in UX layer ("Test Chat").
- **"Draft / Testing / Review / Approved / Published / Deprecated / Archived"** — 7 states. For MVP, ship Draft / Published. Ship the rest on demand.
- **Prompt textarea as the primary editor** — power users love it, SMB owners will fear it. Ship a **form-based agent editor** with "Advanced" toggle in Sprint 5.

### MVP scope violations (planned but should not ship in MVP)
- Custom persona / voice presets (Sprint 10) — voice is deferred; personas can be deferred with it.
- Cost dashboards per tenant (Sprint 12) — you need the *internal* cost tracking (Sprint 6, per Readiness Report), not per-tenant dashboards.
- Reviewer console (Sprint 7) — too early. Ship a "sessions list" only. Full reviewer console is Sprint 10+.
- Prompt versioning UI (implied Sprint 5+) — MVP is a save button + list. No diff view yet.

---

## 6. Security Engineer Perspective

### Multi-tenancy
- **RLS enforcement in Sprint 5 is 4 weeks too late.** Ship RLS enabled in Sprint 1, even in `permissive` mode, so the policies exist and get exercised. Retrofitting RLS into 30+ tables and 60+ endpoints in Sprint 5 is a 2-week project you're pretending is a 2-day project.
- **`TenantScopedSession` wrapper** is not enforceable without a lint rule. Write the rule (`ast_grep` or a Ruff plugin) in Sprint 1 or it will be violated in Sprint 3.
- **Cross-tenant leakage test harness** should be in Sprint 1. The Readiness Report already flagged this; keep it flagged.

### Authentication
- **Clerk JWT verification via `clerk-sdk-python`** — check maintenance status (community SDK, not officially Clerk-blessed). If unmaintained, verify JWTs manually via JWKS (well-documented; ~100 lines). Not a blocker, but a due-diligence item.
- **Clerk webhook** carries authoritative user/org creation. If the webhook fails and retries silently, you have users who logged in but don't exist in your DB. Plan a **lazy upsert on first authenticated request** as a backstop.
- **Session token TTL** not specified. Clerk defaults are fine; document them.

### Authorization
- **Roles: owner / member**. Fine. But: what can a member do? Not defined. You will invent this on the fly; do a 30-minute matrix in Sprint 1.
- **API keys** issued via console. Scopes as `JSONB`. No scope enforcement is planned. **Do not ship API keys in Sprint 1** — remove until you actually need them (Sprint 5+). Every unauthorized-scope test that gets skipped is a future CVE.

### Audit log
- **`audit_log.diff JSONB`** for every mutating action — good intent, ships nothing in Sprint 1. Add a **decorator** in Sprint 1 that logs create/update/delete on every service module. If you don't do it in Sprint 1, you never will.
- **No immutability guarantee**. `DELETE FROM audit_log` will work. For MVP fine; document for SOC 2 later.

### Secrets
- **Env vars in Fly** are OK. **`.env.example`** committed is good practice. **Real `.env`** must be in `.gitignore` and enforced by pre-commit hook. Not specified.
- **Local dev secrets** in a `.env` file — trivial leakage risk if a laptop is compromised. Consider `direnv` + `sops` for team.

### Compliance
- **HIPAA-lite** framing needs actual legal review before going on the website. "HIPAA-friendly" without a BAA is a red flag that plaintiffs' lawyers look for. Draft language must be lawyer-approved.
- **DPA / privacy policy** — not scoped anywhere. Blocking for first paying customer.
- **AI disclosure** — bot must self-identify. Not enforced in prompt template.
- **Consent for data processing** — signup flow needs a "you agree that we send your uploaded content to OpenAI/Anthropic for processing" clause. Currently missing.

### Prompt injection (OWASP LLM Top 10)
- **LLM01 Prompt injection**: mentioned; mitigation is "input classifier + output validator." Neither is built in MVP. Ship the **cheap mitigations from Sprint 2**: (a) delimiter-wrap all user input in system prompt (`<user_input>...</user_input>`), (b) instruct model to ignore instructions inside user tags, (c) refuse tool calls whose args are copy-pasted from user input verbatim. All are string-manipulation, no ML required.
- **LLM02 Insecure output handling**: KB content rendered in agent responses may contain prompt injections. Wrap KB snippets in `<kb_context>` tags and instruct the model to treat them as untrusted content. Missing.
- **LLM06 Sensitive info disclosure**: no PII scrubber runs before embeddings. A patient uploads a PDF with SSNs; those SSNs end up in Qdrant/pgvector, and later in prompts, and later in Sentry traces. Ship a **presidio-lite** scrubber in the ingestion pipeline in Sprint 2.
- **LLM08 Excessive agency**: `create_booking` tool has no confirmation step. Model can invent a booking on a hallucination. Require **explicit user confirmation** ("You want me to book Wed 3pm — confirm?") before the tool fires. Ship in Sprint 4.
- **LLM10 Model theft** & **LLM09 Overreliance**: post-PMF concerns.

---

## 7. VC Technical Due Diligence

**Sequoia investing $10M. Would I approve?**

**Answer:** With significant conditions.

### What I'd approve
- Well-thought-out architecture with genuine long-term design.
- Clear positioning against known competitors.
- Honest technical debt tracking.
- Realistic cost model.
- Founder shows senior-level product + technical thinking.

### What would block investment
1. **Zero customer conversations.** Sequoia expects at least 20 real prospect interviews before Series A term-sheet. Even seed rounds now require this. **The project has zero.** This alone would push a check to "come back when you have 5 LOIs."
2. **Solo engineering team building a platform.** Not a red flag on its own, but paired with the 24-doc architecture, it signals over-engineering risk. VCs will ask: "why didn't you ship a Chatbase clone in 2 weeks and iterate from there?"
3. **Vertical is chosen from a matrix, not from experience.** Founder has no healthcare background disclosed. Sequoia will ask: "why you? why now? why this vertical?" There is no compelling answer in the docs.
4. **Voice deferred despite competing category being voice-first.** Reasonable technically. Fundraising-wise, it will be second-guessed ("Retell/Vapi are voice — are you sure chat is enough for healthcare?"). Founder needs a rehearsed answer.
5. **No moats articulated.** "Vertical templates," "unified runtime," "outcomes not tokens" — all reasonable *positioning*, none are *moats*. A moat is switching cost + data feedback loop + network effects. The docs hint at organizational memory + marketplace but don't build the moat mechanic.
6. **No fine-tuning / proprietary model story.** VCs will ask when you cross the LLM-cost-margin curve. Vague answer in the cost estimation doc ("vertical fine-tunes at Y2"). Acceptable if founder has strong personal ML depth; concerning if not.
7. **HIPAA-lite** is a legal risk they will flag. Health-vertical + no formal BAA = "come back with legal opinion."
8. **Team of 2.** Fine for pre-seed. Not fine for a $10M Series A. Need a hiring plan validated against milestones.

### My recommendation as VC
- **Pre-seed ($1–2M)**: yes, on condition of 10 signed LOIs from clinics within 60 days.
- **Seed ($3–5M)**: no. Get to $30k MRR first with the pre-seed.
- **$10M Series A**: no. Not remotely at this stage.

The plan pretends this is a seed-ready company. It's a pre-seed-ready plan.

---

## 8. Competitor Review

### Missing competitive advantages
- **Vertical data feedback loop**. Retell/Vapi don't own vertical data. You could — but only if you build it explicitly. Currently the eval + memory strategy would make this possible; nothing in the plan makes it explicit as a moat.
- **Integrations depth**. Salesforce Agentforce wins by owning Salesforce. You need to win by owning **one PMS/POS/EHR per vertical** deeply. Dentrix integration in Sprint 9 is a start; there's no serious integration roadmap.
- **Community / creator ecosystem**. Voiceflow's real moat is the community of designers. You have no plan for this until Y2 marketplace. Start Discord + template community in Y1.
- **Speed to first agent**. Retell is < 5 minutes with a template. Your plan is "onboarding wizard in Sprint 6." That's 12 weeks late.
- **Voice quality benchmark**. Retell publishes latency numbers publicly. You will need to match by Y1 end.
- **Developer story**. OpenAI Agents SDK + Cursor + Claude Code have made "build your own agent" nearly free for developers. Your SDK plan is a Sprint-13 afterthought. Either commit to developers or explicitly abandon them.

### Where you should NOT compete
- **Voice latency wars** — Retell will always be faster on pure voice benchmarks; you win on outcomes + omnichannel.
- **Model quality claims** — you are a router, not a model builder.
- **Enterprise contact-center replacement** — Genesys/NICE will crush you on procurement. Wedge in below them.
- **General-purpose agent framework** — LangChain/LlamaIndex own that.
- **Consulting / white-glove implementations** — kills margins. Refuse.

---

## 9. Delete List (before Sprint 1)

Trim aggressively. Every item below either delays revenue or invites overengineering.

**Delete from Sprint 1:**
- `AgentRuntime` abstraction wrapper over LangGraph — use LangGraph directly.
- LangGraph itself in Sprint 1 — single-node "graph" is a function; add LangGraph Sprint 2/3.
- API Keys UI + endpoints — no public API in Sprint 1.
- Multi-provider LLM config — one provider + hard-fail.
- Multi-arch Docker builds — amd64 only.
- `packages/shared-py` — one Python service; extract when needed.
- Structured audit log decorator scope beyond user/org/agent CUD — expand later.
- Sentry + PostHog + Axiom simultaneously — Sentry only in Sprint 1; add PostHog Sprint 3, Axiom Sprint 6.
- Preview Postgres per PR — share a preview DB with per-PR schema for MVP.
- `apps/widget` (as a separate app scaffold) — start as an iframe route in `apps/console`.
- `apps/landing` — use Framer / Webflow.
- `packages/sdk-python` — do not scaffold until Sprint 13 realistically.
- Any UX for "Draft / Testing / Review / Approved / Deprecated / Archived" — Draft + Published only.

**Delete from Sprint 2–5 planning:**
- Autogenerated OpenAPI-typescript pipeline in Sprint 2 — do it Sprint 4 when the surface stops thrashing.
- Cohere reranker mention in Sprint 5 — not for months.
- Vertical template gallery — one template hardcoded through Sprint 8.
- Handoff to human via Zendesk/Intercom in Sprint 4 — email notification only until customer asks.
- MCP client mode in tool framework Sprint 4 — Y2 problem.

**Delete from BACKLOG.md:**
- Sprint 13 (Public API + SDK) — reactivate on developer demand only.
- Sprint 18 (Long-term memory) — reactivate when data shows repeat users are top-3 request.
- All voice sprints (10, 11) if healthcare cold outreach reveals chat-first is acceptable — otherwise keep.

---

## 10. Missing Documents

Only add documents that reduce risk *before Sprint 1*. Everything else is procrastination.

### Must exist before Sprint 1 (small, high-leverage)
- **`DATA_MODEL.md`** — one canonical table + column dictionary. ID prefix table. Ownership map. **Currently scattered across 5 docs and drift-prone.** ~2 pages.
- **`API_GUIDELINES.md`** — endpoint naming, versioning, error format, pagination, idempotency rules, streaming conventions. **Currently in API_DESIGN.md as long-term aspirations, not MVP rules.** ~2 pages.
- **`ERROR_HANDLING.md`** — one page. Problem+JSON shape, error codes taxonomy, retryable vs. not, SSE error events.
- **`PROMPT_ENGINEERING_GUIDE.md`** — one page. Composition order, delimiters (prompt injection defense), citation format, output format per channel.
- **`SECURITY_CHECKLIST.md`** — one page. Pre-launch security must-dos (RLS on, PII scrub, no secrets in logs, HTTPS everywhere, signed webhooks, secure cookies, CSRF, HSTS).

### Small, ships anytime in first month
- **`OBSERVABILITY_GUIDE.md`** — required log fields, span attributes, correlation IDs, PII redaction rules for logs. One page.
- **`RELEASE_PROCESS.md`** — how a change reaches prod, who approves, rollback playbook. One page.
- **`RUNBOOK.md`** — SEV1/SEV2 response, on-call, top 5 alerts and their remediation. Grows over time.

### Deliberately NOT recommended (would be overengineering)
- Full `AGENT_RUNTIME_SPEC.md` — `AGENT_ENGINE.md` in `docs/` is enough for now.
- `TESTING_PLAYBOOK.md` — `TESTING_STRATEGY.md` covers it.
- `DESIGN_SYSTEM.md` — shadcn/ui is your design system for MVP.
- `COMPLIANCE_HANDBOOK.md` — until first regulated customer.
- `ADR-000-template.md` etc. — ADR shape is already in `ARCHITECTURE_DECISIONS.md`.

---

## 11. Architecture Scorecard

Independent scoring. These are lower than the internal self-review's — that's the point of an independent review.

| Area | Score | Note |
|---|---|---|
| Product | 78 | Strong theory, zero customer validation. Positioning solid; personas unvalidated. |
| AI | 74 | Sound choices; over-abstracted for solo team; missing prompt registry + injection hardening. |
| Backend | 82 | Solid FastAPI + Postgres + Redis foundation; module discipline requires enforcement. |
| Frontend | 74 | Next.js is fine; widget-as-separate-app is premature; onboarding UX missing. |
| DevOps | 76 | Fly.io + Neon + Upstash is right; migration + preview infra + rollback are underspecified. |
| Security | 68 | RLS deferral risky; CORS-as-security wrong; PII pipeline missing; prompt injection unmitigated in MVP. |
| Scalability | 80 | Long-term plan is credible; MVP shortcuts have honest triggers. |
| Maintainability | 78 | Excellent standards on paper; enforcement mechanisms sparse. |
| Developer Experience | 82 | Monorepo layout is clean; local dev < 5 min goal is realistic. |
| Startup Execution | 62 | Two-person team + 24-doc arch + 20-sprint backlog + zero customer conversations = execution risk. |
| **Overall** | **75** | Buildable, but needs a handful of hard cuts before Sprint 1. |

---

## 12. Final Verdict

# B — Needs Minor Fixes

Not "A — Ready to Build." The plan is a strong 8-out-of-10 architecture undermined by 5–7 specific pre-implementation gaps that will cost weeks if not addressed in the next 3 days.

**Fix these and start Sprint 1:**

1. **Talk to 10 clinics in the next 7 days.** Any planning conclusions revised by those conversations override any doc.
2. **Delete the items in §9 Delete List.**
3. **Move RLS enablement + cross-tenant test harness to Sprint 1.**
4. **Move the weekly-digest email to Sprint 6.**
5. **Write the 5 missing docs listed in §10 "Must exist before Sprint 1."**
6. **Sign off on the ambiguous decisions** (Clerk vs. our org, ULID vs. UUID storage, `tenant_id` vs. `org_id` naming, cancellation contract, session-version pinning).
7. **Draft prompt-injection mitigation stubs** (delimiter wrapping, `<kb_context>` tags, `<user_input>` tags) into the Sprint 2 KB plan.
8. **Draft embed-token model** for widget origin binding (replace CORS-as-security).
9. **Ship legal boilerplate** (ToS/Privacy/DPA/AUP + AI-disclosure copy) before first paying customer, drafted by the founder in Sprint 4–5 for review.

Every item above is 1–4 hours of work. Together they turn a **B** into an **A**.

See [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) for the exhaustive, dated list.

---

## A Word to the Founder

Your docs are more mature than 90% of what walks through a VC's door. They are also longer than 100% of what the successful ones write pre-code. The dangerous thing about good planning is that it feels like progress. It isn't. **The unit of progress is a customer who paid you, or a decision that was wrong you now understand better.** Neither is generated by another Markdown file.

Start Sprint 1 with the fixes above, and give yourself a hard rule: **no new planning doc for 60 days.** Anything you think of writes to `BACKLOG.md` as a bullet. If it survives 60 days without being obvious it needed to be written, then write it.
