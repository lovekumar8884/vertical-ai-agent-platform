# PRODUCT STRATEGY

> The business bible. Read this before writing a single line of code, before every hiring decision, and at the start of every quarterly planning session.

---

## Vision

**We are becoming the operating system for AI Employees — the Shopify of AI labor.**

Every business — from a 3-person clinic to a Fortune 500 bank — will run a workforce of AI Employees alongside its humans within the next five years. Those AI Employees will answer calls, resolve tickets, book appointments, qualify leads, screen candidates, collect payments, and follow up on collections. They will be **specialized by vertical**, **integrated with real business systems**, **measurable in outcomes**, and **configurable without code**.

Today, building one requires stitching together LLM APIs, telephony, CRMs, vector databases, orchestration frameworks, and evaluation tooling — a multi-month project. That is a temporary state. The winning platform will collapse the entire stack into a single product where a non-technical operator creates, deploys, versions, evaluates, and improves AI Employees in an afternoon.

**Why this company exists:** Small and mid-sized businesses lose billions each year to unanswered inquiries, missed appointments, unqualified leads, and overwhelmed staff — problems large enterprises solved by paying $500k+ to contact-center vendors. We are the version of that solution that a dentist, restaurateur, or loan officer can turn on themselves for the price of a part-time employee.

**The future we believe in:**
- Every SMB will manage AI Employees the same way they manage payroll today.
- Voice, chat, and messaging will all be one interface — the customer chooses; the business doesn't care.
- Vertical templates (not code) will be how AI capability is packaged and sold.
- Outcomes (bookings, closures, resolutions), not "AI usage," will be the unit of value.
- The platform that owns the runtime + template library + marketplace wins the category — the way Shopify won commerce for merchants who couldn't hire engineers.

---

## Mission

**Enable any business to hire, deploy, and improve AI Employees in a day — without writing code — and measure them in real business outcomes.**

---

## Product Philosophy

Nine principles. Every product decision must be justifiable against them.

1. **Outcome-driven, not feature-driven.** We sell "bookings placed," not "chat sessions." Every screen, every metric, every renewal email ties back to a business outcome the customer can quantify.
2. **Vertical-first.** Generic AI is a commodity race to zero. Verticals compound: templates, evals, tools, prompts, integrations, and case studies stack per industry. We win one vertical fully before starting the next.
3. **One platform, unlimited employees.** Every AI Employee shares one runtime, one memory, one knowledge system, one tool framework. Only configuration changes. No forked codepaths per vertical. Ever.
4. **No-code for operators; code for developers.** Non-technical owners must configure everything visually. Developers must have full API/SDK escape hatches. Both audiences co-exist without one taxing the other's experience.
5. **Opinionated defaults, escape hatches everywhere.** New user picks a template and everything works. Power user overrides prompts, tools, models, memory strategy — one setting at a time, never all at once.
6. **Channel-agnostic from Day 1.** The same AI Employee answers a web widget, WhatsApp, SMS, email, and voice call. Owners never rebuild per channel.
7. **Observability-first.** Every conversation is a distributed trace. Every decision auditable. Every version comparable. The reviewer console is not a feature — it's the compounding advantage.
8. **Enterprise-ready without being enterprise-only.** Multi-tenancy, RBAC, audit, BYOK, data residency, SSO, and compliance are baked into the architecture from Day 1 — but the SMB experience never pays their complexity tax.
9. **Open architecture, open standards.** OpenTelemetry, OpenAPI, WebRTC, SIP, MCP. Model, telephony, TTS, STT are all pluggable. Enterprises can deploy in their VPC. Developers can extend anything.

---

## Ideal Customer Profile (ICP)

### Vertical Scoring Matrix

Scoring 1 (worst) → 10 (best). Weighted by launch-time value (Pain × Speed × ACV × Ease-of-MVP dominate; enterprise-only signals like ACV expansion count less at Day 1).

