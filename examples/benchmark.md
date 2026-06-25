# Benchmark Example

## Purpose

Show how to run a small token-efficiency benchmark.

## Files To Use

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
```

## Prompt

```text
Run a baseline and candidate comparison with identical task text. Estimate tokens with ceil(characters / 4) unless exact usage is available. Score quality 1-5 and report savings, quality delta, caveats, and decision.
```

## Expected Output

```text
Result: pass/fail
Savings: percent
Quality: baseline -> candidate
Caveats: exact or estimated tokens
```
