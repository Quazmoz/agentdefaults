# Mobile Release Automation Toolkit

## Purpose

Mobile Release Automation (MRA) gives operators and coding agents a safe,
auditable way to automate repetitive Google Play, RevenueCat, and AdMob work
without placing vendor credentials in Git, prompts, model context, or normal
command output.

Every vendor operation uses a documented public API or an official vendor CLI.
MRA does not scrape vendor consoles or rely on private browser endpoints.

For the cross-platform desired-state workflow, start with
[`AUTOMATION.md`](AUTOMATION.md) and
[`desired-state.example.json`](desired-state.example.json).

## Platform model

| Platform | Authentication | Automation status |
|---|---|---|
| Google Play | Google Cloud service account | Releases, tracks, products, listings, images, tester groups, reviews/replies, country availability, and deobfuscation artifacts are API-driven. |
| RevenueCat | Browser OAuth through the official RevenueCat CLI | Projects, apps, products, entitlements, offerings, packages, product wiring, and webhook integrations are automatable across projects authorized to the RevenueCat account. |
| AdMob | OAuth user credentials | Inventory and reporting are broadly automatable. App/ad-unit and mediation writes exist in the public API but are limited-access per AdMob account. |

AdMob service accounts do not work. A monetization OAuth scope also does not
bypass Google's account-level limited-access gate. MRA exposes those capabilities
conditionally and returns an explicit manual handoff when Google denies them.

RevenueCat is intentionally different from the old MRA design. MRA no longer
uses project-scoped RevenueCat `sk_...` keys for agent workflows. The official
RevenueCat CLI owns browser OAuth, token refresh, and local credential storage,
and MRA calls RevenueCat through that CLI's `rc api` surface.

## Install

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -e ".[mcp]"
```

Install Bitwarden's official Secrets Manager CLI (`bws`) separately and ensure it
is on `PATH`.

Install the official RevenueCat CLI and authenticate once:

```bash
brew install RevenueCat/tap/rc
rc auth login
rc auth status --json
```

Use the browser OAuth path. MRA rejects RevenueCat CLI profiles whose active
method is `api_key`.

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
rotating credentials belong in the vendor/OS credential store. App profiles
contain non-secret identifiers and, for backward compatibility, may still contain
old secret-reference fields that current RevenueCat automation ignores.

Recommended Bitwarden project:

```text
mobile-release-automation
```

Example secret names:

```text
mra/google-play/publisher-service-account
mra/google-play/revenuecat-service-account
mra/admob/oauth-client
mra/webhooks/backend/authorization-header
```

Do not create a RevenueCat bootstrap API key for MRA. Do not create one
RevenueCat secret key per app merely to let Claude or another coding agent manage
RevenueCat. Browser OAuth is the account-level authorization mechanism for this
workflow.

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
mra-agent auth bind-admob --secret-id <ADMOB_DESKTOP_OAUTH_CLIENT_UUID>
```

These references are written to the private local MRA config directory.

Google Play uses separate service-account material for:

1. publishing to Google Play; and
2. the credential RevenueCat receives for Google Play purchase validation.

Keep those bindings distinct.

### RevenueCat OAuth

RevenueCat account authorization is owned by the official `rc` CLI:

```bash
rc auth login
rc auth status --json
```

The browser OAuth session is account-level and can reach the projects and scopes
granted to that RevenueCat account. MRA does not read or copy the OAuth access or
refresh token. Instead it runs `rc api` as a child process and consumes only the
JSON response.

MRA removes these environment variables from the RevenueCat child process:

```text
RC_API_KEY
REVENUECAT_V2_SECRET_KEY
```

That prevents a stale project-scoped API key from silently taking precedence over
the OAuth session.

If you use multiple RevenueCat CLI profiles, select one for MRA with:

```bash
export MRA_REVENUECAT_CLI_PROFILE=<profile-name>
```

The selected CLI profile still must report `method: oauth`.

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

A profile maps one app across the vendors. Example conceptual shape:

```json
{
  "webhookdeck": {
    "package_name": "com.quazmoz.webhookdeck",
    "admob_app_id": "ca-app-pub-...~...",
    "admob_publisher_id": "pub-...",
    "revenuecat_project_id": "proj_...",
    "revenuecat_app_id": "app_..."
  }
}
```

A new profile can begin with only the Android package name. It does not need a
RevenueCat project id or RevenueCat API key before `rc_list_projects` or
`rc_create_project` can run. The OAuth account is the authorization boundary.
Agents using the risk-gated MCP can create that package-only mapping with
`profile_create(profile, package_name)`; operators can use `mra profile set`.
Neither path requires direct editing of `profiles.json`.

Older `profiles.json` files may contain `revenuecat_secret_id`, and older
`secret-refs.json` files may contain `revenuecat_bootstrap_secret_id`. MRA keeps
those fields parseable for migration safety but does not resolve or use them.
The old `mra-agent profile bind-revenuecat` and
`mra-agent auth bind-revenuecat-bootstrap` commands return a deprecation notice
and do not persist new bindings.

