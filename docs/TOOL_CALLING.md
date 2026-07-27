# TOOL CALLING

## 1. Objectives

- Agents can safely call any HTTP/SQL/gRPC/webhook/custom-code operation.
- Tools are **declarative**, **typed**, **versioned**, **sandboxed**, **observable**, and **auditable**.
- Both **first-party built-ins** and **customer-defined** tools.
- **MCP-native** so agents interop with the growing MCP ecosystem.

## 2. Tool Definition (declarative)

```yaml
apiVersion: vsa/v1
kind: Tool
metadata:
  id: tool_check_availability
  name: check_restaurant_availability
  version: 1.2.0
spec:
  description: >
    Checks table availability for a given date, time, and party size.
    Use this before offering a time slot to a customer.
  parameters:
    type: object
    required: [date, time, party_size]
    properties:
      date: { type: string, format: date }
      time: { type: string, format: time }
      party_size: { type: integer, minimum: 1, maximum: 20 }
  returns:
    type: object
    properties:
      available: { type: boolean }
      alternatives: { type: array, items: { type: string, format: date-time } }
  implementation:
    kind: http
    endpoint: https://pizzeria.example.com/api/availability
    method: POST
    auth: { connection_ref: conn_pos_pizzeria }
    timeout_ms: 3000
    retries: { max: 2, backoff_ms: 200 }
    idempotency:
      strategy: header
      key_expression: "${sha256(input)}"
  observability:
    log_request_body: false        # PII-sensitive
    log_response_body: true
    redact: ["input.customer_phone"]
  policy:
    allowed_agents: ["agn_restaurant_*"]
    rate_limit: { per_minute: 60 }
    circuit_breaker: { failure_threshold: 0.5, window_s: 60 }
```

## 3. Implementation Kinds

| Kind | Description | Executor |
|------|-------------|----------|
| `http` | REST/GraphQL/JSON-RPC via HTTPS | Tool Executor (native) |
| `grpc` | gRPC call | Tool Executor |
| `sql` | Parameterized query against connected DB | Tool Executor with query allowlist |
| `webhook` | Fire-and-forget outbound | Tool Executor |
| `mcp` | MCP server (stdio or HTTP) | MCP client in Tool Executor |
| `builtin` | Platform-provided (calendar, email, SMS, calc, code interpreter) | In-process |
| `custom_code` | User Python/JS/TS | **Sandboxed** worker (Firecracker microVM) |
| `zapier` / `pipedream` | Any of 10,000+ apps | Their gateway |
| `handoff` | Special tool that hands off to human/agent | Runtime |

## 4. Auto-Generated Tools

- Import **OpenAPI 3.x** spec → one tool per operation with parameter schema auto-derived.
- Import **GraphQL schema** → one tool per query/mutation.
- Import **Postman collection** → tools per request.
- Auto-derived descriptions from summary/description fields (with LLM assistance for improvement).

## 5. Authentication & Secrets

- **Connections** hold credentials (OAuth tokens, API keys, DB DSNs, certs).
- Stored in **Vault** (KV v2 or dynamic engines); tool config only holds `connection_ref`.
- Tokens refreshed automatically for OAuth flows.
- Per-tenant isolation; connections cannot be shared cross-tenant.

## 6. Argument Validation

- JSON Schema validation before dispatch.
- **Coercion** for common cases (string → int, ISO date).
- **Enum enforcement**.
- On invalid args, return typed error to LLM → LLM self-corrects (or retries with hint).

## 7. Execution Semantics

### 7.1 Concurrency
- Agent can request **parallel tool calls** — executor fans out with concurrency cap (default 5) per turn.
- Results merged in stable order.

### 7.2 Idempotency
- Every tool call gets a unique `call_id`.
- HTTP tools may include `Idempotency-Key` header derived from input hash + `call_id`.
- Duplicate call → return cached result within TTL.

### 7.3 Retries & Circuit Breakers
- Exponential backoff with jitter (defaults: 3 attempts, 200 ms → 3 s).
- Non-retryable errors: 4xx (except 408, 429), schema validation failures.
- Circuit breaker per (tenant, tool): open on failure rate → LLM sees `TOOL_UNAVAILABLE`.

### 7.4 Timeouts
- Per-tool `timeout_ms` (default 5 s; max 30 s).
- Long-running ops → `enqueue` mode returns immediately; result delivered via later event.

## 8. Sandboxing (Custom Code)

- Executed inside **Firecracker microVM** (or gVisor container as fallback).
- No network by default; explicit allowlist via tool spec.
- No filesystem beyond ephemeral scratch.
- CPU/mem quotas; wall-clock timeout.
- Language runtimes: Python 3.12, Node 22, Bun, Deno.
- Static analysis + secret scanner on submission.

## 9. Streaming Tool Results

- Long-running tools may **stream** progress back to the runtime.
- Executor emits `tool.progress` events → runtime may reflect status to user ("Looking that up…").
- Final result marks `tool.completed`.

## 10. Observability

- Every call logged with: `tool_id`, `version`, `call_id`, `session_id`, `latency_ms`, `status`, `attempts`, `bytes_in/out`, `cost` (if metered).
- Redaction rules honored.
- Trace span attached to conversation trace.
- Errors classified: `TIMEOUT`, `AUTH`, `RATE_LIMIT`, `UPSTREAM_5XX`, `INVALID_ARGS`, `POLICY_DENY`, `SANDBOX_VIOLATION`.

## 11. Governance

- Tool review workflow (optional per tenant): new tools require admin approval.
- **Deprecation**: tools versioned; agents pinned to specific versions; migration hints on upgrade.
- **Cost budgets**: per-tool spend caps trigger alerts.
- **Policy engine (OPA)** can restrict which agents / roles can call which tools.

## 12. MCP Integration

- **Client mode**: register MCP servers → their tools appear as native tools.
- **Server mode**: expose our agents as MCP servers so external clients (Claude Desktop, IDEs) can invoke them.
- Transport: stdio for local dev, HTTP+SSE for hosted.

## 13. Built-in Tool Library (day-1)
- `web_search` (SerpAPI / Tavily / Bing)
- `web_scrape` (Firecrawl / Playwright)
- `code_interpreter` (Python sandbox)
- `calendar` (Google, Outlook, Cal.com)
- `email_send` (SES/SendGrid)
- `sms_send` (Twilio)
- `payment_link` (Stripe)
- `crm_lookup` / `crm_upsert` (Salesforce, HubSpot, Zoho)
- `helpdesk_create_ticket` (Zendesk, Intercom, Freshdesk)
- `db_query` (Postgres/MySQL read-only with allowlist)
- `document_generate` (PDF/DOCX)
- `translate`
- `sentiment`
- `handoff_to_human`

## 14. Anti-Patterns Rejected

- ❌ Running user code inside the runtime pod.
- ❌ Tools without schema (LLM guesses → chaos).
- ❌ Silent tool failures (LLM keeps trying blindly).
- ❌ Unbounded loops of tool calls (hard cap per turn: default 10).
- ❌ Storing tool credentials in agent spec (Vault only).

## 15. Assumptions
- MCP will become the de facto standard — worth first-class investment.
- Firecracker is manageable operationally (AWS + Fly proved this) or gVisor as pragmatic fallback.
- Auto-import from OpenAPI covers 70% of enterprise tool needs on day 1.
