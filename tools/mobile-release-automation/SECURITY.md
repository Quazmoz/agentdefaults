# Mobile Release Automation Security Model

## Agent boundary

Version 1.6 uses a risk-gated MCP surface with capability-aware reconciliation.

Both `mra-mcp` and `mra-agent-mcp` expose the same local server. The agent may
perform reads, diagnostics, dry-runs, planning/verification, portfolio audits,
and contained mutations directly. High-risk mutations require a real local
operator approval before the vendor API call occurs.

The MCP boundary resolves vendor credentials internally. Secret values are not
normal tool arguments and are not intentionally returned to the model.

## Risk classes

- `observe`: diagnostics, vendor reads, AdMob reports, plan/verify/audit, and Play dry-runs.
- `contained`: internal-track Play releases, creation of individual RevenueCat objects that do not rewire live access, unlinked AdMob app/ad-unit creation where supported, and local reconciliation of verified non-secret IDs.
- `high`: non-internal Play releases/promotions, public Play metadata/tester/review mutations, irreversible AdMob store linking, mediation/mapping/experiment writes, RevenueCat current-offering changes, entitlement/package wiring, live webhooks, backing-store product creation, and destructive/financial/broad mutations.

High-risk MCP tools do not accept an agent-controlled `confirm=true` bypass. On
macOS they invoke a native approval dialog describing the exact target. If the
operator declines, the dialog times out, or native approval is unavailable, the
action fails closed.

The operator CLI remains a separate trust surface and retains its own explicit
confirmation behavior.

## Credentials

Bitwarden Secrets Manager is the preferred static credential source. The
Bitwarden machine-account token remains in macOS Keychain, and local MRA
configuration stores only immutable secret references.

Google Play publisher credentials and the separate Google credential used by
RevenueCat remain distinct. The publisher credential is used for Play release
and Store management; the RevenueCat credential is the only Google service
account intended to cross into RevenueCat for Play purchase validation.

Legacy owner-only local-file/environment fallbacks remain for migration
compatibility. New installations should use the secret-manager bindings and OS
credential store. Private credential files are rejected if group/world readable.

## Desired-state boundary

`mra_plan`, `mra_apply`, and `mra_verify` accept JSON-shaped desired state.
Desired state is intentionally secret-free.

The validator rejects literal fields such as:

```text
authorization
authorization_header
access_token
refresh_token
client_secret
private_key
signing_secret
api_key
password
```

When a workflow needs a secret, pass an immutable reference such as
`authorization_header_secret_id`. The MCP process retrieves that one value from
Bitwarden and sends it directly to the owning vendor API.

Do not weaken the desired-state validator to make secret literals more
convenient for an agent.

## Defensive output redaction

Secret isolation is the primary control. Recursive redaction is defense in depth
for vendor responses or error strings that unexpectedly echo sensitive data.

The redaction layer masks common sensitive fields and formats including bearer
tokens, RevenueCat `sk_...` keys, OAuth refresh/access tokens, client secrets,
private keys, API keys, authorization headers, and webhook signing secrets.

RevenueCat webhook APIs may return a `signing_secret`. MRA redacts it before the
response crosses the agent boundary. Webhook authorization values are accepted
by secret UUID, not literal MCP input.

Provider secret-retrieval failures must continue to suppress provider
stdout/stderr because provider output itself may contain sensitive material.

## AdMob OAuth and account gates

AdMob does not support service-account authentication. Store the Google Desktop
OAuth client JSON in Bitwarden and bind its UUID locally:

```bash
mra-agent auth bind-admob --secret-id YOUR_BITWARDEN_SECRET_UUID
```

The OAuth client JSON is read into the MCP process. The long-lived AdMob OAuth
refresh token is stored separately in the OS credential store through Python
`keyring` (macOS Keychain on macOS). MRA does not need to persist an authorized-
user token JSON file.

Run browser authorization after the client is bound:

```bash
mra admob login
```

If monetization-management calls are required, the grant needs the
`admob.monetization` scope. That scope is necessary but not sufficient: Google
separately gates documented v1beta app/ad-unit and mediation-management methods
per AdMob account.

MRA therefore distinguishes:

- OAuth authentication failure;
- ordinary permission/scope/API-enablement failure; and
- Google's documented limited-access account denial.

A limited-access denial must not be "fixed" by adding private Console endpoints,
replaying browser cookies, scraping the UI, or claiming a different IAM role or
service account can bypass Google's server-side entitlement. Reconciliation
returns `manual_required`, the operator performs the exact remaining Console
step, and `mra_verify` reads the result afterward.

## Verification

After changing local credential bindings or MRA itself, run:

```bash
mra-agent doctor
```

For MCP clients, `approval_policy` describes the current mutation policy. The
cross-platform health path is:

```text
mra_plan
mra_apply
mra_verify
```

For portfolio-wide read-only inspection use:

```text
mra_audit_profile
mra_audit_portfolio
```

Repository validation must include the full AgentDefaults contract suite and the
offline MRA unit tests.

## Trust boundary

The native approval gate protects the MCP path. It does **not** make unrestricted
shell access safe.

An agent with unrestricted execution under the same macOS user may be able to
invoke `bws`, `security`, Python keyring, local credential files, or operator CLIs
directly. Where this approval/credential boundary matters, expose the MCP server
and restrict direct agent access to those facilities.

Similarly, environment-variable fallbacks such as a Bitwarden machine token or
legacy RevenueCat key are unsafe if they are inherited by an unrestricted agent
process. Prefer Keychain/Bitwarden resolution inside the MCP process.
