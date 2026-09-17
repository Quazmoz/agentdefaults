# Mobile Release and Monetization Automation Quickstart

## Purpose

Set up and use agent-driven automation for Google Play, RevenueCat, and AdMob: uploading builds to internal testing, promoting releases, configuring monetization, and creating ad inventory.

## Canonical Stack

```text
agents/mobile-release-automation-engineer.md
skills/mobile-release-automation-orchestration.md
skills/google-play-release-automation.md
skills/revenuecat-monetization-automation.md
skills/admob-inventory-automation.md
prompts/implementation/mobile-release-automation-task.md
schemas/mobile-release-automation-task.schema.json
examples/mobile-release-automation-task.yaml
docs/mobile-release-automation-acceptance-tests.md
tools/mobile-release-automation/
.github/agents/mobile-release-automation-engineer.agent.md
```

## Read This First: The Platforms Are Not Equal

| Platform | Authentication | Creation via API | First-party agent tooling |
|---|---|---|---|
| Google Play | GCP service account | Yes | None |
| RevenueCat | Browser OAuth through the official `rc` CLI | Yes | Official CLI and MCP |
| AdMob | OAuth user credentials only | Gated per account by Google | None |

RevenueCat secret API keys are project-specific and are not the bootstrap mechanism for MRA. MRA uses the official RevenueCat CLI browser OAuth session for account-level project discovery and creation, then continues using that OAuth session for project configuration.

Planning AdMob automation before probing access is the most common way this work goes wrong. Google documents that AdMob requires an authenticated user and supports no service-account authorization; creation methods remain limited access and may return 403 unless Google has enabled the account.

## Authoritative References

```text
https://developers.google.com/android-publisher/api-ref/rest/v3
https://developers.google.com/admob/api/reference/rest
https://developers.google.com/admob/api/v1/how-tos/authorizing
https://www.revenuecat.com/docs/api-v2
https://www.revenuecat.com/docs/tools/mcp
https://www.revenuecat.com/docs/tools/cli
```

## Fast Start

### 1. Install the toolkit

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -e ".[mcp]"
```

Install the official RevenueCat CLI on macOS:

```bash
brew install RevenueCat/tap/rc
```

### 2. Provision credentials and OAuth

Follow `tools/mobile-release-automation/SECURITY.md` and `INSTALL.md`.

Static Google credentials are resolved through Bitwarden Secrets Manager. The Bitwarden machine-account token remains in macOS Keychain. RevenueCat API authentication is different: the official RevenueCat CLI owns its browser OAuth session and token refresh.

Authenticate RevenueCat once:

```bash
rc auth login
rc auth status --scopes --json
```

Use browser OAuth. If `rc auth status --json` reports `method: api_key`, log out and authenticate again with OAuth:

```bash
rc auth logout
rc auth login
```

MRA intentionally removes `RC_API_KEY` and `REVENUECAT_V2_SECRET_KEY` from RevenueCat child processes so a stale project-scoped key cannot silently override OAuth.

The Google service account RevenueCat needs for Play purchase validation remains a separate credential and should still be bound through Bitwarden:

```bash
mra-agent auth bind-revenuecat-play --secret-id YOUR_REVENUECAT_PLAY_SERVICE_ACCOUNT_UUID
```

For AdMob:

```text
Desktop OAuth client JSON -> Bitwarden Secrets Manager
OAuth refresh token       -> OS credential store / macOS Keychain
access tokens              -> memory only
```

Bind the AdMob Desktop OAuth client UUID and perform browser consent once:

```bash
mra-agent auth bind-admob --secret-id YOUR_BITWARDEN_SECRET_UUID
mra admob login
```

### 3. Confirm what works

```bash
mra-agent doctor
mra admob probe
mra admob apps
mra admob adunits
```

A healthy RevenueCat entry from `mra-agent doctor` reports the source as `official-revenuecat-cli-oauth`. No RevenueCat `sk_...` key or Bitwarden RevenueCat API-key binding is required.

Record the AdMob probe result. It determines whether the monetization scope is accepted. App/ad-unit creation is separately gated by Google and can still return 403 even after the probe succeeds.

### 4. Register the local MCP server

```bash
claude mcp add mobile-release-automation -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/mra-agent-mcp
```

The local MCP server is risk-gated, not read-only. It can inspect state and perform contained automation directly. High-risk actions require a real local human approval before the vendor API call occurs.

### 5. Create a profile

A brand-new app profile needs only the identifiers you already know. It does not need a RevenueCat project ID or RevenueCat secret key:

```bash
mra profile set --slug myapp \
  --package-name com.example.myapp
