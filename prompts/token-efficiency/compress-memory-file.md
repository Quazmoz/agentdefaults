# Compress Memory or Instruction File Prompt

## Purpose

Use this prompt to compress project memory, agent instructions, and reusable prompt files so every future agent session starts with fewer input tokens.

## Prompt

```text
You are compressing a reusable agent memory/instruction file for lower recurring input-token cost.

Goal:
Reduce tokens while preserving behavior, safety, and exact technical details.

Source file:
<paste file or provide path>

Target runtime/model:
<optional>

Hard rules:
- Preserve exact code blocks.
- Preserve exact commands, flags, file paths, URLs, environment variables, API names, version numbers, placeholders, output schemas, and citation/file-reference requirements.
- Preserve safety rules and destructive-action warnings.
- Preserve project-specific facts that affect future work.
- Remove repeated rationale, generic background, duplicate examples, filler, and overlapping rules.
- Do not compress by making instructions vague.
- Do not use novelty/persona speech.

Process:
1. Identify behavior-critical rules.
2. Identify exact strings that must not change.
3. Merge duplicate instructions.
4. Convert long prose into compact directives.
5. Keep examples only when they define output shape or prevent mistakes.
6. Estimate savings using exact tokenizer if available; otherwise use ceil(characters / 4) and mark approximate.

Return:

# Compressed File

```text
<compressed content>
```

# Compression Report

- Estimated original tokens: <count>
- Estimated compressed tokens: <count>
- Estimated savings: <pct>
- Preserved exactly:
  - <item>
- Removed/merged:
  - <item>
- Human review needed:
  - <item or none>
```

## Expected Output

A compressed file and a short report that makes the reduction auditable.

## Quality Bar

- At least 25% shorter when the original has repetition
- No loss of safety or behavior-critical constraints
- Exact technical strings remain intact
- Readable by small and large models
