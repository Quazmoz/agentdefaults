# Ponytail + Graft Setup Guide

## Purpose

Provide a concise human/AI navigation layer around the tested Ponytail + Graft installer prompts without duplicating or changing their behavioral contract.

## Start here

This directory contains the tested AgentDefaults contract for installing Ponytail and Graft together as **repository-local, opt-in agent tooling**.

If you are a person, use this page to choose the right entrypoint. If you are an AI agent, use this page as navigation only: the tested prompt files remain the behavioral source of truth.

| What you are trying to do | Use |
|---|---|
| Ask an AI agent to install or repair Ponytail + Graft in one repository | [`ponytail-graft.md`](ponytail-graft.md) with `TARGET_DIR=<path>` |
| Install across a directory containing multiple immediate child repositories | [`ponytail-graft.md`](ponytail-graft.md) with `TARGET_DIR=<workspace>` and `TARGET_MODE=workspace` |
| Understand the portable installer contract | [`multi-repo-ponytail-graft.md`](multi-repo-ponytail-graft.md) |
| Understand the additional safety/runtime-health requirements | [`HARDENING.md`](HARDENING.md) |
| Operate an already-installed repository or bootstrap a fresh clone | the generated `docs/AGENT_TOOLING.md` in that target repository |
| Validate AgentDefaults' Ponytail + Graft contract | `python3 scripts/validate-ponytail-graft.py` |

**Normal setup entrypoint:** [`ponytail-graft.md`](ponytail-graft.md). It already routes the agent to the portable baseline and hardening contract in the correct order. Do not manually merge or rewrite the three prompt files into a new prompt unless a host genuinely requires that transport format.

## Copy/paste: one repository

Give the coding agent the compatibility entrypoint and the target path:

```text
Install or repair Ponytail + Graft in this repository using the tested AgentDefaults setup contract:

prompts/ponytail-graft/ponytail-graft.md

TARGET_DIR=/path/to/repository
```

For an agent session already running inside the target repository, an explicit path is still preferable. It prevents accidental installation into the AgentDefaults checkout, a parent workspace, or a neighboring repository.

Optional inputs supported by the tested installer specification are:

```text
TARGET_MODE=auto
UPDATE_TOOLS=false
HOSTS=claude,codex,cursor,kiro,copilot
```

`TARGET_MODE=auto` is the normal default. Keep `UPDATE_TOOLS=false` when you want to preserve existing exact pins.

## Copy/paste: multi-repository workspace

Use workspace mode only when the target directory is intentionally a workspace containing immediate child Git repositories:

```text
Install or repair Ponytail + Graft for the repositories in this workspace using the tested AgentDefaults setup contract:

prompts/ponytail-graft/ponytail-graft.md

TARGET_DIR=/path/to/workspace
TARGET_MODE=workspace
UPDATE_TOOLS=false
HOSTS=claude,codex,cursor,kiro,copilot
```

The tested prompt defines the exact workspace-discovery and safety rules. Do not replace those rules with recursive repository scanning or guessed targets.

## What the installer is designed to do

At a high level, the tested contract makes the target repository self-contained for Ponytail + Graft tooling:

- pin both tools together under `.agent-tools/ponytail-graft/`;
- keep application dependency manifests separate from agent-tool dependencies;
- wire only the supported repository-local surfaces for the selected coding hosts;
- preserve foreign instructions, hooks, MCP entries, settings, and rules;
- keep Graft and Ponytail ownership/runtime state separate; and
- verify the repo-local Graft runtime before accepting host integration as healthy.

This page intentionally does **not** restate the implementation procedure line by line. The prompt files own those semantics.

## What it deliberately does not do

The normal AgentDefaults setup does not:

- install Ponytail or Graft globally;
- write user-home Claude, Codex, Cursor, Kiro, or Copilot configuration as part of the portable install;
- use the application's package manifest to host the tools;
- activate automatically merely because AgentDefaults or these prompts are present;
- blindly overwrite configuration it cannot prove it owns; or
- treat package-version equality as proof that the runtime is healthy.

If someone explicitly wants a global/user-scoped install, treat that as a separate machine-configuration task rather than silently changing this portable setup contract.

## Fresh clone or existing installed repository

Once a repository already contains the managed sidecar, bootstrap its ignored/generated runtime state before relying on the integration:

```bash
node .agent-tools/ponytail-graft/bootstrap.cjs
```

Then the minimum repo-local Graft health probes are:

```bash
node .agent-tools/ponytail-graft/bin/graft.cjs --help
node .agent-tools/ponytail-graft/bin/graft.cjs init --list-agents
```

For the exact installed versions, host matrix, fences, update procedure, and uninstall instructions, read the target repository's generated `docs/AGENT_TOOLING.md`.

## Troubleshooting map

| Symptom | Correct direction |
|---|---|
| The agent is unsure which prompt to use | Start with [`ponytail-graft.md`](ponytail-graft.md). |
| The target path is not recognized as a repository/workspace | Fix the target input; do not initialize Git or guess a nearby directory. |
| Graft fails with a native binding/runtime error | Use the tracked bootstrap and its bounded repair path; do not work around it with `--ignore-scripts`. |
| `package.json` and `package-lock.json` pins disagree | Stop and perform a deliberate tool update; do not auto-repair a tracked mismatch. |
| Existing host configuration is not clearly AgentDefaults-owned | Preserve it and report the conflict/ambiguity. |
| A global Graft/Ponytail install already exists | Do not rely on it for this contract; the repository-local sidecar remains authoritative. |
| Files were generated but runtime checks were not run | Report the runtime as unverified rather than claiming setup success. |

## Source-of-truth order

Use these files in this order when interpreting setup behavior:

1. [`ponytail-graft.md`](ponytail-graft.md) — compatibility/normal setup entrypoint.
2. [`multi-repo-ponytail-graft.md`](multi-repo-ponytail-graft.md) — portable per-repository installer specification.
3. [`HARDENING.md`](HARDENING.md) — additive safety and runtime-health constraints; where stricter, it wins.
4. `docs/AGENT_TOOLING.md` in an installed target repository — generated operator documentation for that concrete install.

Repository/runtime evidence and explicit current user instructions still outrank generic documentation when they reveal a real conflict that needs investigation.

## Maintainer rule

The three setup prompt files above are behaviorally significant and may be regression-tested. Improve discoverability, examples, navigation, and explanation around them without casually rewriting their bodies.

After changing surrounding documentation or installer-adjacent code, run:

```bash
python3 scripts/validate-ponytail-graft.py
python3 scripts/validate-agentdefaults.py
```

Do not report either validator as passed unless it actually ran successfully.
