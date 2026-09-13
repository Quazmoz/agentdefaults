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
command -v mra-agent-mcp
```

The secure-agent build is version 1.1.0 or newer.

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
grep -A5 '^\[project.scripts\]' pyproject.toml
ls -l .venv/bin/mra-agent
```

The `pyproject.toml` script table must contain both `mra-agent` and `mra-agent-mcp`. If it does not, the local checkout is stale. Check `git status`, preserve any local work as appropriate, update from `main`, and reinstall the editable package.

After `mra-agent` is available, continue with profile binding and the secret-manager setup documented in `README.md`.
