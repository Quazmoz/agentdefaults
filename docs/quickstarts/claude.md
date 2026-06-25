# Claude Quickstart

## Purpose

Show how to use AgentDefaults with Claude-oriented repository instructions.

## Files

```text
CLAUDE.md
AGENTS.md
INDEX.md
```

## Use

1. Start with `CLAUDE.md`.
2. Read `AGENTS.md` for shared repository rules.
3. Select only the task-relevant canonical agent and skills.

## Starter Prompt

```text
Use CLAUDE.md and AGENTS.md as the instruction layer. For this task, use the token economy stack and return a compact result with validation status.
```

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```
