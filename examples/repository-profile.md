# Repository Profile Example

## Purpose

Show how to use a thin repository wrapper that points back to canonical files.

## Files To Use

```text
.github/copilot-instructions.md
.github/agents/token-efficiency-benchmark.agent.md
agents/token-economy-orchestrator.md
skills/token-efficiency-measurement.md
```

## Prompt

```text
Use the repository instructions and token-efficiency benchmark profile. Keep canonical behavior in agents, skills, and prompts. Return measurements, quality scores, caveats, and recommended changes.
```

## Expected Output

```text
Result: pass/fail
Measurements: token savings and quality delta
Caveats: what was estimated or not verified
Changes: files changed or none
```
