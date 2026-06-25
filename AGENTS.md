# AgentDefaults Generic Agent Instructions

## Purpose

This file is the broad, tool-agnostic entrypoint for AI coding agents that read repository-level instruction files.

Use this repository as a reusable library of agents, skills, prompts, and instruction packs. Do not treat every file as mandatory context. Select only the smallest useful stack for the user's task.

## Repository Map

- `INDEX.md` — fastest selection guide for available agents, skills, prompts, and stacks.
- `README.md` — human-facing overview, usage, and testing workflow.
- `agents/` — complete reusable agent profiles.
- `skills/` — composable task/behavior modules.
- `prompts/` — copy-paste task prompts and benchmark prompts.
- `.github/agents/` — GitHub Copilot custom-agent wrappers.
- `.github/copilot-instructions.md` — GitHub Copilot repository-wide instructions.
- `CLAUDE.md` — Claude-oriented entrypoint.
- `GEMINI.md` — Gemini-oriented entrypoint.
- `docs/tool-integration-guide.md` — integration guide by tool.
- `docs/quickstarts/palmierpro-mcp.md` — Palmier Pro MCP video-editing quickstart.

## Default Operating Rules

1. Start with `INDEX.md` for stack selection.
2. Load one domain agent or behavior agent first.
3. Add only the skills needed for the task.
4. Prefer token-efficient context selection; do not ingest the whole repo unless the user asks for a full audit.
5. Preserve safety, correctness, citations, exact paths, exact commands, output schemas, and validation status.
6. Do not invent files, commands, tests, or benchmark results.
7. When editing this repo, update `README.md` and `INDEX.md` whenever discoverability changes.
8. Keep all defaults model-agnostic unless a file is intentionally tool-specific.

## Recommended Stacks

### Palmier Pro MCP video editing

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
prompts/palmierpro/story-assembly-from-project-media.md
prompts/palmierpro/youtube-short-from-long-form.md
```

### General token-efficient assistant

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Terse coding assistant

```text
agents/terse-technical-coding-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Prompt or memory compression

```text
skills/prompt-and-memory-compression.md
skills/token-efficiency-measurement.md
prompts/token-efficiency/compress-memory-file.md
prompts/token-efficiency/agent-retrofit.md
```

### Benchmark token improvements

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
```

## Response Style

- Use compact, direct engineering language.
- Start with the result, answer, or recommendation.
- Use `Done / Changed / Validate` for completed work.
- Use `Issue → Impact → Fix` for reviews.
- Use `Cause → Fix → Check` for debugging.
- Mark unverified work as `Not verified`.

## Validation

For Markdown-only changes, run the validator described in the README "Validation" section:

```bash
python3 scripts/validate-agentdefaults.py
```

For token-efficiency claims, use:

```text
prompts/token-efficiency/common-task-benchmark.md
skills/token-efficiency-measurement.md
```
