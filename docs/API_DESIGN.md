# API DESIGN

## 1. Principles

- **API-first**: OpenAPI 3.1 for REST, Protobuf for gRPC, AsyncAPI 2.6 for events.
- **Consistent versioning**: URL-prefixed (`/v1/`) for public REST; package-versioned proto (`v1`) for gRPC; topic-versioned events.
- **Backward compatibility**: Never break within a major version. Deprecations announced 6 months ahead.
- **Predictable**: consistent pagination, filtering, error shape, ID conventions (`ULID`).
- **Idempotent** by default for POST/PATCH via `Idempotency-Key` header.
- **Streaming** first-class: SSE for LLM/chat, WebSocket for bi-directional, WebRTC for media.
- **Resource-oriented** REST + **event-driven** async. RPC only for internal gRPC.

## 2. Public REST Surface

Base: `https://api.vsa.ai/v1/`
Auth: `Authorization: Bearer <API_KEY>` or OAuth 2.1.

### 2.1 Resource Groups

```
/tenants                         GET, POST                (admin)
/tenants/{id}                    GET, PATCH, DELETE
/tenants/{id}/members            GET, POST
/tenants/{id}/api-keys           GET, POST, DELETE

/agents                          GET, POST
/agents/{id}                     GET, PATCH, DELETE
/agents/{id}/versions            GET, POST                (immutable)
/agents/{id}/versions/{v}        GET
/agents/{id}/versions/{v}/publish  POST
/agents/{id}/versions/{v}/preview  POST                  (returns test session token)

/tools                           GET, POST
/tools/{id}                      GET, PATCH, DELETE
/tools/{id}/invoke               POST                    (manual test)

/knowledge/corpora               GET, POST
/knowledge/corpora/{id}/documents   GET, POST (multipart)
/knowledge/corpora/{id}/search   POST
/knowledge/documents/{id}        GET, DELETE
/knowledge/documents/{id}/reindex POST

/sessions                        GET (list with filters)
/sessions/{id}                   GET
/sessions/{id}/turns             GET
/sessions/{id}/transcript        GET (jsonl or txt)
/sessions/{id}/recording         GET (signed URL)
/sessions/{id}/handoff           POST

/channels/phone-numbers          GET, POST (purchase), DELETE (release)
/channels/whatsapp               POST (link business account)
/channels/{kind}/webhooks        POST (provider callbacks)

/eval/suites                     GET, POST
/eval/suites/{id}/runs           GET, POST
/eval/runs/{id}                  GET

/billing/subscription            GET, PATCH
/billing/usage                   GET
/billing/invoices                GET

/connections                     GET, POST (OAuth start)
/connections/{id}                GET, DELETE
```

### 2.2 Request/Response Conventions

**IDs**: ULID strings prefixed by type: `agn_01HN...`, `ses_01HN...`, `tur_01HN...`.

**Pagination**: cursor-based.
```json
GET /v1/sessions?limit=100&cursor=eyJ...
{
  "data": [ ... ],
  "page": { "next_cursor": "eyJ...", "has_more": true }
}
```

**Filtering**: RSQL-lite. `?filter=status==active;channel=in=(voice,web)&sort=-created_at`.

**Errors** (RFC 7807 Problem Details):
```json
{
  "type": "https://errors.vsa.ai/agent_not_found",
  "title": "Agent not found",
  "status": 404,
  "detail": "Agent agn_01HN... does not exist in tenant tnt_01HM...",
  "instance": "/v1/agents/agn_01HN...",
  "request_id": "req_01HN...",
  "code": "AGENT_NOT_FOUND"
}
```

**Timestamps**: RFC 3339 UTC (`2026-07-27T10:15:00Z`).
**Money**: minor units + ISO 4217 currency (`{"amount": 1250, "currency": "USD"}`).
**Enums**: `snake_case` strings.

### 2.3 Rate Limits

Headers on every response:
```
RateLimit-Limit: 1000
RateLimit-Remaining: 987
RateLimit-Reset: 42
Retry-After: 42          (only on 429)
```

