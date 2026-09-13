# Mobile Release Automation Toolkit

## Purpose

Give an agent a safe, auditable way to perform the repetitive Google Play,
RevenueCat, and AdMob work that is otherwise done by hand: uploading builds to
internal testing, promoting releases, wiring a new app into RevenueCat, and
creating AdMob inventory.

Every operation is a thin wrapper over a documented public API. No vendor web UI
is scripted. Credentials stay local except when a vendor's documented integration
requires one credential to be sent to another vendor. In particular,
`mra rc create-play-app` sends the Google Play service-account JSON to RevenueCat
so RevenueCat can validate Play purchases.

## The Three Platforms Are Not Equally Automatable

Read this before planning any work. The differences are not preferences.

| Platform | Auth | Automatable today |
|---|---|---|
| Google Play | GCP service account | Yes. Upload, tracks, promotion, and monetization products are all API-driven. |
| RevenueCat | API v2 secret key | Yes. Apps, products, entitlements, offerings, and packages are all API-driven. A first-party MCP server exists. |
| AdMob | OAuth **user** credentials only | Reporting and listing: yes. Creating apps and ad units: **only if Google has allowlisted your AdMob account**. |

Two AdMob facts that cannot be engineered around:

1. **Service accounts do not work.** Google documents that "All requests to the
   AdMob API must be authorized by an authenticated user" and that "No other
   authorization protocols are supported." There is no IAM role that changes
   this. AdMob needs a browser consent from the Google Account that owns the
   publisher account, which this toolkit caches as a local refresh token.
2. **Creation is limited access.** `accounts.apps.create` and
   `accounts.adUnits.create` both carry the note: "This method has limited
   access. If you see a 403 permission denied error, please reach out to your
   account manager for access." The gate is applied per AdMob account by Google.
   Granting yourself the `admob.monetization` scope does not lift it.

Run `mra admob probe` before promising anyone that AdMob setup is automated.

## Portfolio Convention

For this portfolio, use **one RevenueCat project per app**.

That gives every Android or Wear OS product an isolated RevenueCat configuration,
product catalog, entitlement model, offering configuration, and secret API key.
Do not put multiple portfolio apps into one RevenueCat project merely to simplify
automation.

RevenueCat secret API keys are project-wide. Therefore each app project gets its
own V2 secret key. The app profile stores the RevenueCat `proj_...` ID, but the
secret itself stays outside `profiles.json` and outside Git.

Recommended local layout:

```text
~/.config/mobile-release-automation/
  play-service-account.json
  admob-oauth-client.json
  admob-token.json
  profiles.json
  revenuecat-motionguard-v2-secret.key
  revenuecat-pressdeck-v2-secret.key
  revenuecat-adhockit-v2-secret.key
  ...
```

The current CLI reads RevenueCat credentials from `REVENUECAT_V2_SECRET_KEY` or,
if that variable is unset, from the legacy single-project fallback file
`revenuecat-v2-secret.key`. For a portfolio with one RevenueCat project per app,
prefer the per-app files above and inject the matching key into the environment
for each RevenueCat command. Do not copy different app secrets back and forth
into the fallback file.

## Install

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The `mcp` requirement is needed only for the local MCP server. Both mcp 1.x
(`FastMCP`) and mcp 2.x (`MCPServer`) are supported.

## Credential Setup

All credentials live in `~/.config/mobile-release-automation` (override with
`MRA_HOME`). The toolkit refuses to read its credential files if they are group-
or world-readable, so use owner-only permissions for every secret and credential
file.

```bash
mkdir -p ~/.config/mobile-release-automation
chmod 700 ~/.config/mobile-release-automation
```

### Google Play

1. In Google Cloud, create a project and enable the **Google Play Android
   Developer API**.
2. Create a service account and download its JSON key.
3. In Play Console, go to **Users and permissions**, invite the service account
   email, and grant only what the task needs: *Release to testing tracks* for
   internal testing, plus *Manage store presence* or monetization permissions
   only if you intend to script products.
4. Save the key and lock it down:

