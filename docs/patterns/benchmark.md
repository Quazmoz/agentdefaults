# Benchmark Pattern

## Purpose

Provide a reusable structure for benchmark artifact files.

## When To Use

Use when documenting measured or estimated agent behavior.

## Inputs Needed

- Date
- Scope
- Candidate stack
- Counting method
- Task text
- Baseline result
- Candidate result
- Quality scores
- Caveats

## Instructions

1. Separate measured facts from interpretation.
2. Label exact counts versus estimates.
3. Include quality scoring.
4. Preserve caveats.
5. Avoid public benchmark claims unless the run is controlled.

## Expected Output

A benchmark artifact under `docs/benchmarks/`.

## Quality Bar

- Honest scope.
- Reproducible enough for repo-internal use.
- Clear pass/fail decision.
- No overclaiming.
