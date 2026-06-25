# Coding Example

## Purpose

Show a compact coding stack.

## Files To Use

```text
AGENTS.md
agents/terse-technical-coding-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

## Prompt

```text
Use AGENTS.md as the base instruction layer. Use the terse coding stack. Make the smallest focused change and return Done / Changed / Validate.
```

## Expected Output Shape

```text
Done: result
Changed:
- path — change
Validate:
- command or status
```
