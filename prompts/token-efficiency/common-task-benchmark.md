# Common Task Token Efficiency Benchmark Prompt

## Purpose

Use this prompt to compare a normal agent/prompt against a token-efficient candidate across common AI engineering and coding tasks.

This is model-agnostic. It works with hosted models, local LLMs, IDE agents, and chat agents. It can use exact tokenizer counts when available or approximate counts when not.

## When To Use

Use when:

- Testing a new concise agent instruction
- Comparing models for useful density
- Checking whether token reduction hurts answer quality
- Building before/after receipts for prompt changes
- Creating a repeatable benchmark for agent defaults

## Required Inputs

Provide:

```text
Baseline prompt/agent:
<paste baseline>

Candidate prompt/agent:
<paste candidate>

Model/runtime:
<model, provider, IDE agent, or local LLM>

Tokenizer/count method:
<exact tokenizer, API usage, logs, or approximate chars/4>

Tool policy:
<tools allowed or no tools>
```

## Benchmark Prompt

```text
You are evaluating token efficiency for an AI agent prompt.

Goal:
Compare a baseline prompt/agent against a candidate token-efficient prompt/agent on common technical tasks. Measure token savings and quality separately. Do not reward brevity if correctness, safety, validation, or actionability gets worse.

Rules:
- Use the same model/runtime/settings for baseline and candidate.
- Use the same task text for both runs.
- Use the same tool access for both runs.
- If exact token usage is unavailable, estimate tokens as ceil(characters / 4) and mark counts approximate.
- Score quality from 1-5:
  5 = correct, complete, actionable, no material omissions
  4 = correct with minor omissions/style issues
  3 = usable but missing relevant detail/validation
  2 = partially wrong, unsafe, or hard to act on
  1 = wrong, fabricated, unsafe, or fails the task
- Candidate passes only if average quality is no more than 0.5 below baseline.
- For security, production, or destructive-operation tasks, candidate quality must match or exceed baseline.

Task set:
1. Explain a React component re-render bug caused by inline object props.
2. Debug auth token expiry logic where expired tokens are sometimes accepted.
3. Review a small PR for security issues from a short diff.
4. Summarize release blockers from a noisy CI log excerpt.
5. Draft a focused implementation plan for adding a feature flag.
6. Fix a Docker multi-stage build that copies files from the wrong stage.
7. Explain git rebase vs merge to an experienced developer.
8. Create a compact handoff after a long repo-audit session.
9. Compress a project memory/instruction file while preserving behavior.
10. Diagnose a PostgreSQL connection pool exhaustion issue.

For each task, run baseline first, then candidate. Record:
- Task name
- Baseline input tokens
- Baseline output tokens
- Candidate input tokens
- Candidate output tokens
- Baseline quality score
- Candidate quality score
- Output savings %
- Net savings % if input tokens are available
- Material omissions or regressions

Calculations:
output_saved_pct = (baseline_output_tokens - candidate_output_tokens) / baseline_output_tokens * 100
input_saved_pct  = (baseline_input_tokens  - candidate_input_tokens)  / baseline_input_tokens  * 100
net_saved_pct    = (baseline_total_tokens  - candidate_total_tokens)  / baseline_total_tokens  * 100

Final report format:

Result: <pass/fail>

Summary:
- Avg output savings: <pct>
- Avg net savings: <pct or n/a>
- Avg baseline quality: <score>
- Avg candidate quality: <score>
- Decision: <adopt / revise / reject>

Top regressions:
1. <task> — <issue>
2. <task> — <issue>

Recommended changes:
- <specific prompt/agent adjustment>
- <specific prompt/agent adjustment>

Do not include full task outputs unless asked. Keep the report compact and evidence-based.
```

## Expected Output

A compact benchmark report showing whether the candidate prompt is worth adopting.

## Quality Bar

The benchmark is useful only if:

- Baseline and candidate are run under equal conditions
- Savings and quality are reported separately
- Approximate counts are labeled approximate
- Regressions are named specifically
- Adoption decision is justified by evidence
