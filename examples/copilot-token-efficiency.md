# GitHub Copilot Token-Efficiency Example

## Purpose

Give a team a ready-to-deploy set of `.github` files and habits that lower GitHub Copilot spend without losing quality. Drop these into any repo. Canonical guidance lives in [`skills/copilot-token-efficiency.md`](../skills/copilot-token-efficiency.md).

## Files To Use

```text
skills/copilot-token-efficiency.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficiency-measurement.md
```

## The 6 Rules Of Thumb

Teach these first — they move the bill more than any config:

1. **Match model to task.** Cheap/fast model for routine work; reasoning model only for hard problems. Prefer auto-selection.
2. **Inline completions are free** — lean on them; reserve chat/edit/agent for where they add value.
3. **Scope context** — attach specific files with `#file`/`#selection`, not `@workspace`, for narrow tasks.
4. **One chat per task** — long threads re-bill stale context on every request.
5. **Right mode** — completions → ask → edit → agent, cheapest sufficient one. Agent loops cost the most.
6. **Be concise by default** — standing instructions trim output tokens on every response.

## Deploy: `.github/copilot-instructions.md`

Repo-wide standing instructions. Applies to every chat/edit/agent request.

```markdown
# Copilot Instructions

## Response style
- Lead with the answer, change, or recommendation. No preamble or filler.
- Prefer diffs/patches over full-file rewrites. Show only changed regions.
- Use `Done / Changed / Validate` for completed work and `Cause → Fix → Check` for debugging.
- Be terse for an expert audience; expand only when asked.

## Context
- Edit only the files relevant to the task; do not restate unchanged code.
- Ask before pulling in broad workspace context for a narrow change.

## Accuracy
- Preserve exact paths, commands, errors, and identifiers.
- Mark unverified work as `Not verified`. Do not invent results, files, or APIs.
```

## Deploy: `.github/instructions/tests.instructions.md`

Path-specific rules via an `applyTo` glob. Multiple matching files stack (union), so keep each small and targeted.

```markdown
---
applyTo: "**/*.test.*"
---

- Follow the existing test framework and file conventions; do not introduce a new runner.
- Generate only the requested cases plus obvious edge cases. Do not restate the code under test.
- One concise assertion message per failure path.
```

## Deploy: `.github/prompts/review.prompt.md`

Reusable prompt for a recurring task. Invoke it instead of re-typing a long prompt (and re-paying for those input tokens) every time.

```markdown
---
mode: ask
---

Review the selected diff. Return at most 5 findings, ranked, as:
`Issue → Impact → Fix`. Skip style nits already enforced by linters.
End with a one-line `Verdict: ship / revise`.
```

## Prove It

Don't claim savings — measure them with [`skills/token-efficiency-measurement.md`](../skills/token-efficiency-measurement.md):

- Record AI Credit / premium-request usage in GitHub billing before and after.
- A-B one real task: verbose baseline vs the config above, same model. Score quality 1–5 separately; adopt only if quality holds.

## Expected Outcome

```text
- Fewer high-tier-model requests for routine work
- Shorter chat threads (less re-billed context)
- Lower output tokens per response
- Same or better task quality
```

Verify current model prices and plan allowances at GitHub's billing docs before quoting numbers to your team.
