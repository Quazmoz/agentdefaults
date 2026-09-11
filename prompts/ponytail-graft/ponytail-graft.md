# Ponytail + graft Coexistence Setup

## Purpose

Wire graft and Ponytail into one repository so their instruction files, MCP
entries, and lifecycle hooks coexist without collisions, and so the whole
procedure converges: re-running it on an already-configured repo is a no-op.

## Task

Set up **graft** and **Ponytail** together in this repository, so they coexist
without collisions. Configure both for: Claude Code, Codex, Cursor, Kiro,
Devin, and GitHub Copilot (Chat + CLI).

Upstream: graft = npm `@nanonets/graft` · Ponytail = https://github.com/DietrichGebert/ponytail

## Idempotence contract — governs every section below

This procedure is **convergent**: running it once, twice, or ten times leaves
the repository in the same state. A re-run on an already-configured repo ends
with an empty `git diff`, every write reporting `unchanged`, and a report that
says so. Zero file changes is a successful outcome, not a failure to do work —
never manufacture a diff to look productive.

Four rules make that true:

1. **Classify, then act.** Every target is in exactly one state: *absent*,
   *managed-and-current*, *managed-and-stale*, or *foreign*. Create the absent,
   refresh the stale, leave the current alone (do not rewrite bytes that
   already match), never touch the foreign.
2. **Marker-delimited ownership.** Every byte this procedure puts in a shared
   file lives between markers it owns, and every write is an upsert keyed on
   those markers — never a blind append, never a whole-file copy over a file
   someone else owns.
3. **Deterministic content.** Anything generated must be reproducible
   byte-for-byte from a fixed source: upstream text copied verbatim, or literal
   text given in this prompt. No timestamps, run ids, durations, mtimes,
   hostnames, `$HOME` paths, or re-improvised prose — a model paraphrasing its
   own earlier wording is the most common way a "no-op" run produces a diff.
   Where content genuinely cannot be derived (a repo-specific bridge
   paragraph), author it once; on later runs judge it by whether it is still
   *correct*, not by whether it matches what you would write today, and reword
   only what became wrong.
4. **Run-invariant conditions.** Derive each decision from repository state
   that a second run observes identically. A condition that reads the *result*
   of the previous run ("a statusline exists, so suppress it") flip-flops; §3
   has the worked example.

Make writes mechanical, not hand-edited: implement the fence upsert once as a
throwaway script in a scratch dir (§5) and route every instruction-file write
through it. Do not add that script to the repo.

Abort only on genuine ambiguity — foreign ownership, unbalanced markers, a
missing prerequisite. "Already done" is never an abort; it is the expected
steady state. A partially applied earlier run must be completable, so keep each
step independently resumable.

## 0. Read upstream first — do not guess command names

