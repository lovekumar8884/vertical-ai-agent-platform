# CHANGELOG — INDEPENDENT REVIEW ACCEPTANCE

Every recommendation from [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md) and [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) is triaged here.

Legend: **A** = Accepted · **P** = Partially Accepted · **R** = Rejected.

Any item marked **A** or **P** is applied in [ARCHITECTURE_FREEZE_V1.md](ARCHITECTURE_FREEZE_V1.md) and/or [SPRINT1_FINAL_SCOPE.md](SPRINT1_FINAL_SCOPE.md). No source document is edited retroactively — this changelog is the diff.

---

## Section 1 — Startup Founder Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 1.1 | Talk to 10 clinics in the next 7 days before further building | **A** | Zero customer input is the single largest project risk | FREEZE §11, CHECKLIST §A |
| 1.2 | Delete Sprint 1 items: `AgentRuntime` wrapper, LangGraph, API keys, multi-provider LLM config, multi-arch Docker, `packages/shared-py` scaffold, `apps/widget` scaffold, `apps/landing`, `packages/sdk-python` | **A** | All non-essential; each violates minimum-surface principle | FREEZE §4, SPRINT1_FINAL |
| 1.3 | Delete over-abstraction of "11-pillar AI Employee model" as a Sprint-1 canonical schema | **P** | The model stays valid **as long-term intent**; not encoded as a schema until Sprint 5 template. Sprint 1 uses only fields it needs. | FREEZE §5 |
| 1.4 | Delete `apps/landing` (use Framer/Webflow) | **A** | Two frontends kill a two-person team | FREEZE §3, SPRINT1_FINAL |
| 1.5 | Delete `apps/widget` as its own Vite bundle in MVP; inline as iframe route in `apps/console` | **A** | Widget separation is a Sprint 3+ optimization | FREEZE §3 |
| 1.6 | Remove marketplace, Y2/Y3 roadmap items from active thinking | **P** | Long-term docs retain them as **vision** (not roadmap). Not deleted; not part of Sprint 1–20 scope. | BACKLOG unchanged; FREEZE §12 |
| 1.7 | Move weekly-digest email from Sprint 12 → Sprint 6 | **A** | Highest retention lever per unit of engineering | BACKLOG §S6 (annotation), FREEZE §12 |
| 1.8 | Sprint 3 widget = iframe pointing to an existing Next.js route (no separate app) | **A** | Same as 1.5 | FREEZE §3 |
| 1.9 | Presenting a 40-week roadmap is fiction; re-cut monthly | **P** | Backlog remains as ordering intent, not commitment. Explicitly labeled "re-cut monthly." | BACKLOG unchanged; note added via FREEZE §12 |

---

