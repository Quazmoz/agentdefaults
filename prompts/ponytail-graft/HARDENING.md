# Ponytail + Graft Installer Hardening

## Purpose

Add safety and recovery constraints to the portable Ponytail + Graft setup without making either tool mandatory, installing anything globally, or expanding host permissions.

Apply this file together with `multi-repo-ponytail-graft.md` for every new or regenerated portable install.

## Opt-in boundary

Ponytail + Graft coexistence is an **explicit repository choice**. AgentDefaults must not automatically install, bootstrap, upgrade, or activate these tools merely because this prompt exists or because a repository is opened.

Do not wire the setup into package postinstall scripts, shell startup, IDE startup, CI, or another ambient trigger unless the user explicitly asks for that behavior. Running the tracked bootstrap is itself the opt-in action for a repository that already contains the managed sidecar.

A repository that does not already contain the managed sidecar must not receive it unless the task explicitly asks to install or configure Ponytail + Graft.

## Dependency-installation boundary

The tracked bootstrap owns sidecar dependency installation and repair. Agents must not improvise alternate npm install flags or pre-populate the sidecar with a materially different install procedure.

In particular:

- **Do not use `--ignore-scripts`** for the Ponytail + Graft sidecar. Graft has native Tree-sitter dependencies whose install/build lifecycle may be required for a usable runtime.
- Do not use `npm install -g`, floating `npx`, or the application repository's package manifest.
- Prefer the tracked bootstrap. When a direct repair is required, use `npm ci --no-audit --no-fund` from the sidecar's tracked lock with telemetry disabled and lifecycle scripts enabled.
- Never infer runtime health from package-version equality alone. Exact pins and a matching lockfile prove dependency identity, not that native bindings can load.

If an agent encounters a native-module failure after an install that used `--ignore-scripts`, treat the install procedure as suspect before attributing the failure to Node compatibility.

## Runtime selection

Before installing or repairing the sidecar, record `node --version`, `npm --version`, platform, architecture, and Node ABI when practical.

Require a Node release that satisfies the selected Graft package's declared `engines.node` range. Prefer a currently maintained LTS release when the host provides one. Do not invent a narrower support range than upstream declares, and do not diagnose a Node-version incompatibility solely from a native-binding load failure.

If multiple installed Node runtimes are available, prefer an in-range maintained LTS runtime for bootstrap and verification. Do not install or switch machine-wide Node versions unless the user explicitly authorizes that host-level change.

## Hardened bootstrap entrypoint

Use a small tracked `bootstrap.cjs` guard in front of the generated implementation. Preserve the implementation as `bootstrap-core.cjs` so its existing convergence logic remains intact.

The public command remains:

```bash
node .agent-tools/ponytail-graft/bootstrap.cjs
```

The guard must perform these checks before executing `bootstrap-core.cjs`:

1. accept only `--mode=repo` or `--mode=workspace` and reject duplicate/unknown mode values;
2. ensure every known mutable host/config surface remains lexically inside the selected repository root;
3. walk every existing path component for those mutable surfaces with `lstat` and refuse to write through a symbolic link;
4. include the sidecar `node_modules`, lockfile, package manifest, Graft output directory, shared instruction files, host settings/rules/hooks/skills, `.gitignore`, and generated tooling documentation in that preflight as applicable to the selected mode;
5. validate the two exact package pins against `package-lock.json` before touching ignored dependencies;
6. when the tracked pins and lock agree but ignored `node_modules` is absent, partial, or contains the wrong pinned version, repair it with bounded `npm ci` inside the sidecar and then revalidate exact versions;
7. after package validation, prove the repo-local Graft launcher is executable before any host integration is mutated; and
8. execute the generated core using an argument array, bounded timeout, repository working directory, and inherited exit status.

A tracked `package.json` / `package-lock.json` disagreement is **not** an auto-repair case. Stop and require a deliberate tool update. A symlink on a mutable surface is also a refusal, not a reason to follow the link or broaden write authority.

Do not inspect or reject unrelated symlinks elsewhere in application source merely because they exist. The guard is about write containment, not banning symlinks from repositories.

## Runtime health gate

Package presence is not sufficient. Before `bootstrap-core.cjs` may mutate `.mcp.json`, Claude settings/hooks, `AGENTS.md`, Cursor/Kiro configuration, or another host integration surface, the repo-local Graft launcher must successfully execute at least:

```bash
node .agent-tools/ponytail-graft/bin/graft.cjs --help
node .agent-tools/ponytail-graft/bin/graft.cjs init --list-agents
```

Use bounded timeouts and the repository working directory. A zero exit status from both commands is the minimum runtime-health proof.

If the sidecar packages match the tracked pins but either command fails:

1. perform **one** clean `npm ci --no-audit --no-fund` repair from the tracked lock with lifecycle scripts enabled and `DO_NOT_TRACK=1`;
2. rerun both health checks;
3. if either still fails, stop before host-integration mutation;
4. report the exact Node/npm/platform/arch/ABI, command, exit status, and first actionable native-module error without claiming the integration works.

Do not run unbounded rebuild/install loops. Do not use `npm rebuild --build-from-source` as the default recovery path unless upstream package behavior or the observed failure specifically justifies it.

## Coexistence rules that remain unchanged

Hardening does not change the established division of responsibility:

- Graft supplies repository context and graph-first discovery.
- Ponytail governs implementation economy and reuse.
- repository-specific instructions outrank Ponytail defaults;
- neither tool may weaken security, validation, accessibility, data-loss protection, or explicitly requested behavior;
- both packages remain exact, repo-local sidecar dependencies;
- no global npm installation or floating `npx` invocation is introduced;
- Graft keeps the single Claude statusline; Ponytail does not install a competing statusline;
- Ponytail and Graft keep separate instruction fences, skills, hook identities, MCP ownership, and runtime state; and
- foreign files/config entries are preserved rather than overwritten.

## Legacy prompt boundary

`ponytail-graft.md` is the compatibility entrypoint. It must route normal installs to the portable multi-repository specification plus this hardening contract.

Do not restore the old machine-global Graft installation procedure as the default. A global/tool-user installation is a separate user decision and requires explicit authorization.

## Verification

For AgentDefaults itself, static validation must confirm at minimum:

- the public bootstrap delegates to the tracked core;
- the bootstrap contains the symlink write-boundary check;
- stale ignored dependencies are repaired only from a matching tracked lock;
- the bootstrap itself contains no `--ignore-scripts` install path;
- the bootstrap performs repo-local Graft runtime health checks before delegating to the core;
- a failed runtime health check gets at most one clean `npm ci` repair before failing closed;
- only `repo` and `workspace` bootstrap modes are accepted;
- the canonical prompt routes to the portable specification and this hardening file; and
- canonical setup files contain no global npm install command.

Runtime qualification of a target repository requires actually running the bootstrap and observing both the sidecar dependency checks and the repo-local Graft health gate. Static validation alone does not prove npm, Graft, Ponytail, native bindings, or host integration behavior on another machine.
