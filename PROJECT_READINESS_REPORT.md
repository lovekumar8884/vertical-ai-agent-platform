# PROJECT READINESS REPORT

Independent, VC-side review of the planning corpus before code is written.

---

## Scorecard (out of 100)

| Area | Score | Rationale |
|---|---|---|
| **Architecture** | 92 | Long-term design ([docs/](docs/)) is coherent, standards-based, cloud-agnostic, and honestly assumption-labeled. Clear evolutionary path from monolith → services. Minor gap: no explicit ADR yet on data-model bi-temporality for memory facts. |
| **Product** | 90 | Vertical is chosen with rigor; ICP + persona are concrete; value proposition is outcome-anchored; competitive positioning is sharp. Slight risk: HIPAA-lite messaging needs more customer-facing clarity. |
| **Business** | 88 | Pricing is anchored to human-labor cost; expansion path is legible; unit economics land in healthy zone. Weakness: no explicit CAC forecast per channel and no cash-runway modeling (out-of-scope for planning docs but flagged). |
| **Scalability** | 90 | Path from Fly.io monolith → cell-based K8s multi-region is clearly staged with triggers. Every scale trap has a documented ceiling and mitigation. |
| **Maintainability** | 91 | Module boundaries drawn from Day 1; coding standards + testing strategy are strict but pragmatic. Small risk: monolith discipline requires an enforced lint rule we haven't specified. |
| **Security** | 89 | Compliance-ready architecture, layered defenses, OWASP LLM Top-10 addressed. RLS enforcement deferred to Sprint 5 is the honest, correct call — but it is the single biggest tightrope. |
| **Developer Experience** | 88 | `make dev` in < 5 min; devcontainer; hot-reload; typed contracts. Preview environments per PR. Weakness: SDK ergonomics untested — will only be validated when a real developer uses them. |
| **Go-to-Market** | 82 | GTM ranking is honest; founder-sales-first is correct; vertical communities identified. Weakness: no scripted first-touch email, no discovery-call playbook; both need to exist by Week 1 of implementation. |
| **Execution Risk** | 82 | Two-person team, aggressive 10-week sprint. Realistic slippage buffers exist (cut-from-week rule). Voice deferral protects the timeline. Biggest risk = founder-sales bandwidth vs. engineering pull. |
| **Overall Readiness** | **89** | Planning is dense, internally consistent, and evolvable. The remaining work is not more planning — it is customer conversations and shipping. |

**Verdict: mature enough to build.**

---

## 1. What is still missing before coding?

Small, real gaps — none of them require another full planning pass:

1. **Environment variable inventory sign-off.** `.env.example` values are enumerated in [SPRINT_1.md](SPRINT_1.md); we need to actually create Clerk/OpenAI/Anthropic/Sentry/PostHog accounts and populate keys before Day 1.
2. **Domain + Google Workspace.** Buy the domain, set up business email, DNS records — one afternoon, blocks nothing else but let's not do it during Sprint 1.
3. **Design partner list.** 15–20 named clinics/dental practices for outreach in Sprint 5. Should be built up during Sprint 1–4 in parallel.
4. **Landing-page copy skeleton.** Not the design — just the words. Positioning sentence, three value pillars, one testimonial slot, one demo CTA. Founder-writeable in a day.
5. **Discovery-call script + demo checklist.** Founder-sales tooling. One-page each.
6. **Legal essentials.** Terms of Service, Privacy Policy, DPA template, AUP. Boilerplate-generator + one lawyer review before first paying customer (Sprint 8 latest).
7. **CI credentials setup.** GitHub secrets for Fly.io tokens, Neon API key, Upstash tokens, Doppler/Fly.io secrets seeding. Half a day; not blocking Sprint 1 code but blocking preview deploys.
8. **Founder + engineer working agreement.** Weekly rhythm ([FOUNDER_NOTES.md](FOUNDER_NOTES.md)), on-call division, decision authority. One page. Do this before Day 1.

**None of the above requires a new architecture doc.**

---

## 2. What should never be changed now?

Freeze these decisions. Changing them post-Sprint-1 will cascade.