```

The RevenueCat MCP tools can list every project visible to the authenticated OAuth account, create a missing project, then reconcile the returned project/app IDs with `profile_update_identifiers`.

If you maintain multiple official RevenueCat CLI profiles, select one for MRA before starting the MCP server:

```bash
export MRA_REVENUECAT_CLI_PROFILE=<revenuecat-cli-profile>
```

Agents should read profile identifiers with `profile_get` and reconcile verified non-secret IDs with `profile_update_identifiers`. Do not edit `~/.config/mobile-release-automation/profiles.json` directly.

The legacy commands `mra-agent profile bind-revenuecat` and `mra-agent auth bind-revenuecat-bootstrap` remain only as migration-safe deprecated no-ops. Do not use them for new setups.

### 6. Give the agent a task

Fill in `prompts/implementation/mobile-release-automation-task.md`, or write a task document against `schemas/mobile-release-automation-task.schema.json`. `examples/mobile-release-automation-task.yaml` is a worked example.

Before mutation-heavy work, the agent should call the MCP `approval_policy` tool so it can explain which actions are automatic and which will require local approval.

For a brand-new RevenueCat app, list projects first through OAuth so an existing project is not duplicated. After project creation, immediately reconcile the returned project ID into the MRA profile.

For an existing RevenueCat project, read the complete offering/package/product and entitlement/product graph first:

```text
rc_inspect_wiring(profile="myapp")
```

Targeted read tools are also available:

```text
rc_list_projects
rc_list_packages
rc_list_package_products
rc_list_entitlement_products
```

Only invoke high-risk attachment tools when read-back proves a relationship is missing. After an approved mutation, call `rc_inspect_wiring` again and verify the relationship exists.

## Use It For

- Uploading an app bundle to internal testing
- Promoting a qualified build to a wider track
- Setting up a new app across Google Play, RevenueCat, and AdMob where APIs permit it
- Creating a brand-new RevenueCat project through account-level OAuth without first creating a project-specific API key
- Creating and reconciling RevenueCat products, entitlements, offerings, packages, and their relationships
- Creating AdMob apps and ad units where the account permits it
- Diagnosing why a release, product, entitlement, package, or ad unit did not appear
- Reconciling verified cross-platform identifiers into the MRA profile
- Deciding whether a given platform task can be automated at all

## Do Not Use It For

- Android or Wear OS application code and build correctness, which belongs to `agents/android-wearos-release-engineer.md`
- Store listing growth, ASO, and conversion, which belongs to `agents/google-play-growth-optimizer-agent.md`
- CI/CD pipeline design, which belongs to `agents/principal-devops-engineer.md` or `agents/github-actions-engineer.md`
- Release supply-chain security review, which belongs to `agents/devsecops-security-engineer.md`

## Permission Model

```text
observe      read tracks, products, inventory, RevenueCat wiring; dry-run a Play edit
contained    publish to internal testing; create individual RevenueCat or AdMob objects;
             reconcile verified non-secret local profile identifiers
high         non-internal Play releases/promotions; current-offering changes;
             live entitlement/package wiring; backing-store creation; future
             destructive, financial, or broad multi-app mutations
```

Contained actions may execute through MCP. High-risk MCP actions fail closed unless the local operator approves the exact action in the native macOS approval dialog. The AI cannot self-authorize by setting a confirmation boolean.

The operator CLI remains available for explicit local work and retains its `--yes` confirmation behavior.

## What Is Not Automatable

State these plainly rather than working around them:

- Creating a brand-new app in Play Console, plus content rating, Data Safety, and target audience declarations. The Play Developer API cannot do this.
- AdMob app and ad unit creation on an account Google has not allowlisted.
- RevenueCat dashboard-only ad monetization settings that are not exposed by supported APIs, such as rewarded entitlement-duration configuration where no supported API is available.

Scripting a vendor console UI is not an approved workaround for any of these.

## Verification Baseline

Before claiming a result, read it back from the platform:

```bash
mra play tracks --profile myapp
mra rc products --profile myapp
mra admob adunits
```

For RevenueCat relationship changes, MCP read-back is mandatory:

```text
rc_inspect_wiring(profile="myapp")
```

An HTTP 2xx response means the request was accepted. It is not proof the intended state was achieved.

## Validation of This Stack

```bash
python3 scripts/validate-agentdefaults.py
python3 scripts/validate-mobile-release-automation-stack.py
```

Toolkit tests are fully offline:

```bash
cd tools/mobile-release-automation
.venv/bin/python -m unittest discover -s tests -t .
```

## Expected Delivery

```text
STATUS
MODE
DISCOVERED
CAPABILITY
PLAN
IMPLEMENTED
VERIFIED
UNVERIFIED
IDENTIFIERS
RISKS
HANDOFF
USER ACTION
```

`CAPABILITY` states what this account can and cannot automate, with evidence. `IDENTIFIERS` lists every generated ID, flagging any AdMob ad unit ID that must reach source control before the next build.
