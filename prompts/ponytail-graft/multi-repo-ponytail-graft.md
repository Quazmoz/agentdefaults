# Portable, Per-Repo Ponytail + Graft Setup

## Purpose

Install and wire Ponytail and Graft into a repository selected by path, without
depending on either tool being installed globally. The result must be portable
to another clone or machine, safe when several repositories use different
versions, compatible with Claude Code and Codex, and compatible at instruction
tier with GitHub Copilot, Cursor, and Kiro.

This prompt is an installer specification. Execute it against the path supplied
as `TARGET_DIR`; do not assume the current working directory is the target.

Upstream:

- Graft: npm `@nanonets/graft` and <https://github.com/NanoNets/Graft>
- Ponytail: npm `@dietrichgebert/ponytail` and
  <https://github.com/DietrichGebert/ponytail>

## Inputs

Require one input:

```text
TARGET_DIR=<path visible to the agent on this machine>
```

Accept these optional inputs:

```text
TARGET_MODE=auto        # auto | repo | workspace
UPDATE_TOOLS=false      # false preserves existing exact pins; true refreshes them
HOSTS=claude,codex,cursor,kiro,copilot
```

Paths may be absolute or relative and may contain spaces. Canonicalize the path
before using it. `TARGET_DIR` must already exist; never create a guessed target.
For another machine, run this prompt in an agent session on that machine or
against a mounted path visible to the current session. A path is not permission
to open an SSH connection, clone an unrelated repository, or mutate a remote
host.

## Required outcome

For every selected repository root:

1. exact versions of Graft and Ponytail are locked together under
   `.agent-tools/ponytail-graft/`;
2. no app-level dependency manifest or lockfile is changed for the install;
3. every Graft CLI, hook, statusline, and MCP launch resolves that repository's
   locked package rather than a global binary, an unpinned `npx` download, or a
   sibling repository;
4. Ponytail and Graft use separate instruction fences, files, MCP keys, hook
   entries, and runtime state;
5. Claude Code and Codex receive working repository instructions; Claude also
   receives repo-local lifecycle hooks and Graft MCP; and
6. Cursor, Kiro, and GitHub Copilot receive their supported repository-local
   instruction/MCP/hook tier without claiming capabilities their installed host
   does not expose.

Expected support after a successful run:

| Host | Graft | Ponytail | Required limitation |
|---|---|---|---|
| Claude Code | repo skill, MCP, hooks, statusline | repo instructions, skills, hooks | one statusline only; keep Graft's and do not install Ponytail's |
| Codex CLI/IDE | `AGENTS.md` plus repo-local CLI | `AGENTS.md` plus `.agents/skills/` | do not write `~/.codex`; add MCP/hooks only if current official docs and local help prove a repo scope |
| Cursor | repo rule, MCP, project hooks | repo rule | no Ponytail lifecycle hooks unless current Cursor support is verified and implemented without shared state |
| Kiro | repo steering and MCP | repo steering | instruction tier for Ponytail |
| GitHub Copilot Chat/CLI | repo instructions and shell-accessible local CLI | repo instructions | instruction tier; no user-global plugin install |

Instruction tier is a real supported outcome, but it is not the same as a
native Ponytail plugin: it has no automatic mode switching or lifecycle
activation. State this distinction in the final report.

## Authority and safety boundary

Authorized mutations are limited to the resolved target root, its selected
child repository roots in workspace mode, and fresh temporary directories used
for inspection. Network reads and package downloads needed for the two named
upstreams are in scope. Do not:

- install or upgrade a global npm package;
- run any Ponytail marketplace/plugin install command;
- write under `~/.claude`, `~/.codex`, `~/.copilot`, `~/.cursor`, `~/.kiro`,
  `~/.config/ponytail`, the global npm root, or another repository;
- change application source, product behavior, CI, deployment files, or the
  target repository's own dependency manifest merely to host these tools;
