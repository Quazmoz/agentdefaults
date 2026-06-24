# Lossless Technical Compression Skill

## Purpose

Use this skill to compress technical text while preserving all decision-relevant meaning. It is useful for shrinking explanations, reviews, bug reports, tool outputs, implementation notes, and agent handoffs.

"Lossless" here means no critical information is removed. It does not mean every word is preserved.

## When To Use

Use this skill for:

- Turning long findings into ranked action items.
- Compressing tool outputs into final responses.
- Rewriting verbose prompts into compact prompts.
- Preparing handoffs between agents.
- Shrinking meeting notes, issue reports, code-review notes, or debug logs.
- Reducing output tokens in high-volume workflows.

Do not use this skill when the user needs exact legal wording, exact quotes, policy text, contracts, or verbatim source preservation.

## Inputs Needed

- Source text to compress.
- Target audience.
- Required output shape.
- Must-keep facts: paths, commands, errors, dates, versions, risks, citations, constraints.
- Compression level: `light`, `medium`, `heavy`, or `ledger`.

## Compression Levels

| Level | Use For | Target |
|-------|---------|--------|
| `light` | User-facing summary | Remove filler/repetition |
| `medium` | Technical final answer | Keep only actionable substance |
| `heavy` | Agent handoff/status | Dense bullets/key-values |
| `ledger` | Machine/CI/state passing | Minimal structured fields |

## Instructions

### 1. Extract Critical Facts

Before rewriting, identify:

- Decision or answer.
- Actions taken or requested.
- File paths, commands, APIs, variables, versions, dates.
- Error messages and symptoms.
- Validation status.
- Risks, assumptions, and blockers.
- Citations/source IDs when required.
- Explicit user constraints.

### 2. Remove Non-Critical Text

Cut:

- Warm-up phrases.
- Meta-commentary.
- Repeated caveats.
- Duplicated facts.
- Generic background.
- Long examples when one pattern is enough.
- Adverbs/adjectives that do not change meaning.
- Unnecessary transition sentences.

### 3. Replace Prose With Dense Structures

Use these forms:

```text
path — change/reason
issue → impact → fix
cause → fix → check
goal | state | next | risk
```

### 4. Preserve Traceability

When compressing evidence-based or repo-based work:

- Keep source IDs, citations, file paths, or line references.
- Do not merge two facts if their sources differ and traceability matters.
- Mark unverified claims as `not verified`.

### 5. Run a Critical-Omission Check

Before final output, verify:

- Could the next agent/user act from this alone?
- Are any safety constraints gone?
- Are validation results still clear?
- Are assumptions still visible?
- Are file paths and commands still exact?

## Expected Output

```markdown
Compressed:
<compressed text>

Kept:
- <critical fact category>

Dropped:
- <waste category>

Risk:
- <only if compression may lose nuance>
```

For normal use, output only the compressed text unless the user asks for audit detail.

## Measurement

Track:

```text
source_tokens=
compressed_tokens=
savings_percent=
critical_omissions=
readability=<good|acceptable|poor>
```

Approximation is acceptable when exact token counts are unavailable, but label it.

## Copy-Paste Skill Prompt

```text
Apply lossless technical compression. Extract the decision, actions, paths, commands, errors, versions, validation status, risks, assumptions, citations/source IDs, and user constraints. Remove filler, repeated caveats, generic background, duplicated facts, meta-commentary, and unnecessary examples. Replace prose with dense structures such as path — change, issue → impact → fix, cause → fix → check, and goal | state | next | risk. Preserve traceability and mark unverified claims. Do not remove safety constraints or validation status.
```

## Quality Bar

A compressed result is good when:

- A technical user can act immediately.
- Critical facts are preserved.
- The response is much shorter.
- No material risk, validation detail, or hard constraint disappeared.
- It works without relying on a specific model provider.
