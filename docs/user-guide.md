# User Guide

## Purpose

Help users choose the right AgentDefaults entrypoint, stack, and validation path.

## Entrypoints

- Generic repo-aware coding agent: `AGENTS.md`
- Claude: `CLAUDE.md`
- Gemini: `GEMINI.md`
- Cursor: `.cursor/rules/agentdefaults.mdc`
- Windsurf: `.windsurfrules`
- GitHub Copilot custom agents: `.github/agents/*.agent.md`
- Palmier Pro MCP video editing: `docs/quickstarts/palmierpro-mcp.md`
- Google Play growth / ASO: `docs/quickstarts/google-play-growth.md`
- App-market research (browser): `docs/quickstarts/app-market-research.md`
- Wear OS development or release: `WEAROS_DEVELOPMENT_INDEX.md`, `WEAROS_INDEX.md`
- US-to-Europe travel prep: `TRAVEL_INDEX.md`
- Chat or local model: copy files from `agents/`, `skills/`, and `prompts/`

## Goals

- Edit videos through Palmier Pro MCP: `docs/quickstarts/palmierpro-mcp.md`
- Analyze all Palmier project video media and assemble the main YouTube story: `prompts/palmierpro/story-assembly-from-project-media.md`
- Create a 9:16 YouTube Short from long-form Palmier content: `prompts/palmierpro/youtube-short-from-long-form.md`
- Run a Palmier first-pass edit: `prompts/palmierpro/full-edit-pass.md`
- Clean Palmier timeline transcripts: `prompts/palmierpro/transcript-cleanup-pass.md`
- Create Palmier short-form cutdowns: `prompts/palmierpro/short-form-social-cutdown.md`
- Optimize a Google Play listing and app growth: `agents/google-play-growth-optimizer-agent.md`
- Build or fix a Wear OS app: `agents/wearos-app-developer.md`
- Prepare a Wear OS app for Play release: `agents/android-wearos-release-engineer.md`
- Plan a US-to-Europe trip: `agents/us-europe-travel-advisor.md`
- Reduce verbose answers: `agents/token-efficient-response-agent.md` and `skills/token-output-budgeting.md`
- Manage token budgets: `agents/token-economy-orchestrator.md`
- Build a terse coding agent: `agents/terse-technical-coding-agent.md`
- Benchmark token savings: `prompts/token-efficiency/common-task-benchmark.md`
- Compare models: `prompts/token-efficiency/compare-models.md`
- Compress prompts or memory files: `skills/prompt-and-memory-compression.md`
- Add a reusable default: `docs/patterns/`

## Recommended Palmier Pro MCP Stack

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

## Recommended Token-Efficiency Stack

```text
AGENTS.md
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```
