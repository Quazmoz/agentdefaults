# Mobile Release Automation Security Model

## Agent boundary

Version 1.7 uses a risk-gated MCP surface with capability-aware reconciliation.

Both `mra-mcp` and `mra-agent-mcp` expose the same local server. The agent may
perform reads, diagnostics, dry-runs, planning/verification, portfolio audits,
and contained mutations directly. High-risk mutations require a real local
operator approval before the vendor API call occurs.

The MCP boundary resolves vendor credentials internally or delegates credential
ownership to official vendor tooling. Secret values and OAuth tokens are not
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
and Store management; the RevenueCat Google credential is the only Google
service account intended to cross into RevenueCat for Play purchase validation.

RevenueCat API authentication itself does **not** use a Bitwarden `sk_...` key in
MRA 1.7. The official RevenueCat CLI owns browser OAuth, refreshes its tokens, and
stores its credential state in RevenueCat's own local profile. MRA invokes the
CLI and consumes the resulting JSON without reading or copying OAuth tokens.

Legacy RevenueCat secret-reference fields remain parseable for migration safety,
but active RevenueCat authentication ignores them.

## RevenueCat OAuth boundary

Install and authenticate the official RevenueCat CLI locally:

```bash
brew install RevenueCat/tap/rc
rc auth login
rc auth status --scopes --json
```

MRA requires the active RevenueCat CLI method to be `oauth`. An `api_key` login is
rejected because secret API keys are project-scoped and can silently restrict
project discovery/provisioning.

If the active method is `api_key`:

```bash
rc auth logout
rc auth login
```

Choose browser OAuth.

MRA also removes `RC_API_KEY` and `REVENUECAT_V2_SECRET_KEY` from the child
process environment before invoking the RevenueCat CLI. This prevents a stale
project-specific key from overriding the OAuth credential through CLI precedence.

If multiple RevenueCat CLI profiles are in use, MRA can target one with:

```bash
export MRA_REVENUECAT_CLI_PROFILE=<profile-name>
```

The selected profile must still authenticate with OAuth.

## Play reporting and analytics boundary

`play_reporting_freshness` and `mra play freshness` are observe-only. They
mutate no Play state, require no approval, and are the only MRA capability that
uses read-only Google scopes distinct from the publishing scope:

```text
https://www.googleapis.com/auth/playdeveloperreporting
https://www.googleapis.com/auth/devstorage.read_only
```

The publisher service account is reused, but a freshness probe never mints a
token carrying `androidpublisher`, so this path cannot publish even if misused.

The Play bulk-report Cloud Storage bucket id is configuration, not a credential.
It is stored with non-secret profile identifiers or supplied through
`MRA_PLAY_REPORTING_BUCKET`, never in the secret-reference file. Because the
bucket id and the package name are interpolated into request paths, both are
validated against a strict pattern and a value outside it is refused rather
than sent.

Estimated-sales and earnings rows contain buyer city, region, postal code, and
order identifiers. That is purchaser PII and must not cross the agent boundary.
Financial sources return only the newest transaction date, a row count, column
names, and transaction-class counts such as charged versus refunded. Report
content is held in memory for the duration of the probe and is never written to
disk. Do not add a raw-row or "export" mode to this path.

If Google denies a reporting surface, the failure is classified
(`authentication_failed`, `permission_denied`, `api_not_enabled`,
`not_found`, `bucket_not_configured`) and the exact manual Console step is
reported. MRA does not change Google permissions, and a missing bulk-report
grant must not be worked around with Console scraping, cookie replay, browser
automation, or an undocumented endpoint.

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

When a workflow needs a non-RevenueCat secret, pass an immutable reference such
as `authorization_header_secret_id`. The MCP process retrieves that one value
from Bitwarden and sends it directly to the owning vendor API.

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

The RevenueCat portion should report `official-revenuecat-cli-oauth` when the
local RevenueCat CLI is correctly authenticated.

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
invoke `bws`, `security`, the official RevenueCat CLI, Python keyring, local
credential files, or operator CLIs directly. Where this approval/credential
boundary matters, expose the MCP server and restrict direct agent access to those
facilities.

The RevenueCat CLI owns its OAuth token storage. MRA does not copy that token into
Bitwarden, Keychain, environment variables, profiles, logs, or model-visible
state.
