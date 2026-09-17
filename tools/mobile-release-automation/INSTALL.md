# Mobile Release Automation: Install and Update

Always update the repository before installing the editable package. An editable install can succeed against an old checkout while silently missing newer console entry points.

## Update an existing checkout

From the repository root:

```bash
cd /path/to/agentdefaults
git pull --ff-only
cd tools/mobile-release-automation
source .venv/bin/activate
python -m pip install -e ".[mcp]" --upgrade
rehash
```

Verify the installed package and entry points:

```bash
python -m pip show mobile-release-automation | grep '^Version:'
command -v mra-agent
mra-agent --help
command -v mra-mcp
command -v mra-agent-mcp
```

The RevenueCat OAuth transport is MRA **1.7.0 or newer**.

## Fresh install

```bash
cd /path/to/agentdefaults
git pull --ff-only
cd tools/mobile-release-automation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[mcp]"
rehash
mra-agent --help
```

Install the official RevenueCat CLI separately:

```bash
brew install RevenueCat/tap/rc
rc auth login
rc auth status --scopes --json
```

Use browser OAuth. If the status reports `method: api_key`, replace that login with OAuth:

```bash
rc auth logout
rc auth login
```

MRA 1.7.0 uses the official `rc` CLI as its RevenueCat API transport. It does not require a RevenueCat `sk_...` secret key in Bitwarden or in an MRA profile.

## If `mra-agent` is not found

Check the local checkout first:

```bash
grep -A6 '^\[project.scripts\]' pyproject.toml
ls -l .venv/bin/mra-agent
```

The `pyproject.toml` script table must contain `mra`, `mra-agent`, `mra-mcp`, and `mra-agent-mcp`. If it does not, the local checkout is stale. Preserve local work, update from `main`, and reinstall the editable package.

## Security defaults

`mra-mcp` and `mra-agent-mcp` expose the risk-gated local server. Reads, dry-runs, contained single-object mutations, and local reconciliation of verified non-secret profile identifiers are available to agents. High-risk actions require a native local human approval and fail closed if approval is unavailable or declined.

Static Google Play credentials and the AdMob OAuth client should be stored in Bitwarden Secrets Manager and bound by UUID. The Bitwarden machine token and dynamic AdMob OAuth refresh token remain in the OS credential store.

RevenueCat OAuth is owned by the official RevenueCat CLI. MRA never asks the model for an access token or refresh token and strips `RC_API_KEY` and `REVENUECAT_V2_SECRET_KEY` before invoking `rc` so stale project-scoped API keys cannot override OAuth.

The Google service account RevenueCat uses for Play purchase validation is still a separate static credential. Bind it through the existing Bitwarden-backed command:

```bash
mra-agent auth bind-revenuecat-play --secret-id YOUR_REVENUECAT_PLAY_SERVICE_ACCOUNT_UUID
```

After install, run:

```bash
mra-agent doctor
```

The RevenueCat entry should report `official-revenuecat-cli-oauth`.

For AdMob, bind the Desktop OAuth client before browser consent:

```bash
mra-agent auth bind-admob --secret-id YOUR_BITWARDEN_SECRET_UUID
mra admob login
mra admob probe
```

For RevenueCat reconciliation, use `rc_list_projects` before creating a project, then `rc_inspect_wiring` or targeted package/entitlement read tools before changing live wiring. Profile IDs should be changed through `profile_update_identifiers`, not by editing `profiles.json` directly.

If multiple RevenueCat CLI profiles are configured, select the one MRA should use before launching the MCP server:

```bash
export MRA_REVENUECAT_CLI_PROFILE=<profile-name>
```

Review `SECURITY.md` for the full credential and approval model.