- **The 11-pillar AI Employee model** ([AI_EMPLOYEE_FRAMEWORK.md §3](AI_EMPLOYEE_FRAMEWORK.md)).
- **One runtime, N templates** rule (ADR-004).
- **Module-boundaries-as-future-services** discipline in the monolith (ADR-009).
- **Postgres as the source of truth**, with mandatory `org_id` on every tenant table.
- **ULID with type prefix** for all IDs (ADR-038).
- **OpenAPI + Protobuf as contract sources of truth** (ADR-034).
- **Card-required trial, no forever-free** (ADR-040).
- **Chat before voice** (ADR-002).
- **Healthcare beachhead** with legal-intake/appointment-booking as approved pivot fallback (ADR-003).
- **Streaming end-to-end** at every layer.
- **No PII in default logs.**
- **Deterministic replay contract** (ADR-039).

If a decision above is challenged, it should require a full ADR update with explicit trade-off analysis — not a hallway conversation.

---

## 3. What assumptions are most risky?

Ranked worst-first:

1. **Healthcare demos will be bookable at ≥ 30% rate from cold outreach.** If this fails, we pivot verticals at Sprint 4 — planned, but pivot has switching cost.
2. **Founder can genuinely sell.** No product wins with weak founder-sales at this stage. If the founder is uncomfortable with cold outreach, hire fractional SDR support by Sprint 6, not Sprint 12.
3. **Clerk migration to WorkOS/Ory is truly cheap** when the day comes. Estimated at 2 sprints; could balloon if we're deep in Clerk's org model.
4. **Module discipline holds in the monolith.** One violation now = a distributed monolith later. Lint rule + PR review discipline must be enforced from PR #1.
5. **pgvector's ceiling is truly at 10M chunks.** Realistic at MVP scale, but if a design partner uploads a 50k-doc corpus, we hit it early.
6. **Voice deferral doesn't kill deals.** Some SMBs will insist on voice for a receptionist. Mitigation: qualify prospects on "chat-only first is acceptable" during discovery.
7. **LLM prices continue trending down.** Cost model assumes this. If they flatten, pricing needs a bump or fine-tuning arrives earlier.
8. **Templates carry enough quality across verticals.** Universal metrics + eval framework mitigate this, but the first non-launch vertical (Sprint 9) is the real test.
9. **HIPAA-lite framing is legally acceptable.** Not a lawyer — get legal review before saying "HIPAA-friendly" in any marketing.
10. **Fly.io scales cleanly to the projected footprint** without hidden ceilings. Backup plan: Render, then EKS.

---

## 4. What can only be validated with real customers?

- Whether the receptionist actually reduces missed appointments (booking-lift measurement).
- Which questions patients really ask (informs prompt + KB structure).
- Whether $199 / $499 pricing lands or is under/over-priced.
- What the actual containment rate looks like in the wild (not on golden sets).
- How owners react to the AI's failures (do they churn, or do they teach it?).
- Which vertical adjacency is most eager for the next template (dental → physio? aesthetics? vet?).
- How much hand-holding the average non-technical operator needs (informs onboarding complexity).
- Which channel matters most after web widget (WhatsApp vs. SMS vs. voice) — vary by geography.
- What "sounds robotic" means to a real patient (informs persona/tone tuning).
- How reliably Google Calendar / Cal.com integrations behave in edge cases (double bookings, timezone mishaps, recurring events).

None of these can be answered by more planning. They can only be answered by paying customers.

---

## 5. What should be deleted from the roadmap?

Even the trimmed [BACKLOG.md](BACKLOG.md) has weight that can be cut or reshaped:

- **Sprint 13 (Public API + SDK v0.1)** — postpone unless a specific developer customer requests it. Building SDKs before a developer audience exists is a common mistake. Move to "on-demand."
- **Sprint 18 (Long-term Memory + Contact Profiles)** — only ship if design-partner data shows returning-user recall is a top-3 request. Otherwise defer.
- **Sprint 12 (Analytics + tenant-facing metrics)** — the *weekly digest email* is what customers actually value. The full owner analytics dashboard can be a Sprint 14+ item and probably has less impact than we think. Ship the email in Sprint 8 as a small task.
- **Landing site as a Sprint 6 build** — a strong single-page site with a demo CTA is enough for months. Do not scope a full marketing site pre-PMF.
- **A/B versioning within a single customer** — architecturally interesting; low ROI until we have hundreds of customers. Defer past V1.0.
- **`apps/landing` as a standalone Next.js app** — merge with `apps/console` marketing pages or host on Framer/Webflow. Do not maintain two frontends.
- **Multiple LLM provider registrations at MVP** — start with OpenAI + one fallback (Anthropic Haiku). Add Groq/Llama only when cost pressure appears.

---

## 6. What should be accelerated?

