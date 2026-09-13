# Mobile Release Automation Toolkit

## Purpose

Give an agent a safe, auditable way to perform repetitive Google Play,
RevenueCat, and AdMob work without placing vendor credentials in Git, prompts,
agent context, or normal command output.

Every operation is a thin wrapper over documented public APIs. No vendor web UI
is scripted.

## Platform constraints

| Platform | Auth | Automation status |
|---|---|---|
| Google Play | GCP service account | Upload, tracks, promotion, and monetization are API-driven. |
| RevenueCat | API v2 secret key | Apps, products, entitlements, offerings, and packages are API-driven. |
| AdMob | OAuth user credentials | Reporting/listing works. App and ad-unit creation is available only when Google has allowlisted the AdMob account. |

AdMob service accounts do not work. Run `mra admob probe` before depending on
AdMob creation automation.

## RevenueCat project convention

Default to **one RevenueCat project per independently monetized product/app
family**.

RevenueCat projects are a sharing boundary. Apps in one RevenueCat project may
share entitlement state and project-level configuration. Unrelated products such
as MotionGuard, PressDeck, and AdHocKit should normally use separate RevenueCat
projects. Phone, Wear OS, Android, or iOS variants that intentionally share one
paid entitlement may belong to the same RevenueCat project.

Each independent RevenueCat project should have its own V2 secret key.

## Secret architecture

### Use Bitwarden Secrets Manager, not the Password Manager personal API key

The normal Bitwarden Password Manager personal API key authenticates the CLI but
does not replace vault unlock for decrypted data. For unattended local automation,
use **Bitwarden Secrets Manager** instead.

Bitwarden Secrets Manager Free currently provides unlimited secret storage, up
to 3 projects, and up to 3 machine accounts. That is sufficient for this toolkit
without creating one Bitwarden project per app.

Use one Bitwarden Secrets Manager project named:

```text
mobile-release-automation
```

Store app-specific secrets inside that project using clear names such as:

```text
mra/revenuecat/motionguard/v2-secret
mra/revenuecat/pressdeck/v2-secret
mra/revenuecat/adhockit/v2-secret
```

The Bitwarden project is only an access-control grouping. It is unrelated to the
RevenueCat project-per-product convention.

### Machine account

Create one Bitwarden Secrets Manager machine account for this MacBook, for
example:

```text
mra-macbook
```

Grant it **Can read** access to the `mobile-release-automation` project. Routine
release automation does not need permission to edit secrets.

Generate a machine-account access token. This is the one bootstrap credential
that allows the local toolkit to decrypt the secrets the machine account may
read.

### Store the bootstrap token in macOS Keychain

Do not store the Bitwarden machine token in Git, `profiles.json`, shell startup
files, or an agent prompt.

The toolkit looks for this macOS Keychain item:

```text
service: com.quazmoz.mobile-release-automation.bitwarden
account: mra-machine-account
```

Store the generated token without putting its literal value in shell history:

```bash
read -s BWS_TOKEN
security add-generic-password -U \
  -a mra-machine-account \
  -s com.quazmoz.mobile-release-automation.bitwarden \
  -w "$BWS_TOKEN"
unset BWS_TOKEN
```

For CI or another trusted non-macOS environment, `BWS_ACCESS_TOKEN` can be
injected by that platform's secret store instead.

### Secret references, not secret values

`profiles.json` stores only immutable Bitwarden secret UUIDs. Example shape:

```json
{
  "motionguard": {
    "package_name": "com.quazmoz.motionguard",
    "revenuecat_project_id": "proj_example",
    "revenuecat_secret_id": "6f7c12c0-df7b-4a2b-9360-1539a4d13392"
  }
}
```

A Bitwarden UUID is a reference, not the RevenueCat `sk_...` value.

The secret flow is:

```text
AI or operator
    -> mra-agent / local agent MCP
    -> profile slug
    -> Bitwarden secret UUID
    -> bws secret get <UUID>
    -> RevenueCat client in memory
    -> RevenueCat API
```

The AI-facing surface receives the profile slug and API result. It does not
receive the Bitwarden machine token or the RevenueCat secret.

The Bitwarden provider retrieves exactly one secret by UUID. It does not list an
entire project, does not use `bws run`, and does not print secret values.

## Install

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -e ".[mcp]"
```

Install Bitwarden's official Secrets Manager CLI (`bws`) separately and ensure it
is on `PATH`.

Available entry points:

```text
mra        general CLI
mra-agent  agent-safe RevenueCat CLI with profile-bound Bitwarden auth
mra-mcp    existing local MCP server
```

The agent-safe MCP module can currently be run directly with:

```bash
.venv/bin/python -m mra.secure_mcp_server
```

## RevenueCat setup

Inside each independent RevenueCat project, create a V2 secret key for release
automation.

For the current read-and-create workflow use:

```text
project_configuration:projects:read
project_configuration:apps:read_write
project_configuration:products:read_write
```

Endpoint mapping:

| Toolkit operation | RevenueCat endpoint | Required permission |
|---|---|---|
| list projects | `GET /v2/projects` | `project_configuration:projects:read` |
| list apps | `GET /v2/projects/{project_id}/apps` | `project_configuration:apps:read` |
| create Play app | `POST /v2/projects/{project_id}/apps` | `project_configuration:apps:read_write` |
| list products | `GET /v2/projects/{project_id}/products` | `project_configuration:products:read` |
| create product | `POST /v2/projects/{project_id}/products` | `project_configuration:products:read_write` |

For an audit-only key use:

```text
project_configuration:projects:read
project_configuration:apps:read
project_configuration:products:read
```

The toolkit does not create RevenueCat projects, so it does not need
`project_configuration:projects:read_write`.

Do not grant entitlement, offering, package, or customer permissions until a
command actually needs them.

A RevenueCat V2 secret begins with `sk_`. It is a server credential. Never put it
in Android source or use it as the RevenueCat Android SDK key. Android uses the
RevenueCat public SDK key instead.

## Create the MotionGuard secret in Bitwarden

1. Open Bitwarden Secrets Manager.
2. Open the `mobile-release-automation` project.
3. Create a secret named `mra/revenuecat/motionguard/v2-secret`.
4. Paste MotionGuard's RevenueCat V2 `sk_...` value into the secret value.
5. Save it.
6. Copy the Bitwarden secret UUID. Do not copy the `sk_...` value into the MRA
   profile.

## Configure the MotionGuard profile

First create or update its ordinary identity mapping:

```bash
mra profile set --slug motionguard \
  --package-name com.quazmoz.motionguard \
  --revenuecat-project-id proj_YOUR_MOTIONGUARD_PROJECT