| Vertical | Pain | Buy Speed | ACV ($/mo SMB) | Competition (lower=better) | Ease of MVP | Expansion | AI Readiness | Integration Complexity (lower=better) | Revenue Potential | **Score** |
|---|---|---|---|---|---|---|---|---|---|---|
| **Healthcare (small clinic)** | 9 | 8 | 8 ($299–999) | 7 | 8 | 9 | 7 | 6 | 9 | **71** |
| **Dental** | 9 | 8 | 8 ($299–899) | 7 | 9 | 8 | 7 | 7 | 8 | **71** |
| Restaurant (ordering) | 8 | 8 | 5 ($99–299) | 6 | 5 | 6 | 6 | 4 (POS zoo) | 6 | 54 |
| Real Estate | 8 | 7 | 6 ($199–499) | 6 | 6 | 7 | 7 | 5 (MLS/CRM) | 7 | 59 |
| Recruitment | 7 | 5 | 8 ($499–1499) | 6 | 6 | 8 | 8 | 6 (ATS) | 8 | 62 |
| Insurance | 8 | 4 (regulated) | 9 | 5 | 4 | 9 | 6 | 4 | 9 | 58 |
| Finance/Lending | 8 | 4 | 10 | 6 | 4 | 10 | 6 | 3 | 10 | 61 |
| Legal (intake) | 7 | 6 | 7 ($299–799) | 8 | 7 | 6 | 7 | 8 | 7 | 63 |
| Customer Support (generic) | 8 | 6 | 6 | 3 (Intercom Fin, Ada, Chatbase) | 6 | 8 | 8 | 6 | 8 | 59 |
| Sales / SDR | 8 | 5 | 8 | 4 (Clay, 11x, Artisan) | 5 | 8 | 8 | 5 | 8 | 59 |
| Appointment Booking (generic) | 7 | 8 | 5 | 6 | 10 | 6 | 7 | 9 (just Cal/Google) | 6 | 64 |

### Winner: **Healthcare Receptionist (small clinics + dental)** as the launch beachhead.

Why it wins:
- **Pain is universal and quantifiable.** Owners can compute the ROI in a single conversation ("we lost 12 appointments last week to voicemail").
- **Buying speed is fast.** Owner decides; no procurement.
- **ACV of $299–$999/mo** clears our unit economics with room for growth-tier upsell.
- **Adjacent expansion is trivial** — dental → physio → chiro → vet → aesthetics — same runtime, only template + tool changes.
- **Integration complexity is bounded.** Google Calendar + Cal.com covers 80% of the market on Day 1.
- **HIPAA is a growth-tier concern**, not a launch blocker. We ship HIPAA-lite (no PHI stored beyond appointment metadata + explicit consent) and add BAA when a paying customer needs it.
- **Chat + owner-notify email is enough for V1.** Voice is Sprint 10; we don't burn 6 weeks on a media stack before revenue.

### Runner-up vertical (if healthcare demos are hard to book): **Legal Intake** or **Appointment Booking (generic services — salons, spas, coaches)**. Same runtime. Zero rebuild.

---

## Customer Persona (Healthcare / Dental clinic)

- **Business Owner** (also the buyer): Dr. Sarah Patel, DDS, 40s, owns a 4-chair dental practice with 6 staff. Signs the credit card. Skeptical of "AI hype" but tried Intercom last year and hated it. Reads one email newsletter for practice owners and lurks in a Facebook group of ~2k dentists. **Buys when a peer tells her it works.**
- **Office Manager** (day-to-day user + champion): Maria, mid-30s, runs the front desk + schedules + insurance. Overwhelmed. Was hired 6 months ago. Would love to stop answering the same 15 questions a hundred times a week. **Champions us if setup is < 30 minutes.**
- **Front-Desk Staff** (impacted): Two receptionists on rotating shifts. Currently drop 25% of after-hours website chat and 15% of daytime calls-to-voicemail. **Will resent us if we make their job harder, love us if we absorb repetitive tasks.**
- **Decision Maker:** Owner (unilateral). Sometimes the office manager pre-vets. **No IT department; owner's nephew "does the website."**
- **Technical Skill:** Owner ~2/10; office manager ~4/10. Uses Google Workspace, Cal.com or Google Calendar, Dentrix/Open Dental (PMS), maybe Weave/Adit for messaging.
- **Daily Problems:**
  - Phones ring during procedures; nobody to answer.
  - After-hours website inquiries go to voicemail.
  - Same 15 questions answered a hundred times a week (hours, insurance, "do you take Delta?", "what's the cost of a cleaning?").
  - Cancellations create empty chairs no one refills quickly.
  - Missed leads = lost revenue (a single crown = $1,000+).
