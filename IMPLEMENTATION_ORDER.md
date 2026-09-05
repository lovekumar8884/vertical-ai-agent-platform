# IMPLEMENTATION ORDER — Sprint 1

Day-by-day execution for a single engineer. Derived from [SPRINT1_EXECUTION_PLAN.md](SPRINT1_EXECUTION_PLAN.md). Respects the dependency graph and critical path. No scope change.

**Assumptions:** [FINAL_PRE_IMPLEMENTATION_CHECKLIST.md](FINAL_PRE_IMPLEMENTATION_CHECKLIST.md) is green before Day 1. ~9–10 focused hours/day. Each commit is its own PR, reviewed and merged same-day where possible.

**Cadence rule:** open a PR per commit, keep `main` always green, never batch two deliverables into one PR.

---

## Day 1 — Repo + Local Stack (D1, start D2)

Commits **01–06**.

- 01 — chore: initialize monorepo workspaces
- 02 — chore: Makefile + README run-it
- 03 — chore: .env.example + secret hygiene (gitleaks)
- 04 — chore: module import boundaries (import-linter)
- 05 — chore: docker-compose dev stack
- 06 — chore: CI compose override + make dev targets

**End-of-day check:** `make dev` boots Postgres+pgvector, Redis, Mailpit; `make lint` green; gitleaks blocks a planted secret.

---

## Day 2 — Neon Check + FastAPI Platform (finish D2, start D3)

Commits **07–11**.

- 07 — feat(db): Neon pooled-endpoint compatibility script
- 08 — feat(api): app factory, config, health endpoints
- 09 — feat(api): structured logging + Sentry PII scrubber
- 10 — feat(api): async DB engine + TenantScopedSession
- 11 — feat(api): Redis clients + Problem+JSON errors + request_id

**End-of-day check:** `verify_neon.py` passes on a real Neon branch; API boots; `/healthz` 200.

---

## Day 3 — Finish Platform + Console Skeleton (finish D3, D4)

Commits **12–17**.

- 12 — feat(api): ULID/UUID id helpers + tests
- 13 — chore(api): Dockerfile + readyz dependency checks
- 14 — chore(console): Next.js + Tailwind bootstrap
- 15 — chore(console): shadcn/ui init
- 16 — feat(console): app shell + security middleware
- 17 — feat(console): typed API client skeleton

**End-of-day check:** `/readyz` green with DB+Redis; console renders shell with HSTS; typecheck+lint green both stacks.

---

## Day 4 — Authentication (D5)

Commits **18–22**.

- 18 — feat(iam): user/org/membership models
- 19 — feat(api): Clerk JWT verification + auth deps
- 20 — feat(iam): webhook + lazy-upsert service
- 21 — test(iam): webhook + upsert integration tests
- 22 — feat(console): Clerk auth pages + provider wiring

**End-of-day check:** console login works; `/me` returns DB-backed user+org; webhook + lazy-upsert tests green.

**Risk watch:** if `clerk-sdk-python` is flaky, switch commit 19 to manual JWKS verification (budgeted). Do not lose more than half a day here.

---

## Day 5 — Migration 0001 (D6)

Commits **23–28**.

- 23 — feat(agents): agent + agent_version models
- 24 — feat(sessions): session + turn models
- 25 — feat(db): Alembic setup + env
- 26 — feat(db): migration 0001 tables + RLS + pgvector
- 27 — feat(api): audit-log decorator + demo-agent hook
- 28 — test(db): migration round-trip + RLS + audit tests

**End-of-day check:** `up→down→up` green; RLS blocks cross-org reads; audit rows written; Demo Agent auto-created on org upsert.

**This is the multi-tenant keystone day. Do not proceed to D8 until the RLS test is green.**

---

## Day 6 — LLM + Prompt (D7)

Commits **29–31**.

- 29 — feat(runtime): LiteLLM streaming wrapper + timeouts
- 30 — feat(runtime): system prompt template + composer
- 31 — test(runtime): composer + streaming (respx) tests

**End-of-day check:** `stream_chat` yields deltas from a stubbed provider; composer renders the fixed order; hostile `</user_input>` cannot break out; AI-disclosure line present.

Half-day of slack today — use it to absorb any Day 4/5 spillover.

---

## Day 7 — Streaming + Cancellation + Leakage (D8, part 1)

Commits **32–34**.

- 32 — feat(sessions): session CRUD + service
- 33 — feat(platform): Redis rate limiter + per-agent concurrency cap
- 34 — feat(sessions): SSE serializer + streaming endpoint

