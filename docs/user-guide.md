# User Guide

## Purpose

Help users choose the right AgentDefaults entrypoint, stack, and validation path.

## Entrypoints

- Generic repo-aware coding agent: `AGENTS.md`
- Claude: `CLAUDE.md`
- Gemini: `GEMINI.md`
- Cursor: `.cursor/rules/agentdefaults.mdc`
- Windsurf: `.windsurfrules`
- Chat or local model: copy files from `agents/`, `skills/`, and `prompts/`

## Goals

- Reduce verbose answers: `agents/token-efficient-response-agent.md` and `skills/token-output-budgeting.md`
- Manage token budgets: `agents/token-economy-orchestrator.md`
- Build a terse coding agent: `agents/terse-technical-coding-agent.md`
- Benchmark token savings: `prompts/token-efficiency/common-task-benchmark.md`
- Compare models: `prompts/token-efficiency/compare-models.md`
- Compress prompts or memory files: `skills/prompt-and-memory-compression.md`
- Add a reusable default: `docs/patterns/`

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