- delete or replace a foreign instruction, hook, MCP, settings, or rule file;
- initialize Git, commit, push, open a pull request, or contact a remote machine;
- print, copy, or place secrets into prompts, configs, docs, or logs.

If the target is outside the agent's writable workspace, request access to that
exact canonical target. Do not broaden the writable root. Stop before mutation
if the target resolves to `/`, a filesystem root, a home directory, or another
dangerously broad directory.

Read every applicable `AGENTS.md`, `CLAUDE.md`, or narrower repository
instruction before changing that repository. If the target already has a Graft
graph, use its graph-first workflow for target-repository discovery.

## Convergence and ownership contract

The whole procedure is convergent. Running it repeatedly with the same inputs
and pins must produce the same tracked bytes and no second-run diff.

Classify every target before writing it:

- `absent`: safe to create;
- `managed-current`: owned by this procedure and byte-identical; do not rewrite;
- `managed-stale`: owned by this procedure but derived content differs; update
  only the owned region or file;
- `foreign`: not provably owned by this procedure; preserve and report it.

Use these ownership identifiers:

```text
<!-- graft:start --> ... <!-- graft:end -->
<!-- ponytail:start --> ... <!-- ponytail:end -->
<!-- ponytail-graft-local:start --> ... <!-- ponytail-graft-local:end -->
package.json#agentTooling.managedBy = "multi-repo-ponytail-graft/v1"
generated-file header = "generated by multi-repo-ponytail-graft/v1"
```

Every byte added to a shared Markdown file must be inside one of the procedure's
fences. Graft owns only its `graft:*` fence and its documented whole-file
targets. This procedure owns the other two fences. Never put custom content
inside a Graft-owned fence or whole-file target.

For fence upserts, use one deterministic scratch script and these rules:

```text
markers match only when alone on their own line after trimming
0 complete pairs -> append one block, preserving the file's EOL and final-newline convention
1 complete pair  -> unchanged on byte match, otherwise replace only that region
anything else    -> foreign/ambiguous; change nothing and report
```

Do not normalize bytes outside an owned fence. Do not use blind append. Do not
rewrite a file whose desired bytes already match. Generated content must contain
no timestamp, run id, duration, hostname, username, absolute checkout path, or
home-directory path.

When `UPDATE_TOOLS=false`, reuse exact versions already present in a managed
sidecar. Do not query "latest" and manufacture an upgrade. When
`UPDATE_TOOLS=true`, resolve current stable versions from authoritative upstream
metadata, update both exact pins and the lockfile deliberately, then regenerate
derived adapters. Never use a floating version in a committed file.

## 1. Resolve the target topology

Canonicalize `TARGET_DIR`, then classify it without mutation:

### Repository mode

Use one root when `TARGET_DIR` is a Git worktree or lies inside one. If the path
is inside a worktree, resolve to `git rev-parse --show-toplevel`, show the
resolved root, and use it consistently. A monorepo with one `.git` is one
repository install; its subprojects inherit root instructions.

### Workspace mode

Use workspace mode only when the canonical target has no `.git` of its own and
contains at least two immediate child Git repositories, or when
`TARGET_MODE=workspace` explicitly names such a folder. Do not recursively
adopt arbitrary nested clones.

Each immediate child is an independent repository root. Install an isolated
sidecar and the full host wiring in each child. Install a command-only sidecar
at the workspace root so it can build and query the federated
`graft/workspace.json`; because that root is not version-controlled, report that
its files are local to that machine.

Do not run `graft init` at the workspace parent. Current Graft versions make a
parent-level `init` recursively wire every child using the parent's runtime,
which would overwrite the child-local launchers and make the result oscillate
on every pass. Run `graft build` at the parent, compare its workspace child list
with the sorted immediate-child discovery, and stop on a mismatch. An agent
session that opens at the non-repository parent gets federated queries only; it
does not receive host instruction/hooks wiring from this procedure. Start
coding-agent sessions in the child repository roots.

