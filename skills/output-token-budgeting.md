# Output Token Budgeting Skill

## Purpose

Use this skill to force an agent to choose an explicit response budget before generating output, then satisfy the user's request inside that budget without losing correctness, safety, validation, or important uncertainty.

This skill is the professional, model-agnostic equivalent of aggressive terse-mode behavior. It works with any model because it relies on response contracts, pruning rules, and measurable output constraints instead of model-specific features.

## When To Use

Use this skill for:

- Coding agents that over-explain every tool call.
- Review agents that produce long reports when only blockers matter.
- Support or DevOps agents that should answer directly.
- Multi-agent pipelines where every extra token compounds downstream.
- High-volume API workflows with cost or latency constraints.
- Any task where the user asks for fewer tokens, less verbosity, concise mode, compact mode, or terse output.

Do not use this skill to compress legal, medical, safety-critical, or compliance-sensitive guidance below the level needed for safe use.

## Inputs Needed

- Task type: `answer`, `decision`, `plan`, `code-change`, `review`, `debug`, `handoff`, or `benchmark`.
- Audience: `beginner`, `technical`, `expert`, or `agent`.
- Required content: files, commands, validation, citations, risks, assumptions, links, or artifacts.
- Target mode: `normal`, `compact`, `tight`, or `ledger`.
- Optional hard cap: word count, bullet count, or token count.

## Instructions

### 1. Pick the Lowest Sufficient Mode

| Mode | Default Cap | Use When |
|------|-------------|----------|
| `normal` | No strict cap | User asks for teaching/deep dive |
| `compact` | 100-300 words | Default for technical work |
| `tight` | 40-120 words | Iterative coding/status/review |
| `ledger` | 5-12 lines | Agent handoff, CI, repeated updates |

If a hard cap conflicts with safety or accuracy, exceed it only enough to preserve required content.

### 2. Use the Right Contract

#### Answer

```markdown
<answer>. <main reason>. <only caveat if material>.
```

#### Decision

```markdown
Pick: <option>.
Why: <1-3 reasons>.
Avoid: <option> unless <condition>.
```

#### Completed Work

```markdown
Done — <result>.
Changed: `<path>`, `<path>`.
Validation: <pass/fail/not run>.
Risk: <only if material>.
```

#### Review

```markdown
Top findings:
1. <issue> — <impact>. Fix: <action>.
2. <issue> — <impact>. Fix: <action>.
Next: <single action>.
```

#### Handoff

```markdown
Goal: <goal>
State: <state>
Context: <minimal facts>
Next: <steps>
Guardrails: <do-not list>
```

### 3. Apply the Cut List

Remove:

- Filler greetings and acknowledgements.
- Prompt restatement.
- Generic background.
- Tool/process narration.
- Repeated caveats.
- Low-value transitions.
- Overly broad option lists.
- Unrequested theory.
- Repeating code that already exists in a file/diff.

Keep:

- The answer.
- Relevant file paths.
- Commands and validation status.
- Material risks and assumptions.
- User constraints.
- Required citations or source references.
- Refusal/safety text when needed.

### 4. Prefer Dense Technical Syntax

Use:

```text
Root cause: Service selector misses Deployment label `app=api`.
```

Instead of:

```text
The most likely reason this is happening is that Kubernetes Services rely on label selectors to identify which Pods should receive traffic, and your labels appear not to match.
```

### 5. End Without Bloat

Do not add generic offers, summaries, or motivational closing lines. End after the useful action, validation, or result.

## Measurement

Track:

- `baseline_output_tokens`
- `compressed_output_tokens`
- `output_savings_percent`
- `task_success`
- `critical_omissions`
- `user_followup_needed`

Formula:

```text
output_savings_percent = ((baseline_output_tokens - compressed_output_tokens) / baseline_output_tokens) * 100
```

Target: reduce output tokens by at least 30% for normal technical tasks with no critical omissions.

## Expected Output

A response in the selected contract, not a discussion of the contract.

## Quality Bar

A successful application of this skill:

- Starts with the useful result.
- Fits the selected budget unless safety/accuracy requires expansion.
- Does not omit validation or material risk.
- Avoids process narration.
- Reduces output tokens measurably.

## Copy-Paste Skill Prompt

```text
Apply output token budgeting. Choose the lowest sufficient mode: normal, compact, tight, or ledger. Use a fixed output contract for the task. Remove filler, prompt restatement, generic background, process narration, repeated caveats, unrequested theory, and equivalent options. Preserve the answer, files, commands, validation status, material risks, assumptions, user constraints, citations, and safety requirements. End when the useful content is complete.
```
