# PROJECT VISION

## 1. The Opportunity

Every business — from a 10-seat clinic to a Fortune 500 bank — will soon employ **AI Employees**: software agents that answer calls, resolve tickets, book appointments, qualify leads, screen candidates, and collect payments. Today's landscape is fragmented:

- **Voice-only tools** (Retell, Vapi, Bland) — great voice, weak omnichannel, weak enterprise controls.
- **Chatbot builders** (Intercom Fin, Ada, Kore.ai) — text-only, poor voice, closed ecosystems.
- **LLM orchestration** (LangGraph, CrewAI, OpenAI Agents SDK) — developer libraries, not products.
- **Contact-center AI** (Genesys, NICE, Five9) — legacy, expensive, slow to iterate.

**No one has unified voice + chat + async channels behind a single, vertical-tuned, enterprise-grade agent runtime.**

## 2. The Product

A **multi-tenant Vertical AI Agent Platform** that lets businesses:

1. **Design** an AI Employee (persona, knowledge, tools, guardrails) in a visual console *or* code.
2. **Deploy** the same agent across Voice, Web, WhatsApp, SMS, Email, Slack, Teams, and API — with no channel-specific reimplementation.
3. **Observe & Improve** through evals, transcripts, sentiment, and A/B testing.
4. **Scale** to millions of conversations with sub-second latency and 99.95% uptime.
5. **Integrate** with CRMs, EHRs, POS, ERPs, ticketing, calendars via a first-class tool SDK.

## 3. Who We Serve

| Segment | Example Buyer | Primary Channel | Vertical Template |
|---------|--------------|-----------------|-------------------|
| SMB | Restaurant chain | Voice + WhatsApp | Ordering |
| Mid-market | Regional clinic network | Voice + Web | Medical Reception |
| Enterprise | National bank | All channels | Collections + Support |
| ISV / BPO | Contact-center outsourcer | Voice + API | White-labeled |
| Developer | Startup | API + SDK | Custom |

## 4. Non-Goals (Explicit)

- We are **not** a general-purpose LLM. We route to the best model per task.
- We are **not** a low-code app builder. We are an agent platform with a design surface.
- We are **not** a CCaaS replacement. We integrate with Genesys/Twilio/Five9 as a peer.
- We do **not** train foundation models. We fine-tune small models where ROI is clear.

## 5. North-Star Metrics

- **Conversation Success Rate (CSR)** — % of conversations resolved without human handoff, per vertical.
- **Median First-Response Latency (p50)** — < 700 ms voice, < 1.5 s chat.
- **Cost per Resolved Conversation** — target 60–90% below human baseline.
- **Time-to-First-Agent** — from signup to first live conversation < 15 minutes.
- **Enterprise NDR** — > 130% by year 3.

## 6. Competitive Moats

1. **Vertical Templates** — pre-built agents, tools, prompts, evals per industry.
2. **Unified Runtime** — one state machine across all channels (nobody else has this).
3. **Deterministic Replay** — every conversation is a reproducible trace (huge for enterprises).
4. **Eval-as-a-Service** — continuous quality regression testing baked in.
5. **BYO everything** — models, telephony, storage — for regulated enterprises.

## 7. Guiding Bets

- Model prices → 0. Orchestration, tools, and channels are the durable value.
- Voice-first will overtake chat-first for high-value verticals (healthcare, finance, field services).
- Enterprises will demand **on-prem / VPC** deployment; cloud-agnostic architecture is table stakes.
- Regulation (EU AI Act, HIPAA, PCI-DSS 4.0) will consolidate the market to compliant platforms.

## 8. Explicit Assumptions

- Team has funding for 18–24 months of build + go-to-market.
- Primary launch markets: **US + India** (English + Hindi), expanding to EU by year 2.
- We standardize on **Kubernetes** for portability; single-cloud managed alternatives are out of scope.
- We prioritize **open standards** (OpenTelemetry, OpenAPI, WebRTC, SIP, MCP) over proprietary lock-in.
- We accept higher initial complexity in return for architectural longevity.

## 9. Success in 3 Years

> 100,000 organizations · 1B+ conversations/year · 10,000+ concurrent voice sessions · SOC2 Type II + HIPAA + ISO 27001 · Available in 15 languages · Deployable in customer VPCs · $100M+ ARR trajectory.