If `TARGET_MODE=auto` finds neither one Git root nor a valid multi-repo
workspace, stop with the classification evidence. Do not initialize Git or
choose a nearby directory.

Print the exact ordered root list before changing anything. Sort child roots by
repository-relative name so repeated runs use the same order. Snapshot
`git status --porcelain` separately for every Git root and preserve all
pre-existing changes.

## 2. Inspect current upstream behavior

Do not guess commands, host ids, paths, or config schemas.

Require Node.js and npm versions accepted by the selected Graft package. On the
first install, or with `UPDATE_TOOLS=true`, query npm for the stable versions of
`@nanonets/graft` and `@dietrichgebert/ponytail`. Record exact semantic versions,
not tags.

Use fresh `mktemp` directories with cleanup traps to shallow-clone the official
upstreams only when published-package contents or host behavior cannot be
established from the installed packages. Record source commit SHAs in the run
report, never as a timestamp-based identity.

After the sidecar is installed, inspect its actual files as runtime truth:

For Graft, inspect:

- `graft init --help` and `graft init --list-agents` through the local launcher;
- `dist/hosts/registry.js` for host ids, paths, and `section` versus `owned`;
- `dist/hosts/init.js`, `dist/hosts/mcp-config.js`, and
  `dist/claude/init.js` for global-write and MCP behavior;
- `dist/claude/shim-template.js` for package resolution order;
- `dist/claude/settings-merge.js` and `dist/hosts/config-write.js` for merge
  and ownership behavior; and
- the installed package's engine requirement and version.

For Ponytail, inspect:

- installed `AGENTS.md` as the compact canonical instruction body;
- every `skills/*/SKILL.md` that will be copied;
- `hooks/claude-codex-hooks.json` and its referenced scripts;
- the installed package version and published file list; and
- current upstream `docs/agent-portability.md` when a requested adapter is not
  shipped in the npm package.

For Codex-specific paths and capabilities, current official OpenAI
documentation and the installed `codex --help`, `codex plugin --help`, and
`codex mcp --help` outrank this prompt. Repository-local Codex skills currently
belong under `.agents/skills/`; verify that before copying. Do not infer a
repo-local Codex config, MCP registry, plugin install, or hook registry from the
existence of user-level support.

## 3. Create the isolated sidecar

Use this layout in each selected root:

```text
.agent-tools/ponytail-graft/
├── package.json                 # tracked, deterministic, exact versions
├── package-lock.json            # tracked npm integrity lock
├── bin/
│   ├── graft.cjs                # tracked repo-relative Graft launcher
│   └── ponytail-hook.cjs        # tracked repo-relative Claude hook launcher
├── node_modules/                # ignored, regenerated with npm ci
└── state/                       # ignored, repository-local runtime state
```

Do not reuse the app's root `package.json`, lockfile, package manager, or
`node_modules`. The sidecar is intentionally an npm island so it also works in
Python, Go, Rust, Java, and non-Node repositories.

The managed `package.json` must be private, contain the ownership field above,
and declare exactly these two runtime dependencies at exact versions:

```json
{
  "private": true,
  "agentTooling": {
    "managedBy": "multi-repo-ponytail-graft/v1"
  },
  "dependencies": {
    "@dietrichgebert/ponytail": "<exact-version>",
    "@nanonets/graft": "<exact-version>"
  }
}
```

Keep keys in the shown deterministic order. If that path contains a foreign
package manifest, stop for that root instead of merging into an unknown tool
environment.

Install with npm scoped to this sidecar and with telemetry disabled for the
install process. On later machines use `npm ci --prefix
.agent-tools/ponytail-graft`; do not use a global install or `npx -y`.

Upsert these exact ignore patterns into the root `.gitignore` using the
repository's existing style and without duplicating them:

```gitignore
.agent-tools/ponytail-graft/node_modules/
.agent-tools/ponytail-graft/state/
.claude/.ponytail-active
.claude/.ponytail-statusline-nudged
```

