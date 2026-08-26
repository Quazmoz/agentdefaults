# Token Economy Quickstart

## Purpose

Use the Token Economy stack to reduce prompt, context, tool-result, and output waste without sacrificing correctness, safety, validation, or required evidence.

Canonical stack:

```text
agents/token-economy-orchestrator.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

Add [`../../skills/copilot-token-efficiency.md`](../../skills/copilot-token-efficiency.md) only for GitHub Copilot-specific optimization.

## What This Stack Is

Token Economy is primarily a **behavior/orchestration layer**. It changes how much context is loaded, how tools are used, and how results are communicated.

It normally does **not** replace a domain owner.

Example:

```text
agents/principal-ai-engineer.md
+ skills/production-ai-engineering.md
+ token-economy behavior where useful
```

Correctness, safety, user requirements, citations, and verification outrank token reduction.

## Choose a Budget Mode

Use the lowest sufficient mode defined by the canonical agent:

| Mode | Typical use |
|---|---|
| `Micro` | tiny status/answer/correction |
| `Compact` | most technical Q&A and recommendations |
| `Work Summary` | completed engineering/tool work |
| `Review` | ranked findings |
| `Handoff` | resumable continuation state |
| `Deep` | user explicitly needs depth or safety requires it |

A user-supplied word/bullet budget takes precedence unless it would remove required safety or validation information.

## Fast Invocation

For general engineering:

```text
Use the appropriate domain agent for correctness. Apply the Token Economy stack in Compact mode: load only evidence needed for the task, avoid repeated tool reads, report deltas instead of reprinting files, and keep the final answer concise without omitting material risks or validation status.
```

For a review:

```text
Apply Token Economy in Review mode. Return only the highest-impact evidence-backed findings, each as Issue -> Impact -> Fix, followed by the single best next action. Preserve exact paths, error strings, and verification gaps.
```

For a continuation handoff:

```text
Apply Token Economy in Handoff mode. Preserve goal, current state, key constraints/evidence, unresolved risks, next action, and explicit do-not rules. Do not copy raw logs or prior narration unless required.
```

## Context Economy

Before loading more context:

1. Start with the task, repository instructions, indexes/manifests, changed files, failing logs, and directly relevant config.
2. Expand only when evidence requires it.
3. Avoid generated/vendor/build artifacts and giant logs unless material.
4. Summarize a long finding once and reference the summary instead of repeatedly reloading/reprinting it.
5. Keep raw evidence separate from compact handoff state in long workflows.

Do not prune away contracts, schemas, migration state, security boundaries, or failure evidence merely because they are large.

## Tool Economy

- Batch related reads where possible.
- Do not repeatedly fetch unchanged files.
- Prefer targeted search after repository shape is known.
- Use the smallest meaningful validation surface after a change, then broaden when release/task criteria require it.
- Do not narrate every low-level tool call.
- Do not claim a check ran when it did not.

## Output Economy

Prefer:

```text
answer first
ranked findings
exact paths/commands
changed-file deltas
one recommendation when evidence supports it
verified vs unverified separation
```

Avoid:

```text
generic introductions
repeating the user's request
multiple weak alternatives
full-file dumps when a patch/path summary is enough
repeated caveats
long tool-call narration
```

## When Not to Compress Further

Stop compressing when another reduction would hide or weaken:

- a material correctness issue;
- a security/safety boundary;
- required citations/provenance;
- an approval requirement;
- an unresolved blocker;
- exact technical identifiers needed to act;
- validation status;
- uncertainty that changes the decision.

## Benchmarking

Do not assume a shorter answer is better.

Use:

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
docs/benchmarks/
```

Compare at least:

```text
task success / quality
exact token counts when available (or clearly labeled estimate)
latency/cost where relevant
missing constraints or regressions
model/provider/version and prompt/config version
```

A token saving that lowers task quality is not a successful optimization.

## GitHub Copilot

For Copilot-specific cost/context behavior, load:

```text
skills/copilot-token-efficiency.md
```

Keep generic token-economy rules separate from vendor-specific billing/model-selection assumptions so changing platform behavior does not contaminate the canonical cross-model stack.

## Validation

After changing Token Economy repository artifacts, run:

```bash
python3 scripts/validate-agentdefaults.py
```

For benchmark claims, also run the benchmark workflow you are citing. Structural repository validation does not verify claimed token savings.