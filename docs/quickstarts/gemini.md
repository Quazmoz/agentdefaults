# Gemini Quickstart

## Purpose

Show how to use AgentDefaults with Gemini-oriented repository instructions.

## Files

```text
GEMINI.md
AGENTS.md
INDEX.md
```

## Use

1. Start with `GEMINI.md`.
2. Read `AGENTS.md` for shared repository rules.
3. Select only the task-relevant canonical agent and skills.

## Starter Prompt

```text
Use GEMINI.md and AGENTS.md as the instruction layer. For this task, use the token economy stack and return a compact result with validation status.
```

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```
