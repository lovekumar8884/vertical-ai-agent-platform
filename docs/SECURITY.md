# SECURITY

## 1. Security Principles

- **Zero trust** — every request authenticated + authorized, even inside the mesh.
- **Least privilege** — services, roles, keys, network — all narrowly scoped.
- **Defense in depth** — WAF + AuthN + AuthZ + RLS + payload filters + audit.
- **Secure by default** — HTTPS-only, no anonymous access, encrypted at rest.
- **Assume breach** — every action audited, PII segregated, blast radius bounded.
- **Fail closed** — on ambiguity, deny.
- **Privacy by design** — data minimization, purpose limitation, user rights.

## 2. Threat Model (STRIDE, condensed)

| Threat | Example | Mitigation |
|--------|---------|-----------|
| **Spoofing** | Fake webhook | HMAC signatures, mTLS for internal |
| **Tampering** | Modified request | TLS, signed events, immutable audit log |
| **Repudiation** | "I didn't do that" | Immutable audit, per-user API keys |
| **Info disclosure** | Cross-tenant leak | RLS, isolation, encryption, filter tests |
| **Denial of Service** | Flood inbound calls | Rate limits, WAF, quotas, autoscaling |
| **Elevation of privilege** | User → admin | Scoped roles, OPA, step-up auth |
| **Prompt injection** | Malicious content in KB | Input filters, output validators, sandboxed tools |
| **Model output abuse** | Toxic/illegal output | Safety classifiers, guardrails, refusal policies |
| **Supply chain** | Compromised dep | SBOM, Sigstore, dependabot, pinned digests |

## 3. Network Security

- All external ingress via **Cloudflare / AWS ALB + WAF** with:
  - DDoS mitigation
  - Bot detection
  - Rule-based blocking (OWASP CRS)
  - Geo-fencing per tenant policy
- **Private subnets** for services; only ingress controllers public.
- **VPC peering** for enterprise customer integrations.
- **Egress control**: default deny; per-tenant allowlists for outbound (tool endpoints).
- **Service mesh** (Istio) with **mTLS everywhere**; SPIFFE identities.
- **NetworkPolicies** per namespace; default deny.

## 4. Data Security

- **In transit**: TLS 1.3 everywhere (external + internal mTLS).
- **At rest**: AES-256 disk encryption; column-level for PII with per-tenant DEKs.
- **Backups**: encrypted with same or higher-strength keys.
- **KMS**: AWS KMS / GCP KMS / Vault Transit; per-tenant CMKs for Dedicated+.
- **BYOK**: Enterprise can supply keys; **HYOK (Hold Your Own Key)** on roadmap for finance/health.

## 5. Secrets Management

- **HashiCorp Vault** primary (or cloud SM).
- No secret in Git, ConfigMap, or env var directly.
- Vault Agent injects secrets to pods; short-lived tokens (1h).
- Dynamic DB creds (Vault DB engine) — no static DSNs.
- Rotation: automatic on schedule + on-demand + on staff offboarding.
- Secret scanning in CI (gitleaks) + at rest (Trufflehog on repos).

## 6. Application Security (AppSec)

- **SDLC gates**:
  - Static analysis (Semgrep, Bandit, ESLint security, gosec)
  - Dependency scan (Snyk / Trivy / Dependabot) — fail on High/Critical
  - Container scan (Trivy) — no known CVEs > High
  - Secret scan (gitleaks)
  - IaC scan (Checkov, tfsec)
  - SAST + SCA on every PR
- **DAST** weekly (OWASP ZAP baseline).
- **Fuzz testing** on parsers (KB ingestion).
- Annual **pentest** (external firm); quarterly internal red-team.
- **Bug bounty** program via HackerOne (invite-only in year 1).

## 7. LLM-Specific Security (OWASP Top 10 for LLMs)