Shallow-clone Ponytail into a fresh `mktemp -d` (never into this repo, never a
fixed path a previous run may have left behind) and delete it from a trap so an
aborted run leaves no residue. Read `README.md` (per-host Install sections),
`docs/agent-portability.md` (the adapter table with each host's tier), and
`scripts/check-rule-copies.js` (defines the canonical rule body + its pinned
invariants). Record the clone's commit SHA — that, not a date, is how a later
run tells whether upstream actually changed.

For graft, read its **installed** source rather than docs — it is authoritative
about what it writes:
- `graft init --help` and `graft init --list-agents`
- `<npm-root-g>/@nanonets/graft/dist/hosts/registry.js` — every host's `relPath` and `kind`
- `.../dist/hosts/init.js` — what each flag actually suppresses
- `.../dist/hosts/sections.js` — the marker-fence upsert contract
- `.../dist/hosts/config-write.js` and `.../dist/claude/settings-merge.js` — how
  graft keeps its own writes idempotent (§3). Mirror those semantics; do not
  invent a different convention next to them.

## 1. Detection pass — classify before touching anything

Report what already exists and who owns it: `AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `.github/copilot-instructions.md`, `.claude/`, `.cursor/`,
`.kiro/`, `.codex/`, `.mcp.json`, existing lifecycle hooks, existing statusline,
and any `graft/` graph. Give each target one of the four states from the
contract.

Detect a prior run of this procedure from the markers in the files themselves
(`<!-- graft:start -->`, `<!-- ponytail:start -->`) and from graft's own files —
never from memory, and do not add a state file to the repo to track it.

Record mtimes of `~/.claude`, `~/.codex`, `~/.copilot`, `~/.cursor` so §9 can
prove what you did and didn't touch. Print the classification table before
changing anything: it is both the plan and the evidence a re-run compares against.

## 2. Install the graft CLI only if missing — machine-level, and never an upgrade

If `command -v graft` resolves, record `graft --version` and move on. **Do not
install or upgrade** because a newer version exists: an upgrade rewrites every
`kind: 'owned'` file and can change fenced bodies, turning a no-op run into a
diff. Upgrading is the user's separate decision, not a side effect of this
setup.

If it does not resolve, graft must be installed before it can wire anything. Be
honest that this is **unavoidably machine-level**: graft's hook shim resolves
the package via `npm root -g`, so it expects a global install
(`npm install -g @nanonets/graft`). A repo devDependency will not reliably
satisfy the shims.

**Ask before installing.** Installing a CLI on the user's machine is not
repository-local; the *repo-local* part of this task is graft's configuration,
not its binary. If the user declines, stop and report which steps are blocked.
Report `graft --version` after install and record it in §8's doc — when a later
run sees a different version, owned-file churn is version-driven and
legitimate, and should be reported as such rather than as non-idempotence.

## 3. Wire graft — repo-local, correct host ids, dry run first

Host ids are **not** the product names. Verified valid ids (graft 0.16.0):
`agents, adal, cursor, gemini, grok, hermes, antigravity, copilot, kiro,
windsurf, claude`. Re-verify against `--list-agents` for the installed version.
Map the requested hosts:

| Requested host | graft id | graft writes |
|---|---|---|
| Claude Code | `claude` | `.claude/settings.json` (hook + statusline blocks), `.claude/helpers/graft-{hooks,statusline}.cjs`, `.claude/skills/graft/SKILL.md`, `.mcp.json` |
| Codex | `agents` | `AGENTS.md` (fenced section) |
| Cursor | `cursor` | `.cursor/rules/graft.mdc`, `.cursor/mcp.json`, `.cursor/hooks.json`, `.cursor/hooks/graft-hooks.cjs` |
| Kiro | `kiro` | `.kiro/steering/graft.md`, `.kiro/settings/mcp.json` |
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` (fenced section) |
| Devin | **none — no graft adapter exists** | see §4 |

There is no `codex` id (Codex is served by `agents` reading repo-root
`AGENTS.md`) and no `devin` id. Do not invent either.

Use the **same argv on every run** — record it in §8's doc and reuse it
verbatim. A different `--agents` set later wires or strands hosts and produces
churn that reads like a bug.

Dry run (read-only, always safe), show the user, then run for real:

```bash
graft init --agents claude agents cursor kiro copilot --no-global --dry-run
graft init --agents claude agents cursor kiro copilot --no-global
graft build     # deterministic, no API key
```

Flag semantics, verified in `init.js` — get these right:
- `--no-global` suppresses the `~/.codex/config.toml` MCP entry, `~/.codex/hooks.json`,
  `~/.codex/hooks/graft/*`, and the Antigravity global skill. **Use it**; without
  it graft writes machine-wide config affecting all repos.
- `--no-global` does **not** suppress Cursor's hooks — those are repo-local
  (`.cursor/hooks.json`) by design; only `--no-hooks` suppresses them. Keep them.
- **`--dry-run` output ignores `--no-global`** and still prints the "your
  machine, affects ALL repos" section (confirmed: output is byte-identical with
  and without the flag). Do not treat that block as proof of a global write —
  verify with mtimes after the real run.
- **`--no-statusline` is the flip-flop trap.** Verified in
  `dist/claude/settings-merge.js`: graft already leaves a *foreign* `statusLine`
  untouched (it only warns) and replaces only its own, while the flag *deletes*
  graft's statusline when one is present. So never pass it just because "a
  statusline exists" — after run 1 the statusline is graft's, and run 2 would
  delete what run 1 wrote. Pass it only when `.claude/settings.json` has a
  `statusLine` whose `command` does **not** contain `graft-statusline.cjs`, or
  when the user asked for no statusline. That condition reads the same on every run.

