# FINAL PRE-IMPLEMENTATION CHECKLIST

Everything that must be done **before the first commit** to `services/api` or `apps/console`. This is short by design. If it were long, we'd be planning again instead of building.

Estimated total effort: **3–4 focused days** for founder + engineer combined.

Legend: 👤 = founder · 🛠 = engineer · 👥 = both

---

## Section A — Business & Customer (do this FIRST)

- [ ] **A1 👤 Book 10 clinic / dental-practice discovery calls for the next 14 days.** Any single call reveals more than a week of planning. If you can't get 10 calls in 7 days from cold, the vertical or the pitch is wrong — solve *now*, not in Sprint 5.
- [ ] **A2 👤 Write the one-sentence discovery-call script** ("I'm building X for practices like yours; can I ask you 10 questions about how you handle after-hours inquiries?"). Save in `/notes/discovery_script.md` (not committed).
- [ ] **A3 👤 List 20 named target clinics** (practice name, owner name, contact channel). Save in your CRM / spreadsheet.
- [ ] **A4 👤 Validate pricing on the first 3 calls.** Ask "if a tool booked X extra patients a month, what would that be worth to you?" Adjust $199 / $499 before shipping the Stripe integration.
- [ ] **A5 👤 Draft positioning sentence in 12 words or fewer**, tested verbally on 3 non-technical people. Owns landing page and cold email copy.
- [ ] **A6 👤 Draft ToS + Privacy + AUP + AI-disclosure boilerplate** using Termly / Iubenda / Rocket Lawyer. Do not launch to a paid user without lawyer sign-off; can start with boilerplate.
- [ ] **A7 👤 Working agreement (one page)**: weekly rhythm, decision authority, on-call division, no-fix-after-11pm rule, "no new planning doc for 60 days" rule.

## Section B — Delete List (execute the review's §9)

- [ ] **B1 🛠 Remove from Sprint 1 plan**: `AgentRuntime` wrapper, LangGraph (defer to Sprint 2), API Keys UI + endpoints, multi-provider LLM config, multi-arch Docker, `packages/shared-py` scaffold, `apps/widget` scaffold, `apps/landing` scaffold, `packages/sdk-python`.
- [ ] **B2 🛠 Update `SPRINT_1.md`** to reflect deletions (do NOT delete the file; annotate the changed items).
- [ ] **B3 🛠 Trim `BACKLOG.md`** — mark Sprint 13 (Public API/SDK) and Sprint 18 (Long-term memory) as "on-demand only."
- [ ] **B4 👥 Confirm collapsed observability stack**: Sentry only in Sprint 1; PostHog Sprint 3; Axiom Sprint 6. Update `.env.example` accordingly.

## Section C — Ambiguous Decisions to Freeze (sign-off, then document as ADRs)

Add one-line ADRs to [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) for each:

- [ ] **C1 👥 ADR-041**: canonical name is **`org_id`** everywhere (not `tenant_id`). Rewrite mismatched references in `docs/` on first PR touching them (not upfront).
- [ ] **C2 👥 ADR-042**: Postgres ID column type = **`UUID`** on-disk, ULID **presentation-only** in API. Store as `UUID`, wrap ULID/UUID conversion in a `packages/shared` helper (or `services/api` `platform/ids.py`).
- [ ] **C3 👥 ADR-043**: **ID prefix table** frozen (`org_`, `usr_`, `mem_`, `key_`, `agn_`, `agv_`, `cor_`, `doc_`, `chk_`, `ses_`, `tur_`, `tol_`, `bnd_`, `con_`, `inv_`, `evt_`, `evr_`, `sub_`, `usg_`, `aud_`). Publish in `DATA_MODEL.md`.
- [ ] **C4 👥 ADR-044**: **Clerk owns identity + membership. Our DB owns entitlement + billing + agent state.** Overlap fields: name, email — replicated to our DB on webhook, but Clerk is source of truth. Never write to Clerk from our DB.
- [ ] **C5 👥 ADR-045**: **Sessions are pinned to `agent_version_id` at start.** Mid-session publishes do not affect running sessions.
- [ ] **C6 👥 ADR-046**: **SSE cancellation contract.** On client disconnect: (a) LLM stream `abort()`, (b) assistant turn persisted with `end_reason='client_cancel'` and whatever partial content was streamed, (c) token counts reflect what was actually generated.
- [ ] **C7 👥 ADR-047**: **LangGraph checkpointer OR our Redis short-term state — not both.** Choose one; document. Recommended: our Redis + Postgres; do NOT enable LangGraph's checkpointer.
- [ ] **C8 👥 ADR-048**: **Embed-token model** for widget origin binding. Each customer gets a `widget_public_key` + optional allowed-origin list; loader script issues a short-lived signed JWT bound to origin + agent_id + IP; endpoint validates. CORS remains, but is not the security boundary.

