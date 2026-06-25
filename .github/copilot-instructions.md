# Copilot Instructions for AgentDefaults

## Purpose

This repository is a reusable library of AI agent defaults. GitHub Copilot should help maintain the library and should use the existing defaults as source material for custom agents, skills, prompts, and integration wrappers.

## Important Files

- `AGENTS.md` — generic agent instructions for broad compatibility.
- `CLAUDE.md` — Claude-oriented entrypoint.
- `GEMINI.md` — Gemini-oriented entrypoint.
- `INDEX.md` — fastest discovery and stack selection.
- `README.md` — human-facing docs and test workflow.
- `agents/` — canonical agent profiles.
- `skills/` — canonical reusable skills.
- `prompts/` — canonical task and benchmark prompts.
- `.github/agents/` — Copilot custom-agent wrappers.
- `docs/tool-integration-guide.md` — cross-tool usage instructions.

## Repository Rules

1. Keep canonical reusable content in `agents/`, `skills/`, and `prompts/`.
2. Keep Copilot-specific files in `.github/` as thin wrappers that reference or summarize canonical content.
3. Keep Claude-specific behavior in `CLAUDE.md` only when needed.
4. Keep Gemini-specific behavior in `GEMINI.md` only when needed.
5. Update `README.md` and `INDEX.md` when adding, renaming, or removing defaults.
6. Preserve exact paths, code fences, copy-paste prompts, and output schemas.
7. Do not invent benchmark results. Use `skills/token-efficiency-measurement.md` and `prompts/token-efficiency/common-task-benchmark.md`.
8. Do not add secrets, private URLs, credentials, or environment-specific tokens.

## Preferred Response Style

- Be concise and implementation-focused.
- Use `Done / Changed / Validate` for completed repo work.
- Use `Issue → Impact → Fix` for reviews.
- Use `Cause → Fix → Check` for debugging.
- Mark unverified commands or tests as `Not verified`.

## Default Token-Efficiency Stack

Use this stack when the user asks to reduce token usage or make agents more efficient:

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

## Validation

For Markdown-only changes, use the testing commands in `README.md` under `Testing the Defaults`.
