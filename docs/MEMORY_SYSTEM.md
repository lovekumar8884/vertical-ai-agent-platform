# MEMORY SYSTEM

## 1. Memory Tiers

| Tier | Scope | Store | TTL | Purpose |
|------|-------|-------|-----|---------|
| **Working memory** | Single turn | In-process | Turn | Scratchpad for LLM |
| **Short-term** | Session (call/chat) | Redis + Postgres | Session end + 24h | Rolling transcript window + variables |
| **Long-term facts** | Per end-user, per tenant | Postgres | Configurable (default forever) | Structured facts ("prefers vegan", "DOB 1990-05-01") |
| **Episodic memory** | Per end-user, per tenant | Qdrant | Configurable | Semantic search over past interactions |
| **Organizational memory** | Per tenant | Qdrant + Postgres | Curated | Learned patterns across all users (opt-in) |
| **Global memory** | Cross-tenant | N/A | Never | ❌ **Explicitly forbidden** (privacy) |

## 2. End-User Identity

- Each conversation is associated with an **`end_user_ref`** (external ID from CRM, phone number hash, email hash, or generated).
- Tenant chooses **identity resolution** strategy:
  - Exact match on external ID
  - Phone / email normalization
  - Deterministic hash for privacy-preserving mode
- All memory keyed by `(tenant_id, end_user_ref)`.
- **Right to be forgotten**: hard delete by `end_user_ref` cascades across tiers within 30 days.

## 3. Short-Term Memory

### 3.1 Structure

```python
class ShortTerm(BaseModel):
    session_id: ULID
    messages: deque[Message]         # last N; older summarized
    summary: str                     # rolling summary of older turns
    variables: dict[str, Any]        # slot values, tool results
    checkpoints: list[Checkpoint]    # for rollback
```

### 3.2 Token Budgeting

- Configurable `short_term_window` (default 20 turns) + `max_prompt_tokens` (default 12k).
- On overflow: compress oldest turns via LLM summarization → append summary chunk, drop raw turns.
- Compression prompt uses a cheap model (Haiku / gpt-4o-mini) with strict schema.

### 3.3 Persistence

- Live: Redis hash `t:{tid}:sess:{sid}:state` with TTL 24h sliding.
- Durable: Postgres `turns` + `sessions` tables (write after each turn end).
- On crash: session resumable within 24h from Redis; from Postgres beyond that.

## 4. Long-Term Facts

Structured, human-inspectable, revocable.

```sql
memory_facts(
  id, tenant_id, end_user_ref, key, value jsonb,
  confidence float, source_turn_id, valid_from, valid_to,
  created_at, updated_at
)
```

- **Extractor pipeline**: after each session, an async job runs an LLM-fact-extractor with strict JSON schema against the transcript → dedupe + upsert.
- **Human-editable** in the console (per end-user profile).
- **Confidence** field enables threshold policies (e.g., only inject facts > 0.7).
- **Versioning**: `valid_from` / `valid_to` allow bi-temporal history.

### 4.1 Fact Categories (default schema, extensible)
- Identity: name, preferred_name, pronouns, DOB, language
- Contact: phone, email, address (encrypted)
- Preferences: communication_style, product_prefs, dietary
- History: last_order, last_issue, past_agents_used
- Constraints: allergies, contract_terms, credit_limit

## 5. Episodic Memory (Semantic)

- Every completed session is chunked and embedded:
  - Chunk = 1–3 turns of coherent exchange, summarized.
  - Embedded with `text-embedding-3-large` (or BGE-M3 for self-host).
  - Stored in Qdrant with payload `{tenant_id, end_user_ref, session_id, timestamp, topic, sentiment}`.
- Retrieval: on new session start, query top-k relevant past interactions → inject as "context you may recall" section (few-shot style).
- Retention configurable per tenant; end-user can request deletion.

## 6. Organizational Memory

- **Opt-in per tenant**.
- Learns cross-user patterns: common questions, effective responses, failure modes.
- Populated by:
  - Curated reviewer input (from Console Reviews)
  - Automatic mining (top-K queries + successful resolutions)
- Stored in a separate Qdrant collection with **anonymization** (PII stripped) — never contains user data.
- Used as retrieval augmentation for all sessions in that tenant.

## 7. Memory Injection into Prompts

Composition order (managed by Agent Runtime):
```
[system]
  agent persona + policies + tools
[system]
  long-term facts about this user (top-K by relevance & recency, capped)
[system]
  relevant past interaction snippets (episodic, top-3)
[system]
  organizational memory snippets (top-3)
[system]
  KB snippets (top-K)
[assistant/user...]
  rolling short-term window
  summary of older turns
[user]
  current input
```

Each block sized to a **budget** with graceful shedding: KB < episodic < org < long-term facts (never dropped unless empty).

## 8. Consistency & Race Conditions

- Facts extraction is **async**; may lag by a few seconds.
- For critical variables (e.g., a just-collected phone number), use **session variables** (short-term), not long-term facts.
- Long-term writes use optimistic concurrency (`updated_at` + retry).

## 9. Privacy Controls

- Per-tenant toggle: "Enable long-term memory".
- Per-end-user API: "Forget me" → cascades in 30 days (safety window).
- Automatic PII classification on fact insertion → sensitive fields encrypted with tenant CMK.
- **No cross-tenant memory ever** (enforced by RLS + Qdrant collection scoping + code review).

## 10. Observability

- Every prompt injection logged with which facts/snippets were used and their scores.
- "Memory drawer" in console shows what the agent "knew" at each turn (for support/debug).

## 11. Anti-Patterns Rejected

- ❌ Dumping raw transcripts into vector store without chunking (poor retrieval).
- ❌ Unbounded fact accumulation (leads to prompt bloat + contradictions).
- ❌ Storing PII in vectors without payload encryption.
- ❌ Global memory shared across tenants.
- ❌ Silently updating facts without audit / user-visible edit.

## 12. Assumptions
- Fact extractor accuracy will be > 90% for structured fields with well-designed schema (validated by evals).
- Episodic memory improves resolution rate ~10–20% for returning users (measured, else disabled by default).
- Users expect their data to be under their control; memory UI is a **feature** not an afterthought.