- **Buying Motivation:**
  - Recover missed revenue.
  - Free front-desk time for higher-value work.
  - Get ahead of larger practices marketing "AI-powered scheduling."
  - Reduce owner anxiety about missed calls.
- **Budget:** $200–$1,000/month for tools like this. Compare to hiring an evening receptionist at $1,800+/month.
- **Objections:**
  - "Will it sound robotic to my patients?"
  - "What if it books wrong / double-books?"
  - "Is my patient data safe?" (HIPAA)
  - "How is this different from a chatbot?"
  - "Do I need my IT guy?"
- **Success Criteria (their words):**
  - "We booked X more appointments last month."
  - "Maria isn't drowning anymore."
  - "I didn't get a single complaint about the bot."

---

## Customer Journey

| Stage | What happens | Our job | Success signal |
|---|---|---|---|
| **Discovery** | Owner sees a LinkedIn post, hears a peer mention us, or Googles "AI receptionist dental." Lands on our page. | Vertical-specific landing pages ("AI Receptionist for Dental Practices"). Concrete numbers, one testimonial, one demo video, "See it in action" CTA. | Demo booked within 2 minutes. |
| **Demo** | 30-min screen-share with founder (Y1) or async self-serve tour (Y2). Live demo on THEIR website URL (we crawl it in 90 seconds). | Show it working on their content. Not on ours. Ask about missed appointments last month. | "How soon can I try this?" |
| **Trial** | 14-day free trial. Card upfront (reduces flakes; refundable). Widget installed on their site with their content ingested. Calendar connected. | Personal onboarding (first 20 customers). Daily monitoring first 3 days. | Widget live + first real patient chat within 48 hours. |
| **Activation** | First real conversation happens; first booking placed via the agent. | Alert us on every first-booking event. Send an "🎉 first booking!" email to the owner. | First booking in < 7 days of trial. |
| **First Success** | Owner sees a booking in their calendar they know they wouldn't otherwise have gotten. Emails us "wow." | Capture that story. Ask for a testimonial + logo. | Owner tells one peer. |
| **Paid** | Trial converts at day 14. Card is charged automatically. | Automatic conversion; no billing conversation required unless downgrade. | ≥ 25% trial→paid conversion. |
| **Renewal** | Monthly renewal (SMB) or annual invoice (mid-market). | Weekly digest email: bookings placed, questions answered, containment %. Show the value. | ≥ 85% D30, ≥ 75% D90 retention. |
| **Expansion** | Owner adds a second location; enables WhatsApp; enables voice; adds a second AI Employee (billing follow-ups, appointment reminders). | In-app upsell prompts on quota thresholds. Founder-led outreach on high-usage accounts. | Net revenue retention > 120%. |

---

## Value Proposition

**We are not selling an AI chatbot.**

We are selling: **"Never miss a patient inquiry again — day, night, or during a procedure."**

### The transformation

| Before | After |
|---|---|
| "We miss 25% of after-hours website inquiries." | "Every inquiry is answered in under 3 seconds, 24/7." |
| "Maria is on hold with insurance; the front desk is drowning." | "The AI handles the 15 repeat questions so Maria can focus on patients in the chair." |
| "We track lost leads with a spreadsheet, if at all." | "The dashboard shows exactly how many appointments the AI booked this week." |
| "Our chatbot was a joke — canned responses, no bookings." | "The AI actually books the appointment, syncs to Google Calendar, and emails the patient." |
| "I don't have time for another tool." | "Setup took 20 minutes. It runs itself." |

### Value pillars

1. **Never miss another appointment.** Direct revenue recovery.
2. **Answer patients 24/7.** Reduces friction; wins against slower practices.
3. **Reduce front-desk workload.** Absorbs the repetitive 60% of inbound.
4. **Show measurable ROI.** Weekly digest email with bookings placed and questions answered.
5. **Turn every channel into a booking channel.** Website today; WhatsApp, SMS, voice tomorrow — same agent.
6. **Stay compliant.** HIPAA-lite defaults; BAA available; PHI never stored in prompts by default.

---

## Pricing Strategy

Simple, vertical-aware, outcome-anchored. Two paid tiers at launch. Free trial is time-boxed, card-required.

### Tiers

