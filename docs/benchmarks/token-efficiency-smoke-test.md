# Token Efficiency Smoke Test

## Purpose

Document the initial local IDE-agent smoke test for the AgentDefaults token-efficiency stack.

## Date

2026-06-25

## Scope

Local IDE agent smoke test using estimated token counts. This is an initial validation artifact, not a controlled multi-model benchmark.

## Candidate Stack

```text
AGENTS.md
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
```

## Counting Method

Estimated tokens using:

```text
ceil(characters / 4)
```

Exact tokenizer/API usage data was not available for this run.

## Results

| Task | Baseline Tokens | Candidate Tokens | Output Savings | Quality |
|---|---:|---:|---:|---:|
| React inline object prop | 162 | 67 | 58.6% | 5 → 5 |
| Auth token expiry logic | 130 | 85 | 34.6% | 5 → 5 |
| PR/security diff | 108 | 60 | 44.4% | 5 → 5 |
| CI/Docker failure excerpt | 93 | 65 | 30.1% | 5 → 5 |
| Compact repo-audit handoff | 95 | 70 | 26.3% | 5 → 5 |

## Aggregate Result

```text
Average output savings: 38.8%
Average quality delta:  0.0
Decision:               initial pass
```

## Regressions

No material regressions found in this smoke test.

Task 5 fell below 30% savings individually, but the average result passed the target threshold and quality did not drop.

## Caveats

- This was a local IDE-agent run.
- Token counts were estimated, not measured with model/provider tokenizer output.
- Baseline and candidate behavior may not be fully independent when run inside one IDE-agent session.
- This result should not be used as a public benchmark claim without a controlled multi-model run.

## Next Validation

Run [`prompts/token-efficiency/compare-models.md`](../../prompts/token-efficiency/compare-models.md) across at least:

```text
- One frontier chat model
- One coding-specialized model
- One local or smaller model
```

For a stricter benchmark, capture exact input/output token counts from provider usage logs or a tokenizer for each run.