| Risk | Mitigation |
|------|-----------|
| LLM01 Prompt injection | Input classifier + system prompt hardening + tool whitelist + output validator + spotlighting/delimiters |
| LLM02 Insecure output handling | Never `eval`; sanitize HTML; escape SQL; sandbox code |
| LLM03 Training data poisoning | We don't train on tenant data by default |
| LLM04 Model DoS | Token budgets, rate limits, cost caps |
| LLM05 Supply chain (models) | Provider trust tier + reproducible eval on new versions |
| LLM06 Sensitive info disclosure | PII scrubbing pre-embed + post-answer filter |
| LLM07 Insecure plugin design | Tool schema + sandbox + OPA policy |
| LLM08 Excessive agency | Human-in-the-loop for high-risk tools (transactions > threshold) |
| LLM09 Overreliance | Confidence signals, refusal templates, escalation |
| LLM10 Model theft | Rate limits, watermarking prompts (research), obfuscation of system prompts |

### Prompt Injection Specifics
- **Instruction delimiter** (XML tags) around all untrusted content.
- **Spotlighting** — annotate untrusted content with markers.
- **Dual LLM pattern** — a "quarantined" LLM reads user content, produces structured data only.
- **Output policy check** — dedicated safety model validates responses before send.

## 8. Compliance Roadmap

| Standard | Target |
|----------|--------|
| **SOC 2 Type I** | Month 6 |
| **SOC 2 Type II** | Month 12 |
| **HIPAA** (BAA offered) | Month 9 |
| **GDPR / DPA** | Day 1 architecture |
| **ISO 27001** | Month 18 |
| **PCI-DSS SAQ-A** | As needed (payments via Stripe) |
| **CCPA / CPRA** | Day 1 |
| **EU AI Act** (high-risk agents) | Ongoing; conformity assessment for regulated verticals |
| **India DPDP Act** | Day 1 |
| **HITRUST / FedRAMP Moderate** | On enterprise demand (year 2–3) |

## 9. Privacy & Data Rights

- **DSR (Data Subject Requests)** portal: export, correction, deletion.
- **DPA** template ready; sub-processor list published.
- **Purpose limitation**: tenant data not used to train models unless opted-in.
- **Regional pinning** enforced via KMS + storage placement.

## 10. Endpoint / Workforce Security

- MDM (JAMF/Kandji) on all corp devices.
- Hardware keys (Yubikey) mandatory for prod access.
- **Zero standing production access** — Just-In-Time via Teleport/Boundary with approval workflow.
- SSH via ephemeral certs (short TTL).
- All prod actions logged; recording for admin sessions.

## 11. Incident Response

- **On-call rotation** via PagerDuty.
- **Severity matrix** (SEV1–SEV4) with response SLA.
- Runbooks in Notion/Backstage; drills quarterly.
- **Blameless post-mortems** within 5 business days.
- Customer notification per contractual SLA (default 72h for breach involving PII).

## 12. Audit Trail

- Every mutating admin/API action logged with actor, before/after, IP, UA.
- Immutable (append-only) storage; separate account; tamper-evident (Merkle hash chain).
- Exportable to tenant SIEM (Splunk/Datadog) via streaming.

## 13. Voice-Specific
- **Call recording consent** enforced per jurisdiction.
- **STIR/SHAKEN** attestation for outbound.
- Do-Not-Call scrubbing pre-dial.
- Voice cloning consent verification.

## 14. Anti-Patterns Rejected

- ❌ Long-lived shared prod credentials.
- ❌ "Just this once" backdoors.
- ❌ Storing PII in logs, metrics, traces.
- ❌ Cross-tenant caches keyed by non-tenant keys.
- ❌ Disabling MFA for convenience.

## 15. Assumptions
- Compliance investment is priced into Enterprise plans.
- We pursue certifications only when a customer requires it — but architect for them from day 1.
- Prompt injection is an unsolved problem; we mitigate with layered defenses and continuously updated classifiers.
