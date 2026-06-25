# Tool Integration Guide

## Purpose

This guide explains how to use AgentDefaults with common AI coding tools without duplicating or fragmenting the canonical prompt library.

AgentDefaults should work in two modes:

1. **Prompt library mode** — copy files from `agents/`, `skills/`, or `prompts/` into any chat/model/tool.
2. **Native wrapper mode** — use tool-specific files such as `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.github/agents/*.agent.md`, or an MCP quickstart.

## Canonical Content vs Wrappers

Canonical reusable content lives here:

```text
agents/
skills/
prompts/
```

Tool-specific wrappers live here:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.github/copilot-instructions.md
.github/agents/*.agent.md
.cursor/rules/agentdefaults.mdc
.windsurfrules
docs/quickstarts/*.md
```

Rule: update canonical content first, then keep wrappers thin and discoverable.

## GitHub Copilot

Use these files:

```text
.github/copilot-instructions.md
.github/agents/token-economy-orchestrator.agent.md
.github/agents/terse-technical-coding.agent.md
.github/agents/token-efficiency-benchmark.agent.md
.github/agents/palmierpro-video-editor.agent.md
```

Recommended uses:

- Repository-wide guidance: `.github/copilot-instructions.md`
- Selectable/custom agent profiles: `.github/agents/*.agent.md`
- General prompt/library maintenance: `AGENTS.md`, `INDEX.md`, `README.md`

After adding or changing Copilot agent profiles:

1. Commit to the default branch.
2. Refresh the Copilot/GitHub agent UI.
3. Confirm the agent description appears.
4. Run the README smoke test.

## Claude / Claude Code

Use these files:

```text
CLAUDE.md
AGENTS.md
INDEX.md
README.md
```

Recommended read order:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `INDEX.md`
4. Only task-relevant canonical files

For reusable token-efficiency work, start with:

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

For Palmier Pro work through Claude Code, start with:

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
```

## Gemini / Gemini CLI

Use these files:

```text
GEMINI.md
AGENTS.md
INDEX.md
README.md
```

Recommended behavior:

- Treat `GEMINI.md` as the tool entrypoint.
- Treat `AGENTS.md` as the interoperable base layer.
- Pull canonical behavior from `agents/`, `skills/`, and `prompts/` only as needed.

## Generic Agents / Codex-Style Agents

Use:

```text
AGENTS.md
INDEX.md
README.md
```

Best for:

- Codex-style repo agents
- Local model runners
- Agent frameworks
- Custom MCP/IDE agents
- Any tool that reads repository-level instructions

For Palmier Pro via Codex, connect MCP first, then use:

```text
docs/quickstarts/palmierpro-mcp.md
prompts/palmierpro/full-edit-pass.md
```

## Cursor

Use:

```text
.cursor/rules/agentdefaults.mdc
AGENTS.md
INDEX.md
```

The Cursor rule is intentionally thin. It points back to the canonical AgentDefaults files rather than duplicating the full library.

For Palmier Pro, use the app's `Help -> MCP Instructions -> Install in Cursor` flow when available, or use the manual MCP JSON from `docs/quickstarts/palmierpro-mcp.md`.

## Windsurf

Use:

```text
.windsurfrules
AGENTS.md
INDEX.md
```

The Windsurf wrapper should stay compact and focused on repository maintenance rules.

## Palmier Pro MCP

Use:

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
```

Best for:

- First-pass video edits
- Transcript cleanup
- Captioning
- Short-form cutdowns
- Existing b-roll placement
- Approved AI generation inside Palmier Pro
- Review exports

Rules:

- Palmier Pro must be open with a project loaded.
- The MCP client should connect to the local Palmier endpoint from the quickstart.
- Live Palmier tool output is the source of truth over static docs.
- Generation/upscale actions require explicit user approval.
- Final export should happen only when requested.

## Copy-Paste Usage For Any Model

For any chat model, paste this stack:

```text
Use AgentDefaults token economy stack:
- agents/token-economy-orchestrator.md
- agents/token-efficient-response-agent.md
- skills/context-budgeting-and-pruning.md
- skills/token-output-budgeting.md
- skills/token-efficient-response-compression.md

Task:
<your task>

Output budget:
<word limit or mode>
```

For any MCP-capable model connected to Palmier Pro, paste this stack:

```text
Use AgentDefaults Palmier Pro MCP stack:
- docs/quickstarts/palmierpro-mcp.md
- agents/palmierpro-mcp-video-editor-agent.md
- skills/palmierpro-mcp-setup-and-safety.md
- skills/palmierpro-timeline-editing.md
- skills/palmierpro-transcript-cuts-and-captions.md

Task:
<your video-editing task>
```

## Testing Tool Compatibility

Run the validator from the README "Validation" section:

```bash
python3 scripts/validate-agentdefaults.py
```

Minimum test:

1. Static file existence check.
2. Markdown structure check.
3. Markdown link/path check.
4. Agent smoke test.
5. Token-efficiency benchmark if claiming improvement.

## Maintenance Rules

- Do not let wrapper files drift from canonical files.
- Do not paste whole canonical files into every wrapper.
- Keep wrappers small enough that tools will reliably ingest them.
- Link to canonical files by exact path.
- Update `README.md` and `INDEX.md` when adding a new tool wrapper.
- Mark tool-specific behavior clearly.
