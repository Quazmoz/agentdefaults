# Claude Code Project Integration

## Purpose

Explain the Claude-specific files under `.claude/`, especially the optional Graft status-line/hook integration that is separate from the canonical AgentDefaults instruction stack.

Claude's canonical repository routing remains:

```text
CLAUDE.md
  -> @AGENTS.md
  -> ENGINEERING_AGENTS_INDEX.md
  -> selected canonical agent/skills
```

The files in `.claude/` configure **Claude Code runtime behavior**. They do not replace `CLAUDE.md`, `AGENTS.md`, or canonical agents.

## Files

```text
.claude/settings.json
.claude/helpers/graft-hooks.cjs
.claude/helpers/graft-statusline.cjs
```

### `settings.json`

Configures:

- a Claude status line and subagent status line through `graft-statusline.cjs`;
- optional Graft hook dispatch for `SessionStart`, `UserPromptSubmit`, selected `PostToolUse` events, and `Stop`;
- a narrow Claude permission allowlist for Graft-related shell commands.

### Helper scripts

The helper scripts try to locate the installed `@nanonets/graft` Claude integration from known/local/global Node package locations and delegate to its `hooks.js` or `statusline.js` entrypoint.

If the Graft module cannot be resolved/imported, the helpers catch the failure and **no-op**. AgentDefaults does not install Graft through these files.

The Graft package owns the semantics of the delegated hook/status-line implementation; these helpers are adapters, not a copied implementation.

## Hook Routing

The current `.claude/settings.json` dispatches:

| Claude event | Adapter action |
|---|---|
| `SessionStart` | Graft `session-start` hook |
| `UserPromptSubmit` | Graft `prompt` hook |
| `PostToolUse` for `Write|Edit|MultiEdit` | Graft `post-edit` hook |
| `PostToolUse` for `Bash|mcp__graft__` | Graft `tool-savings` hook |
| `Stop` | Graft `stop` hook |

Do not infer behavior beyond what the installed Graft runtime actually implements.

## Permissions Are Not Authority

The Claude `permissions.allow` entries make selected commands available to the runtime. They are **not user approval** for consequential work.

A hook or allowed command cannot widen:

- the selected canonical agent's authority;
- repository/user instructions;
- production/deployment approval;
- destructive-action approval;
- credential or secret access.

## Failure and Portability Behavior

The helpers intentionally search several package locations because Node/npm installation layouts differ across local environments.

Operational implications:

- an unavailable Graft installation should degrade to no Graft status/hook behavior rather than break the agent task;
- Node/npm must exist for the helper commands themselves to run meaningfully;
- a hard-coded candidate path is only one lookup candidate, not the sole supported installation path;
- when debugging, verify the actually resolved Graft package/runtime instead of assuming a particular installation location.

## Debugging

When Claude routing is wrong, debug in this order:

```text
1. CLAUDE.md loaded?
2. @AGENTS.md import loaded?
3. selected canonical agent/skills correct?
4. Claude tool permissions correct?
5. .claude/settings.json hook configuration correct?
6. Graft package actually installed/resolvable?
```

Do not blame Graft hooks for canonical routing defects before checking the instruction stack.

## Editing Rules

- Shared AgentDefaults behavior belongs in canonical agents/skills, not `.claude/settings.json`.
- Claude-specific instruction routing belongs in `CLAUDE.md` / [`../docs/quickstarts/claude.md`](../docs/quickstarts/claude.md).
- Graft adapter behavior belongs here only when it is truly Claude/Graft-runtime-specific.
- Keep helper scripts small and fail-safe; do not copy an external package implementation into the repository.
- Never put secrets in `.claude/settings.json` or hook command lines.

## Validation

After AgentDefaults/Claude routing changes run:

```bash
python3 scripts/validate-agentdefaults.py
python3 scripts/validate-cross-tool-routing.py
```

Those validators do not prove an external Graft installation works. Verify the local Claude/Graft runtime separately when changing or troubleshooting that integration.