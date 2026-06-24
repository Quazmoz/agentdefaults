# Context Budgeting and Pruning Skill

## Purpose

Use this skill to reduce input/context token usage by selecting, summarizing, and pruning context before an agent answers or edits code.

This skill is model-agnostic and works for chat agents, coding agents, MCP workflows, repo-review agents, and local models with smaller context windows.

## When To Use

Use when:

- A task may require many files, logs, docs, or tool results
- The model is approaching context limits
- A repo review is becoming noisy
- The agent is repeatedly reading the same context
- You want smaller prompts without losing key facts
- You need a compact handoff to another model or session

Do not use to remove required citations, exact errors, security details, or user constraints.

## Inputs Needed

- Task goal
- Available context sources
- Known relevant files/logs/docs
- Required evidence or citations
- Output format requested by the user
- Current context budget, if known

## Instructions

### 1. Define the Context Goal

Before loading context, write a one-line goal internally or explicitly when useful:

```text
Need enough context to <decision/change/review>, not to understand the entire repo.
```

### 2. Rank Context Sources

Use this priority order for engineering tasks:

1. User-provided error, requirement, or diff
2. Directly referenced file/path/function
3. Adjacent tests/usages
4. Package/build/config files
5. README/architecture docs
6. Recent changelog or issue context
7. Broad repo search
8. Generated/vendor/lock/build files only when directly relevant

### 3. Use a Context Ledger

Maintain a compact ledger while working:

```markdown
Context ledger:
- Goal: <task>
- Known: <facts>
- Open question: <only blockers>
- Relevant files: `<path>`, `<path>`
- Do not need: <excluded context>
```

Do not print the ledger unless it helps the user or becomes a handoff.

### 4. Prune Aggressively

Remove or avoid:

- Duplicate logs
- Repeated stack frames
- Generated artifacts
- Full dependency trees
- Unrelated docs
- Large code blocks when line-level snippets are enough
- Prior messages that are superseded by a newer summary

Keep:

- Exact failing command
- Exact error message
- Relevant file paths
- User constraints
- Security/safety boundaries
- Decisions already made
- Validation results

### 5. Summarize Long Inputs

When an input is large, compress it into:

```markdown
Source: <file/log/doc>
Relevant facts:
- <fact>
- <fact>
Needed later:
- <path/error/constraint>
Discarded:
- <why remaining content not needed>
```

### 6. Handoff Before Context Overflow

When the session is long, produce:

```markdown
Goal: <goal>
Done:
- <done>
Current state:
- <fact>
Relevant files:
- `<path>` — <why>
Next:
- <step>
Constraints:
- <guardrail>
Validation:
- <run/not run>
```

## Expected Output

This skill usually shapes internal behavior. When asked to output the pruning result, return a compact context plan or handoff.

## Quality Bar

A successful context-pruning pass:

- Reduces loaded context by at least 30% compared with broad inspection
- Keeps all facts required for correctness
- Avoids repeated reads
- Keeps exact technical identifiers intact
- Makes follow-up work possible from the compact summary

## Common Failure Modes

Avoid:

- Summarizing away exact error strings
- Dropping a user constraint because it seems minor
- Reading the whole repo before forming a hypothesis
- Omitting citations/evidence when required
- Treating generated files as source of truth without checking source files

## Copy-Paste Skill Prompt

```text
Apply context budgeting. Load only the smallest context needed for the task. Prioritize user-provided requirements/errors, direct files, adjacent tests/usages, config, and docs before broad search. Avoid generated/vendor/build outputs unless directly relevant.

Maintain a compact context ledger: goal, known facts, open blockers, relevant files, excluded context. Summarize large inputs into relevant facts and exact identifiers. Preserve user constraints, exact errors, file paths, safety boundaries, and validation results. Prune duplicates and superseded context.

If context gets long, produce a handoff with goal, done, current state, relevant files, next steps, constraints, and validation status.
```