| Plan | Price | Who it's for | Included |
|---|---|---|---|
| **Free Trial** | $0 for 14 days, card required | Everyone | 1 agent, 1 channel (web widget), 500 messages, KB up to 25 MB, Google Calendar, community support. Auto-converts to Starter. |
| **Starter** | $199/mo | Solo practices, 1–3 staff | 1 agent, web widget, 3,000 messages/mo, 100 MB KB, Google Calendar/Cal.com, owner-notify email, weekly digest, email support (48h). |
| **Growth** | $499/mo | Small practices, 4–10 staff | 3 agents, web widget + WhatsApp (Sprint 8) + owner-notify SMS, 15,000 messages/mo, 1 GB KB, Google + Outlook, priority email support (24h), conversation review, custom persona/voice presets (Sprint 10). |
| **Business** | $1,499/mo | Multi-location / small groups | 10 agents, all channels including voice (1 phone number + 500 min/mo), 50,000 messages, 10 GB KB, roles + audit log, weekly QA review by us (first 90 days), Slack support. |
| **Enterprise** | Custom (starting ~$5k/mo) | Multi-site groups, DSOs, health systems, regulated buyers | Unlimited agents, SSO/SCIM, BAA (HIPAA), audit exports, data residency (US/EU/IN), BYOK, dedicated Slack + CSM, SLAs, on-prem/VPC option. |

### Pricing philosophy

- **Anchor to human labor cost**, not to LLM tokens. A part-time evening receptionist costs $1,800+/mo; $199 is a bargain by comparison.
- **Charge per outcome-capacity, not per token.** Message quota is the visible unit; overage soft-caps to keep pricing predictable.
- **No usage panic.** If a customer exceeds quota, we soft-throttle (respond slower / warn owner) rather than surprise-bill.
- **Yearly = 2 months free** to lock in retention.
- **Vertical bundles later.** "Dental Package" = Starter + Dentrix connector + dental prompt library.

### When customers upgrade

- **Free → Starter:** trial ends (automatic).
- **Starter → Growth:** they want WhatsApp/SMS OR they have >1 use case (booking + reminders).
- **Growth → Business:** they want voice OR they have multiple locations.
- **Business → Enterprise:** they need BAA, SSO, or their compliance team gets involved.

### Pricing anti-patterns we avoid

