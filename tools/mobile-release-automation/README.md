# Mobile Release Automation Toolkit

## Purpose

Mobile Release Automation (MRA) gives operators and coding agents a safe,
auditable way to automate repetitive Google Play, RevenueCat, and AdMob work
without placing vendor credentials in Git, prompts, model context, or normal
command output.

Every vendor operation uses a documented public API. MRA does not scrape vendor
consoles or rely on private browser endpoints.

For the cross-platform desired-state workflow, start with
[`AUTOMATION.md`](AUTOMATION.md) and
[`desired-state.example.json`](desired-state.example.json).

## Platform model

| Platform | Authentication | Automation status |
|---|---|---|
| Google Play | Google Cloud service account | Releases, tracks, products, listings, images, tester groups, reviews/replies, country availability, and deobfuscation artifacts are API-driven. |
| RevenueCat | API v2 secret key | Projects, apps, products, entitlements, offerings, packages, product wiring, and webhook integrations are API-driven. |
| AdMob | OAuth user credentials | Inventory and reporting are broadly automatable. App/ad-unit and mediation writes exist in the public API but are limited-access per AdMob account. |

AdMob service accounts do not work. A monetization OAuth scope also does not
bypass Google's account-level limited-access gate. MRA exposes those capabilities
conditionally and returns an explicit manual handoff when Google denies them.

## Install

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -e ".[mcp]"
```

Install Bitwarden's official Secrets Manager CLI (`bws`) separately and ensure it
is on `PATH`.

Entry points:

```text
mra            operator CLI
mra-agent      agent-safe read/binding CLI
mra-mcp        risk-gated local MCP server
mra-agent-mcp  alias for the same risk-gated MCP server
```

The MCP server can be launched directly with:

```bash
.venv/bin/python -m mra.secure_mcp_server
```

For an MCP-capable client:

```bash
claude mcp add mobile-release-automation-agent -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/python \
  -m mra.secure_mcp_server
```

## Secret architecture

Static credentials belong in **Bitwarden Secrets Manager**. Machine-local
rotating credentials belong in the **OS credential store**. App profiles contain
only identifiers and immutable secret references.

Recommended Bitwarden project:

```text
mobile-release-automation
```

Example secret names:

```text
mra/google-play/publisher-service-account
mra/google-play/revenuecat-service-account
mra/revenuecat/bootstrap/v2-secret
mra/admob/oauth-client
mra/revenuecat/motionguard/v2-secret
mra/revenuecat/pressdeck/v2-secret
mra/webhooks/backend/authorization-header
```

### Bitwarden machine account

Use a read-only machine account for routine automation. Store its machine access
token in macOS Keychain rather than Git, shell startup files, profiles, or agent
prompts.

MRA looks for:

```text
service: com.quazmoz.mobile-release-automation.bitwarden
account: mra-machine-account
```

One safe way to store it without putting the value in shell history is:

```bash
read -s BWS_TOKEN
security add-generic-password -U \
  -a mra-machine-account \
  -s com.quazmoz.mobile-release-automation.bitwarden \
  -w "$BWS_TOKEN"
unset BWS_TOKEN
```

For trusted CI or another non-macOS environment,
`BWS_ACCESS_TOKEN` may be injected by that platform's secret store. Do not export
it into an unrestricted coding-agent environment.

### Global credential bindings

Bind immutable Bitwarden UUIDs, never secret values:

```bash
mra-agent auth bind-play --secret-id <PLAY_PUBLISHER_SERVICE_ACCOUNT_UUID>
mra-agent auth bind-revenuecat-play --secret-id <RC_PLAY_SERVICE_ACCOUNT_UUID>
mra-agent auth bind-revenuecat-bootstrap --secret-id <RC_BOOTSTRAP_V2_KEY_UUID>
mra-agent auth bind-admob --secret-id <ADMOB_DESKTOP_OAUTH_CLIENT_UUID>
```

These references are written to the private local MRA config directory.

Google Play uses separate service-account material for:

1. publishing to Google Play; and
2. the credential RevenueCat receives for Google Play purchase validation.

Keep those bindings distinct.

The RevenueCat bootstrap key solves a different problem: a brand-new MRA profile
may not have a RevenueCat project yet, so it cannot already have that project's
narrow project-specific API key. The bootstrap key is a RevenueCat v2 secret key
with only the provisioning permissions the portfolio needs, such as project,
app, and entitlement read/read-write access. Its value stays in Bitwarden and is
resolved only inside MRA.

### Per-app RevenueCat key

Each independently monetized app/app family should normally have its own
RevenueCat project and scoped V2 secret key after the project exists.

Bind the key by Bitwarden secret UUID:

```bash
mra-agent profile bind-revenuecat \
  --profile motionguard \
  --secret-id <REVENUECAT_V2_KEY_UUID>