## Section 2 — Principal Software Architect Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 2.1 | Delete `packages/shared-py` scaffold in MVP | **A** | One Python service; extract when second exists | FREEZE §3 |
| 2.2 | Delete `packages/sdk-python` from MVP planning | **A** | No developer audience yet | FREEZE §3 |
| 2.3 | Skip `ports.py` for `iam`, `billing`, `notifier`; keep for `runtime`, `knowledge`, `tools` | **A** | Draw seams only where extraction is realistic | FREEZE §3, §6 |
| 2.4 | Delete `AgentRuntime` abstraction wrapper over LangGraph | **A** | Leaky, does not help swap; LangGraph used directly when introduced Sprint 2 | FREEZE §5, §7, ADR-006 note |
| 2.5 | Do not encode the 11-pillar model as canonical schema in Sprint 1 | **A** | See 1.3 | FREEZE §5 |
| 2.6 | Add explicit trigger for splitting pgvector out (e.g., > 2M chunks/tenant or > 200 ms p95) | **A** | Concrete measurement, not vibes | FREEZE §8, ADR-011 refinement |
| 2.7 | Clarify Clerk vs. our DB source-of-truth boundary | **A** | Removes drift bugs | FREEZE §9, new ADR-044 |
| 2.8 | Define Redis→Postgres reconciliation for session state | **A** | Race safety | FREEZE §7 |
| 2.9 | Replace CORS-as-security on widget with signed embed token | **A** | Real security control | FREEZE §10, new ADR-048 |
| 2.10 | Freeze `org_id` naming (not `tenant_id`) | **A** | Prevent cross-doc drift | FREEZE §9, new ADR-041 |
| 2.11 | Document full ID prefix table | **A** | Prevent inconsistent prefixes | FREEZE §9 |
| 2.12 | Store IDs as `UUID` on-disk, present as ULID string in API | **A** | Index performance + ergonomics | FREEZE §9, new ADR-042 |
| 2.13 | Version `agent_version.spec JSONB` via typed Pydantic per version | **P** | For Sprint 1: single Pydantic model + `spec_schema_version` int on the row. Migration tooling deferred until v2 of spec. | FREEZE §7 |
| 2.14 | GitHub Actions path filters so TS and Python don't build each other's changes | **A** | CI speed | FREEZE §11, SPRINT1_FINAL D10 |
| 2.15 | `turn.role` needs `tool_call` and `tool_result` values (or structured content) | **A** | Required for tools sprint | FREEZE §9 |
| 2.16 | Session pinned to `agent_version_id` at start; publishes mid-session don't affect it | **A** | Deterministic behavior | FREEZE §7, new ADR-045 |
| 2.17 | Add placeholder `contact` and `memory_facts` tables now (empty), so future sprints don't reshape | **R** | Adds noise without benefit; empty tables invite premature use. Reserve in DATA_MODEL notes only. | FREEZE §9 |
| 2.18 | Cap `audit_log.diff JSONB` size; overflow to R2 | **P** | Cap at 32 KB in Sprint 1; overflow-to-R2 is Sprint 8+. | FREEZE §9 |
| 2.19 | Design entitlement / feature-flag data model now | **P** | Add `entitlements JSONB` column on `org` in Sprint 1 (single JSON blob). Full entitlement table when billing lands (Sprint 6). | FREEZE §9 |
| 2.20 | Define SSE cancellation contract | **A** | Prevents billing anomalies + orphan spans | FREEZE §7, new ADR-046 |
| 2.21 | Per-agent concurrency cap defined | **A** | Back-pressure required | FREEZE §7 |
| 2.22 | Remove `Idempotency-Key` from SSE stream endpoint; keep for tool-invoke + admin mutations | **A** | Streaming + idempotency semantics don't compose | FREEZE §10, SPRINT1_FINAL D8 |
| 2.23 | Structure system prompt: static prefix + dynamic suffix (for future prompt caching) | **A** | Cheap; enables future 30–90% savings | FREEZE §7 |
| 2.24 | Hard provider timeouts (chat 20 s, embeddings 60 s) | **A** | Fail fast | FREEZE §7 |

---

## Section 3 — Staff AI Engineer Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 3.1 | Defer LangGraph from Sprint 1 → Sprint 2 (single-node "graph" = a function) | **A** | LangGraph earns weight at ≥ 3 nodes | FREEZE §5, SPRINT1_FINAL D7 |
| 3.2 | Pin LangGraph to a specific minor version when introduced | **A** | Reduce upgrade surprises | FREEZE §7 (Sprint 2 constraint) |
| 3.3 | Choose LangGraph checkpointer OR custom Redis state — not both | **A** | Race-condition prevention | new ADR-047; FREEZE §7 |
| 3.4 | Set explicit trigger for LiteLLM SDK → proxy migration | **A** | Removes ambiguity | ADR-007 refinement |
| 3.5 | Do NOT enable multi-provider fallback in Sprint 1 | **A** | Fallback masks bugs | FREEZE §7, SPRINT1_FINAL D7 |
| 3.6 | Add per-provider integration tests when second provider appears | **A** | Tool-calling parity | FREEZE §7 (Sprint 4 constraint) |
| 3.7 | Ship `prompt_template` table with diff view | **P** | For Sprint 1: `agent_version.system_prompt TEXT` is enough. Full `prompt_template` table + diff UX = Sprint 5. Composition primitives (Jinja2 strict) added Sprint 2 alongside RAG. | FREEZE §9 |
| 3.8 | Adopt Jinja2 (strict undefined) + fixed composition order | **A** | Composition order becomes contract, not accident | FREEZE §7 |
| 3.9 | Codify channel-aware output rules (voice hates markdown) | **P** | Add `channel` variable in prompts. Actual voice-specific output rules land Sprint 10. | FREEZE §7 |
| 3.10 | Make LLM-judge advisory in Sprint 5–7; blocking only after 3 months of judge stability | **A** | Blocking on flaky judges = churned releases | BACKLOG §S7 note |
| 3.11 | Ship "trace-diff" tool in Sprint 6 instead of Sprint 12+ | **A** | Cheap; high-leverage | BACKLOG §S6 note |
| 3.12 | Add corpus size cap (Starter: 200 pages / 100 MB) in Sprint 2 | **A** | Cost control | BACKLOG §S2 note |
| 3.13 | Header-aware chunker for Sprint 5 template | **A** | Medical/legal quality | BACKLOG §S5 note |
| 3.14 | Enforce import boundary: no `unstructured` in API process | **A** | Prevents 3–5 GB image accident | FREEZE §11 |
| 3.15 | Trigger pgvector → Qdrant migration at ~500k chunks/tenant (empirically test in Sprint 3) | **A** | Doc's 10M number is unrealistic for HNSW on 1536d | ADR-011 refinement |
| 3.16 | Measure hit@k from Sprint 3 to build reranker baseline | **A** | Baseline before optimization | BACKLOG §S3 note |
| 3.17 | Plan tool routing (shortlist per turn) by Sprint 7 | **A** | Tool-selection accuracy cliff at ~10 tools | BACKLOG §S7 note |
| 3.18 | Google Calendar edge-case checklist + integration tests in Sprint 4 | **A** | Most common source of "AI booked wrong" | BACKLOG §S4 note |
| 3.19 | Tool `create_booking` idempotency: retry returns existing event (read-back) | **A** | Correctness | BACKLOG §S4 note |
| 3.20 | Add dry-run mode on tools | **P** | Full dry-run harness Sprint 7. Sprint 4 ships `?dry_run=true` on `create_booking` only. | BACKLOG §S4 note |

