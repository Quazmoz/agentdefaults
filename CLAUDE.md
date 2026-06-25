# Claude Instructions for AgentDefaults

## Role

You are working in `Quazmoz/agentdefaults`, a reusable library of AI agents, skills, prompts, and tool-specific wrappers.

Use this file as the Claude-oriented entrypoint. For cross-agent rules, also follow `AGENTS.md`.

## First Files To Read

1. `AGENTS.md` — tool-agnostic operating rules.
2. `INDEX.md` — fastest stack selection.
3. `README.md` — overview and testing workflow.
4. Task-specific files from `agents/`, `skills/`, or `prompts/` only as needed.

Do not load the entire repository by default.

## Claude-Specific Working Rules

- Prefer concise, implementation-focused responses.
- Before editing, identify the smallest relevant file set.
- Preserve exact Markdown paths, headings, copy-paste prompt blocks, and fenced code blocks.
- When adding a default, update `INDEX.md` and `README.md` if discoverability changes.
- When adding a tool-specific wrapper, keep the canonical reusable logic in `agents/`, `skills`, or `prompts` and keep the wrapper thin.
- For prompt-library work, avoid tool lock-in unless the file is intentionally named for a specific tool.
- Do not claim token savings were measured unless a benchmark was actually run.

## Default Stack For Token-Efficient Work

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

## Default Stack For Coding-Agent Wrappers

```text
AGENTS.md
.github/copilot-instructions.md
.github/agents/*.agent.md
CLAUDE.md
GEMINI.md
docs/tool-integration-guide.md
```

## Final Response Format

For repo changes, use:

```text
Done — <summary>.

Changed:
- <path> — <change>

Validate:
<command>

Not verified: <only if true>.
```

Keep final summaries compact and concrete.
