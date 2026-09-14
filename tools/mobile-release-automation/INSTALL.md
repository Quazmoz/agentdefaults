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

The RevenueCat wiring-readback and safe profile-reconciliation build is version 1.5.0 or newer.

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

## If `mra-agent` is not found

Check the local checkout first:

```bash
grep -A6 '^\[project.scripts\]' pyproject.toml
ls -l .venv/bin/mra-agent
```

The `pyproject.toml` script table must contain `mra`, `mra-agent`, `mra-mcp`, and `mra-agent-mcp`. If it does not, the local checkout is stale. Preserve local work, update from `main`, and reinstall the editable package.

## Security defaults

`mra-mcp` and `mra-agent-mcp` expose the risk-gated local server. Reads, dry-runs, contained single-object mutations, and local reconciliation of verified non-secret profile identifiers are available to agents. High-risk actions require a native local human approval and fail closed if approval is unavailable or declined.

Static Google Play, RevenueCat, and AdMob OAuth client credentials should be stored in Bitwarden Secrets Manager and bound by UUID. The Bitwarden machine token and the dynamic AdMob OAuth refresh token remain in the OS credential store.

After install, run:

```bash
mra-agent doctor
```

For AdMob, bind the Desktop OAuth client before browser consent:

```bash
mra-agent auth bind-admob --secret-id YOUR_BITWARDEN_SECRET_UUID
mra admob login
mra admob probe
```

For RevenueCat reconciliation, MCP 1.5.0+ can read package and entitlement wiring before changing it. Agents should use `rc_inspect_wiring` (or the targeted package/entitlement read tools), then invoke attachment mutations only when a verified relationship is missing. Profile IDs should be changed through `profile_update_identifiers`, not by editing `profiles.json` directly.

Review `SECURITY.md` for the full credential and approval model.
