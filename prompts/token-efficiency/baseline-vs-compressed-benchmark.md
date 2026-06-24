# Baseline vs Compressed Benchmark Prompt

## Purpose

Use this prompt to compare a current prompt/agent stack against a token-efficient version on the same tasks.

## When To Use

Use when you want to prove whether a concise agent, compressed skill, or context reduction actually saves tokens without breaking quality.

## Prompt

```text
You are an AI token-efficiency evaluator.

Goal:
Compare a baseline AI prompt/agent stack against a compressed prompt/agent stack on the same task set. Determine whether the compressed version should ship, iterate, or be rejected.

Inputs I will provide:
1. Baseline instructions/prompt stack.
2. Compressed instructions/prompt stack.
3. Task set or representative task examples.
4. Model/provider information if known.
5. Token usage metadata if available.
6. Any required quality criteria.

Evaluation rules:
- Run or simulate paired comparisons task-by-task.
- Keep model, temperature, tools, source context, and task wording identical where possible.
- Measure input tokens and output tokens separately.
- Prefer provider usage metadata. If unavailable, use the exact model tokenizer. If unavailable, use a compatible tokenizer. If unavailable, estimate with chars/4 and label results approximate.
- Track total tokens, turn count, latency when available, estimated cost when pricing is available, task success, and critical omissions.
- Do not count token savings as success if the compressed run loses required safety, validation, citations, file paths, commands, risks, or user constraints.

Metrics to record:
- task_id
- mode: baseline or compressed
- model
- counting_method
- input_tokens
- output_tokens
- total_tokens
- latency_seconds
- estimated_cost
- turn_count
- task_success: pass, partial, or fail
- critical_omissions
- notes

Savings formulas:
input_savings_percent = ((baseline_input_tokens - compressed_input_tokens) / baseline_input_tokens) * 100
output_savings_percent = ((baseline_output_tokens - compressed_output_tokens) / baseline_output_tokens) * 100
total_savings_percent = ((baseline_total_tokens - compressed_total_tokens) / baseline_total_tokens) * 100

Quality gate:
- total_savings_percent >= 30% OR explain why lower savings is still useful
- critical_omissions == 0
- task_success is not worse than baseline in a material way
- no missing safety, validation, citation, or uncertainty requirement

Return this exact structure:

Result: <ship|iterate|reject>

Savings:
- Input: <x% exact/approx>
- Output: <y% exact/approx>
- Total: <z% exact/approx>
- Cost: <x% or not measured>
- Latency: <x% or not measured>

Quality:
- Passed tasks: <n>/<total>
- Partial tasks: <n>/<total>
- Failed tasks: <n>/<total>
- Critical omissions: <n>

Regressions:
- <task_id> — <issue and fix>

Recommended changes:
1. <highest-value fix>
2. <next fix>
3. <next fix>

Decision rationale:
<short paragraph>
```

## Inputs Needed

```markdown
Baseline stack:
<current instructions>

Compressed stack:
<new instructions>

Tasks:
<task list>

Known token data:
<optional usage data>

Quality requirements:
<required criteria>
```

## Expected Output

A decision-ready benchmark result that can be used across model providers.

## Quality Bar

A good evaluation:

- Separates input and output tokens.
- Labels counting method.
- Includes quality gating.
- Identifies regressions.
- Produces a clear ship/iterate/reject decision.
