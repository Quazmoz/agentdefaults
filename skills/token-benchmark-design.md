# Token Benchmark Design Skill

## Purpose

Use this skill to measure whether token-efficient agents, skills, prompts, or instruction stacks actually reduce token consumption without harming task quality.

The benchmark is model-agnostic: it can use provider usage metadata, native tokenizers, compatible tokenizers, or labeled approximations.

## When To Use

Use this skill when:

- Adding a concise or compressed agent profile.
- Comparing verbose vs compact prompt stacks.
- Testing one model against another on common tasks.
- Evaluating context reduction in RAG, memory, MCP, or coding-agent workflows.
- Estimating cost savings for API usage.
- Deciding whether a compression policy is safe enough to make default.

Do not use token savings as the only success metric. A shorter failed answer is worse than a longer correct answer.

## Inputs Needed

- Baseline prompt stack.
- Compressed prompt stack.
- Model/provider(s), if known.
- Task suite.
- Scoring rubric.
- Token counting method.
- Quality gate thresholds.

## Benchmark Design

### 1. Use Paired Tasks

Run the same task twice:

1. `baseline`: normal/current instructions.
2. `compressed`: token-efficient instructions.

Keep the user prompt, files, tools, model, temperature, and available context as identical as possible.

### 2. Measure Both Input and Output

Record:

```text
run_id=
model=
mode=<baseline|compressed>
task_id=
input_tokens=
output_tokens=
total_tokens=
latency_seconds=
estimated_cost=
turn_count=
task_success=<pass|partial|fail>
critical_omissions=
notes=
```

### 3. Use a Quality Gate

A compressed run passes only if:

- Task success is equal or better than baseline, or still acceptable.
- No required safety/citation/validation detail is missing.
- Critical omissions are `0`.
- The user would not need extra follow-up to recover missing essentials.

Recommended default gate:

```text
total_token_savings >= 30%
critical_omissions == 0
task_success in [pass, partial]
```

### 4. Include Common Task Types

At minimum include:

- Direct technical Q&A.
- Code review.
- Debugging from an error/log.
- Repo change summary.
- Implementation plan.
- Agent handoff.
- Prompt rewrite/compression.
- RAG/retrieval answer with citations.

### 5. Normalize Results

Calculate:

```text
input_savings_percent = ((baseline_input_tokens - compressed_input_tokens) / baseline_input_tokens) * 100
output_savings_percent = ((baseline_output_tokens - compressed_output_tokens) / baseline_output_tokens) * 100
total_savings_percent = ((baseline_total_tokens - compressed_total_tokens) / baseline_total_tokens) * 100
```

When using approximations, label results `approx` and avoid over-precision.

### 6. Report With Decisions

Avoid huge benchmark reports. Output:

```markdown
Result: <ship|iterate|reject>

Savings:
- Input: <x%>
- Output: <y%>
- Total: <z%>

Quality:
- Pass: <n>/<n>
- Critical omissions: <n>
- Regressions: <short list>

Decision:
- <what to make default or change>
```

## Token Counting Methods

Use in this priority order:

1. Provider usage fields from API/tool logs.
2. Native tokenizer for the exact model.
3. Compatible tokenizer family.
4. Generic tokenizer if the model family is unknown.
5. Approximation: `chars / 4` for English-heavy text.

Always record `counting_method`.

## Example Benchmark Matrix

| Task ID | Task | Quality Signal |
|---------|------|----------------|
| `qa-001` | Answer a technical tradeoff question | Decision and caveat correct |
| `review-001` | Find top issues in a code snippet | Valid findings, ranked properly |
| `debug-001` | Diagnose stack trace | Correct root cause/fix/check |
| `repo-001` | Summarize code changes | Changed files and validation preserved |
| `plan-001` | Produce implementation plan | Steps complete, not bloated |
| `handoff-001` | Compress agent handoff | Next agent can continue |
| `prompt-001` | Rewrite verbose prompt | Shorter, still executable |
| `rag-001` | Answer from retrieved docs | Citations preserved |

## Expected Output

A benchmark plan, result table, or decision summary that can be reused across model providers.

## Copy-Paste Skill Prompt

```text
Design a token-efficiency benchmark. Compare baseline vs compressed prompt stacks on paired tasks. Keep model, prompt, context, tools, and temperature as identical as possible. Measure input_tokens, output_tokens, total_tokens, latency_seconds, estimated_cost, turn_count, task_success, critical_omissions, and counting_method. Use provider usage metadata when available; otherwise native tokenizer, compatible tokenizer, or clearly labeled chars/4 approximation. Compression passes only if it saves tokens without critical omissions or unacceptable quality regressions. Report ship/iterate/reject with savings and regressions.
```

## Quality Bar

A good benchmark:

- Uses paired tasks.
- Measures input and output tokens separately.
- Includes quality gates.
- Works across models.
- Captures cost/latency when available.
- Produces a decision, not just numbers.