**End-of-day check:** streaming endpoint returns tokens end-to-end (stubbed LLM); rate limiter + concurrency cap enforced.

**Peak-risk deliverable. No other work today.**

---

## Day 8 — Finish D8 + Start Console Flows (finish D8, start D9)

Commits **35–38**.

- 35 — test(sessions): streaming happy-path + cancellation
- 36 — test(security): cross-tenant leakage harness
- 37 — feat(console): agents list + create form
- 38 — feat(console): SSE parser + streaming chat hook

**End-of-day check:** cancellation persists assistant turn with `end_reason='client_cancel'` + correct token count; leakage harness green across all endpoints; console can list/create agents.

---

## Day 9 — Console Flows + CI/CD (finish D9, D10)

Commits **39–44**.

- 39 — feat(console): agent detail + Test Chat tab
- 40 — feat(console): Conversations transcript + Members view
- 41 — test(console): agent-chat e2e (Playwright)
- 42 — ci: lint/test/build with per-language path filters
- 43 — ci: PR preview (Neon branch + Upstash namespace + Fly)
- 44 — ci: prod deploy + migration release command

**End-of-day check:** full cold-user flow works on localhost; e2e smoke green; a throwaway PR produces a preview URL; merge path deploys prod.

---

## Day 10 — Deploy, Ops, Docs (D10 finish, D11, D12, D13)

Commits **45–48**.

- 45 — ci: manual rollback action
- 46 — chore(infra): Fly region + health-check config + secrets runbook
- 47 — docs(ops): runbook + restore drill + Sentry alert tags
- 48 — docs: finalize README + Sprint 1 retro

**End-of-day check (Sprint 1 exit):**
- Prod URLs live over HTTPS+HSTS; Sentry receiving events; Better Stack pings green.
- Real cold sign-up → create agent → streamed chat → refresh → history, on the prod URL.
- Rollback action verified on a test release.
- Neon PITR restore drill completed once with written evidence.
- Loom demo recorded; retro written.

---

## Schedule-at-a-Glance

| Day | Deliverables | Commits | Theme |
|---|---|---|---|
| 1 | D1, D2 (start) | 01–06 | Repo + local stack |
| 2 | D2 (finish), D3 (start) | 07–11 | Neon check + platform |
| 3 | D3 (finish), D4 | 12–17 | Platform + console skeleton |
| 4 | D5 | 18–22 | Authentication |
| 5 | D6 | 23–28 | Migration + RLS (keystone) |
| 6 | D7 | 29–31 | LLM + prompt |
| 7 | D8 (part 1) | 32–34 | Streaming (peak risk) |
| 8 | D8 (finish), D9 (start) | 35–38 | Cancellation + leakage + console |
| 9 | D9 (finish), D10 | 39–44 | Console flows + CI/CD |
| 10 | D11, D12, D13 | 45–48 | Deploy + ops + docs |

**Critical path:** D1→D2→D3→D5→D6→D7→D8→D9→D13, with D10→D11→D12 as the overlapping infra track finishing on Day 10.

---

## Buffer & Slip Rules

- **Built-in slack:** Day 6 is light by design. Use it to absorb Day 4 (auth) or Day 5 (migration) overruns — the two most likely to slip.
- **If a day slips, cut from that day's tail, never push the exit date.** Preserve, in priority order: D6 (RLS), D8 (streaming+leakage), D9 (the demoable flow). Everything else can compress.
- **Non-negotiable before Sprint 1 closes:** RLS test green (D6), leakage harness green (D8), cancellation contract verified (D8), cold-user prod flow works (D9+D11).
- **Deferrable to Sprint 2 kickoff if truly stuck:** the manual rollback action (45), the restore-drill evidence (47) — but only with explicit founder sign-off in the retro.

## Daily Discipline

- Start each day by re-reading the day's row here and the relevant Deliverable in [SPRINT1_EXECUTION_PLAN.md](SPRINT1_EXECUTION_PLAN.md).
- One commit = one PR = one review pass against [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md).
- Keep `main` green; never leave the day on a red build.
- Log blockers as a single line in `notes/sprint1_retro.md` — do not write a new planning doc.
- No scope additions. Ideas → [BACKLOG.md](BACKLOG.md).

When Day 10's exit checklist is fully ticked, **Sprint 1 is done.** Stop. Do not start Sprint 2 without an explicit go.