## Section D — Missing Docs (must exist before Sprint 1)

Each is 1–2 pages. Do NOT write novels.

- [ ] **D1 🛠 `docs/DATA_MODEL.md`** — canonical table list, column dictionary, ID prefix table, ownership map, RLS policy template.
- [ ] **D2 🛠 `docs/API_GUIDELINES.md`** — endpoint naming, versioning, error format (Problem+JSON), pagination (cursor), idempotency rules, SSE event conventions, rate-limit headers.
- [ ] **D3 🛠 `docs/ERROR_HANDLING.md`** — error code taxonomy, retryable vs. permanent, SSE error events, user-facing vs. internal messages.
- [ ] **D4 🛠 `docs/PROMPT_ENGINEERING_GUIDE.md`** — composition order, delimiter tags (`<user_input>`, `<kb_context>`, `<tool_result>`), citation format, channel-aware output rules, prompt-injection defenses.
- [ ] **D5 🛠 `docs/SECURITY_CHECKLIST.md`** — pre-launch must-dos (RLS enabled, PII scrubber on ingestion, no PII in logs, HTTPS everywhere, signed webhooks, HSTS, secure cookies, CSRF, pre-commit gitleaks).
- [ ] **D6 🛠 `docs/OBSERVABILITY_GUIDE.md`** — required log fields, trace/span attributes, correlation IDs, PII redaction rules for logs.
- [ ] **D7 🛠 `docs/RELEASE_PROCESS.md`** — how a change reaches prod, approval, rollback command (`fly releases rollback`), migration policy (expand/contract).
- [ ] **D8 🛠 `docs/RUNBOOK.md`** — stub with top 5 anticipated incidents: LLM provider down, Postgres pool exhausted, Fly machine crash, Clerk webhook failure, unauthenticated widget flood.

## Section E — Sprint 1 Scope Corrections

- [ ] **E1 🛠 Move to Sprint 1** (from later): Postgres RLS enabled in permissive mode from migration `0001`; a cross-tenant leakage test that creates 2 orgs and asserts isolation on every endpoint.
- [ ] **E2 🛠 Move to Sprint 1**: PII log-redaction middleware (regex for email/phone/CC) + Sentry `before_send` scrubber.
- [ ] **E3 🛠 Move to Sprint 1**: pre-commit hooks (gitleaks, ruff, ruff-format, mypy on changed files, prettier, eslint).
- [ ] **E4 🛠 Move to Sprint 1**: import boundary lint rule (`ast-grep` or `import-linter`) enforcing `services/api/modules/*` cannot cross-import except via `ports.py` — even if `ports.py` files are empty for now.
- [ ] **E5 🛠 Move to Sprint 1**: Alembic `up → down → up` on fresh DB in CI.
- [ ] **E6 🛠 Move to Sprint 1**: `pgvector` extension enabled + a dummy `chunk` table with a HNSW index (not used yet), so Sprint 2 doesn't debug pgvector in production.
- [ ] **E7 🛠 Remove from Sprint 1**: LangGraph integration (defer to Sprint 2 when the second node exists). Sprint 1's runtime is a single async function calling LiteLLM directly.
- [ ] **E8 🛠 Remove from Sprint 1**: API key generation UI + endpoints.
- [ ] **E9 🛠 Remove from Sprint 1**: `Idempotency-Key` on the SSE endpoint. Keep it for `POST /v1/agents` and any future mutating endpoints.

