# CLI Quickstart

## Purpose

Show how to use AgentDefaults with a local repo-aware coding CLI.

## Basic Use

Start the coding CLI from the repository root so it can read `AGENTS.md`.

```bash
python3 scripts/validate-agentdefaults.py
```

## Task-Specific Profile

For benchmark work, explicitly reference:

```text
.github/agents/token-efficiency-benchmark.agent.md
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
```

## Starter Prompt

```text
Use AGENTS.md as the base instruction file. For this task, also use .github/agents/token-efficiency-benchmark.agent.md and the token-efficiency measurement prompt stack. Run a local mini benchmark with estimated tokens and return pass/fail, measurements, quality scores, and recommended repo changes.
```