Allow Graft itself to manage its `graft/` ignore entry. If `.gitignore` is a
symlink, generated file, or otherwise foreign-controlled, stop before changing
it and report the required manual ignore entries.

## 4. Make Graft resolution repository-local

`bin/graft.cjs` must be a small deterministic Node launcher. It must:

1. derive the sidecar root from `__dirname`;
2. resolve `@nanonets/graft/package.json` with `require.resolve(..., { paths:
   [sidecarRoot] })`;
3. construct `<resolved-package>/dist/cli.js`;
4. set `DO_NOT_TRACK=1` unless the caller explicitly set another value;
5. import that CLI via `pathToFileURL`; and
6. fail loudly when the locked package is absent or cannot load.

It must not call `graft` from `PATH`, run `npm root -g`, invoke `npx`, contain an
absolute repo path, or search a parent/sibling `node_modules`.

The canonical invocation for every selected root is:

```bash
node .agent-tools/ponytail-graft/bin/graft.cjs <graft-arguments>
```

Add this fixed bridge inside `ponytail-graft-local:*` fences in `AGENTS.md`,
`CLAUDE.md`, and `.github/copilot-instructions.md`, and as separate always-on
owned rules named `ponytail-graft-local.mdc` and `ponytail-graft-local.md` for
Cursor and Kiro:

```md
## Repository-local agent tools

This repository pins Ponytail and Graft under
`.agent-tools/ponytail-graft/`. Run every Graft command as
`node .agent-tools/ponytail-graft/bin/graft.cjs ...`; any bare `graft ...`
example in generated Graft guidance is shorthand for that repository-local
launcher. Never substitute a global `graft` or an unpinned `npx` invocation.
Ponytail governs implementation economy; Graft supplies repository evidence,
especially for Ponytail ladder rung 2 (reuse what already exists).
```

Keep that body byte-identical across hosts, adding only required host
frontmatter outside its Markdown body.

## 5. Wire Graft without global writes

Resolve requested host names to ids from the installed registry. The expected
baseline is `claude`, `agents` for Codex, `cursor`, `kiro`, and `copilot`, but
the installed registry wins. Never invent `codex` if the installed version uses
`agents`.

Before `init`, inventory Graft adapters already present. Because current Graft
versions may retract hosts omitted from a later `--agents` invocation, use the
stable union of requested supported host ids and already-wired recognized host
ids. Do not silently remove an existing Graft adapter.

Validate any pre-existing JSON that Graft may touch, especially
`.claude/settings.json`, `.mcp.json`, `.cursor/mcp.json`,
`.cursor/hooks.json`, and `.kiro/settings/mcp.json`. If a file is invalid or its
expected parent key has the wrong type, stop for that file/root; never let a
best-effort upstream parser replace it with an empty object.

From each Git repository root, run the local launcher with the same sorted
host-id list on every pass. Do not run these `init` commands at a non-Git
workspace parent:

```bash
node .agent-tools/ponytail-graft/bin/graft.cjs init . --agents <sorted-ids> --no-global --dry-run
node .agent-tools/ponytail-graft/bin/graft.cjs init . --agents <sorted-ids> --no-global
node .agent-tools/ponytail-graft/bin/graft.cjs build .
```

If a foreign Claude statusline exists, use the installed Graft version's
documented run-invariant `--no-statusline` behavior. Do not alternate the flag
based on state created by the previous run. When Graft owns the statusline,
keep it; Ponytail must not install a second one.

`--no-global` is mandatory even if dry-run output still lists candidate global
writes. Verify the postcondition against the user config snapshot.

Graft may generate hook shims with a baked absolute package directory and may
generate MCP entries that prefer `graft` from `PATH` or `npx -y`. Those forms do
not satisfy this prompt. After every `init`, deterministically replace only the
Graft-owned launch surface:

- `.claude/helpers/graft-hooks.cjs` and
  `.claude/helpers/graft-statusline.cjs` must resolve the Graft package only
  from `.agent-tools/ponytail-graft/`, then import the appropriate
  `dist/claude/*.js` entry;
