# AUTHENTICATION & AUTHORIZATION

## 1. Identity Model

```
Tenant (Organization)
 └── Workspaces (billing + data residency boundary)
      └── Projects (grouping of agents + resources)
           └── Agents / Tools / Corpora
Users ── belong to Tenants (may be multi-tenant)
API Keys ── belong to Tenant + Workspace (+ optional Project scope)
Service Accounts ── machine principals (M2M)
```

## 2. Authentication Methods

| Method | Use Case | Standard |
|--------|---------|---------|
| **Password + MFA** | Console UI | Argon2id + TOTP/WebAuthn |
| **SSO** | Enterprise console | SAML 2.0, OIDC (Okta, Azure AD, Google, Ping) |
| **API Key** | Server-to-server | Prefix + secret (`sk_live_...`), Argon2 hashed at rest |
| **OAuth 2.1** | Third-party integrations | Auth code + PKCE, client credentials |
| **JWT (short-lived)** | Session tokens for WebSocket/WebRTC | RS256, 5-min TTL, refresh via cookie |
| **mTLS** | Internal service-to-service | Istio SPIFFE identities |
| **HMAC signing** | Inbound webhooks (Twilio, WhatsApp, Stripe) | Provider-specific |

## 3. API Key Format & Storage

- Format: `sk_{env}_{keyId}_{secret}` (e.g., `sk_live_01HN...ABC...`).
- **Only the prefix + `keyId` stored** alongside `hash = argon2id(secret)`.
- Secret shown **once** at creation; download-only.
- Support **key rotation** (create new → coexist → revoke).
- Support **scoped keys** (`agents:read`, `sessions:write`, `kb:*`).
- Support **IP allowlist** and **origin allowlist**.
- Auto-detect leaked keys via GitHub secret scanning integration → auto-revoke + notify.

## 4. Session Tokens

- Console UI logs in → short-lived access JWT (15 min) + refresh token (rotating, 30 days, httpOnly, Secure, SameSite=Lax).
- Refresh tokens stored server-side as rotating opaque tokens; **reuse detection** → invalidate family.
- WebSocket/WebRTC tokens: single-use JWTs scoped to `session_id` with 60s TTL.

## 5. Authorization Model

**Hybrid RBAC + ABAC + ReBAC**.

### 5.1 Roles (built-in)
- **Owner** — everything
- **Admin** — everything except billing/ownership transfer
- **Developer** — build, deploy, invoke; no billing
- **Reviewer** — read sessions, run evals
- **Analyst** — read dashboards
- **Support** — read-only sessions, initiate handoff
- **Billing** — billing + usage only

### 5.2 Scopes (fine-grained)

Format: `<resource>:<action>[:<qualifier>]`

Examples:
- `agents:read`, `agents:write`, `agents:publish`
- `sessions:read`, `sessions:read:pii` (extra grant for PII)
- `kb:read`, `kb:write`
- `tools:invoke`, `tools:manage`
- `billing:read`, `billing:write`
- `admin:users`, `admin:sso`, `admin:audit`

### 5.3 Policy Engine

- **OPA (Open Policy Agent)** with Rego for centralized policy.
- Policies distributed via `opa` sidecar in each service.
- Every gRPC/HTTP handler wraps decision:
```rego
allow if {
  input.principal.tenant_id == input.resource.tenant_id
  has_scope(input.principal, required_scope)
  not resource_locked(input.resource)
}
```

### 5.4 Row/Object-Level

- Postgres RLS enforces `tenant_id` on every query.
- OPA layer enforces workspace/project scoping + PII scope.
- Qdrant queries carry `tenant_id` + `acl_tags` filters.

## 6. SSO / SCIM

- **SAML 2.0** and **OIDC** for login.
- **SCIM 2.0** for user + group provisioning.
- **Just-in-time provisioning** with attribute mapping (`role_mapping.json` per tenant).
- **Enforce SSO** toggle per tenant → disables password login.

## 7. MFA / Step-Up
- TOTP + WebAuthn (Yubikey / Passkeys).
- **Step-up auth** required for: billing changes, key creation, PII export, tenant deletion, SSO config.

## 8. Machine-to-Machine (M2M)
- OAuth 2.1 client credentials → short-lived JWT (15 min).
- Optionally bound to workload identity (SPIFFE) for internal callers.

## 9. Delegated Access
- **Tenant impersonation** by Vertical SASAI staff requires:
  - Explicit tenant approval (in-console consent + email).
  - Time-boxed grant (max 24h).
  - Every action logged with `impersonator_id` + `impersonated_id`.
  - Reason required, visible to tenant admins.

## 10. Threat Considerations
- **Credential stuffing** → progressive slowdown + CAPTCHA + IP reputation (Cloudflare Turnstile).
- **Session fixation** → rotate session on privilege change.
- **CSRF** → SameSite cookies + double-submit tokens for cookie-auth endpoints.
- **JWT pitfalls** → asymmetric only (RS256/EdDSA), short TTL, `kid` header, JWKS rotation quarterly.
- **Token in URL** → forbidden except one-time signed download URLs (with narrow scope).

## 11. Audit
- Every authN event (success + failure) logged with `tenant_id`, `user_id`, `ip`, `ua`, `geoip`.
- Failed auth surges → automated alerts.
- Session inventory visible to user + admin; remote sign-out available.

## 12. Assumptions
- Auth service uses **Ory Kratos + Hydra + Keto** (or Auth0/WorkOS for time-to-market) — decision deferred to [TECH_STACK.md](TECH_STACK.md).
- All internal traffic runs within mesh with mTLS; if not, JWT + IP allowlist required.