---

## Section 4 — Infrastructure Engineer Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 4.1 | Aggregate incident notifications across Neon + Upstash + Fly + Clerk | **P** | Sprint 1: single `#alerts` Slack channel with vendor webhooks. Full aggregator Sprint 8. | FREEZE §11 |
| 4.2 | Upstash preview namespacing per PR | **A** | Prevent cross-PR pollution | SPRINT1_FINAL D10, FREEZE §11 |
| 4.3 | Wire `fly releases rollback` into deploy workflow with manual trigger | **A** | Rollback readiness on Day 1 | SPRINT1_FINAL D10 |
| 4.4 | CI check for backward-compatible migrations (`pgroll`/`atlas`) | **R for Sprint 1**, **A for Sprint 5** | Overhead vs. one-engineer at Sprint 1 discipline. Adopt tooling when team > 2. | BACKLOG §S5 note |
| 4.5 | Enable Docker layer caching (buildx + GHA cache) | **A** | CI speed | SPRINT1_FINAL D10 |
| 4.6 | Playwright smoke in every PR, full suite nightly | **A** | Reduce flakes blocking PRs | SPRINT1_FINAL D10 |
| 4.7 | Fly SSE routing: `fly-replay` header OR single-region pinning | **A** | Single-region pinning in MVP (already the plan); document explicitly | FREEZE §11 |
| 4.8 | Verify Neon pooled endpoint + async SQLAlchemy prepared-statement gotcha | **A** | Prevents prod bug in Week 1 | SPRINT1_FINAL D2 |
| 4.9 | Confirm Fly region + Neon region match | **A** | Latency + egress | SPRINT1_FINAL D11 |
| 4.10 | Enable Neon PITR (30 days); upgrade tier if free doesn't allow | **A** | Data safety | SPRINT1_FINAL D12 |
| 4.11 | Two Upstash DBs (session-state `noeviction`, cache `allkeys-lru`) | **A** | Correctness | SPRINT1_FINAL D2 |
| 4.12 | pgvector: HNSW index created in migration (not later) | **A** | Prevent Sprint 2 pgvector debugging | SPRINT1_FINAL D6 |
| 4.13 | UUID on-disk with ULID surface | **A** | See 2.12 | FREEZE §9 |
| 4.14 | Confirm Neon PITR retention in plan tier | **A** | See 4.10 | SPRINT1_FINAL D12 |
| 4.15 | Secrets rotation policy (90 days; on off-boarding) | **P** | Documented in FREEZE §10; automated rotation Sprint 8+. | FREEZE §10 |
| 4.16 | SBOM (`syft`) generated on every image build | **A** | Cheap; enables signing later | FREEZE §11 |
| 4.17 | Rate limit `(agent_id, IP)` at widget + `(user_id)` at API | **A** | Correct rate-limit keys | FREEZE §10 |
| 4.18 | Clerk webhook HMAC (Svix) secret from secret manager, not env | **P** | Fly.io secrets are our secret manager in MVP; env is populated from them. Not violating spirit. | FREEZE §10 |

