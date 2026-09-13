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

Follow `tools/mobile-release-automation/SECURITY.md` and `INSTALL.md`. Static vendor credentials are resolved through Bitwarden Secrets Manager; the Bitwarden machine-account token remains in macOS Keychain; profiles and local binding files contain secret references rather than secret values.

### 3. Confirm what works

```bash
mra-agent doctor
mra admob probe
```

Record the AdMob probe result. It determines whether AdMob creation work is automatable for this account.

### 4. Register the local MCP server

```bash
claude mcp add mobile-release-automation -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/mra-agent-mcp
```

The local MCP server is risk-gated, not read-only. It can inspect state and perform contained automation directly. High-risk actions require a real local human approval before the vendor API call occurs.

### 5. Create a profile

```bash
mra profile set --slug myapp \
  --package-name com.example.myapp \
  --revenuecat-project-id proj_abc123
```

Bind the app's RevenueCat secret reference with `mra-agent profile bind-revenuecat` and bind the global Google credential references as documented in `SECURITY.md`.

### 6. Give the agent a task

Fill in `prompts/implementation/mobile-release-automation-task.md`, or write a task document against `schemas/mobile-release-automation-task.schema.json`. `examples/mobile-release-automation-task.yaml` is a worked example.

Before mutation-heavy work, the agent should call the MCP `approval_policy` tool so it can explain which actions are automatic and which will require local approval.

## Use It For

- Uploading an app bundle to internal testing
- Promoting a qualified build to a wider track
- Setting up a new app across Google Play, RevenueCat, and AdMob where APIs permit it
- Creating RevenueCat products, entitlements, offerings, and packages
- Creating AdMob apps and ad units where the account permits it
- Diagnosing why a release, product, or ad unit did not appear
- Deciding whether a given platform task can be automated at all

## Do Not Use It For

- Android or Wear OS application code and build correctness, which belongs to `agents/android-wearos-release-engineer.md`
- Store listing growth, ASO, and conversion, which belongs to `agents/google-play-growth-optimizer-agent.md`
- CI/CD pipeline design, which belongs to `agents/principal-devops-engineer.md` or `agents/github-actions-engineer.md`
- Release supply-chain security review, which belongs to `agents/devsecops-security-engineer.md`

## Permission Model

```text
observe      read tracks, products, inventory; dry-run a Play edit
contained    publish to internal testing; create individual RevenueCat or AdMob objects
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
- Creating a RevenueCat project, which is a dashboard action.

Scripting a vendor console UI is not an approved workaround for any of these.

## Verification Baseline

Before claiming a result, read it back from the platform:

```bash
mra play tracks --profile myapp
mra rc products --profile myapp
mra admob adunits
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
