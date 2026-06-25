# Token Efficiency Measurement Skill

## Purpose

Use this skill to measure whether a token-efficiency agent, skill, or prompt actually improves common task performance without degrading quality.

It supports any model, provider, tokenizer, IDE agent, or local LLM. It intentionally separates token reduction from answer quality.

## When To Use

Use when:

- Adding a terse-output agent or skill
- Comparing baseline vs compressed prompts
- Evaluating different models with the same task set
- Measuring output-token savings for coding/review/debug tasks
- Checking whether compression harms accuracy, safety, or usefulness
- Building regression tests for agent defaults

## Inputs Needed

- Baseline prompt or agent behavior
- Candidate token-efficient prompt/agent/skill
- Shared task set
- Model/provider/runtime used
- Tokenizer or token-count method
- Quality rubric
- Whether tool calls are allowed

## Measurement Principles

Measure four things separately:

```text
Input tokens      Prompt/context size
Output tokens     Assistant-visible response size
Tool tokens       Tool calls/results injected into context, if measurable
Quality           Human/rubric score for correctness and usefulness
```

Do not claim improvement from output savings alone if quality drops materially.

## Token Counting Methods

Pick the most accurate method available and always record which one you used:

1. Provider usage metadata from API/tool logs (most accurate).
2. Native tokenizer for the exact model.
3. Compatible tokenizer from the same model family.
4. Generic tokenizer when the family is unknown.
5. Approximation `ceil(characters / 4)` for English-heavy text (least accurate).

Label any result that uses methods 4-5 as `approx` and avoid over-precise percentages.

## Benchmark Procedure

### 1. Freeze Test Conditions

Keep constant:

- Model
- Temperature/settings
- Tool availability
- Task text
- Starting context
- Time limit, if any
- Required output format

### 2. Run Baseline

Use the normal/default prompt or agent.

Record:

```markdown
Task: <name>
Input tokens: <count>
Output tokens: <count>
Tool calls: <count>
Tool/result tokens: <count or n/a>
Quality score: <1-5>
Notes: <issues>
```

### 3. Run Candidate

Use the token-efficient prompt/agent/skill with the same task and settings.

Record the same fields.

### 4. Score Quality

Use this rubric:

| Score | Meaning |
|-------|---------|
| 5 | Correct, complete, actionable, no material omissions |
| 4 | Correct with minor omissions or style issues |
| 3 | Usable but missing relevant details or validation |
| 2 | Partially wrong, unsafe, or hard to act on |
| 1 | Wrong, fabricated, unsafe, or fails the task |

Candidate passes only if:

```text
quality_score >= baseline_quality_score - 0.5
```

For safety/security/production tasks, candidate must match or exceed baseline quality.

### 5. Calculate Savings

```text
output_saved_pct = (baseline_output_tokens - candidate_output_tokens) / baseline_output_tokens * 100
input_saved_pct  = (baseline_input_tokens  - candidate_input_tokens)  / baseline_input_tokens  * 100
net_saved_pct    = (baseline_total_tokens  - candidate_total_tokens)  / baseline_total_tokens  * 100
```

If using approximate token counts:

```text
estimated_tokens = ceil(characters / 4)
```

Mark estimates as approximate.

### 6. Report Result

```markdown
Result: <pass/fail>

Savings:
- Input: <pct>
- Output: <pct>
- Net: <pct>

Quality:
- Baseline: <score>
- Candidate: <score>

Decision: <adopt / revise / reject>
Main reason: <short reason>
```

## Common Task Set

Use a mix of common agent workloads:

1. Explain a React render bug
2. Debug auth token expiry logic
3. Review a PR for security issues
4. Summarize a repo audit
5. Draft a focused implementation plan
6. Fix a Dockerfile or CI failure
7. Explain rebase vs merge for an experienced developer
8. Create a compact handoff after a long task
9. Compress a project memory file
10. Write release-blocker findings from logs

## Pass Criteria

A token-efficiency prompt is production-worthy when:

- Average output reduction ≥ 30%
- Net token reduction ≥ 20% when input/tool tokens are included
- No safety-critical quality drop
- Average quality drop ≤ 0.5 points
- No increased hallucination rate
- Required citations/validation preserved
- Users can still act on the answer without follow-up

## Failure Criteria

Reject or revise if:

- It omits important risks
- It hides uncertainty
- It removes citations or validation
- It produces terse but ambiguous output
- It changes technical meaning
- It performs worse on small/local models
- It requires a model-specific hidden behavior to work

## Expected Output

A compact benchmark report with savings, quality, and adoption decision.

## Copy-Paste Skill Prompt

```text
Measure token-efficiency impact for this agent/prompt/skill. Compare baseline vs candidate under the same model, settings, tools, task text, and context.

For each task, record input tokens, output tokens, tool calls, tool/result tokens if available, the counting method used, quality score from 1-5, and notes. Prefer provider usage metadata, then a native or compatible tokenizer; if none is available, estimate tokens as ceil(characters / 4) and mark approximate.

Calculate input_saved_pct, output_saved_pct, and net_saved_pct. Score quality separately; candidate passes only if quality is no more than 0.5 points below baseline, and safety/production tasks must match or exceed baseline quality.

Return a compact report: pass/fail, savings, baseline quality, candidate quality, adopt/revise/reject decision, and the main reason.
```