## MCP risk model

The agent chooses an operation and non-secret parameters. The local MCP process
enforces the action boundary.

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
Where a non-RevenueCat secret is needed, use an immutable `*_secret_id`
reference.

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
vendor binding does not abort every app. A Play package configures Play; RevenueCat
and AdMob are audited only when their own profile identifiers are present. Merely
having an Android package does not opt an app into those vendors. Desired-state
setup can still request unbound RevenueCat or AdMob discovery explicitly. It can
surface, among other things:

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

## Play analytics and reporting freshness

Play Console appears to lag. `play freshness` answers how much of that lag is
Google's data pipeline and how much is only the Console UI, using official
Google surfaces alone. It is observe-only: it mutates nothing, needs no
approval, and never scrapes the Console.

```bash
mra play freshness --profile motionguard
mra play freshness --profile motionguard --skip-financial
```

```text
play_reporting_freshness(profile, include_financial=true)
```

### Which surface carries which dataset

| Dataset | Official source | Available? |
|---|---|---|
| Daily installs / user acquisitions | bulk report `stats/installs/` | yes |
| Daily uninstalls | bulk report `stats/installs/` (uninstall columns) | yes |
| Store-listing visitors / clicks | bulk report `stats/store_performance/` | yes |
| Acquisitions / installers | bulk report `acquisition/retained_installers/` | only where Play generates it for the account |
| Store conversion rate | `Store listing conversion rate` in `stats/store_performance/` | published, plus a derived aggregate |
| In-app purchases / sales | bulk report `sales/salesreport_YYYYMM.zip` | yes |
| Refunds | `Financial Status` in estimated sales; `Refund Type` in earnings | yes |
| Subscriptions | bulk report `financial-stats/subscriptions/` | only where Play generates it for the account |
| ANRs, crashes, errors, memory, wakeups, startup | Play Developer Reporting API | yes |

The Play Developer Reporting API is the only one of these that is a real API.
Its entire published surface is Android vitals metric sets. It exposes **no**
installs, uninstalls, acquisitions, store-listing, purchase, refund, or
subscription metric set, so no scope, role, or service account can obtain
acquisition data from it. The Android Publisher API used for releases exposes no
analytics at all. Everything except vitals arrives as monthly CSV/ZIP objects in
the developer's Play bulk-report Cloud Storage bucket.

### Reporting bucket configuration

The bucket id is per developer account, is shown in Play Console under
**Download reports** as a Cloud Storage URI, and is not a secret. No public API
exposes it, so it is operator-supplied. Copy the id Console shows rather than
constructing one: older accounts use `pubsite_prod_rev_<developer account id>`
and newer accounts use `pubsite_prod_<developer account id>`.

```bash
mra profile set --slug motionguard --play-reporting-bucket pubsite_prod_0123456789
export MRA_PLAY_REPORTING_BUCKET=pubsite_prod_0123456789   # account-wide default
```

The per-profile value wins over the environment default, which matters only if
you publish under more than one developer account. It is stored with the other
non-secret profile identifiers, never in the secret-reference file, and a value
that is not a valid bucket name is refused rather than sent.

### Required scopes and permissions

| Surface | OAuth scope | Google-side requirement |
|---|---|---|
| Play Developer Reporting API | `.../auth/playdeveloperreporting` | Play Developer Reporting API enabled in the service account's Cloud project |
| Bulk and financial reports | `.../auth/devstorage.read_only` | Play Console user "View app information" set to **Global**; financial exports also need "View financial data" |

Both are read-only and are requested separately from the `androidpublisher`
publishing scope, so a freshness probe never holds a token that could publish.
MRA does not change Google permissions. A denial is reported with the exact
manual Console step instead.

Listing the bucket and reading an object are separate grants, and Play
enforces them separately: a service account with "View app information" can
enumerate every report yet receive 403 `storage.objects.get` on
`sales/` and `earnings/` until "View financial data" is also Global. The probe
reports that as `permission_denied` against the named object rather than as a
missing report.

Failures are classified rather than merged: `authentication_failed`,
`permission_denied`, `api_not_enabled`, `not_found`, `rate_limited`,
`server_error`, `bucket_not_configured`, `report_not_generated`,
`report_not_generated_for_recent_months`, `empty_report`, `no_date_column`,
`no_parsable_dates`, `malformed_report`, and `report_too_large`.

### Time-zone semantics

Google states report dates in different zones, so a date is never compared
against a bare UTC clock. Each report carries its `timezone` and a
`timezone_basis` of `documented` or `assumed`:

| Report | Zone | Basis |
|---|---|---|
| Subscriptions | UTC | documented |
| Earnings | America/Los_Angeles | documented |
| Retained installers, buyers | America/Los_Angeles | documented |
| Installs, store performance, ratings, crashes | America/Los_Angeles | assumed |
| Estimated sales | UTC | assumed |
| Developer Reporting metric sets | whatever `latestEndTime.timeZone` states | returned by Google |