---

## Section 5 — Product Manager Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 5.1 | Ship onboarding wizard skeleton in Sprint 3 (not Sprint 6) | **R** | Sprint 3 is widget + KB installation is easier when onboarding lives post-KB. Kept at Sprint 6 (with clarified scope). Founder-led onboarding continues to Sprint 8. | BACKLOG §S6 unchanged |
| 5.2 | Widget install-verification ping (origin → green check) | **A** | Fixes silent-install failure | BACKLOG §S3 note |
| 5.3 | Handoff / owner-notify UX design | **A** | Email + deep link to conversation in Sprint 4; Slack in Sprint 8 | BACKLOG §S4 note |
| 5.4 | "Test the agent before going live" — staging vs. published distinction | **A** | Basic version model: Draft + Published only in Sprint 2 | FREEZE §5, SPRINT1_FINAL D9 |
| 5.5 | Reduce agent lifecycle from 7 states to Draft + Published for MVP | **A** | Matches 5.4 | FREEZE §5 |
| 5.6 | Auto-created "Demo Agent" on org creation | **A** | Empty-state fix; ~30 min of code | SPRINT1_FINAL D9 |
| 5.7 | Rename "Playground" channel to "Test Chat" in UX | **A** | Owner-friendly | SPRINT1_FINAL D9 |
| 5.8 | Standardize product noun: "Agent" (internal) → "AI Employee" (marketing). Console uses "Agent" for MVP. | **P** | Both terms allowed. **Marketing = "AI Employees." Console = "Agents." API = `agent`.** Not renaming until PMF. | FREEZE §5 |
| 5.9 | Ship form-based agent editor with "Advanced" toggle Sprint 5 | **A** | Non-technical operators need this | BACKLOG §S5 note |
| 5.10 | Delete custom persona/voice presets from Sprint 10 (deferrable with voice) | **A** | Ties to voice; safe to defer | BACKLOG §S10 note |
| 5.11 | Delete per-tenant cost dashboards from Sprint 12; keep internal cost tracking | **A** | Internal is what matters | BACKLOG §S12 note |
| 5.12 | Reviewer console minimized to "sessions list" through Sprint 7; full reviewer console Sprint 10+ | **A** | Matches actual review volume | BACKLOG §S7 note |
| 5.13 | Weekly digest email pulled to Sprint 6 | **A** | Duplicate of 1.7 | BACKLOG §S6 note |

---

## Section 6 — Security Engineer Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 6.1 | Enable Postgres RLS from migration `0001` (permissive is fine) | **A** | Prevents Sprint-5 retrofit disaster | FREEZE §10, SPRINT1_FINAL D6 |
| 6.2 | `TenantScopedSession` wrapper enforced via import-boundary lint | **A** | Discipline without human vigilance | FREEZE §11, SPRINT1_FINAL D3 |
| 6.3 | Cross-tenant leakage test harness in Sprint 1 | **A** | Foundation for multi-tenant confidence | SPRINT1_FINAL D8 |
| 6.4 | Verify `clerk-sdk-python` maintenance status; fall back to manual JWKS if needed | **A** | De-risk auth path | SPRINT1_FINAL D5 |
| 6.5 | Clerk webhook lazy-upsert backstop | **A** | Prevents "user exists in Clerk but not us" | SPRINT1_FINAL D5 |
| 6.6 | 30-minute owner-vs-member permission matrix | **A** | Prevents ad-hoc role invention | FREEZE §10 |
| 6.7 | Remove API keys from Sprint 1 | **A** | Attack surface without value | SPRINT1_FINAL removed items |
| 6.8 | Audit-log decorator on create/update/delete in Sprint 1 | **A** | Foundation for SOC 2 | SPRINT1_FINAL D6 |
| 6.9 | `DELETE FROM audit_log` allowed for MVP; document for SOC 2 later | **A** | Acceptable now | FREEZE §10 |
| 6.10 | Pre-commit hook gitleaks + secrets scan | **A** | Prevents leaks | SPRINT1_FINAL D1 |
| 6.11 | HIPAA-lite marketing wording lawyer-reviewed | **A** | Legal risk avoidance | CHECKLIST §A6 |
| 6.12 | DPA + Privacy + AUP + AI-disclosure copy ready before first paid customer | **A** | Blocker for Sprint 8 | CHECKLIST §A6 |
| 6.13 | Bot self-identifies as AI on first message (enforced in system prompt) | **A** | Compliance in multiple jurisdictions | FREEZE §7 |
| 6.14 | Signup includes clear "your content processed by OpenAI/Anthropic" clause | **A** | Consent | CHECKLIST §A6 |
| 6.15 | Delimiter defense in system prompt (`<user_input>`) in Sprint 1 | **A** | Cheap; huge injection mitigation | SPRINT1_FINAL D7 |
| 6.16 | `<kb_context>` tags around KB snippets (Sprint 2) | **A** | LLM02 mitigation | BACKLOG §S2 note |
| 6.17 | PII scrubber (`presidio`-lite) in ingestion pipeline (Sprint 2) | **A** | LLM06 mitigation | BACKLOG §S2 note |
| 6.18 | Explicit user confirmation before `create_booking` fires (Sprint 4) | **A** | LLM08 mitigation | BACKLOG §S4 note |
| 6.19 | Signed embed-token model for widget (Sprint 3) — replaces CORS-as-security | **A** | Real security | new ADR-048, BACKLOG §S3 note |

