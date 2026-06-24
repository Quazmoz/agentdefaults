# Token Output Budgeting Skill

## Purpose

Use this skill to control output verbosity with explicit budgets, response modes, and final cut passes.

This is for reducing completion/output tokens while preserving technical precision, safety, citations, and validation.

## When To Use

Use for:

- Technical Q&A
- Coding work summaries
- Debugging help
- PR/repo reviews
- DevOps runbooks
- Agent handoffs
- Prompt generation
- Support workflows where concise answers are preferred

Do not use to shorten legal, safety-critical, medical, compliance, or beginner-teaching explanations below what accuracy requires.

## Inputs Needed

- Task type
- User expertise level, if known
- Required output format
- Hard budget, if supplied
- Required evidence/citations/files
- Validation status

## Instructions

### 1. Select Output Mode

| Mode | Default Budget | Shape |
|------|----------------|-------|
| Micro | 25-75 words | Direct answer only |
| Compact | 75-200 words | Answer + key bullets |
| Work Summary | 100-250 words | Done + changed + validate |
| Review | 3-7 findings | Ranked issue list |
| Handoff | 100-250 words | Goal + state + next |
| Deep | No fixed budget | Structured, still no filler |

### 2. Use the Right Template

#### Direct Answer

```markdown
<answer>. Best move: <action>. Reason: <one concise reason>.
```

#### Decision

```markdown
Pick <option>.

Why:
- <reason>
- <reason>

Avoid <other option> unless <condition>.
```

#### Review

```markdown
Top findings:
1. **<issue>** — <impact>. Fix: <action>.
2. **<issue>** — <impact>. Fix: <action>.
3. **<issue>** — <impact>. Fix: <action>.
```

#### Completed Work

````markdown
Done — <result>.

Changed:
- `<path>` — <change>

Validate:
```bash
<command>
```
````

#### Prompt

````markdown
```text
<copy-paste prompt>
```
````

### 3. Apply the Final Cut Pass

Before answering, remove:

- Greetings and filler
- Repetition
- Meta-commentary about the response
- Generic background
- Obvious explanations for expert users
- Low-priority alternatives
- “Let me know if” closers
- Tables with only 2-3 rows unless useful

Keep:

- Final answer
- Required caveats
- Exact commands/paths/errors
- Citations/file references
- Validation status
- Safety warnings
- User constraints

### 4. Preserve Precision

Do not shorten:

- Code identifiers
- CLI flags
- Error strings
- API names
- File paths
- Version numbers
- Security warnings
- Citation/source references

### 5. Use Compression Operators

Use these structures:

- `Cause → Fix → Check`
- `Issue → Impact → Fix`
- `Path — change`
- `Goal / State / Next`
- `Pick / Why / Avoid`
- `Done / Changed / Validate`

## Expected Output

A response that is materially shorter than a default assistant response and still complete enough to act on.

## Quality Bar

- First sentence is useful
- No filler
- No repeated caveats
- No unnecessary background
- Exact technical identifiers preserved
- Validation/citations retained when required
- Uses the smallest response mode that fits the task

## Measurement Target

For common technical tasks, this skill should reduce output tokens by:

- 25-40% for already concise models
- 40-70% for verbose default assistants
- 10-25% for tasks requiring citations, safety caveats, or detailed validation

The goal is not maximum compression. The goal is maximum useful density.

## Copy-Paste Skill Prompt

```text
Apply token output budgeting. Pick the lowest sufficient output mode: micro, compact, work summary, review, handoff, or deep. Start with the answer/result. Use compressed structures like Cause → Fix → Check, Issue → Impact → Fix, Path — change, or Done → Changed → Validate.

Remove filler, repetition, generic background, obvious explanations, low-priority alternatives, and closing offers. Preserve exact commands, paths, errors, code identifiers, version numbers, citations, validation status, user constraints, uncertainty, and safety warnings.

Do not optimize for the fewest possible words. Optimize for the fewest words that still let the user act correctly.
```