- `.cursor/hooks/graft-hooks.cjs`, when present, must use the same local-only
  resolution;
- each Graft-owned command in `.cursor/hooks.json` must be project-relative,
  for example `node ".cursor/hooks/graft-hooks.cjs" <subcommand>`, rather than
  retaining the absolute shim path emitted by some Graft versions. Identify
  only entries whose exact command shape points at Graft's owned hook shim,
  preserve foreign hook entries and sibling keys, and rely on Cursor's verified
  project-hook working directory; and
- every repo-local `mcpServers.graft` entry written for Claude, Cursor, or Kiro
  must be exactly equivalent to:

```json
{
  "command": "node",
  "args": [".agent-tools/ponytail-graft/bin/graft.cjs", "mcp"]
}
```

Merge by the `graft` key and preserve every foreign MCP server and config key.
Do not add an absolute `cwd`; these project configs launch at their project
root. If the installed host does not guarantee that, use that host's verified
portable project-root variable or report MCP as unsupported rather than
committing a machine path.

Do not rewrite Graft's instruction body merely to change the command spelling;
the separate local-launch bridge supplies that precedence. Do not add content
to Graft `kind: owned` files such as `.cursor/rules/graft.mdc`,
`.kiro/steering/graft.md`, or `.claude/skills/graft/SKILL.md`.

On a fresh clone the ignored Graft wiring stamp is absent. Therefore the
documented bootstrap must run local `graft init` and the deterministic
local-launch post-processing before an agent session starts. Do not claim that
copying tracked wiring without installing/bootstrap is sufficient.

## 6. Install Ponytail's repository adapters

Derive the compact canonical Ponytail body from the installed package's
`AGENTS.md`, removing only its Ponytail-repository self-reference when present.
Copy it verbatim inside `ponytail:*` fences in:

- `AGENTS.md` for Codex and other AGENTS-aware hosts;
- `CLAUDE.md` for Claude Code; and
- `.github/copilot-instructions.md` for GitHub Copilot Chat/CLI.

Append this fixed composition note inside the same fence, after the canonical
body:

```md
> **Ponytail + Graft precedence.** Ponytail governs how much code to write,
> never whether to keep a safeguard. Repository-specific instructions win over
> Ponytail defaults. No Ponytail rule authorizes weakening security,
> trust-boundary validation, error handling that prevents data loss,
> accessibility, or anything explicitly requested. Before writing new code,
> answer ladder rung 2 by querying this repository's locked Graft launcher.
```

Verify the extracted Ponytail body is byte-identical in all three shared files.
Heading demotion, if required to preserve a host file's hierarchy, must be a
deterministic transformation applied identically on every run.

Create or refresh these whole-file instruction adapters from the same canonical
body, with upstream-compatible frontmatter:

```text
.cursor/rules/ponytail.mdc
.kiro/steering/ponytail.md
```

Never concatenate Ponytail into `.cursor/rules/graft.mdc` or
`.kiro/steering/graft.md`; Graft owns those files wholesale. If a Ponytail path
already exists and is not byte-identical or provably managed by this procedure,
leave it and report the conflict.

Kiro's ordinary workspace sessions load steering from `.kiro/steering/`.
Custom Kiro agents may restrict their resource set; claim Ponytail support for
one only after its resource configuration is verified to include the managed
steering file. Do not mutate a foreign custom-agent definition merely to make
that claim.

Copy every installed Ponytail skill directory, byte-for-byte, to both:

```text
.claude/skills/<ponytail-skill>/
.agents/skills/<ponytail-skill>/
```

Use the installed package as the one source. Copy only directories containing a
valid `SKILL.md`; do not paraphrase skills or generate two variants. Track a
deterministic manifest of relative file names and SHA-256 hashes under the
managed sidecar so a later run can distinguish a managed stale copy from a
foreign skill of the same name. Never overwrite a foreign same-name skill.

### Claude lifecycle hooks