A daily row dated D is complete only once D has ended in the report's own zone,
so `lag_hours` is measured from the end of D, and `lag_days` compares D against
today in that same zone. Metric-set freshness needs no such reconstruction
because `latestEndTime` is already an exclusive instant.

### Store-listing conversion rate

Google changed this model on 10 July 2026. Store-listing acquisitions, store
listing visitors, and the legacy conversion rate were replaced by unique
install/open/pre-registration clicks and a click-through rate: intent, not
outcome.

The bulk export and the Console are not on the same schedule: as of September
2026 data this account's `store_performance` CSVs still carry the legacy
`Store listing acquisitions`, `Store listing visitors`, and
`Store listing conversion rate` columns. So MRA reads the report's actual header
rather than assuming either schema:

- legacy columns present: Google's own `Store listing conversion rate` is echoed
  for a single row, and for a breakdown MRA reports
  `sum(acquisitions) ÷ sum(visitors)` across **all rows of the newest date**.
  Play writes no dimensionless overview for store performance, only `_country`
  and `_traffic_source` breakdowns, so one row is one country and a per-row rate
  is not the app's rate. Summing the counts is correct where the breakdown
  partitions the population; averaging the per-row rates would weight a country
  with five visitors like one with five thousand, so MRA never does that.
- 2026 click columns present: the available columns are reported and no rate is
  computed, because clicks and installs are different events and combining them
  with anything from the retired model would manufacture a number.

### Expected Google-side latency

Google documents bulk report data as "captured daily and posted within 3 to 7
days", and the earnings report as monthly, typically available by the fifth of
the following month. Measured lag is reported per source so the documented
figure never has to be trusted on its own.

### Known limitations

- API availability does not imply fresher data than Play Console. Both the
  Console and these surfaces read the same Google pipeline, so a dataset that is
  delayed upstream is delayed in both. Measure before claiming otherwise.
- MRA cannot read the Play Console UI. `console_visible_through` is always
  `operator_input_required`, and the probe prints exactly which Console values
  to read for the comparison.
- The bulk reports are monthly files of daily rows. There is no intraday
  official surface for installs or revenue.
- Report families are generated per account, not guaranteed. An account can
  legitimately have no `acquisition/` or `financial-stats/` directory at all,
  which MRA reports as `report_not_generated` rather than as a failure.
- Bulk report families do not advance together. Measured on this account,
  ratings were two days behind while the installs export had not been rewritten
  in eight and its newest row was thirteen days old. Probe each family; do not
  infer one from another.
- Financial reports are summarized, never returned. Buyer rows carry location
  data and do not cross the agent boundary.

## RevenueCat

MRA automates the project/app/catalog setup needed for Android monetization:

- account-wide project list/create through RevenueCat OAuth
- Play app creation using the dedicated Google Play validation credential
- products and backing-store creation
- entitlements and product attachment
- offerings/packages and product attachment
- current-offering changes
- webhook list/get/create/update/delete

The transport is the official RevenueCat CLI `rc api` command. That keeps OAuth
client registration, browser consent, access-token refresh, and refresh-token
rotation inside RevenueCat's maintained tooling rather than duplicating them in
MRA.

If a RevenueCat operation is denied, first inspect:

```bash
rc auth status --scopes --json
```

Re-authenticate with browser OAuth if needed. Do not work around an OAuth scope
problem by pasting an `sk_...` key into MRA.

RevenueCat webhook authorization material is still passed as a Bitwarden UUID.
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

If an actual required write receives Google's limited-access denial,
reconciliation returns `manual_required` with the exact remaining console action.
Complete that single step and run `mra_verify` again.

Do not add private Console APIs, cookie replay, or browser automation to bypass
Google's account gate.

## Defensive redaction

Secret isolation is the primary control; redaction is defense in depth. Vendor
responses handled by the management/reconciliation paths are recursively scrubbed
for common sensitive fields and credential formats such as bearer tokens,
RevenueCat `sk_...` keys, private keys, refresh tokens, client secrets, and
webhook signing secrets.

Provider retrieval failures also avoid echoing secret-provider stdout/stderr.
RevenueCat OAuth tokens never enter MRA command arguments or model-visible output.

## Trust boundary

The native approval gate protects the MCP path. It does **not** make unrestricted
shell execution under the same OS user safe.

An unrestricted local agent running as the same macOS user may be able to invoke
`bws`, `security`, the RevenueCat CLI, Python keyring, or operator CLIs directly.
Where the credential and approval boundary matters, expose the MCP surface while
restricting direct agent access to those facilities.

## Legacy compatibility

MRA 1.7.0 keeps old RevenueCat key-reference fields parseable so upgrading does
not break an existing local profile file. Those fields are ignored by active
RevenueCat authentication. The official RevenueCat CLI OAuth session is now the
only supported agent authentication path.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

The suite is offline and covers vendor request shapes, edit cleanup, risk gates,
secret-provider behavior, RevenueCat OAuth transport and API-key override
suppression, AdMob access classification/reporting, webhook redaction, and
desired-state planning. Repository CI also runs the full AgentDefaults contract
validation before the MRA unit suite.
