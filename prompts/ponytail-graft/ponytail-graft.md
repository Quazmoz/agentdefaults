# Ponytail + Graft Coexistence Setup

## Purpose

Route Ponytail + Graft setup work to the current portable, repository-local installation contract without silently installing either tool globally or making the integration mandatory.

## Use this entrypoint

For a normal or new setup, read and execute **both** of these files in order:

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
