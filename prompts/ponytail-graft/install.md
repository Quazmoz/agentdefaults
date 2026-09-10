Set up Ponytail for this repository, alongside the existing graft integration.

Upstream: https://github.com/DietrichGebert/ponytail

## 0. Read upstream before editing anything

Shallow-clone Ponytail into a scratch directory (not into this repo) and read it.
Do not rely on guessed command names, file paths, or install verbs.

Read at minimum:
- `README.md` — the per-host Install sections, for exact command names
- `docs/agent-portability.md` — the adapter table; it states each host's tier
  (plugin-tier vs instruction-tier) and which files that host reads
- `scripts/check-rule-copies.js` — defines the *canonical* instruction body and
  the rule invariants that must survive verbatim
- `.github/copilot-instructions.md` and `AGENTS.md` — the actual adapter text

Delete the scratch clone when done.

## 1. Inventory this repo's existing agent configuration first

Read, and report what owns what:
- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`
- `.claude/` (settings.json, hooks, helpers, skills), `.codex/`, `.mcp.json`
- any existing graft configuration, lifecycle hooks, or generated `graft/` graph

Determine **which files graft claims**, from graft's own installed source rather
than by assumption — check its host registry
(`$(dirname $(readlink -f $(command -v graft)))/hosts/registry.js`) for the
`relPath` each host writes. As of graft 0.16.0: the `agents`/`hermes`/
`antigravity` hosts own `AGENTS.md`, `copilot` owns
`.github/copilot-instructions.md`, and the `claude` host owns
`.claude/settings.json` — **not** `CLAUDE.md`, which is therefore free to use.

## 2. Repository-local only

Make the setup repository-local wherever possible. Do not modify:
`~/.claude`, `~/.codex`, `~/.copilot`, global shell profiles, global package
configuration, or unrelated repositories.

Note that graft's own SessionStart hook may itself touch `~/.codex` — that is
graft's doing, not yours. Leave it alone, record global config mtimes before and
after your work, and prove in your report that you wrote nothing global.

## 3. Hosts to support, at the correct tier

- **Claude Code** — instruction tier via `CLAUDE.md` + `AGENTS.md`
- **Codex** — instruction tier via repo-root `AGENTS.md`
- **GitHub Copilot Chat** — `.github/copilot-instructions.md`
- **GitHub Copilot CLI** — same repo-local instructions

Add Codex-specific *repository* configuration only if the installed Codex
version actually supports it. Verify with `codex --help` / `codex plugin --help`:
as of `codex-cli` 0.139.0 there is **no repo-local config** — config loads from
`~/.codex/config.toml` plus `$CODEX_HOME/<name>.config.toml` profiles, and
`codex plugin add` writes to that user config and cache. If that is still true,
add no `.codex/` directory and say so.

## 4. Native plugin installs are user-global — document, never run

Ponytail's plugin tier (`/ponytail` levels, extra commands, lifecycle hooks)
installs into the user's home config for all their repos. Do not execute any of
them. Capture the exact commands from the README and document them as optional
and user-scoped. Note that the plugin tier needs `node` on the non-interactive
shell's PATH for its two lifecycle hooks.

## 5. Coexistence with graft — the load-bearing part

**Ponytail publishes no marker convention.** Its instruction-tier adapters are
whole-file copies that assume they own the file. Copying one over an
AGENTS.md that graft already owns would destroy the graft section. So:

- Append Ponytail inside its own fence, `<!-- ponytail:start -->` …
  `<!-- ponytail:end -->`, mirroring graft's convention. Document that this
  fence is *this repo's* convention and upstream tooling won't recognise it.
- Append **strictly after** graft's `<!-- graft:end -->`. Guard the append:
  assert the file's last line is that end marker and abort if not.
- Never merge the two sections, and never touch bytes inside graft's fence.
- **Keep lifecycle hooks separate.** Do not merge into graft's hooks in
  `.claude/settings.json`. Ponytail's hooks ship only with the user-global
  plugin, so at instruction tier there is no hook merge to perform at all — if
  you think you need one, re-check which tier you're installing.

Then **prove** coexistence empirically rather than trusting a code comment:
graft does a marker-fenced upsert (`dist/hosts/sections.js`), so import its real
`upsertSection`, run it against a *copy* of your modified file with a dummy
body, and confirm graft's region was replaced while the Ponytail fence survived
intact. Report the result.

## 6. Content rules

- Use Ponytail's canonical compact ruleset. Derive it the way upstream does
  (`AGENTS.md` minus its repo-self-referential closing line) and **assert
  programmatically** that it equals upstream's
  `.github/copilot-instructions.md` before using it.
- Copy it **verbatim** — do not abridge or summarise. `check-rule-copies.js`
  pins the "not lazy about…" carve-outs (trust-boundary validation, data loss,
  security, accessibility) as invariants; trimming the block silently deletes
  safeguards. Demoting the leading `#` heading to match the host file's
  structure is the only edit permitted.
- Keep the identical block in every instruction file, and verify they match.
- Add a short precedence paragraph: Ponytail governs *how much* code to write,
  never whether to keep a safeguard; repo-specific rules win; and point
  Ponytail's ladder rung 2 ("does it already exist in this codebase?") at graft
  as the way to answer it.
- Do not weaken security, validation, accessibility, error handling, or
  data-loss protection. Do not remove repository-specific workflows. Do not add
  dependencies, scripts, hooks, or abstractions. Do not change application
  source code.
- `CLAUDE.md`: add or update as a small bridge to `AGENTS.md` — a pointer, not
  a second copy of the rules.

## 7. Documentation

Add `docs/AGENT_TOOLING.md` only if the repo already has a docs location.
Before adding it, confirm no build/validation script globs `docs/*.md` (so a new
file can't change generated output or break a validator). Explain: files added
or changed; that the setup is repository-local; how graft and Ponytail coexist
(including the marker-fence diagram and why hooks stay separate); which native
commands are optional and user-scoped; per-host limitations; and how to update
or uninstall the block.

## 8. Validate, concretely

- Parse every changed JSON/TOML/YAML file; also re-parse the untouched agent
  config (`.claude/settings.json`, `.mcp.json`) to prove it still loads.
- `git diff --numstat` — a correct instruction-file change is **additions only**;
  any deletion means you clobbered someone's section.
- `git diff --check` for whitespace.
- Assert marker fences are balanced 1/1 in each instruction file, and that the
  Ponytail block is byte-identical across them.
- Run the repo's relevant lint/config checks — but **inspect the npm
  pre-scripts first**. If `prelint`/`pretest` runs a generator that rewrites
  tracked files, invoke the underlying tool directly (e.g. `npx tsc --noEmit`)
  so validation can't dirty unrelated generated output. Say which you ran and why.
- Verify graft still works: execute its hooks and statusline, and run a live
  graft query.
- Re-check the working tree at the end: only your intended files should appear.

## 9. Report

Make the smallest coherent change. Preserve unrelated user changes. Do not
commit. Summarise the files changed, the validation performed with its actual
output, and any host-specific limitation honestly — including which hosts get
only the instruction tier and what capability they therefore lack.
