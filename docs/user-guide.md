# User Guide

## Purpose

Help users choose the right AgentDefaults entrypoint, stack, and validation path.

## Choose Your Entrypoint

| Tool style | Start with | Add |
|---|---|---|
| Generic repo-aware coding agent | `AGENTS.md` | selected canonical agents and skills |
| Claude | `CLAUDE.md` | `AGENTS.md`, then selected stack |
| Gemini | `GEMINI.md` | `AGENTS.md`, then selected stack |
| Cursor | `.cursor/rules/agentdefaults.mdc` | `AGENTS.md`, then selected stack |
| Windsurf | `.windsurfrules` | `AGENTS.md`, then selected stack |
| GitHub repo assistant | `.github/copilot-instructions.md` | optional profile from `.github/agents/` |
| Chat or local model | `agents/`, `skills/`, `prompts/` | copy the smallest useful stack |

## Choose Your Goal

| Goal | Use |
|---|---|
| Reduce verbose answers | `agents/token-efficient-response-agent.md` and `skills/token-output-budgeting.md` |
| Manage token budgets | `agents/token-economy-orchestrator.md` |
| Build a terse coding agent | `agents/terse-technical-coding-agent.md` |
| Benchmark token savings | `prompts/token-efficiency/common-task-benchmark.md` |
| Compare models | `prompts/token-efficiency/compare-models.md` |
| Compress prompts or memory files | `skills/prompt-and-memory-compression.md` |
| Add a reusable default | `templates/` |

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