graft's own writers are idempotent by construction — read them, then verify:
`writeOwned` returns `unchanged` on a byte match; `upsertSection` returns
`unchanged` when the fenced block already matches and otherwise replaces the
region in place; the Claude settings merge filters graft's prior hook,
allowlist and footer-regex entries before re-adding the current set, so
re-running `init` cannot stack a second copy beside a stale one; the MCP merge
compares the serialized entry and returns `unchanged`. `kind: 'owned'` files are
overwritten wholesale each run, which is deterministic for a fixed graft
version. Prove all of this with the §9 gate rather than trusting this paragraph.

Run `graft build` when the graph is absent or stale. With unchanged sources a
second build must leave `graft/` byte-identical; if it does not, report that as
a graft determinism finding instead of committing the churn.

## 4. Devin — report the gap, don't fake it

graft ships no Devin adapter. Devin's only possible graft coverage is a generic
instruction file it reads on its own (`AGENTS.md` being the common convention).
**Verify** whether this Devin version reads repo-root `AGENTS.md`; if it does,
say Devin is covered incidentally by the `agents` host, and if it does not, say
Devin has no graft coverage. Re-verify on each run rather than trusting a
previous run's verdict recorded in the doc. Do not hand-author a `.devin/` file
to fake it.

Ponytail *does* have a Devin plugin: `devin plugins install
DietrichGebert/ponytail` (note the plural `plugins`, unlike the other hosts) —
user-global, so document it, don't run it (§7).

## 5. Ordering, upsert semantics, and the collision rules

**Run graft first, then Ponytail.** graft's `upsertSection` appends its fence at
the end of a file that has no graft markers, so wiring Ponytail first inverts
the sections. Once graft's markers exist it replaces in place, so anything below
its fence is safe.

**Ponytail publishes no marker convention** — its instruction-tier adapters are
whole-file copies that assume they own the file, so copying one over a
graft-managed `AGENTS.md` destroys the graft section. Put Ponytail's body in its
own fence instead, `<!-- ponytail:start -->` … `<!-- ponytail:end -->`,
mirroring graft's; document that this fence is *this repo's* convention and
upstream tooling will not recognise it.

**The upsert — this replaces the old "append and guard" step.** Implement it
once as a scratch-dir script mirroring `dist/hosts/sections.js`, and route every
instruction-file write through it:

```text
markers match only when alone on their own line after trim (as graft does)

0 marker pairs → append the fence at EOF. For a graft-managed file, first
                 require a balanced graft fence to be present — that is the
                 real precondition, not "the last line is <!-- graft:end -->",
                 which is false on every run after the first.
1 marker pair  → build the desired block and compare it to the current region.
                 Equal → unchanged: write nothing at all, not even the same
                 bytes. Different → replace that region in place, leaving
                 everything outside it untouched.
otherwise      → unbalanced, duplicated, nested, or end-before-start: abort
                 this file, report it, change nothing.
```

Preserve each file's dominant line ending and its trailing-newline convention,
and normalise nothing outside the fence. Only files in the table below are fence
targets — never scan the repo for markers, and never treat `docs/AGENT_TOOLING.md`
as a target, since it documents these marker names in prose.

If a repo already has the two fences in the other order, leave them: they only
need to be disjoint, and reordering is pure churn.

Verify this collision matrix rather than trusting it:

| Path | graft | Ponytail | Verdict, and what a re-run does |
|---|---|---|---|
| `AGENTS.md` | `graft:*` fence (`section`) | `ponytail:*` fence after it | safe — disjoint fences; both upserts report `unchanged` |
| `.github/copilot-instructions.md` | `graft:*` fence (`section`) | `ponytail:*` fence after it | safe — disjoint fences; both upserts report `unchanged` |
| `.cursor/rules/` | `graft.mdc` (`owned`) | `ponytail.mdc` | safe — different filenames; `graft.mdc` rewritten identically per init |
| `.kiro/steering/` | `graft.md` (`owned`) | `ponytail.md` | safe — different filenames; same rewrite behaviour |
| `.mcp.json` / `.cursor/mcp.json` | `mcpServers.graft` | `ponytail-mcp` | safe — distinct keys; merge by key, never rewrite the file; matching entry → `unchanged` |
| `CLAUDE.md` | **not** a graft target | Ponytail bridge fence | safe — unclaimed; no graft-fence precondition applies here |
| `.claude/settings.json` | graft's hook + statusline blocks | **nothing at instruction tier** | graft drops its own prior entries before re-adding, so nothing stacks; see hook rule below |