```bash
cp ~/Downloads/play-sa.json ~/.config/mobile-release-automation/play-service-account.json
chmod 600 ~/.config/mobile-release-automation/play-service-account.json
```

Play Console propagates new permissions slowly. A fresh invite can take a while
before the API accepts it.

### AdMob

1. In the same Google Cloud project, enable the **AdMob API**.
2. Configure the OAuth consent screen. Add the AdMob scopes you intend to use.
   `admob.readonly` and `admob.report` are publicly documented;
   `admob.monetization` is required for creation and is the gated one.
3. Create an OAuth client of type **Desktop app** and download its JSON.

```bash
cp ~/Downloads/admob-client.json ~/.config/mobile-release-automation/admob-oauth-client.json
chmod 600 ~/.config/mobile-release-automation/admob-oauth-client.json
mra admob login       # one-time browser consent, caches a refresh token
mra admob probe       # says whether monetization access is actually granted
```

Sign in as the Google Account that owns the AdMob publisher account. If
`mra admob login` fails because `admob.monetization` is not permitted on your
consent screen, re-run `mra admob login --read-only` to get reporting working
and treat creation as unavailable.

### RevenueCat

Create a separate RevenueCat project for each app. Inside each project, create a
**V2 secret API key** specifically for this automation toolkit.

For the toolkit as currently implemented, grant this minimum useful permission
set:

```text
project_configuration:projects:read
project_configuration:apps:read_write
project_configuration:products:read_write
```

Why these are needed:

- `project_configuration:projects:read` allows `mra rc projects` to verify the
  project visible to the key.
- `project_configuration:apps:read_write` allows the toolkit to list and create
  the RevenueCat Play app.
- `project_configuration:products:read_write` allows the toolkit to list and
  register products.

Do not grant entitlement, offering, package, customer, or other permissions
until a command actually needs them. If automation is later extended to create
the complete RevenueCat paywall model, add only the corresponding
`entitlements`, `offerings`, and `packages` permissions at that time.

A RevenueCat V2 secret begins with `sk_`. It is a server credential. Never put it
in Android source, Gradle properties that ship with the app, a GitHub repository,
screenshots, issue comments, or the RevenueCat SDK configuration. The Android app
uses its RevenueCat **public SDK key**, not this secret.

For each app, save the generated secret in its own owner-only file. Avoid putting
the secret directly into your shell history:

```bash
read -s RC_KEY
printf '%s' "$RC_KEY" > ~/.config/mobile-release-automation/revenuecat-motionguard-v2-secret.key
unset RC_KEY
chmod 600 ~/.config/mobile-release-automation/revenuecat-motionguard-v2-secret.key
```

Repeat with a different filename for each app project, for example:

```text
revenuecat-motionguard-v2-secret.key
revenuecat-pressdeck-v2-secret.key
revenuecat-adhockit-v2-secret.key
```

When running a RevenueCat command, inject only the matching app's key into that
process:

```bash
REVENUECAT_V2_SECRET_KEY="$(cat ~/.config/mobile-release-automation/revenuecat-motionguard-v2-secret.key)" \
  mra rc products --profile motionguard
```

This keeps each app's RevenueCat project isolated while preserving the existing
CLI contract. `REVENUECAT_V2_SECRET_KEY` takes precedence over the legacy
`revenuecat-v2-secret.key` fallback file.

### Verify

```bash
.venv/bin/python -m mra.cli doctor
```

`doctor` checks the legacy/global RevenueCat credential location. In a per-app
RevenueCat layout, a missing global RevenueCat key is expected if the other
credential checks pass. Validate each RevenueCat app key explicitly with the
commands in the next section.

## Profiles

A profile maps one app's identity across all three platforms so commands do not
need long flags. Under the portfolio convention, each profile should point to a
different RevenueCat project ID.

Example for MotionGuard:

```bash
mra profile set --slug motionguard \
  --package-name com.example.motionguard \
  --revenuecat-project-id proj_abc123 \
  --admob-app-id ca-app-pub-000~111
```

Example for PressDeck:

```bash
mra profile set --slug pressdeck \
  --package-name com.example.pressdeck \
  --revenuecat-project-id proj_def456 \
  --admob-app-id ca-app-pub-000~222
```

