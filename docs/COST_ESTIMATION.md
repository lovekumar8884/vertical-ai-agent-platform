# COST ESTIMATION

> All figures are **planning estimates**, not commitments. Reality varies with region, contracts, and usage mix. Numbers based on public pricing as of mid-2026 and industry benchmarks; refresh quarterly.

## 1. Unit Cost Model

Per **1 minute of voice conversation** (assumes English, 1 turn/10s ≈ 6 turns/min):

| Component | Provider | Rate | Cost / min |
|-----------|---------|------|-----------|
| STT (streaming) | Deepgram Nova-3 | $0.0043/min | **$0.0043** |
| TTS (streaming) | ElevenLabs Turbo v2.5 | $0.0006/char × ~800 chars | **$0.048** |
| LLM (in) | GPT-4o-mini | $0.15/M tok × ~2000 tok | **$0.0003** |
| LLM (out) | GPT-4o-mini | $0.60/M tok × ~600 tok | **$0.00036** |
| Telephony (PSTN) | Twilio US | $0.014/min inbound | **$0.014** |
| Infra (compute, media, storage) | Self-hosted | Allocated | **$0.005** |
| **Total** | | | **~$0.072/min** |

Same call **with prompt caching + smaller TTS voice + Groq Llama-3.3**:
- LLM (via Groq) ≈ $0.00005/turn
- TTS with cheaper voice ≈ $0.02/min
- **Total ≈ $0.045/min** — target for cost-optimized tier.

**Per chat conversation** (typical support, ~8 turns):
| Component | Cost |
|-----------|------|
| LLM (mix) | $0.002–$0.010 |
| RAG retrieval + rerank | $0.001–$0.003 |
| Infra + storage | $0.001 |
| Channel (WhatsApp session msg) | $0.005–$0.05 (per Meta conversation) |
| **Total** | **$0.01–$0.07** |

## 2. LLM Cost Assumptions (per 1M tokens)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| GPT-4o | $2.50 | $10.00 | Escalation tier |
| GPT-4o-mini | $0.15 | $0.60 | Workhorse |
| Claude 3.5 Sonnet | $3.00 | $15.00 | Reasoning tier |
| Claude 3.5 Haiku | $0.80 | $4.00 | Fast fallback |
| Llama-3.3-70B via Groq | $0.59 | $0.79 | Speed play |
| Gemini 1.5 Flash | $0.075 | $0.30 | Cheapest managed |
| Self-host Llama-3.3-70B (vLLM, H100 80GB) | ~$0.30/M blended | | Break-even at ~2B tok/day per GPU |

Prompt caching saves 30–90% on repeated system prompts (Anthropic 90%, OpenAI 50%).

## 3. Infrastructure Cost (per-region baseline)

Assumptions: US-East, medium production load (1k concurrent voice, 20k concurrent chat).

| Item | Spec | Monthly ($) |
|------|------|------------|
| EKS control plane | 1 cluster | 75 |
| Worker nodes (mixed) | 40 × m7g.2xlarge on-demand + spot | ~10,000 |
| RDS Postgres (multi-AZ) | db.r7g.4xlarge + 2 replicas | ~5,000 |
| ElastiCache Redis | cache.r7g.2xlarge × 3 (cluster) | ~3,000 |
| Qdrant (self-hosted) | 3 nodes × r7g.2xlarge + 2 TB gp3 | ~2,500 |
| ClickHouse (self-hosted) | 3 nodes × r7g.4xlarge + 10 TB gp3 | ~4,500 |
| Kafka/Redpanda | 3 brokers × m7g.xlarge | ~1,500 |
| S3 | 20 TB standard + lifecycle | ~600 |
| NAT + egress | Estimated | ~2,000 |
| Cloudflare (WAF + CDN) | Business plan + Argo | ~600 |
| Observability (Grafana Cloud alt) | Self-host prom/loki/tempo w/ storage | ~1,500 |
| Vault (self-host) | 3 nodes | ~500 |
| LiveKit media servers | 6 × c7gn.2xlarge (for 1k concurrent) | ~4,000 |
| Backups (cross-region) | | ~1,000 |
| Misc (bastion, DNS, monitoring vendor extras) | | ~1,500 |
| **Region baseline** | | **~38,000/mo** |

Scaling with load is largely linear on compute + LiveKit; DB scale is stepwise.

## 4. Third-Party SaaS (monthly, MVP)