**The one real hazard — hooks.** Ponytail's `hooks/claude-codex-hooks.json`
registers `SessionStart`, `SubagentStart`, and `UserPromptSubmit`; graft's
`.claude/settings.json` registers `SessionStart`, `UserPromptSubmit`,
`PostToolUse`, `Stop`. Two events overlap. **Never hand-merge Ponytail's hook
JSON into `.claude/settings.json`**: its commands reference
`${CLAUDE_PLUGIN_ROOT}`, which is only defined when Claude Code loads it as a
plugin, so a copied entry breaks *and* collides with graft's entries — and a
hand-merged entry is invisible to graft's own de-duplication, so it stacks a
fresh copy on every re-run. Ponytail's hooks ship exclusively with its
user-global plugin, and plugin hooks are additive to project-settings hooks, so
the two coexist only if you leave them in their separate registries. At
instruction tier Ponytail has no hooks at all.

**Never place your own content in a graft `kind: 'owned'` file**
(`.cursor/rules/graft.mdc`, `.kiro/steering/graft.md`, `.windsurf/rules/graft.md`,
`*/skills/graft/SKILL.md`) — graft overwrites those wholesale on every `init`.

Finally, **prove** coexistence and idempotence empirically, against copies in
the scratch dir and never the real files:

1. import graft's real `upsertSection` from its installed `dist/hosts/sections.js`,
   run it against a copy of each modified instruction file with a dummy body, and
   confirm graft's region was replaced while the Ponytail fence survived byte-intact;
2. run your own Ponytail upsert twice against a copy and confirm the second call
   reports `unchanged` and leaves the bytes identical.

Report both results.

## 6. Ponytail content rules

- Derive the canonical body the way upstream does (its `AGENTS.md` minus the
  repo-self-referential closing line) and **assert programmatically** that it
  equals upstream's `.github/copilot-instructions.md` before use.
- Copy it **verbatim**. Do not abridge: `check-rule-copies.js` pins the "not
  lazy about…" carve-outs (trust-boundary validation, data loss, security,
  accessibility) as invariants, so trimming silently deletes safeguards.
  Demoting the leading `#` to match the host file's heading structure is the
  only permitted edit, and it must be a deterministic function of that file's
  heading levels so every run computes the same demotion.
- The fence body is exactly: the demoted canonical body, then this precedence
  note verbatim. It is fixed text so that every run reproduces the same bytes —
  do not rewrite it in your own words:

```md
> **Precedence.** Ponytail governs *how much* code to write, never whether to
> keep a safeguard. Repo-specific rules in this file win over Ponytail's
> defaults, and no Ponytail rule authorises weakening security, validation,
> error handling, accessibility, or data-loss protection. To answer ladder
> rung 2 — "does it already exist in this codebase?" — query the graft graph
> (`graft ask "<what you are about to write>"`) before writing new code.
```

  That rung-2 pointer is where the two tools actually compose.
- Keep the block byte-identical across every instruction file; verify by diffing
  the *extracted fence bodies*, not the whole files.
- `CLAUDE.md`: a small bridge to `AGENTS.md` naming both sections — a pointer,
  not a second copy of the rules — inside its own `ponytail:*` fence. Author it
  once; on later runs leave it unless it became wrong (a renamed path, a missing
  section), and never reword it just to match your current phrasing.
- Codex repo config: add `.codex/` **only if this Codex version supports it**.
  Verify via `codex --help` / `codex plugin --help`; as of `codex-cli` 0.139.0
  there is no repo-local config (it reads `~/.codex/config.toml` plus
  `$CODEX_HOME/<name>.config.toml` profiles), so add nothing and say so.
- Do not weaken security, validation, accessibility, error handling, or
  data-loss protection. Do not remove repo-specific workflows. Do not add
  dependencies, scripts, hooks, or abstractions. Do not change application source.

## 7. Native plugin installs are user-global — document, never run

