# Editor Quickstart

## Purpose

Show how to use AgentDefaults with editor rule files.

## Files

```text
.cursor/rules/agentdefaults.mdc
.windsurfrules
AGENTS.md
INDEX.md
```

## Use

1. Keep editor rule files thin.
2. Point back to `AGENTS.md`, `INDEX.md`, and selected canonical files.
3. Add only the agent and skills needed for the task.

## Starter Prompt

```text
Use the AgentDefaults editor rule and the token economy stack. Keep the result compact, exact, and validation-oriented.
```

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```