Claude Code supports project settings, so install Ponytail's hooks there without
using its user-global plugin.

`bin/ponytail-hook.cjs` must:

1. derive the repo and sidecar roots from its own location;
2. accept only the fixed actions `activate`, `subagent`, and `track`;
3. map them respectively to `ponytail-activate.js`,
   `ponytail-subagent.js`, and `ponytail-mode-tracker.js` under the locked npm
   package's `hooks/` directory;
4. set `CLAUDE_CONFIG_DIR` to the repo's `.claude` directory and
   `XDG_CONFIG_HOME` to the sidecar's ignored `state/config` directory so mode
   and default-mode state remain per repo;
5. clear plugin-only host variables that would make a project hook emit the
   wrong host output schema; and
6. load only the allowlisted local hook file, failing loudly on an unknown
   action or missing package.

Merge one Ponytail-owned entry into each applicable array in
`.claude/settings.json`, preserving Graft and every foreign hook entry:

| Event | Ponytail action |
|---|---|
| `SessionStart` | `node "${CLAUDE_PROJECT_DIR:-.}/.agent-tools/ponytail-graft/bin/ponytail-hook.cjs" activate` |
| `SubagentStart` | `node "${CLAUDE_PROJECT_DIR:-.}/.agent-tools/ponytail-graft/bin/ponytail-hook.cjs" subagent` |
| `UserPromptSubmit` | `node "${CLAUDE_PROJECT_DIR:-.}/.agent-tools/ponytail-graft/bin/ponytail-hook.cjs" track` |

Use the installed Ponytail hook manifest for matchers and timeouts. Identify
this procedure's old hook entries by the exact `ponytail-hook.cjs` path, remove
those old entries, then append the desired entry once. Never filter an entry
merely because it contains the word `ponytail`.

Do not merge commands containing `${CLAUDE_PLUGIN_ROOT}` into project settings;
that variable belongs to a native plugin install. Do not configure Ponytail's
statusline. Graft and Ponytail may both have `SessionStart` and
`UserPromptSubmit` entries: separate entries are intentional and additive, not
a collision.

### Codex lifecycle boundary

Use `.agents/skills/` and `AGENTS.md` for a fully repo-scoped Codex instruction
tier. Current Codex plugin installs and its ordinary MCP/hook config may be
user-scoped. Unless current official documentation plus installed CLI evidence
proves a project-only registry, do not install the Ponytail plugin, write
`~/.codex`, or claim repo-local lifecycle hooks/MCP. Codex can still run Graft
through the locked launcher described in `AGENTS.md`.

If a future Codex version proves a repo-local MCP or hook registry, add only a
repo-relative `node .agent-tools/ponytail-graft/...` command, preserve foreign
entries, and include it in the isolation tests. Host evolution may increase the
supported tier; it never relaxes the no-global requirement.

## 7. Collision matrix

Verify this matrix against the installed versions rather than trusting it
blindly:

| Surface | Graft owns | Ponytail owns | Coexistence rule |
|---|---|---|---|
| `AGENTS.md` | `graft:*` fence | `ponytail:*` fence | disjoint; local-launch bridge is a third fence |
| `CLAUDE.md` | nothing | `ponytail:*` fence | local-launch bridge remains disjoint |
| `.github/copilot-instructions.md` | `graft:*` fence | `ponytail:*` fence | disjoint; Copilot gets instruction tier |
| `.claude/skills/` | `graft/` | `ponytail*/` | different directories |
| `.agents/skills/` | nothing | `ponytail*/` | Codex repo-local skills |
| `.cursor/rules/` | `graft.mdc` | `ponytail.mdc` | local bridge uses `ponytail-graft-local.mdc` |
| `.kiro/steering/` | `graft.md` | `ponytail.md` | local bridge uses `ponytail-graft-local.md` |
| repo MCP JSON | `mcpServers.graft` | none | rewrite only Graft's value to the local launcher |
| `.claude/settings.json` hooks | entries containing `graft-hooks.cjs` | entries containing exact `ponytail-hook.cjs` path | filter and upsert by exact owner signature |
| Claude statusline | Graft | none | never install a second statusline |
| runtime state | `graft/` and its cache | ignored repo-local Ponytail state | never use shared home-state for Ponytail |
| package runtime | sidecar dependency `@nanonets/graft` | sidecar dependency `@dietrichgebert/ponytail` | one lockfile, separate package names, no app deps |

