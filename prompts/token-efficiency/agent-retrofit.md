# Token Efficiency Agent Retrofit Prompt

## Purpose

Use this prompt to retrofit an existing agent, skill, instruction file, or project memory with token-efficiency behavior while preserving its original domain expertise and safety constraints.

## When To Use

Use when:

- An existing agent is too verbose
- A project `AGENTS.md` / `CLAUDE.md` / custom system prompt is too large
- You want concise outputs without changing the agent's core role
- You need the same agent to work across multiple models
- You want a reviewable before/after prompt update

## Prompt

```text
You are an expert AI prompt engineer and agent-systems engineer.

Task:
Retrofit the provided agent/prompt/skill/instruction file with token-efficiency behavior while preserving the original role, domain expertise, safety rules, output requirements, and tool-use constraints.

Do not copy novelty/persona wording from other token-compression projects. Use professional, model-agnostic instructions suitable for any hosted or local model.

Inputs:
- Existing prompt/agent/instruction:
<paste content>
- Target runtime/model, if any:
<runtime>
- Hard constraints:
<constraints>
- Desired verbosity default:
<micro / compact / work summary / dense review / deep>

Requirements:
1. Preserve all behavior-critical instructions.
2. Preserve exact commands, paths, URLs, schemas, API names, error strings, and safety boundaries.
3. Add explicit rules for:
   - context budgeting
   - tool-call economy
   - output budgeting
   - final cut pass
   - compact work summaries
   - compact handoff summaries
   - honesty about unverified work
4. Remove duplicate rules, filler, repeated rationale, and generic background.
5. Keep the result readable by smaller models.
6. Avoid vendor-specific assumptions unless the original prompt requires them.
7. Do not weaken safety, citation, validation, or uncertainty requirements.

Return:

# Retrofitted Prompt

```text
<complete updated prompt>
```

# Change Notes

- Token-efficiency additions:
  - <item>
- Preserved exactly:
  - <item>
- Removed/merged:
  - <item>
- Estimated reduction:
  - <approx percent or n/a>
- Risks / human review needed:
  - <item or none>

# Suggested Benchmark

Run `prompts/token-efficiency/common-task-benchmark.md` with the original as baseline and this retrofit as candidate.
```

## Expected Output

A complete, copy-paste-ready replacement prompt plus concise change notes.

## Quality Bar

A successful retrofit:

- Reduces recurring prompt tokens where possible
- Adds output/token discipline
- Preserves the original agent's identity and guardrails
- Does not make the prompt brittle or model-specific
- Includes a benchmark recommendation
