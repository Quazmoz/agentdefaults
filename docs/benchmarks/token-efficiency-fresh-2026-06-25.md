# Token Efficiency Fresh Benchmark

## Purpose

Document a fresh third-pass benchmark of the AgentDefaults token-efficiency stack after adding validation micro-examples.

## Date

2026-06-25

## Scope

Fresh local IDE-agent benchmark using generated baseline and candidate outputs. This run used identical task text for baseline and candidate responses and estimated output tokens with `ceil(characters / 4)`.

This artifact is stronger than a source-only review, but it is still not a controlled public benchmark because exact provider token usage was not available.

## Candidate Stack

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

## Reference Files

```text
docs/benchmarks/token-efficiency-smoke-test.md
skills/token-output-budgeting.md
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
```

## Counting Method

Estimated tokens using:

```text
ceil(characters / 4)
```

Exact tokenizer/API usage data was not available for this run.

## Results

| Task | Baseline Tokens | Candidate Tokens | Output Savings | Baseline Quality | Candidate Quality | Notes |
|---|---:|---:|---:|---:|---:|---|
| React inline object prop | 133 | 88 | 33.8% | 5 | 5 | Candidate includes `useMemo` and `console.count` validation. |
| Auth token expiry | 107 | 74 | 30.8% | 5 | 5 | Candidate includes enforced `exp` rejection and replay check. |
| PR/security review | 129 | 88 | 31.8% | 5 | 5 | Candidate includes `gitleaks` validation. |
| CI/Docker blocker | 112 | 68 | 39.3% | 5 | 5 | Candidate includes `docker build -t app:test . && npm test`. |
| Repo-audit handoff | 104 | 61 | 41.3% | 5 | 5 | Candidate follows `Goal / State / Next`. |

## Aggregate Result

```text
Average output savings: 35.4%
Average quality delta:  0.0
Security quality drop:  none
Decision:               pass
```

## Comparison To Historical Smoke Test

```text
Historical smoke-test average output savings: 38.8%
Fresh benchmark average output savings:       35.4%
Difference:                                   -3.4 points
```

Interpretation: the fresh run remained above the 30% output-token reduction target while adding explicit validation checks. Savings were slightly lower than the historical smoke test, which is expected because validation micro-examples add small token cost.

## Validation Micro-Example Impact

The validation micro-examples helped preserve actionability and verification quality without making candidate answers too verbose.

Observed benefits:

- React task retained both `useMemo` and `console.count` validation.
- Security task retained a concrete `gitleaks` command.
- CI/Docker task retained a minimal build/test command.
- Handoff task retained a compact `Goal / State / Next` structure.

## Regressions

No material regressions found.

All tasks retained candidate quality score 5/5, and the security task had no quality drop.

## Caveats

- Token counts were estimated, not measured with provider tokenizer output.
- The benchmark ran in a local IDE-agent environment.
- Input tokens were treated as identical by design, so net savings track output savings.
- This result is suitable as repo-internal evidence, not a public benchmark claim.

## Next Validation

Run [`prompts/token-efficiency/compare-models.md`](../../prompts/token-efficiency/compare-models.md) across at least:

```text
- One frontier chat model
- One coding-specialized model
- One local or smaller model
```

For a stricter run, capture exact provider input/output token usage and record model names, model versions, temperature, tool policy, and full task text.
