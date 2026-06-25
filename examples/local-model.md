# Local Model Example

## Purpose

Show how to use AgentDefaults with a chat or local model that has no native repo instruction format.

## Files To Use

```text
AGENTS.md
agents/token-efficient-response-agent.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

## Prompt

```text
Use the following AgentDefaults files as your instruction stack: AGENTS.md, agents/token-efficient-response-agent.md, skills/token-output-budgeting.md, and skills/token-efficient-response-compression.md. Answer compactly while preserving exact technical identifiers and validation status.
```

## Expected Output

A concise, high-signal answer with no filler and no lost constraints.
