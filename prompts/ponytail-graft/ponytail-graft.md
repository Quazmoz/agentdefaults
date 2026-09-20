# Ponytail + Graft Coexistence Setup

## Purpose

Route Ponytail + Graft setup work to the current portable, repository-local installation contract without silently installing either tool globally or making the integration mandatory.

## Required target input

`TARGET_DIR` is required. If it is absent and cannot be determined safely from the user's request, ask for it instead of guessing a repository or directory.

## Source resolution

Resolve the AgentDefaults source contract before treating any setup artifact as a target prerequisite. A new target is not expected to contain:

- `multi-repo-ponytail-graft.md`;
- `HARDENING.md`; or
- `.agent-tools/ponytail-graft/`.

Use exactly one of these paths:

1. **Verified local source.** When this entrypoint is a real file inside a verified AgentDefaults checkout and its adjacent `multi-repo-ponytail-graft.md` and `HARDENING.md` files are available, record the checkout's exact commit SHA and use the router, baseline, and hardening contract from that same snapshot.
2. **Standalone/pasted entrypoint.** When this text was pasted into a session or either sibling is unavailable, do not search `TARGET_DIR`, its parents, or the target's Git origin for AgentDefaults source files. Route source discovery through the canonical [AgentDefaults cross-repository handoff](https://github.com/Quazmoz/agentdefaults/blob/main/prompts/ponytail-graft/CROSS_REPO_HANDOFF.md).

`CROSS_REPO_HANDOFF.md` remains the transport/source-discovery owner. Through that handoff, prefer an existing verified AgentDefaults checkout visible to the session; otherwise use a fresh temporary checkout of `https://github.com/Quazmoz/agentdefaults`. Resolve one coherent source snapshot, record its exact commit SHA, and read this router, the baseline, and the hardening contract from that same commit.

Source resolution is read-only with respect to `TARGET_DIR`: do not mutate the target, install anything globally, write user-home configuration, or use floating `npx` while obtaining the contract. If the source snapshot cannot be obtained or verified, stop before target mutation and report a source-resolution failure, not a missing-target-file failure.

After the handoff resolves a verified snapshot, continue with the local-source path above; do not route back into the handoff. This prevents recursive routing between this entrypoint and `CROSS_REPO_HANDOFF.md`.

## Use this entrypoint

After source resolution, read and execute **both** of these files from the resolved snapshot in order:

1. [`multi-repo-ponytail-graft.md`](multi-repo-ponytail-graft.md) — portable per-repository coexistence baseline.
2. [`HARDENING.md`](HARDENING.md) — opt-in, write-containment, runtime-health, stale-dependency recovery, and bootstrap hardening requirements.

Treat the hardening file as an additive constraint. Where it is stricter, it wins.

The expected design is repository-local and reproducible:

- exact Graft and Ponytail versions live in the isolated `.agent-tools/ponytail-graft/` sidecar;
- application dependency manifests are not used to host agent tooling;
- Graft context discovery and Ponytail implementation-minimalism coexist through separate owned surfaces;
- foreign instructions, hooks, MCP entries, rules, and runtime state are preserved;
- no global install, user-home configuration write, floating `npx`, postinstall hook on the application, CI auto-install, or ambient activation is performed by default; and
- a repository that has not explicitly opted into Ponytail + Graft is left unchanged.

## Installation discipline

Use the tracked bootstrap as the authoritative installation/repair path. Do not pre-install the managed sidecar with improvised npm flags.

Specifically:

- never use `--ignore-scripts` for the managed sidecar;
- never treat matching package versions as proof that Graft is runnable;
- require the repo-local Graft launcher health checks defined in `HARDENING.md` before accepting or mutating host integration; and
- if a native-binding error appears after a noncanonical install, repair once from the tracked lock with lifecycle scripts enabled before diagnosing Node compatibility.

## Legacy behavior

Older revisions of this prompt described a machine-global Graft installation. That is no longer the default AgentDefaults setup contract.

If a user explicitly asks for a global/user-scoped installation, treat it as a separate machine-configuration task: inspect current upstream behavior, explain the scope, obtain the required authorization, and do not confuse it with the portable repository-local setup above.

## Completion rule

Do not claim the integration works merely because files were generated. Report separately what was written, what was statically inspected, which bootstrap/tool commands actually ran, and which host/runtime behaviors remain unverified.

A successful portable setup requires, at minimum, successful repo-local execution of:

```bash
node .agent-tools/ponytail-graft/bin/graft.cjs --help
node .agent-tools/ponytail-graft/bin/graft.cjs init --list-agents
```

If either command still fails after the bounded repair path in `HARDENING.md`, the setup is blocked and host-integration mutation must stop.
