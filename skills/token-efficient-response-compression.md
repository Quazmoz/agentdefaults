# Token-Efficient Response Compression Skill

## Purpose

Use this skill when an agent needs to turn verbose reasoning, findings, tool results, or implementation details into a concise, high-signal response.

This skill supports `agents/token-efficient-response-agent.md` and can be layered onto any technical or research agent.

## When To Use

Use this skill for:

- Compressing long tool results into a short final answer
- Turning a repo review into prioritized findings
- Summarizing completed code changes
- Producing compact handoffs for another agent
- Answering expert users without unnecessary background
- Reducing token usage in iterative agent workflows

Do not use this skill to hide uncertainty, omit required citations, skip safety warnings, or remove validation steps that materially matter.

## Inputs Needed

The agent should know:

- User's requested output style, if specified
- Task type: answer, recommendation, code change, review, debug, prompt, or handoff
- Required citations/file references, if any
- Important risks, constraints, or validation results
- Whether work was completed, partial, or analysis-only

## Instructions

### 1. Classify the Response

Choose one response type:

| Type | Use For | Output Shape |
|------|---------|--------------|
| Direct answer | Simple Q&A | 1-3 sentences |
| Decision | Choosing between options | Pick + 2-3 reasons |
| Work summary | Completed repo/tool work | Done + changed files + validation |
| Review | Audits/findings | Top findings ranked |
| Debug | Error diagnosis | Cause + fix + check |
| Prompt | User asks for prompt | Copy-paste prompt only or brief note |
| Handoff | Passing context to another agent | Goal + context + constraints + next steps |

### 2. Keep the First Sentence Useful

The first sentence should answer the user's question or state what was done.

Good:

```text
Done — added the Flux validation skill and indexed it in the README.
```

Bad:

```text
I took a careful look at the repository and considered how best to structure this.
```

### 3. Preserve Required Content

Never compress away:

- The answer or recommendation
- Files changed
- Commit/artifact link or SHA, if applicable
- Validation commands or test status
- Material risks
- Rollback notes for risky changes
- Required citations or file references
- Explicit uncertainty or unverified status

### 4. Remove Waste

Cut:

- Generic introductions
- Repetition
- Over-explaining obvious concepts
- Multiple equivalent options when one is best
- Long tables unless they add clarity
- Long code blocks when a command or focused patch is enough
- Meta-commentary about being concise
- Apologies unless a real error occurred

### 5. Use Compression Templates

#### Completed Work

````markdown
Done — <summary>.

Changed:
- `<file>` — <change>
- `<file>` — <change>

Commit: `<sha>`

Validate:
```bash
<command>
```
````

#### Review

```markdown
Top findings:

1. **<issue>** — <impact>. Fix: <action>.
2. **<issue>** — <impact>. Fix: <action>.
3. **<issue>** — <impact>. Fix: <action>.

Next: <single best action>.
```

#### Debug

````markdown
Likely cause: <cause>.

Fix:
```bash
<command>
```

Check:
```bash
<command>
```
````

#### Prompt

````markdown
```text
<copy-paste-ready prompt>
```
````

#### Handoff

```markdown
Goal: <goal>

Context:
- <constraint>
- <constraint>

Do:
- <step>
- <step>

Do not:
- <guardrail>
```

### 6. Preserve Traceability

When compressing evidence-based or repo-based work:

- Keep source IDs, citations, file paths, or line references that let the reader trace a claim.
- Do not merge two facts into one if their sources differ and traceability matters.
- Mark unverified claims as `not verified` rather than dropping the caveat to save space.

### 7. Apply a Final Cut Pass

Before sending, ask:

- Can the first sentence stand alone?
- Are there more than three main points?
- Is any sentence generic?
- Did I preserve all required safety, validation, and citation details?
- Did I avoid claiming unverified work was done?

## Expected Output

A compact response that gives the user what they need to act immediately.

## Quality Bar

A successful compressed response is:

- Correct
- Short
- Specific
- Actionable
- Honest about uncertainty
- Free of filler
- Still safe and verifiable

## Notes

This skill is a behavior layer. Pair it with domain skills such as `skills/kubernetes-gitops-change-management.md` or `skills/comet-authenticated-research.md`.