```

A persisted project-specific profile key always takes precedence over the global
bootstrap key. For a profile that does not have one yet, `load_profile()` inherits
the bootstrap UUID in memory only. `load_profiles()` and `profiles.json` continue
to represent the real persisted state, so the bootstrap reference is not copied
into every app profile.

The normal secret flow is:

```text
agent/operator
    -> profile slug
    -> project-specific Bitwarden UUID if bound
       else global RevenueCat bootstrap Bitwarden UUID
    -> bws secret get <UUID>
    -> credential held in MCP process memory
    -> RevenueCat API
```

MRA retrieves one secret by UUID. It does not list a Bitwarden project and does
not return the secret value to the model.

### AdMob OAuth

The static Desktop OAuth client comes from Bitwarden. The long-lived refresh
token is generated by the local browser-consent flow and stored in the OS
credential store.

Run once, or again after a grant is revoked/scopes change:

```bash
mra admob login
```

Normal calls reconstruct short-lived Google credentials in memory. No authorized
user JSON needs to be persisted.

## Profiles

A profile maps one app across the vendors. Example conceptual shape after
project-specific RevenueCat binding:

```json
{
  "motionguard": {
    "package_name": "com.quazmoz.motionguard",
    "admob_app_id": "ca-app-pub-...~...",
    "admob_publisher_id": "pub-...",
    "revenuecat_project_id": "proj_...",
    "revenuecat_app_id": "app_...",
    "revenuecat_secret_id": "6f7c12c0-df7b-4a2b-9360-1539a4d13392"
  }
}
```

A new profile may initially contain only `package_name` and vendor identifiers
that are already known. It does not need a RevenueCat project id or per-app
RevenueCat key before `rc_list_projects`/`rc_create_project` can run, provided the
global bootstrap key is bound.

`revenuecat_secret_id` is a Bitwarden object UUID, not an `sk_...` secret value.
Agent-visible `profile_get` output intentionally excludes secret-reference fields.

## MCP risk model

The agent chooses an operation and non-secret parameters. The local MCP process
resolves credentials and enforces the action boundary.

### Observe

Examples:

- diagnostics and capability discovery
- Play/RevenueCat/AdMob reads
- AdMob reporting
- desired-state planning and verification
- Play edit dry-runs
- portfolio audits

### Contained mutation

Examples:

- internal Play release
- creating one RevenueCat project/app/product/empty entitlement/package/offering
- creating an unlinked AdMob app or one ad unit where Google permits it
- reconciling verified non-secret IDs into a local profile

### High-risk mutation

Examples:

- non-internal Play releases/promotions
- public Play Store metadata/images/tester changes
- public review replies
- irreversible AdMob app-store linking
- live mediation/mapping/experiment changes
- RevenueCat current-offering changes
- RevenueCat entitlement/package wiring
- RevenueCat webhook create/update/delete
- backing-store product creation
- destructive, financial, or broad multi-app changes

High-risk MCP actions do **not** accept an agent-controlled `confirm=true` bypass.
They invoke the native local human-approval gate and fail closed if the operator
declines, times out, or the approval UI is unavailable.

The operator `mra` CLI remains a separate trust surface and uses explicit
operator confirmation such as `--yes` for mutation commands.

## Plan, apply, verify

The MCP exposes:

```text
mra_plan(profile, desired_state)
mra_apply(profile, desired_state)
mra_verify(profile, desired_state)
```

Desired state is secret-free JSON. Literal fields such as `api_key`,
`private_key`, `authorization_header`, OAuth tokens, or passwords are rejected.
Where a secret is needed, use an immutable `*_secret_id` reference.

`mra_apply` re-plans after each attempted write. That allows a newly created
RevenueCat project/app or AdMob app to unblock later resources in the same run.
Actions that are declined, denied, or fail are not blindly retried in that
invocation.

For the full schema and example, see [`AUTOMATION.md`](AUTOMATION.md).

## Portfolio audit

Use:

```text
mra_audit_profile(profile)
mra_audit_portfolio()
```

The audit reads each configured vendor independently so one broken credential or
vendor binding does not abort every app. It can surface, among other things:

- vendor read/auth failures
- unanswered one- or two-star Play reviews
- a RevenueCat app missing for the configured package
- products with no observed current RevenueCat offering
- AdMob `ACTION_REQUIRED` and `IN_REVIEW` states
- a configured AdMob app ID absent from inventory
- a matched AdMob app with no ad units

Snapshots returned through MCP are defensively redacted.

## Google Play

MRA currently automates:

- AAB upload
- track reads and releases
- promotion between tracks
- staged rollout fractions
- release notes
- subscriptions and one-time products
- localized store listings
- screenshots/images
- Google Group tester configuration
- country availability
- reviews and developer replies
- ProGuard/R8 and native deobfuscation uploads

Read-only operations discard their temporary edit. Dry-run edit mutations are
validated and discarded. A committed public-facing change is approval-gated.

## RevenueCat

MRA automates the project/app/catalog setup needed for Android monetization:

- project list/create, including new-project bootstrap through the global Bitwarden key
- Play app creation using the dedicated Google Play validation credential
- products and backing-store creation
- entitlements and product attachment
- offerings/packages and product attachment
- current-offering changes
- webhook list/get/create/update/delete

For a global bootstrap key, grant only the provisioning permissions the portfolio
needs. A typical project/app/entitlement bootstrap may require:

```text
project_configuration:projects:read
project_configuration:projects:read_write
project_configuration:apps:read
project_configuration:apps:read_write
project_configuration:entitlements:read
project_configuration:entitlements:read_write
```

Add products/offerings/packages/integrations permissions only if the bootstrap
workflow really needs those resources. After the project exists, prefer a
narrower project-specific v2 key for ongoing automation.

For keys that only need read access, grant only the corresponding
`project_configuration:*:read` permissions. Add `read_write` only for resources
an automation path actually mutates.

Typical broader mutation permissions may include:

```text
project_configuration:projects:read_write
project_configuration:apps:read_write
project_configuration:products:read_write
project_configuration:entitlements:read_write
project_configuration:offerings:read_write
project_configuration:packages:read_write
project_configuration:integrations:read_write
```

Do not grant customer/refund/promotional-entitlement permissions unless a
specific workflow genuinely requires them.

RevenueCat webhook authorization material is passed as a Bitwarden UUID.
RevenueCat may return a webhook `signing_secret`; MRA redacts that field before it
reaches agent-visible output.

## AdMob

AdMob inventory/reporting and limited-access monetization management are modeled
separately.

Broadly useful reads include:

- accounts/apps/ad units
- app approval state
- ad sources and adapters
- network report
- mediation report
- campaign report
- monetization-health report by app version, GMA SDK, format, and serving restriction

Where Google enables the account, MRA also implements:

- app creation
- ad-unit creation
- mediation group create/update
- ad-unit mapping create/batch create
- mediation A/B experiment create/stop

`admob_capabilities` reports observed/documented capability state. MRA does not
create dummy objects just to probe write access.

If an actual required write receives Google's limited-access denial, reconciliation
returns `manual_required` with the exact remaining console action. Complete that
single step and run `mra_verify` again.

Do not add private Console APIs, cookie replay, or browser automation to bypass
Google's account gate.

## Defensive redaction

Secret isolation is the primary control; redaction is defense in depth. Vendor
responses handled by the new management/reconciliation paths are recursively
scrubbed for common sensitive fields and credential formats such as bearer
tokens, RevenueCat `sk_...` keys, private keys, refresh tokens, client secrets,
and webhook signing secrets.

Provider retrieval failures also avoid echoing secret-provider stdout/stderr.

## Trust boundary

The native approval gate protects the MCP path. It does **not** make unrestricted
shell execution under the same OS user safe.

An unrestricted local agent running as the same macOS user may be able to invoke
`bws`, `security`, Python keyring, or operator CLIs directly. Where the credential
and approval boundary matters, expose the MCP surface while restricting direct
agent access to those facilities.

## Legacy compatibility

Some credential loaders retain owner-only local-file/environment fallbacks for
migration compatibility. New installations should use Bitwarden bindings and the
OS credential store. Private credential files are rejected if group/world
accessible.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

The suite is offline and covers vendor request shapes, edit cleanup, risk gates,
secret-provider behavior, RevenueCat bootstrap credential inheritance, AdMob
access classification/reporting, webhook redaction, and desired-state planning.
Repository CI also runs the full AgentDefaults contract validation before the MRA
unit suite.
