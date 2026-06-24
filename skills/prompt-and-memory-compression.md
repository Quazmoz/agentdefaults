# Prompt and Memory Compression Skill

## Purpose

Use this skill to rewrite reusable prompts, memory files, agent instructions, and project notes into smaller model-agnostic context while preserving behavior.

This reduces recurring input tokens, not just one-off output tokens.

## When To Use

Use for:

- `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, Codex/Gemini/Cline/Windsurf instruction files
- Agent system prompts
- Project memory files
- Repo-specific operating notes
- Long task prompts that are reused often
- MCP tool descriptions or skill descriptions that are too verbose

Do not use for legal text, policy text, license text, compliance requirements, or source material where exact wording matters unless the user explicitly approves a paraphrase.

## Inputs Needed

- Source prompt/memory/instruction text
- Target agent/runtime, if relevant
- Must-preserve sections
- Maximum size target, if any
- Whether exact wording must be preserved for any blocks

## Preservation Rules

Always preserve exactly:

- Code blocks
- Commands
- File paths
- URLs
- Environment variables
- API names
- Version numbers
- Secrets placeholders
- Safety rules
- Destructive-action warnings
- Required output schemas
- Citation/file-reference requirements

Do not preserve:

- Repeated goals
- Long rationale
- Generic background
- Duplicated examples
- Overlapping rules
- Polite filler
- Vendor marketing language

## Compression Process

### 1. Segment

Classify the source into:

- Mission / role
- Scope
- Hard rules
- Workflow
- Output format
- Examples
- Safety boundaries
- Project-specific facts

### 2. Deduplicate

Merge repeated instructions. Keep the strictest version when rules overlap.

### 3. Normalize

Convert prose into compact directives:

```text
Do X. Avoid Y. Preserve Z. Output A.
```

### 4. Preserve Schemas

Keep exact output shapes where agents depend on them.

### 5. Add Change Notes

When returning the compressed version, include a tiny summary:

```markdown
Saved: ~<percent>% by removing repetition, rationale, and duplicate examples.
Preserved: commands, paths, schemas, safety rules.
```

## Output Format

````markdown
# Compressed Version

```text
<compressed prompt or memory>
```

# Compression Notes

- Estimated reduction: <percent or token estimate>
- Preserved exactly: <items>
- Removed/merged: <items>
- Risk: <only if something may need human review>
````

## Estimating Savings

Use the best available tokenizer when possible. If no tokenizer exists, estimate with:

```text
estimated_tokens = ceil(characters / 4)
```

Report estimates as approximate unless measured with the target model tokenizer.

## Quality Bar

A good compressed prompt:

- Is shorter by at least 25%
- Preserves behavior-critical rules
- Keeps exact technical identifiers
- Removes duplicate rationale
- Still works without the original text
- Is readable by small and large models
- Avoids novelty/persona wording unless explicitly requested

## Common Failure Modes

Avoid:

- Compressing so hard that small models miss intent
- Removing examples that define output shape
- Losing safety constraints
- Rewriting commands incorrectly
- Changing file paths or flags
- Replacing precise rules with vague words like “be good”

## Copy-Paste Skill Prompt

```text
Compress this prompt/memory/instruction file for recurring agent context. Preserve behavior while reducing tokens.

Segment into mission, scope, hard rules, workflow, output format, examples, safety boundaries, and project facts. Deduplicate overlapping rules. Convert long prose to compact directives. Preserve exact code blocks, commands, file paths, URLs, environment variables, API names, version numbers, placeholders, safety rules, destructive-action warnings, required schemas, and citation/file-reference requirements.

Return the compressed version plus notes: estimated reduction, preserved exactly, removed/merged, and any risk requiring human review. If no tokenizer is available, estimate tokens as ceil(characters / 4) and mark the result approximate.
```