If current upstream behavior contradicts a row, stop and report the exact source
file/version and conflict. Do not improvise a destructive merge.

## 8. Portable bootstrap and documentation

Create a deterministic, tracked bootstrap under the managed sidecar using the
smallest implementation suitable for the target. It must perform only these
steps:

```text
npm ci in the sidecar
validate installed exact versions against package.json/package-lock.json
run local graft init --no-global with the recorded host set
restore the local-only shims and MCP entries
refresh Ponytail instruction/skill/hook adapters from the locked package
build the local Graft graph
run the fast isolation and structure checks
```

The bootstrap must accept its repo root explicitly or derive it from its own
location. A workspace parent's bootstrap is command-only: install its sidecar,
build the federated graph, and validate the child list; it must never call
`graft init`. A child repository's bootstrap performs the full sequence above.
Both forms must work when invoked from another current directory and when the
path contains spaces. They must contain no absolute path from the generating
machine. Use argument arrays rather than shell interpolation for paths. Bound
subprocess timeouts and propagate non-zero exits.

Do not commit `node_modules`, runtime state, temporary clones, or Graft's
regenerable graph. A new clone becomes ready by running the documented bootstrap
inside that clone; no global package is a prerequisite.

Create `docs/AGENT_TOOLING.md` only when the repository has a normal docs
location and no docs generator owns that path. Start a procedure-owned file
with:

```text
<!-- generated by multi-repo-ponytail-graft/v1; regenerate, do not hand-edit -->
```

If the path is foreign, leave it and place a concise managed README under the
sidecar instead. Document:

- exact locked versions and the package-lock integrity source;
- bootstrap, update (`UPDATE_TOOLS=true`), and uninstall procedures;
- the canonical local Graft invocation;
- the host support table and Codex limitation;
- the three instruction fences and collision matrix;
- why Graft owns the only Claude statusline;
- ignored graph/dependency/state directories; and
- that every clone/machine must run bootstrap before opening an agent session.

Documentation must be deterministic and contain no timestamp, duration,
hostname, username, home path, or absolute checkout path.

## 9. Validation

Validation must use the actual selected roots and locked tools. Report each
executed check separately.

### Structure and syntax

- Parse every changed JSON and the sidecar lockfile.
- Parse TOML/YAML only when changed and with a repository-approved parser.
- Validate every copied `SKILL.md` has `name` and `description` frontmatter.
- Assert exactly one balanced pair for each applicable fence.
- Assert extracted Ponytail bodies match the installed canonical source.
- Assert the requested host files exist and Graft-owned files match the
  installed version except for the documented local-only launch shims.
- Run `git diff --check` and review `git diff --numstat`; changes outside owned
  regions or unexpected deletions fail the run.

### Dependency and provenance

- Run `npm ci --prefix .agent-tools/ponytail-graft` from a clean sidecar
  dependency state when safe, then `npm ls --prefix
  .agent-tools/ponytail-graft --depth=0`.
- Compare installed package versions with exact manifest and lockfile versions.
- Confirm the Ponytail canonical body and skills came from that installed
  package, and record source SHAs when a clone was required.
- Scan tracked generated files for absolute target/home paths and fail if any
  appear.

### Runtime isolation

- Snapshot hashes or mtimes of relevant user configs and the global npm package
  before and after. They must remain unchanged.
- Prepend a temporary directory containing a fake failing `graft` executable to
  `PATH`. The repo launcher, Claude Graft shims, and MCP launch command must
  still resolve the locked sidecar version and never execute the fake.