```

Then bind the Bitwarden secret UUID:

```bash
mra-agent profile bind-revenuecat \
  --profile motionguard \
  --secret-id YOUR_BITWARDEN_SECRET_UUID
```

The binding writes only the UUID to `profiles.json`.

## Verify MotionGuard without exposing the secret

```bash
mra-agent doctor
mra-agent rc projects --profile motionguard
mra-agent rc apps --profile motionguard
mra-agent rc products --profile motionguard
```

No manual `export REVENUECAT_V2_SECRET_KEY=...` is required.

A 403 normally means the RevenueCat V2 key lacks an endpoint permission. A 404
usually means the profile's `proj_...` ID does not belong to the RevenueCat
project that issued that secret key.

## Agent and MCP usage

For a local coding agent, expose `mra-agent` rather than raw `bws` commands. The
agent should be allowed to select a profile and an operation, but should not be
allowed to ask the secret provider to print values.

For MCP-capable clients, run the local agent-safe server:

```bash
claude mcp add mobile-release-automation-agent -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/python \
  -m mra.secure_mcp_server
```

The MCP tools accept inputs such as:

```text
rc_list_products(profile="motionguard")
rc_list_apps(profile="motionguard")
```

Mutating MCP tools still require `confirm=true`.

The MCP server resolves the profile, Bitwarden UUID, Bitwarden machine token, and
RevenueCat key behind the tool boundary. None of those secret values are returned
to the model.

## Google Play

Google Play currently still uses the owner-only local service-account file:

```text
~/.config/mobile-release-automation/play-service-account.json
```

Setup:

1. Enable the Google Play Android Developer API in Google Cloud.
2. Create a service account and download its JSON key.
3. Add the service-account email under Play Console **Users and permissions**.
4. Grant only the Play permissions required by the workflow.
5. Save the JSON with mode 600.

```bash
mkdir -p ~/.config/mobile-release-automation
chmod 700 ~/.config/mobile-release-automation
cp ~/Downloads/play-sa.json ~/.config/mobile-release-automation/play-service-account.json
chmod 600 ~/.config/mobile-release-automation/play-service-account.json
```

`mra-agent rc create-play-app` sends this JSON to RevenueCat because RevenueCat
requires Play service credentials to validate Google Play purchases.

## AdMob

AdMob currently still uses its OAuth Desktop client locally. The resulting
refresh token is dynamic machine-local state and should not be exposed to an AI
model.

```bash
cp ~/Downloads/admob-client.json ~/.config/mobile-release-automation/admob-oauth-client.json
chmod 600 ~/.config/mobile-release-automation/admob-oauth-client.json
mra admob login
mra admob probe
```

Service accounts do not work for AdMob.

## Next secret migrations

RevenueCat is the first provider moved behind Bitwarden because it has a natural
per-app secret model.

Next migrations should be:

1. Google Play service-account JSON into Bitwarden Secrets Manager.
2. AdMob OAuth client JSON into Bitwarden Secrets Manager.
3. Move the generated AdMob refresh token from a plaintext owner-only file into
   macOS Keychain rather than treating a rotating OAuth token as a static
   Bitwarden secret.

That gives the desired end state: static vendor credentials are centrally stored
in Bitwarden, machine-local rotating tokens live in the OS credential store, and
AI agents receive only narrow profile-bound operations.

## Safety model

- Mutating commands require explicit confirmation (`--yes` or `confirm=true`).
- Profiles contain identifiers and secret UUIDs only, never secret values.
- The Bitwarden machine account should have read-only access for normal release
  automation.
- The Bitwarden machine access token is stored in macOS Keychain.
- `bws secret get` is called for one immutable secret UUID at a time.
- Provider stdout/stderr is not echoed on retrieval failure because it could
  contain sensitive material.
- RevenueCat keys never need to be exported manually for normal `mra-agent`
  operations.
- Google Play and AdMob credentials remain outside Git.
- RevenueCat projects define purchase-sharing boundaries. Bitwarden projects
  define secret-access boundaries. Do not confuse the two.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

The test suite is offline. Secret-provider tests verify that the Bitwarden access
token is passed only to the child `bws` environment, invalid secret IDs are
rejected before provider access, provider failures do not echo provider output,
and profile binding stores only the Bitwarden UUID.
