Set up **graft** and **Ponytail** together in this repository, so they coexist
without collisions. Configure both for: Claude Code, Codex, Cursor, Kiro,
Devin, and GitHub Copilot (Chat + CLI).

Upstream: graft = npm `@nanonets/graft` · Ponytail = https://github.com/DietrichGebert/ponytail

## 0. Read upstream first — do not guess command names

Shallow-clone Ponytail to a scratch dir (never into this repo) and read
`README.md` (per-host Install sections), `docs/agent-portability.md` (the
adapter table with each host's tier), and `scripts/check-rule-copies.js`
(defines the canonical rule body + its pinned invariants). Delete the clone after.

For graft, read its **installed** source rather than docs — it is authoritative
about what it writes:
- `graft init --help` and `graft init --list-agents`
- `<npm-root-g>/@nanonets/graft/dist/hosts/registry.js` — every host's `relPath` and `kind`
- `.../dist/hosts/init.js` — what each flag actually suppresses
- `.../dist/hosts/sections.js` — the marker-fence upsert contract

## 1. Inventory before touching anything

Report what already exists and who owns it: `AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `.github/copilot-instructions.md`, `.claude/`, `.cursor/`,
`.kiro/`, `.codex/`, `.mcp.json`, existing lifecycle hooks, existing statusline,
and any `graft/` graph. Record mtimes of `~/.claude`, `~/.codex`, `~/.copilot`,
`~/.cursor` so you can prove later what you did and didn't touch.

## 2. Install the graft CLI only if missing — this step is machine-level

If `command -v graft` fails, graft must be installed before it can wire
anything. Be honest that this is **unavoidably machine-level**: graft's hook
shim resolves the package via `npm root -g`, so it expects a global install
(`npm install -g @nanonets/graft`). A repo devDependency will not reliably
satisfy the shims.

**Ask before installing.** Installing a CLI on the user's machine is not
repository-local; the *repo-local* part of this task is graft's configuration,
not its binary. If the user declines, stop and report which steps are blocked.
Report `graft --version` after install.

## 3. Wire graft — repo-local, correct host ids, dry run first

Host ids are **not** the product names. Verified valid ids (graft 0.16.0):
`agents, adal, cursor, gemini, grok, hermes, antigravity, copilot, kiro,
windsurf, claude`. Map the requested hosts:

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

Dry run, show the user, then run for real:

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
- `--no-statusline` if the repo already has a statusline you must preserve.
- If graft is already wired here, re-running `init` is safe for content outside
  its fences (see §5) but will overwrite its `kind: 'owned'` files.

## 4. Devin — report the gap, don't fake it

graft ships no Devin adapter. Devin's only possible graft coverage is a generic
instruction file it reads on its own (`AGENTS.md` being the common convention).
**Verify** whether this Devin version reads repo-root `AGENTS.md`; if it does,
say Devin is covered incidentally by the `agents` host, and if it does not, say
Devin has no graft coverage. Do not hand-author a `.devin/` file to fake it.

Ponytail *does* have a Devin plugin: `devin plugins install
DietrichGebert/ponytail` (note the plural `plugins`, unlike the other hosts) —
user-global, so document it, don't run it (§7).

## 5. Ordering and the collision rules

**Run graft first, then append Ponytail.** graft's `upsertSection` appends its
fence at the end of a file that has no graft markers, so installing Ponytail
first would leave the sections inverted and break the append guard below.

**Ponytail publishes no marker convention** — its instruction-tier adapters are
whole-file copies that assume they own the file. Copying one over a
graft-managed `AGENTS.md` destroys the graft section. So append Ponytail inside
its own fence, `<!-- ponytail:start -->` … `<!-- ponytail:end -->`, mirroring
graft's; document that this fence is *this repo's* convention and upstream
tooling will not recognise it. Guard each append: assert the file's last line is
`<!-- graft:end -->` and abort if not.

Then verify this collision matrix rather than trusting it:

| Path | graft | Ponytail | Verdict |
|---|---|---|---|
| `AGENTS.md` | `graft:*` fence (`section`) | `ponytail:*` fence appended after it | safe — disjoint fences |
| `.github/copilot-instructions.md` | `graft:*` fence (`section`) | `ponytail:*` fence appended after it | safe — disjoint fences |
| `.cursor/rules/` | `graft.mdc` (`owned`) | `ponytail.mdc` | safe — different filenames |
| `.kiro/steering/` | `graft.md` (`owned`) | `ponytail.md` | safe — different filenames |
| `.mcp.json` / `.cursor/mcp.json` | `mcpServers.graft` | `ponytail-mcp` | safe — distinct keys; merge by key, never rewrite the file |
| `CLAUDE.md` | **not** a graft target | Ponytail bridge goes here | safe — unclaimed |
| `.claude/settings.json` | graft's hook + statusline blocks | **nothing at instruction tier** | see hook rule below |

**The one real hazard — hooks.** Ponytail's `hooks/claude-codex-hooks.json`
registers `SessionStart`, `SubagentStart`, and `UserPromptSubmit`; graft's
`.claude/settings.json` registers `SessionStart`, `UserPromptSubmit`,
`PostToolUse`, `Stop`. Two events overlap. **Never hand-merge Ponytail's hook
JSON into `.claude/settings.json`**: its commands reference
`${CLAUDE_PLUGIN_ROOT}`, which is only defined when Claude Code loads it as a
plugin, so a copied entry breaks *and* collides with graft's entries. Ponytail's
hooks ship exclusively with its user-global plugin, and plugin hooks are
additive to project-settings hooks — so the two coexist only if you leave them
in their separate registries. At instruction tier Ponytail has no hooks at all.

**Never place your own content in a graft `kind: 'owned'` file**
(`.cursor/rules/graft.mdc`, `.kiro/steering/graft.md`, `.windsurf/rules/graft.md`,
`*/skills/graft/SKILL.md`) — graft overwrites those wholesale on every `init`.

Finally, **prove** coexistence empirically: import graft's real `upsertSection`
from its installed `dist/hosts/sections.js`, run it against a *copy* of each
modified instruction file with a dummy body, and confirm graft's region was
replaced while the Ponytail fence survived byte-intact. Report the result.

## 6. Ponytail content rules

- Derive the canonical body the way upstream does (its `AGENTS.md` minus the
  repo-self-referential closing line) and **assert programmatically** that it
  equals upstream's `.github/copilot-instructions.md` before use.
- Copy it **verbatim**. Do not abridge: `check-rule-copies.js` pins the "not
  lazy about…" carve-outs (trust-boundary validation, data loss, security,
  accessibility) as invariants, so trimming silently deletes safeguards.
  Demoting the leading `#` to match the host file's heading structure is the
  only permitted edit.
- Keep the block byte-identical across every instruction file; verify with `diff`.
- Add a short precedence paragraph: Ponytail governs *how much* code to write,
  never whether to keep a safeguard; repo-specific rules win; and point
  Ponytail's ladder rung 2 ("does it already exist in this codebase?") at graft
  as the way to answer it. This is where the two tools compose.
- `CLAUDE.md`: a small bridge to `AGENTS.md` naming both sections — a pointer,
  not a second copy of the rules.
- Codex repo config: add `.codex/` **only if this Codex version supports it**.
  Verify via `codex --help` / `codex plugin --help`; as of `codex-cli` 0.139.0
  there is no repo-local config (it reads `~/.codex/config.toml` plus
  `$CODEX_HOME/<name>.config.toml` profiles), so add nothing and say so.
- Do not weaken security, validation, accessibility, error handling, or
  data-loss protection. Do not remove repo-specific workflows. Do not add
  dependencies, scripts, hooks, or abstractions. Do not change application source.

## 7. Native plugin installs are user-global — document, never run

These install into the user's home config for *all* their repos. Do not execute
them; capture exact verbs from the README and list them as optional and
user-scoped (note Devin's plural `plugins`, and that the plugin tiers need
`node` on the non-interactive shell's PATH for their lifecycle hooks):

```text
Claude Code:  /plugin marketplace add DietrichGebert/ponytail
              /plugin install ponytail@ponytail          (two separate prompts)
Codex:        codex plugin marketplace add DietrichGebert/ponytail
              codex plugin add ponytail@ponytail         (then /hooks → trust)
Copilot CLI:  copilot plugin marketplace add DietrichGebert/ponytail
              copilot plugin install ponytail@ponytail
Devin CLI:    devin plugins install DietrichGebert/ponytail
```

## 8. Documentation

Add `docs/AGENT_TOOLING.md` only if the repo already has a docs location, and
only after confirming no build/validation script globs `docs/*.md`. Cover: files
added or changed; that graft's *configuration* is repo-local (and that its CLI
is not); the fence diagram and the collision matrix; why hooks stay in separate
registries; the `kind: 'owned'` files nobody should edit; per-host tiers and
gaps (Devin, Copilot Chat); the optional user-global commands; and how to update
or uninstall each block.

## 9. Validate, concretely

- Parse every changed JSON/TOML/YAML (`.claude/settings.json`, `.mcp.json`,
  `.cursor/mcp.json`, `.cursor/hooks.json`, `.kiro/settings/mcp.json`).
- `git diff --numstat`: changes to *pre-existing* instruction files must be
  **additions only** — any deletion means a section got clobbered.
- `git diff --check` for whitespace.
- Assert fences balanced 1/1 per file; Ponytail block identical across files.
- Confirm MCP configs contain **both** keys where expected, and that graft's
  entry still resolves.
- Execute graft's hooks and statusline (expect exit 0) and run a live `graft`
  query to prove the graph answers.
- Run the repo's lint/config checks — but **inspect npm pre-scripts first**; if
  `prelint`/`pretest` runs a generator that rewrites tracked files, invoke the
  underlying tool directly (e.g. `npx tsc --noEmit`) so validation can't dirty
  generated output. Say which you ran and why.
- Re-check `~/.claude`, `~/.codex`, `~/.copilot`, `~/.cursor` mtimes and show
  they are unchanged (excepting an install the user approved in §2).
- Re-check the working tree: only intended files should appear.

## 10. Report

Make the smallest coherent change. Preserve unrelated user changes. Do not
commit. Summarise files changed, the collision matrix as *verified*, validation
output, and every host-specific limitation honestly — which hosts get only the
instruction tier, what capability they therefore lack, and that Devin has no
graft adapter.
