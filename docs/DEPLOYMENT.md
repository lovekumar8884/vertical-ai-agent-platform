# DEPLOYMENT

## 1. Environments

| Env | Purpose | Data | Access |
|-----|---------|------|--------|
| `local` | Dev laptop (docker-compose) | Ephemeral | Dev |
| `ci` | PR previews (ephemeral k8s ns) | Seeded | Dev |
| `dev` | Shared integration | Seeded | Dev + QA |
| `staging` | Pre-prod, prod-like | Anonymized snapshot | Dev + QA + PM |
| `prod` | Live | Real | Restricted + on-call |
| `dr` | Disaster recovery replica | Replicated | Automated |
| `enterprise-<tenant>` | Single-tenant dedicated / VPC | Real | Restricted |

## 2. Local Development

Goal: **`make dev` → full stack up in < 5 min on a laptop.**

- **docker-compose** orchestrates:
  - Postgres, Redis, Qdrant, Kafka (Redpanda), MinIO, Temporal, LocalStack (for AWS APIs).
  - LiveKit local server.
  - Wiremock for provider stubs (Twilio, WhatsApp, LLMs) → deterministic tests.
- **Devcontainer** (VS Code) definition for zero-setup onboarding.
- Hot-reload for each service via `uvicorn --reload` / `ts-node-dev`.
- `make seed` populates demo tenant + agents.
- Optional: **Tilt** for k8s-based local dev when needed.

## 3. Kubernetes as the Substrate

- **EKS / GKE / AKS** in cloud; **k3s** for edge/on-prem; **OpenShift** for enterprise if required.
- **Helm** charts per service; **umbrella chart** per environment.
- **Argo CD** for GitOps continuous delivery.
- **Cert-manager** for TLS (Let's Encrypt + private CA for internal).
- **External-DNS** for automated DNS.
- **Cluster autoscaler** + **Karpenter** (AWS) for node right-sizing.
- **KEDA** for event-driven autoscaling.
- **Vertical Pod Autoscaler** in "recommender" mode for right-sizing.

## 4. CI/CD Pipeline

```
PR opened
  → lint (ruff, eslint, buf lint)
  → unit tests
  → contract tests (proto/openapi)
  → build multi-arch image (amd64/arm64)
  → SBOM (syft) + sign (cosign)
  → security scans (trivy, semgrep, gitleaks)
  → deploy preview env (namespace-per-PR)
  → e2e tests (Playwright + Pytest)
  → eval regressions (agent evals)
  → destroy preview

Merge to main
  → build + push signed image
  → Argo CD auto-syncs to dev
  → smoke + integration tests
  → manual promote to staging → prod (progressive)
```

**Tooling**: GitHub Actions (or GitLab CI) primary; Buildkite for large parallel jobs.

## 5. Release Strategies

- **Progressive delivery** with **Argo Rollouts**: Canary → 5% → 25% → 100% based on SLO metrics.
- **Feature flags** (OpenFeature / Unleash) — toggle new agent runtime nodes per tenant.
- **Automated rollback** on SLO breach (error rate, latency).
- **Blue/green** for stateful services during major upgrades.
- **Schema migrations**: expand/contract, never a single breaking migration.

## 6. Zero-Downtime Deploys

- Rolling updates with `maxSurge: 25%, maxUnavailable: 0`.
- Graceful shutdown (30s SIGTERM window; drain long-lived connections).
- **In-flight session preservation**:
  - Voice: workers drained by refusing new; old calls finish (drain up to 10 min).
  - WS/SSE: send `reconnect` hint; clients reconnect via sticky WS gateway.
- Kafka consumers with cooperative rebalance (no stop-the-world).

## 7. Configuration Management

- 12-factor: env vars for env-specific, Helm values for structural.
- **Sealed Secrets / SOPS** for secrets in Git (or ESO reading Vault).
- **Dynamic config** via feature flags — never redeploy for a toggle.
- Config schemas versioned; validated on load.

## 8. Multi-Region Deployment

- Argo CD **ApplicationSet** deploys the same app to multiple regional clusters.
- Region-specific overlays (Kustomize) inject: KMS ARN, S3 bucket, region-local endpoints.
- **DNS**: Global Accelerator (AWS) or Cloudflare Load Balancer for anycast entrypoint.
- **Data**: pinned per region; replication only for control plane.

## 9. On-Prem / VPC Deployment

- **Air-gap friendly**: images mirrored to customer registry; Helm charts self-contained.
- **k3s** or customer's existing k8s.
- **Backing services**: prefer customer-managed (their Postgres, Kafka) with adapters.
- **License server** offline-friendly.
- **Support tunnel** via Teleport Cloud (customer-controlled).

## 10. Disaster Recovery

| Scenario | RPO | RTO | Mechanism |
|----------|-----|-----|-----------|
| Pod crash | 0 | seconds | K8s restart |
| Node loss | 0 | < 2 min | Reschedule + PDB |
| AZ loss | 0 | < 5 min | Multi-AZ redundancy |
| Region loss (control plane) | ≤ 5 min | ≤ 30 min | Failover to DR region |
| Region loss (data plane) | ≤ 5 min | ≤ 60 min | Restore from cross-region backup; tenants notified |
| Accidental delete | ≤ 24 h | ≤ 4 h | PITR + tombstone recovery |

- Backups tested via **quarterly restore drills**.
- DR runbook rehearsed every 6 months.

## 11. Observability of Deploys

- Every deploy annotates Grafana with build SHA + service.
- Deployment events on Slack (per env).
- Sentry release tracking.
- **Change-log** auto-generated per release.

## 12. Compliance & Deployment
- SBOM published with each release.
- Image signatures verified by admission controller (Kyverno / OPA Gatekeeper).
- Only signed images admitted to prod namespaces.
- No production access without ticket + approval (Teleport).

## 13. Cost Guardrails
- **Kubecost** dashboards per namespace/tenant.
- Alerts on overspend (per team, per tenant).
- Nightly right-sizing recommendations (VPA + custom scripts).
- Spot instances for stateless workers with disruption budgets.

## 14. Anti-Patterns Rejected
- ❌ `kubectl apply` in prod by humans.
- ❌ Snowflake environments (dev vs. prod drift).
- ❌ Secrets in Helm values.yaml.
- ❌ Long-lived branch environments.
- ❌ Deploying via `latest` tag.

## 15. Assumptions
- We commit to GitOps (Argo CD) from Day 1.
- We accept the operational cost of running Kubernetes in exchange for portability and consistency.
- On-prem is a real (paid) product line, priced accordingly.
