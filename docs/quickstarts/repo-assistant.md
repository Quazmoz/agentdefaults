# Repository Assistant Quickstart

## Purpose

Show how to use AgentDefaults with repository-level assistant instructions and profile wrappers.

## Files

```text
.github/copilot-instructions.md
.github/agents/token-economy-orchestrator.agent.md
.github/agents/terse-technical-coding.agent.md
.github/agents/token-efficiency-benchmark.agent.md
```

## Use

1. Commit the wrapper files to the default branch.
2. Refresh the assistant UI.
3. Select the profile that matches the task.
4. Keep canonical behavior in `agents/`, `skills/`, and `prompts/`.

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```