Default limits (per API key):
| Endpoint class | Limit |
|----------------|-------|
| Read | 1000 req/min |
| Write | 300 req/min |
| KB search | 60 req/min |
| Session create (live) | 100 req/s |
| LLM proxy (per model) | Model-specific |

## 3. Streaming APIs

### 3.1 SSE (Server-Sent Events)

`POST /v1/agents/{id}/chat/stream`
Body: `{ session_id, message, tools_override? }`
Response: `text/event-stream`
```
event: token
data: {"delta":"Hello"}

event: token
data: {"delta":", how"}

event: tool_call
data: {"id":"tc_...","name":"lookup_order","args":{...}}

event: tool_result
data: {"id":"tc_...","result":{...}}

event: done
data: {"turn_id":"tur_...","tokens_in":123,"tokens_out":45,"latency_ms":812}
```

### 3.2 WebSocket

`wss://api.vsa.ai/v1/ws?token=...`
- Multiplexed channels via `stream_id`.
- Client sends `{op: "send_message", session_id, content}`.
- Server pushes `{op:"token"|"tool_call"|"tool_result"|"agent_message"|"typing"|"error"|"done"}`.
- Heartbeat every 20s; reconnect with `Last-Event-Id`.

### 3.3 WebRTC / SIP (Voice)

- WebRTC via LiveKit rooms; JWT for room join.
- SIP inbound/outbound via LiveKit SIP or Twilio Elastic SIP trunk.
- Media never touches the app tier; only control events do.

## 4. Webhooks (Outbound)

Signed with HMAC-SHA256:
```
X-VSA-Signature: t=1721995200,v1=abc123...
X-VSA-Event: session.completed
X-VSA-Delivery: dlv_01HN...
```

Delivery: at-least-once, exponential backoff (1s → 24h), 7-day retention, dead-letter to console.

Event catalog (subset):
- `session.created`
- `session.turn.completed`
- `session.handoff.requested`
- `session.completed`
- `agent.version.published`
- `document.indexed`
- `eval.run.completed`
- `invoice.finalized`

## 5. Internal gRPC

- Package: `vsa.<service>.v1`.
- All RPCs have deadlines; propagate via `grpc-timeout`.
- Use **server-streaming** for LLM/TTS/STT streams; **bidi** for realtime turn state.
- mTLS between services (Istio/Linkerd).
- Retries via service mesh with idempotency keys.

Example:
```proto
service AgentRuntime {
  rpc StartTurn(StartTurnRequest) returns (stream TurnEvent);
  rpc InjectToolResult(InjectToolResultRequest) returns (Ack);
  rpc EndSession(EndSessionRequest) returns (SessionSummary);
}
```

## 6. Async / Event API (Kafka)

- Topics: `<domain>.<entity>.<verb>.v<n>`.
- Format: Protobuf w/ Buf schema registry; envelope includes `event_id`, `tenant_id`, `occurred_at`, `trace_id`.
- Keys: usually `tenant_id:aggregate_id` for co-partitioning.
- Retention: 7 days hot, then archived to S3 (Iceberg).

## 7. SDKs

- **Python** (async-first, httpx + websockets).
- **Node/TypeScript** (fetch + ws + eventsource-parser).
- **Go** (grpc + protobuf) for infra tooling.
- Auto-generated from OpenAPI + `.proto`; hand-polished ergonomics layer on top.

## 8. Model Context Protocol (MCP)

- Tools may be defined as **MCP servers**; platform is an MCP client.
- Bidirectional: agents can also **expose** an MCP server so external LLMs (Claude Desktop, Cursor) can call our agents.

## 9. Versioning & Deprecation

- Public REST: `v1`, `v2`, etc. Two versions live simultaneously.
- Deprecation headers: `Deprecation: true`, `Sunset: <RFC-3339>`, `Link: <docs>; rel="deprecation"`.
- Breaking changes trigger email + console banner + 6-month sunset minimum.

## 10. Testing the API
- OpenAPI-driven contract tests (Schemathesis).
- Postman/Insomnia collections generated in CI.
- Public sandbox `https://sandbox.api.vsa.ai/` with test tenants, ephemeral data.