These install into the user's home config for *all* their repos. Do not execute
them, and do not probe-and-install them on a re-run — just re-list them. Capture
exact verbs from the README and present them as optional and user-scoped (note
Devin's plural `plugins`, and that the plugin tiers need `node` on the
non-interactive shell's PATH for their lifecycle hooks):

```text
Claude Code:  /plugin marketplace add DietrichGebert/ponytail
              /plugin install ponytail@ponytail          (two separate prompts)
Codex:        codex plugin marketplace add DietrichGebert/ponytail
              codex plugin add ponytail@ponytail         (then /hooks → trust)
Copilot CLI:  copilot plugin marketplace add DietrichGebert/ponytail
              copilot plugin install ponytail@ponytail
Devin CLI:    devin plugins install DietrichGebert/ponytail
```

Their state lives outside this repo, so it is outside the convergence guarantee
in the contract — say so rather than implying the repo controls it.

## 8. Documentation

Add `docs/AGENT_TOOLING.md` only if the repo already has a docs location, and
only after confirming no build/validation script globs `docs/*.md`.

This procedure owns that file. Start it with

```text
<!-- generated by the ponytail+graft setup prompt; regenerate, do not hand-edit -->
```

and regenerate it deterministically — same inputs, same bytes, written only when
they differ from what is on disk. If a file already exists at that path
**without** that marker, someone else owns it: leave it and report. Include no
timestamps, durations, mtimes, home-directory paths, or run ids; record instead
the facts a later run needs — the exact `graft init` argv, the graft version,
the Ponytail upstream commit SHA, and the fence names.

Cover: files added or changed; that graft's *configuration* is repo-local (and
that its CLI is not); the fence diagram and the collision matrix; why hooks stay
in separate registries; the `kind: 'owned'` files nobody should edit; per-host
tiers and gaps (Devin, Copilot Chat); the optional user-global commands; how to
update or uninstall each block; and that re-running this setup is a no-op by
design.

## 9. Validate, concretely

**The idempotence gate — run it, don't reason about it.** When the first pass is
complete, run the whole procedure again end to end. Every target must report
`unchanged` or no-action, and `git status --porcelain` and `git diff` must both
be empty. If the second pass writes anything, fix the non-determinism in the
procedure; do not commit the churn or explain it away.

Then:

- Parse every changed JSON/TOML/YAML (`.claude/settings.json`, `.mcp.json`,
  `.cursor/mcp.json`, `.cursor/hooks.json`, `.kiro/settings/mcp.json`).
- `git diff --numstat`: on the first pass, changes to *pre-existing* instruction
  files must be **additions only** — any deletion means a section got clobbered.
  On the second pass the numstat must be empty.
- `git diff --check` for whitespace.
- Assert exactly one balanced `graft:*` pair and one balanced `ponytail:*` pair
  per shared file, and that the extracted Ponytail bodies are byte-identical
  across files.
- `.claude/settings.json`: exactly one graft entry (`graft-hooks.cjs`) per event
  graft registers — more than one means something stacked; pre-existing foreign
  hook entries still present; `statusLine` matching whatever §3's run-invariant
  condition selected.
- Confirm MCP configs contain **both** keys where expected, and that graft's
  entry still resolves.
- Execute graft's hooks and statusline (expect exit 0) and run a live `graft`
  query to prove the graph answers.
- Confirm a second `graft build` leaves `graft/` byte-identical.
- Run the repo's lint/config checks — but **inspect npm pre-scripts first**; if
  `prelint`/`pretest` runs a generator that rewrites tracked files, invoke the
  underlying tool directly (e.g. `npx tsc --noEmit`) so validation can't dirty
  generated output. Say which you ran and why.
- Re-check `~/.claude`, `~/.codex`, `~/.copilot`, `~/.cursor` mtimes and show
  they are unchanged (excepting an install the user approved in §2).
- Re-check the working tree: only intended files should appear.
- Confirm the scratch clone and scratch scripts were removed and that nothing
  from them landed in the repo.

## 10. Report

Make the smallest coherent change. Preserve unrelated user changes. Do not
commit. Summarise: each target's action (created / replaced / unchanged /
skipped-foreign); the collision matrix as *verified*; the result of the
idempotence gate; validation output; and every host-specific limitation
honestly — which hosts get only the instruction tier, what capability they
therefore lack, and that Devin has no graft adapter. If this run changed
nothing because the repo was already configured, say exactly that.
