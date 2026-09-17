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

| Platform | Authentication | Creation via API | First-party MCP |
|---|---|---|---|
| Google Play | GCP service account | Yes | None |
| RevenueCat | API v2 secret key | Yes | Yes, `https://mcp.revenuecat.ai/mcp` |
| AdMob | OAuth user credentials only | Gated per account by Google | None |

Planning AdMob automation before probing access is the most common way this work goes wrong. Google documents that AdMob requires an authenticated user and supports no other authorization protocol, so service accounts do not work at all; and both AdMob creation methods are marked limited access, returning 403 unless Google has allowlisted the account.

## Authoritative References

```text
https://developers.google.com/android-publisher/api-ref/rest/v3
https://developers.google.com/admob/api/reference/rest
https://developers.google.com/admob/api/v1/how-tos/authorizing
https://www.revenuecat.com/docs/api-v2
https://www.revenuecat.com/docs/tools/mcp
```

## Fast Start

### 1. Install the toolkit

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -e ".[mcp]"
```

### 2. Provision credentials

Follow `tools/mobile-release-automation/SECURITY.md` and `INSTALL.md`.

Static vendor credentials are resolved through Bitwarden Secrets Manager. The Bitwarden machine-account token remains in macOS Keychain. Profiles and local binding files contain secret references rather than secret values.

For a portfolio that creates new RevenueCat projects through MRA, bind one global RevenueCat API v2 bootstrap key by its Bitwarden UUID:

```bash
mra-agent auth bind-revenuecat-bootstrap --secret-id YOUR_BITWARDEN_SECRET_UUID
```

The bootstrap key exists only to break the new-project circular dependency. It should have the minimum provisioning permissions required, typically project/app/entitlement read or read-write permissions. A narrower project-specific key remains preferred after a project exists.

For AdMob specifically:

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

`mra-agent doctor` reports the RevenueCat API credential source class without exposing a secret value. A brand-new profile can report/use `global-bootstrap-bitwarden` before it has its own RevenueCat project-specific key.

Record the AdMob probe result. It determines whether the monetization scope is accepted. App/ad-unit creation is separately gated by Google and can still return 403 even after the probe succeeds.

### 4. Register the local MCP server

```bash
claude mcp add mobile-release-automation -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/mra-agent-mcp
```

The local MCP server is risk-gated, not read-only. It can inspect state and perform contained automation directly. High-risk actions require a real local human approval before the vendor API call occurs.

### 5. Create a profile

A brand-new app profile does not need a RevenueCat project id or project-specific RevenueCat key yet:

```bash
mra profile set --slug myapp \
  --package-name com.example.myapp
```

With the global bootstrap key bound, the RevenueCat MCP tools can list projects and create a missing project. Reconcile the returned project/app identifiers with `profile_update_identifiers` as they are verified.

After the RevenueCat project exists, bind a narrower project-specific RevenueCat secret reference when desired:

```bash
mra-agent profile bind-revenuecat \
  --profile myapp \
  --secret-id YOUR_PROJECT_SPECIFIC_REVENUECAT_V2_KEY_UUID
```

A persisted per-app key takes precedence over the global bootstrap key. The bootstrap UUID is inherited in memory only and is not written into `profiles.json` for unbound profiles.

Bind the global Google credential references as documented in `SECURITY.md`.

Agents should read profile identifiers with `profile_get` and reconcile verified non-secret IDs with `profile_update_identifiers`. Do not edit `~/.config/mobile-release-automation/profiles.json` directly.

### 6. Give the agent a task

Fill in `prompts/implementation/mobile-release-automation-task.md`, or write a task document against `schemas/mobile-release-automation-task.schema.json`. `examples/mobile-release-automation-task.yaml` is a worked example.

Before mutation-heavy work, the agent should call the MCP `approval_policy` tool so it can explain which actions are automatic and which will require local approval.

For a brand-new RevenueCat app, first call/list projects through the bootstrap credential before creating one, so an existing project is not duplicated. After project creation, immediately reconcile the returned project id into the profile.

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

Only invoke the high-risk attachment tools when read-back proves a relationship is missing. After an approved mutation, call `rc_inspect_wiring` again and verify the relationship exists.

## Use It For

- Uploading an app bundle to internal testing
- Promoting a qualified build to a wider track
- Setting up a new app across Google Play, RevenueCat, and AdMob where APIs permit it
- Bootstrapping a brand-new RevenueCat project without first requiring a project-specific API key
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

- Creating a brand-new app in Play Console, plus content rating, Data safety, and target audience declarations. The Play Developer API cannot do this.
- AdMob app and ad unit creation on an account Google has not allowlisted.
- RevenueCat dashboard-only ad monetization settings that are not exposed by the v2 API, such as rewarded entitlement-duration configuration where no supported API is available.

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

An HTTP 200 means the request was accepted. It is not proof the intent was achieved.

## Validation of This Stack

```bash
python3 scripts/validate-agentdefaults.py
python3 scripts/validate-mobile-release-automation-stack.py
```

Toolkit tests, which are fully offline:

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

`CAPABILITY` states what this account can and cannot automate, with evidence. `IDENTIFIERS` lists every generated id, flagging any AdMob ad unit id that must reach source control before the next build.
