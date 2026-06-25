# Gemini Instructions for AgentDefaults

## Purpose

Use this file as the Gemini-oriented entrypoint for `Quazmoz/agentdefaults`. It keeps Gemini usage aligned with the shared AgentDefaults library while delegating common behavior to `AGENTS.md`.

## Role

You are working in `Quazmoz/agentdefaults`, a reusable prompt and agent-defaults repository.

For cross-tool behavior, also follow `AGENTS.md`.

## Read Order

1. `AGENTS.md`
2. `INDEX.md`
3. `README.md`
4. Only the task-relevant files under `agents/`, `skills/`, `prompts/`, `.github/agents/`, or `docs/`

## Gemini Working Rules

- Keep responses concise and task-focused.
- Prefer model-agnostic Markdown instructions over vendor-specific phrasing.
- Preserve exact paths, file names, output schemas, and fenced prompt blocks.
- Treat `agents/`, `skills/`, and `prompts/` as canonical library content.
- Treat `GEMINI.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.github/agents/*.agent.md` as integration wrappers.
- Update `INDEX.md` and `README.md` when adding new reusable defaults.
- Do not claim benchmark results unless the benchmark was actually run.

## Useful Stacks

### Palmier Pro MCP video editing

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
```

### Token-efficient assistant

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Token benchmark assistant

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
```

### Prompt/memory compression assistant

```text
skills/prompt-and-memory-compression.md
prompts/token-efficiency/compress-memory-file.md
prompts/token-efficiency/agent-retrofit.md
```

## Output Preference

Use compact structures:

- `Done / Changed / Validate`
- `Issue → Impact → Fix`
- `Cause → Fix → Check`
- `Goal / State / Next`

Mark unverified work clearly.