---

## Section 7 — VC Technical DD Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 7.1 | 20 real prospect conversations before serious fundraising | **A** | Sanity + narrative | CHECKLIST §A |
| 7.2 | Rehearse voice-deferral answer for prospects who ask | **A** | Positioning | FOUNDER_NOTES (unchanged) |
| 7.3 | Articulate moat mechanic explicitly (data feedback loop + templates + integrations depth) | **P** | Deferred: not needed to start building. Founder captures in `notes/moat.md` before first VC call. | Not affecting FREEZE |
| 7.4 | Hiring plan validated against milestones | **R (out of scope)** | Business planning, not engineering freeze | — |

---

## Section 8 — Competitor Review Recommendations

| # | Recommendation | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 8.1 | Make vertical data feedback loop an explicit moat mechanic | **P** | Design-level: eval + memory already enables it. Explicit "capture successful → contribute to org memory" loop = Sprint 7+. | BACKLOG §S7 note |
| 8.2 | Speed-to-first-agent < 5 min (Retell parity) | **P** | Sprint 6 onboarding wizard targets this. Not Sprint 1. | BACKLOG §S6 note |
| 8.3 | Publish voice latency benchmarks by Y1 end | **A** | Delivered as part of Sprint 10 (voice v1) exit criteria | BACKLOG §S10 note |
| 8.4 | Commit-or-abandon developer story | **A** | ABANDON developers for MVP; SDK on-demand only | FREEZE §12, BACKLOG §S13 deferred |
| 8.5 | Do not compete on voice latency wars, model quality, enterprise CCaaS, general framework | **A** | Already positioning; codified | FREEZE §12 |

---

## Section 9 — Delete List

All items **Accepted** and applied in FREEZE + SPRINT1_FINAL. Referenced above under §1–§6.

---

## Section 10 — Missing Documents

Docs from review §10:

| # | Doc | Decision | Reason | Affected docs |
|---|---|---|---|---|
| 10.1 | `docs/DATA_MODEL.md` | **A** | Critical to prevent drift | See SPRINT1_FINAL D0 |
| 10.2 | `docs/API_GUIDELINES.md` | **A** | Endpoint conventions | D0 |
| 10.3 | `docs/ERROR_HANDLING.md` | **A** | Error contract | D0 |
| 10.4 | `docs/PROMPT_ENGINEERING_GUIDE.md` | **A** | Prompt hygiene from Day 1 | D0 |
| 10.5 | `docs/SECURITY_CHECKLIST.md` | **A** | Pre-launch security | D0 |
| 10.6 | `docs/OBSERVABILITY_GUIDE.md` | **A** | Log/trace conventions | D0 |
| 10.7 | `docs/RELEASE_PROCESS.md` | **A** | Rollback playbook | D0 |
| 10.8 | `docs/RUNBOOK.md` (stub) | **A** | Top 5 incidents; grows | D0 |
| 10.9 | Explicitly rejected: full `AGENT_RUNTIME_SPEC.md`, `TESTING_PLAYBOOK.md`, `DESIGN_SYSTEM.md`, `COMPLIANCE_HANDBOOK.md`, ADR templates | **R** | Existing docs cover; would be overengineering | — |