## Section F — Infrastructure Prep

- [ ] **F1 👤 Buy domain + set up Google Workspace + set up business email.**
- [ ] **F2 👤 Create accounts + capture API keys**: Clerk (Pro trial), OpenAI, Anthropic, Neon, Upstash, Cloudflare (R2), Fly.io, Sentry, Resend (or Postmark), GitHub org.
- [ ] **F3 👥 Set up GitHub org** with branch protection on `main`, required reviews, signed commits recommended.
- [ ] **F4 🛠 Add repository secrets**: `FLY_API_TOKEN`, `NEON_API_KEY`, `UPSTASH_TOKEN`, `SENTRY_AUTH_TOKEN`.
- [ ] **F5 🛠 Verify Neon pooled endpoint** works with async SQLAlchemy + asyncpg (prepared-statement gotcha). One 10-line script; run it before Day 1.
- [ ] **F6 🛠 Verify Fly.io region + Neon region match** (both `iad` or both `ord`); document in `infra/fly/README.md`.
- [ ] **F7 🛠 Enable Neon PITR (30 days)**. Confirm plan tier allows it; upgrade if not.
- [ ] **F8 🛠 Set Upstash to `noeviction` on the session-state DB; `allkeys-lru` on the cache DB**. Use two separate DBs.

## Section G — Security Hardening (day-zero minimums)

- [ ] **G1 🛠 Enable HSTS + secure cookies + SameSite=Lax on the console** in Sprint 1's Next.js middleware.
- [ ] **G2 🛠 Svix HMAC verification** on Clerk webhook (do not skip signature check even in dev).
- [ ] **G3 🛠 gitleaks pre-commit hook + GitHub secret scanning enabled.**
- [ ] **G4 🛠 SBOM (`syft`) generated on every image build** and stored as release artifact. (Signing with `cosign` optional in MVP.)
- [ ] **G5 🛠 Rate limits at API gateway**: per-IP (60/min for auth endpoints, 300/min for read, 60/min for chat/session write) using `slowapi` or Upstash rate-limit primitives.

## Section H — LLM & Prompt Hygiene

- [ ] **H1 🛠 Hard timeouts**: LiteLLM `timeout=20` (chat), `timeout=60` (embeddings). No exceptions.
- [ ] **H2 🛠 System prompt template split**: static prefix (agent persona, safety, tool list) + dynamic suffix (user input, memory). Structured for future prompt caching.
- [ ] **H3 🛠 Delimiter defense**: wrap all user input in `<user_input>...</user_input>` and instruct the model to treat instructions inside those tags as data, not commands. Ship in Sprint 1's system prompt.
- [ ] **H4 🛠 Token cap per response** (e.g., 800 tokens) enforced in LiteLLM call — no unbounded generation.
- [ ] **H5 🛠 Model default: `gpt-4o-mini`**. No fallback in Sprint 1. Fallback added Sprint 4 after one month of prod signal.

## Section I — Observability Baseline

- [ ] **I1 🛠 Sentry initialized in API + console** with `before_send` PII scrubber.
- [ ] **I2 🛠 Every request carries a `request_id` header + is included in every log line.**
- [ ] **I3 🛠 Every DB query includes `org_id` filter** (verified by SQLAlchemy event hook that logs a warning if a query on a tenant table lacks `org_id`).
- [ ] **I4 🛠 `/healthz` (liveness) + `/readyz` (DB + Redis + LLM ping)** — both cheap.

## Section J — Definition of Done for the Checklist Itself

- [ ] **J1 👥** All of Section A completed.
- [ ] **J2 👥** All of Sections B, C, D, E completed (or explicitly deferred with a written justification).
- [ ] **J3 👥** All of Sections F, G, H, I completed at least to the "verify the tool exists" level.
- [ ] **J4 👥** Both founder and engineer have re-read `SPRINT_1.md` in its post-fix form and signed off in `notes/sprint1_signoff.md`.
- [ ] **J5 👤** At least 3 clinic discovery calls **completed** (not just scheduled). Findings written up in `notes/customer_discovery.md`.