- If another selected repo is available, give it a deliberately different
  locked-version fixture in a scratch copy and prove each launch reports its own
  version. Never alter the real sibling repo merely to make this test.
- Inspect the effective MCP entries and assert they use `node` plus the
  repo-relative sidecar launcher, with no bare `graft`, `npx`, global npm root,
  or absolute path.
- Inspect `.cursor/hooks.json`, when present, and assert every Graft-owned
  command uses the repo-relative `.cursor/hooks/graft-hooks.cjs` path and no
  absolute package, target, or home path.

Graft may maintain an optional tool-update cache under `~/.graft`; that cache
is neither a package installation nor host configuration, and is outside this
prompt's repo-isolation guarantee. Set `DO_NOT_TRACK=1` for every scripted
Graft invocation. If the operator requires zero home-directory writes, report
the installed Graft version's cache behavior as a blocker unless an official
no-cache switch is verified; do not fake isolation by changing `HOME`.

### Functional checks

- Run the local Graft version command, `graft build`, `graft check`, and one live
  `graft ask` through `bin/graft.cjs`.
- Launch the Graft MCP server far enough to complete an MCP `initialize` and
  `tools/list` handshake for every configured host schema that can be exercised.
- Execute each Claude Graft helper directly with safe representative input and
  require exit 0.
- Execute Ponytail `activate`, `subagent`, and `track` wrappers with valid sample
  input; confirm the expected instruction output and that all state lands only
  in the repo's ignored paths.
- Confirm `.claude/settings.json` contains exactly one Graft entry and one
  Ponytail entry for each event they own, and that all foreign hooks survive.
- Run repository-native lint/config/docs checks relevant to the files changed.
  Inspect pre-scripts before running package commands that could regenerate
  unrelated files.

### Idempotence gate

Run the tracked bootstrap twice after the first successful setup. Capture a
checksum manifest of every managed tracked file after pass one. Pass two must:

- report every target as unchanged or no-action;
- produce the same checksum manifest;
- leave the per-root `git diff` exactly as it was after pass one; and
- leave user/global config snapshots unchanged.

Because the target may already have unrelated changes, do not require an empty
whole-tree diff. Compare against the captured pre-run status/diff and assert
that the second pass introduces no additional change. Never reset, stash, or
discard user work to simplify this check.

For workspace mode, run the command-only gate at the workspace root and the
full gate in every child, then run one federated query from the parent and one
local query from each child. Confirm parent results carry child scope labels,
the parent never runs `graft init`, and child queries do not resolve through a
sibling's sidecar.

## 10. Report

Use this report shape:

```text
STATUS: completed | partially_completed | blocked | failed
MODE: implement
TARGETS
DISCOVERED
IMPLEMENTED
VERIFIED
UNVERIFIED
RISKS
USER ACTION
```

Under `TARGETS`, list only canonical target paths needed to disambiguate the
run; do not put those machine-specific paths into generated repository files.
For every root, report:

- selected topology and hosts;
- locked Graft and Ponytail versions;
- created/replaced/unchanged/skipped-foreign actions;
- actual support tier per host;
- collision-matrix result;
- local-resolution and fake-global test result;
- idempotence result; and
- any manual action required on a new clone.

Do not report a dry run, static config review, or instruction copy as runtime
verification. Put checks that did not execute under `UNVERIFIED` with the
reason. Do not claim Codex MCP/hooks, Ponytail mode switching, or full native
plugin behavior for a host that only received repository instructions.

## Done when

The task is complete only when every non-foreign selected root has exact locked
sidecar dependencies, portable repo-relative launchers, collision-safe host
adapters, a built and queryable Graft graph, working required Claude/Codex
instruction paths, unchanged user/global configs, passing isolation checks, and
a no-change second bootstrap pass. A foreign collision or unsupported host
capability yields a truthful partial/blocked result for that root; it never
authorizes overwriting the conflicting file or escaping to a global install.