- ❌ Free forever tier that never converts (costs money, no signal).
- ❌ Per-seat pricing (SMB doesn't have seats).
- ❌ Pure per-token pricing (customer can't predict spend).
- ❌ "Contact sales" for anything under $2k/mo.
- ❌ Feature-gating the outcome (bookings must work on Starter).

---

## Go-To-Market Strategy

Ranked by ROI **at our stage** (0 → 100 customers). Re-rank at 500 customers and again at 5,000.

| Rank | Channel | Why now | Effort | When to lean in |
|---|---|---|---|---|
| 1 | **Founder Sales (Direct Outbound + Demos)** | Fastest revenue signal; every call teaches the product | High but essential | Days 1–180 |
| 2 | **Vertical Communities (Facebook groups, Reddit, Slack)** | Dentists trust dentists; single testimonial → 5 signups | Low | Days 1–365 |
| 3 | **Referral Program** | Highest CAC efficiency once a few love the product | Low | After 20 customers |
| 4 | **Cold Email (targeted, vertical-specific)** | Volume when your ICP is defined | Medium | Days 30–365 |
| 5 | **Content SEO** (vertical-specific: "AI receptionist for dental practices") | Compounding, but slow | Medium | Continuous; monthly cadence from Day 30 |
| 6 | **Vertical Partnerships** (PMS vendors like Dentrix, industry consultants, dental supply reps) | Massive multiplier once we have proof | Very high | After 50 customers |
| 7 | **LinkedIn (Founder-led)** | Founder brand + industry authority | Medium | Continuous |
| 8 | **Vertical Events / Trade Shows** (Dental conferences) | High-quality leads, expensive | Very high | After Series A |
| 9 | **Inbound (Landing + Product Hunt)** | Modest at our stage; useful for credibility | Medium | Product Hunt at V1.0 launch |
| 10 | **Paid Ads** | Bad ROI until landing pages + funnels are tuned | High | After $50k MRR |

**Motion:** Founder-led sales for the first 100 customers, no exceptions. Every call is a Sprint input. Delegate outbound only after the founder has done 100 discovery calls personally.

---

## Product Metrics

### The North Star Metric

**Weekly Successful Outcomes Delivered per Customer.**

For our launch vertical: **bookings placed by the AI per week per customer.** This is the single number that means the product is working. If it drops, we churn. If it grows, we expand.

### Metric hierarchy

**Business (weekly review)**
- **MRR** and **Net MRR (ARR)** — the ledger.
- **New MRR / Expansion MRR / Churned MRR** — the movement.
- **CAC** — fully-loaded cost to acquire, tracked per channel.
- **LTV** (LTV = ARPA / gross-monthly-churn) — worst → best.
- **Gross margin per tenant** — LLM/infra spend allocated by usage.
- **Payback period** — target ≤ 12 months at scale.

**Customer (weekly)**
- **Activation rate** — % of new orgs that install widget AND connect calendar within 24 hours (target ≥ 60%).
- **Time-to-first-value** — time from signup to first agent-driven booking (target < 48 hours).
- **D30 / D90 retention** (targets ≥ 85% / ≥ 75%).
- **NPS** (start collecting after 30 customers).
- **Weekly digest open rate** (proxy for perceived value; target ≥ 55%).

**Product Quality (continuous)**
- **Conversation Success Rate (CSR)** — % of conversations that reach a defined "success" outcome (booked, answered, escalated cleanly).
- **Containment rate** — % of conversations resolved without human handoff (target ≥ 70% for receptionist).
- **Booking rate** — % of chat sessions ending in a scheduled event (target ≥ 15% for our vertical).
- **Response accuracy / faithfulness** (LLM-judge score on sampled prod traffic).
- **Hallucination rate** — % of answers with unsupported claims (target < 2%).
- **Tool success rate** — % of tool calls that succeed on first attempt (target ≥ 98%).
- **First-response latency** (p50 / p95) — chat < 1.5s / 3s; voice < 700ms / 1200ms.
- **Cost per resolved conversation** — the unit economics north star of quality × efficiency.

### Metrics we deliberately ignore

- GitHub stars.
- Model benchmark scores.
- Feature count.
- Twitter engagement.
- Session count (without outcome tie-in).
- p99 API latencies below thresholds nobody notices.
- Any dashboard our investors don't ask about (they will ask about MRR, NDR, retention, containment, LTV/CAC).

---

## Competitive Positioning

| Competitor | Category | Strengths | Weaknesses | Where we win | Where we should NOT compete | Never copy |
|---|---|---|---|---|---|---|
| **Retell AI** | Voice-first AI agents | Best-in-class voice latency; polished; developer-loved | Voice-only mindset; weak omnichannel; SMB console is thin | Verticals + omnichannel + outcomes | Raw voice benchmark battles | Their "voice-only pipeline" positioning |
| **Vapi** | Voice AI infra | Excellent DX; composable | Infra-flavored, not product-flavored; enterprise controls late | Owner-facing product + templates | Voice infra as a category | "Assemble your own voice stack" surface |
| **Bland AI** | Autonomous phone calls | Marketing muscle; brand recognition | Trust issues; regulatory exposure; opaque | Trust + compliance + observability | Cold-call automation at scale | Auto-outbound-first product |
| **Chatbase** | Website chatbot builder | Fast setup; SEO strong; cheap | Shallow outcomes; no booking; generic | Vertical-tuned outcomes + calendar integration | Generic Q&A bots | Chatbot-as-first-product framing |
| **Voiceflow** | Visual conversation designer | Design UX; enterprise features | Requires design skill; not vertical | Templated verticals; setup speed | Complex flow-authoring UX | Their step-by-step designer as the primary interface |
| **Botpress** | Open-source bot framework | OSS credibility; extensible | Devs-only; no outcome layer | No-code operator UX + hosted | Framework/infra positioning | "Framework for developers" positioning |
| **Intercom Fin** | AI support for existing Intercom customers | Distribution via Intercom | Locked to Intercom; expensive; enterprise SaaS motion | SMB + non-support verticals | Support inside big Intercom accounts | Their bundled/attached pricing model |
| **Ada** | Enterprise AI support | Large enterprise references | Long sales cycles; high floor price | SMB-mid-market speed | 6-figure enterprise support deals | Enterprise-only sales motion |
| **Salesforce Agentforce** | AI agents inside Salesforce | Distribution; ecosystem | Requires Salesforce; expensive; slow | Anyone outside Salesforce | Anything requiring deep SF workflows | Their consulting-heavy delivery model |
| **Microsoft Copilot Studio** | Agents in Microsoft stack | M365/Teams distribution | Enterprise IT motion; slow; opinionated | SMB + non-Microsoft shops | M365-native workflows | Their "power platform" complexity |
| **Google Vertex AI Agents** | Cloud-vendor agent platform | GCP integration | Infra-flavored; devs-only | No-code vertical templates | Cloud infra bake-offs | Vendor-lock-in features |
| **OpenAI Agents SDK** | Developer SDK | Best model access; DX | Framework, not product | Product for buyers, not builders | SDK category | "Build your own agent" positioning |

### The positioning sentence

> **"For [vertical] businesses that lose revenue to unanswered inquiries, [Company] is the AI Employee platform that answers, books, and follows up 24/7 across chat, WhatsApp, and voice — set up in a day, priced like a part-time hire, and measured in real bookings, not chat sessions."**

### Anti-features (we deliberately never copy)

- ❌ "Contact sales" pricing hidden behind a form.
- ❌ Voice-only positioning.
- ❌ Framework-first UX for non-technical buyers.
- ❌ Bring-your-own-integration-stack complexity.
- ❌ Autonomous multi-agent orchestration marketing (looks cool, ships poorly).
- ❌ Model-mystique marketing ("powered by our proprietary AI"). We are transparent about using OpenAI, Anthropic, Groq, Llama.
- ❌ Consulting-services revenue mixed with SaaS revenue (kills margins and focus).

---

## Long-Term Expansion

### Year 1 — Own the Beachhead
- **Products:** AI Receptionist (chat), AI Appointment Booker (chat), then Voice v1.
- **Verticals:** Dental + General Medical + Physio + Aesthetics + Legal Intake.
- **Markets:** US + Canada.
- **Regions:** US-East primary; US-West secondary.
- **Channels:** Web widget, WhatsApp, SMS, email, voice inbound.
- **Enterprise:** BAA + SOC 2 Type I.
- **Marketplace:** No marketplace; internal template library only.
- **Milestone target:** $1M ARR, 300+ customers, 3 verticals.

### Year 2 — Platform Emerges
- **Products:** AI Recruiter, AI SDR, AI Debt Collector, AI Support Agent (as separate templates on the same runtime).
- **Verticals:** Add real estate, restaurant, insurance intake, recruiting.
- **Markets:** UK + EU (English) + India.
- **Regions:** EU-West, IN-South data planes.
- **Channels:** Voice outbound (compliance-scoped), Slack, MS Teams.
- **Enterprise:** SOC 2 Type II + ISO 27001 + HIPAA BAA productionized + BYOK + SSO/SCIM + Dedicated tier.
- **Marketplace:** Public template marketplace (verified templates only; no third-party paid templates yet).
- **Milestone target:** $10M ARR, 3,000+ customers, 8 verticals.

### Year 3 — The Shopify of AI Employees
- **Products:** AI Employee Store (third-party templates), AI Employee analytics products, AI Employee "training school" (fine-tunes per vertical), video agents (v1).
- **Verticals:** 15+, expansion via partners.
- **Markets:** Global English + Spanish + Hindi + Portuguese + French.
- **Regions:** 5+ regions with data residency.
- **Channels:** All above + emerging (Discord, WeChat, etc. via partners).
- **Enterprise:** FedRAMP Moderate work; on-prem/VPC GA; HITRUST for healthcare.
- **Marketplace:** Third-party partners monetize templates and tools (rev share).
- **Milestone target:** $100M ARR trajectory, 30,000+ customers, ecosystem of 200+ template creators, 10,000+ AI Employees deployed per day.

### The compounding logic

Each vertical adds:
1. A template + prompt library (asset).
2. An eval suite (moat).
3. An integrations bundle (moat + upsell).
4. A cohort of case studies (marketing).
5. A community of practitioners (referral engine).

None of this requires a code rewrite — because the platform in [docs/](docs/) was designed for it.