---

## Time-Boxed Plan (5 elapsed days)

| Day | 👤 Founder | 🛠 Engineer |
|---|---|---|
| Mon | A1, A2, A3, A5, F1 | B1, B2, B3, D1, D2 |
| Tue | A1 (calls), A6 draft | D3, D4, D5, E7, E8, E9 |
| Wed | A1 (calls), A4, A7 | E1, E2, E3, E4, E5, E6 |
| Thu | A1 (calls) → J5 | F2–F8, G1–G5 |
| Fri | signoff + kickoff prep | H1–H5, I1–I4, J1–J4 |

Sprint 1 begins Monday of Week 2.

---

## Sprint 1 Kickoff Prompt (paste into Claude Code AFTER this checklist is green)

```
You are the sole engineer implementing Sprint 1 of the Vertical AI Agent Platform.

Sources of truth (in strict priority order):
1. SPRINT_1.md (scope — do not exceed)
2. FINAL_PRE_IMPLEMENTATION_CHECKLIST.md (frozen decisions from Section C, corrections from Section E)
3. REPOSITORY_STRUCTURE.md (folder layout)
4. docs/DATA_MODEL.md, docs/API_GUIDELINES.md, docs/ERROR_HANDLING.md, docs/PROMPT_ENGINEERING_GUIDE.md, docs/SECURITY_CHECKLIST.md, docs/OBSERVABILITY_GUIDE.md
5. MVP_IMPLEMENTATION_PLAN.md (rationale reference only, not scope)

Overrides from the pre-implementation review (apply first):
- DELETE from Sprint 1: LangGraph integration, API keys UI/endpoints, multi-provider LLM config, multi-arch Docker, packages/shared-py scaffold, apps/widget scaffold, apps/landing scaffold, Idempotency-Key on SSE endpoint.
- ADD to Sprint 1: Postgres RLS enabled from migration 0001; cross-tenant leakage test harness; PII log-redaction middleware; import-boundary lint rule; pgvector extension + dummy table + HNSW index; system-prompt delimiter defense (<user_input> tags); hard LLM timeouts (20s chat).
- Frozen decisions: org_id everywhere (not tenant_id); UUID on-disk with ULID presentation; Clerk owns identity + membership, our DB owns entitlement; sessions pinned to agent_version_id at start; SSE cancellation persists partial assistant turn with end_reason='client_cancel'.

STRICT RULES
1. Do only what is in SPRINT_1.md after the DELETE/ADD overrides above. Any tempting extra goes into BACKLOG.md — not implemented.
2. Every tenant table has org_id + RLS policy from migration 0001.
3. Never log PII (email, phone, message content) at INFO level.
4. Every mutating endpoint has an audit log entry.
5. Alembic migrations reversible; CI runs up → down → up.
6. All DB access async (asyncpg via SQLAlchemy async engine, pooled Neon endpoint).
7. No LangGraph. No API keys. No widget. No RAG. No tools. No billing. No voice. Those are later sprints.
8. Ask before adding any dependency not explicitly implied.

DELIVERABLE
A cold laptop runs: git clone → cp .env.example .env → make dev, and within 5 minutes a signed-in user in their own org can create an agent, send a message, and see a streamed LLM response — with real Postgres (RLS on) + Redis + FastAPI + Next.js. Every PR gets a preview deploy on Fly.io. Main auto-deploys to prod.

HOW TO WORK
1. Read SPRINT_1.md + FINAL_PRE_IMPLEMENTATION_CHECKLIST.md end to end.
2. List the exact deviations from the original SPRINT_1.md caused by the review overrides.
3. Propose the first 3 commits as a file list with purpose. Wait for approval.
4. After each deliverable (D1–D13), STOP, summarize, and request review.
5. When the Exit Checklist is fully green, STOP. Do not begin Sprint 2 without explicit approval.

Begin by reading SPRINT_1.md and FINAL_PRE_IMPLEMENTATION_CHECKLIST.md and reporting the delta, plus any clarifying questions.
```
