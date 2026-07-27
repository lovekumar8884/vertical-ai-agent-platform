# AGENT ENGINE

The **Agent Runtime** is the channel-agnostic conversation engine. Every message from any channel enters here; every response leaves here.

## 1. Design Goals

- **Channel-agnostic** — same graph runs over Voice, Chat, WhatsApp, Email.
- **Streaming-native** — every step yields deltas.
- **Deterministic where possible** — reproducible from event log.
- **Composable** — nodes are pluggable; verticals compose them.
- **Interruptible** — voice barge-in and message-during-response supported.
- **Observable** — every node emits a span; every decision auditable.

## 2. Runtime Choice

- **LangGraph** as the graph orchestration primitive (state machine + persistence + streaming + human-in-the-loop).
- Wrapped in our own **`AgentRuntime`** abstraction so we can swap engines later.
- **OpenAI Agents SDK** patterns influence tool-calling ergonomics; we adopt their handoff idea.
- We avoid heavyweight autonomous frameworks (CrewAI/AutoGen) for prod — too non-deterministic.

## 3. Agent Specification (declarative)

An agent is a **versioned YAML/JSON artifact**:

```yaml
apiVersion: vsa/v1
kind: Agent
metadata:
  id: agn_restaurant_ordering
  name: "Pizzeria Roma — Order Bot"
  vertical: restaurant_ordering
spec:
  persona:
    voice: elevenlabs/rachel
    language: en-US
    tone: friendly-casual
    speaking_rate: 1.05
  llm:
    primary: openai/gpt-4o-mini
    fallback: [anthropic/claude-3.5-haiku, groq/llama-3.3-70b]
    temperature: 0.3
  guardrails:
    profanity: block
    pii_redaction: [phone, email, credit_card]
    off_topic_policy: redirect
    max_turns: 60
  knowledge:
    corpora: [cor_menu_v3, cor_faqs_v1]
    strategy: hybrid   # bm25 + vector
    top_k: 6
  tools:
    - id: tool_check_availability
    - id: tool_place_order
    - id: tool_get_delivery_eta
  memory:
    short_term_window: 20
    long_term: per_customer
  graph:
    entrypoint: greet
    nodes:
      - id: greet
        type: prompt
        template: greetings/warm_intro
        next: intent
      - id: intent
        type: classify
        classes: [order, question, complaint, other]
        transitions:
          order: take_order
          question: rag_answer
          complaint: escalate
          other: clarify
      - id: take_order
        type: slot_fill
        slots: [items, size, toppings, address, payment_method]
        on_complete: confirm_order
      - id: confirm_order
        type: tool_call
        tool: tool_place_order
        on_success: farewell
        on_failure: retry_or_escalate
      - id: rag_answer
        type: rag
        next: intent
      - id: escalate
        type: handoff
        target: human_queue/support
      - id: farewell
        type: prompt
        template: farewell/warm_close
        terminal: true
```

## 4. Node Types

| Type | Purpose |
|------|---------|
| `prompt` | Render Jinja2 template → LLM → stream response |
| `classify` | Constrained-output classifier (function calling or logit-bias) |
| `slot_fill` | Gather typed variables with validation + re-ask |
| `rag` | Retrieve → augment → answer |
| `tool_call` | Invoke tool with argument validation |
| `condition` | Branch on expression over state |
| `parallel` | Fan-out to sub-graphs |
| `handoff` | Transfer to human or another agent |
| `end` | Terminal node with summary |
| `custom` | User-defined Python node (sandboxed) |

## 5. State Model

Per-session state is a typed pydantic model:
```python
class SessionState(BaseModel):
    tenant_id: ULID
    session_id: ULID
    channel: Channel
    locale: str
    turn_idx: int
    messages: list[Message]              # rolling window
    variables: dict[str, Any]            # slot values, tool results
    long_term_context: list[MemoryFact]
    kb_snippets: list[KBHit]
    active_tools: list[ToolBinding]
    graph_cursor: NodeRef
    handoff: HandoffState | None
    trace_id: str
```

- Persisted to **Redis** (hot) + **Postgres** (durable) after each turn.
- **Checkpointed** every N turns or on tool boundary → resumable after crash.

## 6. Turn Lifecycle

```
receive(input) -> load_state -> compose_prompt -> call_llm (stream)
   -> [maybe tool_call loop] -> post_process -> update_state -> emit_response
   -> persist -> emit_events (analytics, billing)
```

Each step wrapped in an OTEL span with `session_id`, `turn_id`, `node_id`.

## 7. Prompt Composition

Prompt assembler builds messages array in strict order:

1. **System**: agent persona + policies + safety + tool list.
2. **Long-term memory** (summarized facts about this end-user).
3. **Vertical templates** (industry-specific rules).
4. **KB snippets** (top-k, deduped, cited).
5. **Rolling short-term window** (last N turns; older turns summarized).
6. **Current user input**.

- Token budgeting via `tiktoken`; oldest turns summarized when budget exceeded.
- **Prefix caching** exploited (OpenAI/Anthropic) — stable prefix first, dynamic content last.

## 8. Interruption & Barge-In (Voice)

- Realtime Gateway watches user audio energy while TTS is playing.
- On detected speech (VAD confidence + duration threshold):
  1. **Cancel** current TTS stream.
  2. **Cancel** in-flight LLM stream (via provider abort).
  3. **Rewind** state to pre-response checkpoint.
  4. Start new turn with mid-word truncation acknowledged.
- Backchanneling ("mm-hmm", "right") without turn boundary detection.

## 9. Handoff to Human

- Emit `handoff.requested` event with context bundle:
  - Full transcript
  - Extracted intent + entities
  - Suggested response
  - CRM ticket link (if opened via tool)
- Voice: warm transfer via SIP REFER; whisper announcement to agent before bridge.
- Chat: assign to helpdesk (Zendesk/Intercom/Freshdesk connector); AI stays in thread as assistant unless disabled.

## 10. Multi-Agent Handoffs

- Agent may `handoff` to another agent (e.g., support → billing sub-agent).
- Context bundle transferred; new agent may see prior transcript per policy.
- Router agent pattern supported (single entry → dispatches to specialists).

## 11. Safety Layer

- **Input filters**: prompt-injection detector, jailbreak classifier, PII detector.
- **Output filters**: policy check, competitor mention filter, hallucination scorer.
- **Refusal templates** localized.
- **Grounding check** for RAG answers — cite-or-refuse mode configurable.
- Guardrails implemented via a middleware pipeline (compose-able).

## 12. Determinism & Replay

- All non-deterministic inputs (LLM responses, tool results, current time, random) captured to event log.
- **Replay mode**: re-run graph feeding recorded outputs → identical trace.
- Used for eval, debugging, and regression testing.

## 13. Vertical Templates

Each vertical ships with:
- Agent YAML skeleton
- Prompt templates (system + role-specific)
- Tool signatures (calendar, CRM, POS, EHR, LOS, etc.)
- Evaluation suite (golden conversations, KPIs)
- Compliance overlay (HIPAA for medical, PCI for finance, etc.)

## 14. Assumptions

- We accept LangGraph's Python-centric stack; Node runtime is only for edge/tools.
- We reserve the right to compile hot agents (verticals) to lower-level state machines for latency wins.
- LLM providers will continue to improve function-calling and streaming; we build to the streaming contract.