- **Sprint 5's RLS enforcement** — pull into Sprint 3 or 4. Every day without RLS is a day one bad query can leak across tenants. Cost is one afternoon.
- **Cost-per-tenant tracking** — pull from Sprint 12 into Sprint 6. Founders should never fly blind on unit economics.
- **Weekly digest email to owners** — pull into Sprint 6 as a small feature. It's the single strongest retention lever and cheap to build.
- **Cross-tenant leakage test harness** — build in Sprint 1 as part of test infrastructure. Zero cost pre-multi-tenant traffic; massive cost after.
- **Log PII redaction defaults** — Sprint 1, not later. Retrofitting is painful.
- **Runbook stub** — create in Sprint 2 (5 pages max) and grow with every incident. Do not wait until Sprint 8.

---

## 7. Is the planning phase complete?

**Yes.** The corpus now spans:

- 24 architecture documents (long-term truth).
- 5 MVP planning documents (short-term truth).
- 3 strategy documents (business truth).
- This report.

Total ~32 documents. Any additional planning at this stage is procrastination.

The remaining unknowns are learnable only through **shipping and selling.**

---

## Final Recommendation

# READY FOR IMPLEMENTATION

Start Sprint 1. Nothing else.

---

## Sprint 1 Kickoff Prompt (paste this into Claude Code)

```
You are the sole engineer implementing Sprint 1 of the Vertical AI Agent Platform.

Your only source of truth for scope is: SPRINT_1.md
Your only source of truth for repo layout is: REPOSITORY_STRUCTURE.md
Your only source of truth for tech-choice rationale is: MVP_IMPLEMENTATION_PLAN.md

You may consult (for context, not scope): AI_EMPLOYEE_FRAMEWORK.md, ARCHITECTURE_DECISIONS.md, and the docs/ folder.

STRICT RULES
1. Implement ONLY the deliverables listed in SPRINT_1.md. If a change is tempting but not in SPRINT_1.md, append it to BACKLOG.md and do NOT implement it.
2. Follow the folder layout in REPOSITORY_STRUCTURE.md exactly — names, boundaries, ownership.
3. Stack (fixed): Python 3.12 + FastAPI + async SQLAlchemy + Alembic + Postgres (pgvector-ready image) + Redis + LangGraph + LiteLLM (SDK mode) + Clerk (auth) + Next.js 15 (App Router) + Tailwind + shadcn/ui + Docker Compose + GitHub Actions + Fly.io.
4. Do NOT introduce: Kubernetes, Qdrant, ClickHouse, Kafka, Temporal, Istio/service mesh, Vault, Prometheus/Grafana/Loki/Tempo, or any observability tool beyond Sentry + PostHog + Axiom.
5. Do NOT implement (yet): voice, WhatsApp, SMS, email channel, Slack, Teams, billing, knowledge base / RAG, tools / calendar, embeddable widget, evals, analytics, RBAC beyond owner/member. These are later sprints.
6. Enforce from Day 1: every tenant table has org_id, every mutating action goes through audit log, no PII in default logs, coding standards per CODING_STANDARDS.md, testing standards per TESTING_STRATEGY.md (unit + integration via testcontainers + one Playwright e2e).
7. Every migration must be reversible; run up → down → up in CI on a fresh DB.
8. Never commit secrets. Use .env.example as the single source of required env vars.
9. Ask before adding any dependency not implied by SPRINT_1.md.

DELIVERABLE DEFINITION
A cold laptop runs: git clone → cp .env.example .env → make dev, and within 5 minutes an authenticated user in their own org can create an agent, open the Playground, send a message, and see a streamed LLM response — with Postgres + Redis + FastAPI + Next.js all real. On PR: preview environment auto-deploys to Fly.io with a URL commented on the PR. On merge to main: prod auto-deploys. All items in SPRINT_1.md's Exit Checklist pass.

HOW TO WORK
1. First, read SPRINT_1.md end to end. Confirm your understanding of the Exit Checklist and list any clarifying questions.
2. Propose the first three commits as a plan (files to create, purpose of each). Wait for approval before writing files.
3. After completing each Deliverable (D1 through D13), STOP, summarize what changed and what tests pass, and request a review before continuing.
4. When every item in the Exit Checklist is green, STOP. Do NOT begin Sprint 2 work. Wait for explicit approval to start the next sprint.

Begin by reading SPRINT_1.md and reporting your understanding of the Exit Checklist plus any questions.
```