| Service | Purpose | Cost |
|---------|---------|------|
| WorkOS | SSO/SCIM | $125 + $2.50/SSO conn |
| Stripe | Payments | 2.9% + $0.30 per txn |
| Metronome (usage billing) | Enterprise metering | ~$1k+ |
| PagerDuty | On-call | ~$500 |
| Sentry | Errors | ~$500 |
| GitHub Team / Enterprise | Repos + Actions | ~$1k |
| Vanta / Drata | SOC 2 automation | ~$1k+ |
| Notion / Linear / Slack | Team ops | ~$1k |
| **Total (MVP)** | | ~$5k/mo |

## 5. LLM Provider Cost Modeling (blended)

For **10M turns/month** at MVP mix (75% gpt-4o-mini, 15% Haiku, 10% GPT-4o):

- Avg tokens: 2000 in / 600 out per turn.
- Monthly tokens: 20B in / 6B out.
- Cost @ blended $0.30/M in + $1.20/M out = **$6k in + $7.2k out ≈ $13k/mo**.
- With **prompt caching 40% savings** → **~$8k/mo**.

At Year 3 with **500M turns/month** and vertical fine-tunes running on our GPUs → LLM cost ≈ $150k/mo (rather than $650k+ pass-through).

## 6. Telephony Cost

- Twilio inbound US: ~$0.014/min + $1/number/month.
- Outbound US: $0.014/min.
- WhatsApp: per-conversation Meta pricing ($0.005–$0.15 based on country + type).
- SMS: $0.0079–$0.10 depending on country.

## 7. Storage & Bandwidth

- Audio recording: ~0.5 MB/min Opus. 100M min/mo = 50 TB/mo → $1.5k/mo storage; lifecycle to Glacier after 30d for compliance-only tenants.
- Transcripts: ~2 KB/turn. Negligible.
- Traces: sampled 10% → ~5–20 TB/mo (retention 14d hot → cold).

## 8. Human Cost (for context)

- SRE ~ $200k FCC
- Senior BE / AI eng ~ $220k
- Support agent (comparison baseline): ~$0.80/min blended; **AI target: <$0.15/min** → 5x cost savings.

## 9. Unit Economics Targets

| Segment | Price/min or msg | Cost/unit | Gross margin |
|---------|-----------------|-----------|--------------|
| SMB voice | $0.20/min | $0.08 | 60% |
| Enterprise voice | $0.35/min (bundled) | $0.10 | 71% |
| Chat (per resolved) | $0.30 | $0.05 | 83% |
| Enterprise chat | $0.75 | $0.08 | 89% |

## 10. Total Company Cost (rough)

| Stage | Monthly infra + SaaS + LLM | Notes |
|-------|---------------------------|-------|
| MVP (1 region, small load) | $50–70k | Most cost is idle capacity |
| Year 1 (3 regions, real load) | $250–400k | LLM starts dominating |
| Year 3 (8 regions, scale) | $3–5M | LLM cost mitigated by fine-tunes + on-prem inference |

## 11. Cost Optimization Roadmap

1. **Prompt caching** (immediate) — 30–50% LLM savings.
2. **Semantic cache** (Q2) — additional 10–20% for repetitive workloads.
3. **Model routing** (Q1) — cheapest capable model per task.
4. **Vertical fine-tunes** (Q3) — small models beating GPT-4o on narrow tasks.
5. **On-prem inference** for high-volume tenants (Year 2).
6. **Regional egress optimization** via R2 for public assets (Year 1).
7. **Reserved capacity** on cloud (Year 1) — 30–50% infra savings.
8. **Spot instances** for stateless workers (Year 1) — 50–70% on eligible workloads.
9. **Tiered storage** everywhere (Year 1) — 60% storage savings for archival.

## 12. Sensitivity Analysis

| Factor | ±20% impact on cost/min |
|--------|------------------------|
| STT provider swap | ±30% |
| TTS provider swap (biggest single line) | ±40% |
| LLM provider tier | ±60% |
| Cache hit rate | ±25% |
| Voice concurrency (idle capacity) | ±20% |

## 13. Anti-Patterns Rejected

- ❌ Predicating pricing on today's LLM prices without buffer.
- ❌ Ignoring egress + storage in infra estimates.
- ❌ Undercutting price without measured unit cost.
- ❌ Free trials without usage caps.
- ❌ Reserved instances before load stability (waste).

## 14. Assumptions
- LLM prices continue trending down; we hedge by architecting for provider portability.
- We negotiate volume contracts once past $50k/mo per provider.
- On-prem inference viable when a single tenant's spend > break-even for a dedicated GPU (~$4k/mo per H100 equivalent).
- Voice TTS remains the most expensive line item until custom small TTS models mature.