Do not store a RevenueCat `sk_...` secret in `profiles.json`. Profiles contain
identifiers only.

## RevenueCat Per-App Verification

After creating an app project, its V2 secret, and its local profile, verify it
read-only before making any RevenueCat changes.

For MotionGuard:

```bash
export REVENUECAT_V2_SECRET_KEY="$(cat ~/.config/mobile-release-automation/revenuecat-motionguard-v2-secret.key)"

mra rc projects
mra rc apps --profile motionguard
mra rc products --profile motionguard

unset REVENUECAT_V2_SECRET_KEY
```

Confirm that:

1. `mra rc projects` returns the expected RevenueCat project.
2. The returned `proj_...` ID matches the `revenuecat_project_id` stored in the
   profile.
3. `mra rc apps --profile motionguard` succeeds against that project.
4. `mra rc products --profile motionguard` succeeds, even if the product list is
   currently empty.

If a command returns HTTP 403, check the V2 key permissions first. If it returns
HTTP 404, verify that the profile's project ID belongs to the same RevenueCat
project that issued the secret key.

## Common Commands

```bash
# Google Play
mra play tracks --profile myapp
mra play publish --profile myapp --aab app/build/outputs/bundle/release/app-release.aab --dry-run
mra play publish --profile myapp --aab ... --track internal --notes "en-US=Bug fixes" --yes
mra play promote --profile myapp --source internal --target alpha --yes

# AdMob
mra admob probe
mra admob apps
mra admob create-app --name "My App" --platform ANDROID --app-store-id com.example.myapp --yes
mra admob create-adunit --app-id ca-app-pub-000~111 --name "Rewarded" --format REWARDED --type VIDEO --yes

# RevenueCat: load the secret for the profile's RevenueCat project first
export REVENUECAT_V2_SECRET_KEY="$(cat ~/.config/mobile-release-automation/revenuecat-myapp-v2-secret.key)"
mra rc projects
mra rc create-play-app --profile myapp --name "My App" --yes
mra rc products --profile myapp
unset REVENUECAT_V2_SECRET_KEY
```

Every command prints JSON on stdout so an agent can parse the result. Failures
go to stderr with a non-zero exit code.

## Safety Model

- **Mutating commands refuse to run without `--yes`.** There is no way to
  configure that away.
- **`mra play publish` supports `--dry-run`**, which validates the Play edit and
  then discards it. The upload still reaches Google, because Play cannot
  validate a bundle it has not received, but nothing reaches testers.
- **Play edits are always cleaned up.** A failed or dry-run edit is deleted so
  nothing is left dangling in the Console.
- **Credential files must be owner-only** or the toolkit refuses to read them.
- **RevenueCat secrets are project-wide.** With one project per app, use a
  different V2 secret for every app project and never store those secrets in a
  profile or repository.
- **`mra rc create-play-app` sends your Play service account key to
  RevenueCat.** That is the documented way RevenueCat validates Play purchases,
  but it is a real credential leaving your machine, so the command says so.

## MCP Server

`mra.mcp_server` exposes the same operations over stdio MCP, with `confirm=true`
required for every mutating tool and `dry_run` defaulting to `true`.

Register it with Claude Code:

```bash
claude mcp add mobile-release-automation -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/python -m mra.mcp_server
```

For RevenueCat, prefer the first-party hosted server instead:

```bash
claude mcp add --transport http revenuecat https://mcp.revenuecat.ai/mcp
```

The RevenueCat tools in this local server exist only to cover gaps in that
server and to support unattended scripting.

Do not install a third-party Play Console or AdMob MCP server. There is no
first-party one, and any such server would hold your Play Console service
account and AdMob refresh token.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

The suite is fully offline: it uses in-memory HTTP doubles and never contacts a
real platform. It covers the Play edit lifecycle and its cleanup paths, release
validation, promotion, AdMob 403 handling and the access probe, RevenueCat
request shaping and pagination, credential permission enforcement, and the
confirmation gates in both the CLI and the MCP server.