---

## Section 11 — Scoring & Verdict

Review verdict **B — Needs Minor Fixes** is **Accepted**. All B → A upgrades are captured above.

---

## Section 12 — New ADRs Introduced by This Acceptance

| ADR | Title | Origin |
|---|---|---|
| ADR-041 | `org_id` is the canonical tenant column name | Review §2.10 |
| ADR-042 | IDs stored as UUID on-disk, ULID string in API | Review §2.12 |
| ADR-043 | Frozen ID prefix table | Review §2.11 |
| ADR-044 | Clerk = source of truth for identity/membership; our DB = entitlement/billing/state | Review §2.7 |
| ADR-045 | Sessions pinned to `agent_version_id` at start; publishes don't affect running sessions | Review §2.16 |
| ADR-046 | SSE cancellation contract (abort LLM, persist partial turn with `end_reason='client_cancel'`) | Review §2.20 |
| ADR-047 | Session state = our Redis + Postgres. LangGraph checkpointer is disabled. | Review §3.3 |
| ADR-048 | Widget uses signed embed token bound to origin + agent_id + short TTL (CORS not a security boundary) | Review §2.9 |

These are enumerated in FREEZE §6.

---

## Section 13 — Rejections Summary (with reasoning)

| Rejection | Reason |
|---|---|
| Add placeholder `contact` and `memory_facts` tables in Sprint 1 (2.17) | Empty tables invite premature use; recorded only in DATA_MODEL notes |
| CI backward-compatibility migration tooling in Sprint 1 (4.4) | Discipline sufficient; tooling arrives Sprint 5 |
| Onboarding wizard skeleton pulled to Sprint 3 (5.1) | Founder-led onboarding fits Sprint 6 timing; wizard needs KB + billing to be useful |
| Hiring plan (7.4) | Not an engineering-freeze artifact |
| Rename "Agent" → "AI Employee" in console (5.8) | Kept dual terminology (marketing vs. product) intentionally until PMF |
| Full new documents beyond the 8 accepted (`AGENT_RUNTIME_SPEC`, `TESTING_PLAYBOOK`, `DESIGN_SYSTEM`, `COMPLIANCE_HANDBOOK`, ADR templates) | Redundant with existing docs; would be overengineering |

---

## Section 14 — Effect on Existing Documents

The following planning documents are **frozen** (no edits). This changelog + FREEZE + SPRINT1_FINAL are the authoritative overrides.

| Document | Status after freeze |
|---|---|
| [docs/](docs/) (all 24 architecture docs) | **Immutable** — long-term reference only |
| [PROJECT_VISION.md](docs/PROJECT_VISION.md) → [COST_ESTIMATION.md](docs/COST_ESTIMATION.md) | Immutable |
| [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) | Immutable |
| [AI_EMPLOYEE_FRAMEWORK.md](AI_EMPLOYEE_FRAMEWORK.md) | Immutable (long-term intent) |
| [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) | Immutable; new ADRs 041–048 recorded here + in FREEZE §6 |
| [MVP_IMPLEMENTATION_PLAN.md](MVP_IMPLEMENTATION_PLAN.md) | Superseded by FREEZE + SPRINT1_FINAL where they conflict |
| [SPRINT_1.md](SPRINT_1.md) | **Superseded by [SPRINT1_FINAL_SCOPE.md](SPRINT1_FINAL_SCOPE.md)** |
| [BACKLOG.md](BACKLOG.md) | Retained; annotated per accepted recommendations (annotations documented above, not editing the file) |
| [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) | Refined by FREEZE §3 |
| [PROJECT_READINESS_REPORT.md](PROJECT_READINESS_REPORT.md) | Immutable |
| [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md) | Immutable — the input to this changelog |
| [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) | Active — must be green before Sprint 1 |
| [FOUNDER_NOTES.md](FOUNDER_NOTES.md) | Immutable |

**Nothing else is being rewritten.** All acceptance decisions live in [ARCHITECTURE_FREEZE_V1.md](ARCHITECTURE_FREEZE_V1.md) and [SPRINT1_FINAL_SCOPE.md](SPRINT1_FINAL_SCOPE.md).
