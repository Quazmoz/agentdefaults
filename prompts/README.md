# Prompts

## Purpose

Explain how reusable prompts under `prompts/` fit into AgentDefaults and how to choose them without confusing task invocation with canonical agent behavior.

A prompt is a **repeatable request template**. It tells an already selected agent/runtime what task to perform, what evidence to inspect, and what output or acceptance criteria matter.

Canonical behavior belongs in [`../agents/`](../agents/) and [`../skills/`](../skills/). Prompts should reference or invoke those contracts rather than silently redefining them.

## Prompt Categories

| Directory | Use |
|---|---|
| [`planning/`](planning/) | Architecture, agent design, platform selection, trip planning and other plan-first work. |
| [`implementation/`](implementation/) | Concrete implementation, hardening, maintenance, documentation and engineering execution. |
| [`review/`](review/) | Independent challenge, release review, architecture challenge and bounded-completion review. |
| [`research/`](research/) | Evidence-gathering and research workflows. |
| [`orchestration/`](orchestration/) | Start/resume/reset/escalate commands for formal orchestration workflows. |
| [`token-efficiency/`](token-efficiency/) | Compression, benchmarking and model/token-efficiency tasks. |
| [`palmierpro/`](palmierpro/) | Palmier Pro MCP video-editing workflows. |

## How to Use a Prompt

Use this sequence:

```text
1. Select the owning agent.
2. Load the smallest relevant skills.
3. Choose a prompt that matches the task phase.
4. Fill repository/task-specific values.
5. Preserve explicit authority, non-goals and acceptance criteria.
6. Run target-system verification.
```

For structured/repeatable tasks, pair the prompt with the relevant schema/example rather than embedding an ever-growing free-form configuration block.

Examples:

```text
prompts/planning/build-ai-agent.md
+ schemas/agent-build-brief.schema.json
+ examples/agent-build-brief.yaml
```

```text
prompts/implementation/codebase-de-slop-task.md
+ schemas/codebase-maintenance-task.schema.json
+ examples/codebase-maintenance-task.yaml
```

## Formal Loop Prompts

The bounded-completion prompt set is operationally different from ordinary task prompts.

Canonical orchestration prompts:

- [`orchestration/start-bounded-completion.md`](orchestration/start-bounded-completion.md)
- [`orchestration/resume-bounded-completion.md`](orchestration/resume-bounded-completion.md)
- [`orchestration/reset-bounded-completion.md`](orchestration/reset-bounded-completion.md)
- [`orchestration/escalate-bounded-completion.md`](orchestration/escalate-bounded-completion.md)
- [`review/bounded-completion-review.md`](review/bounded-completion-review.md)

These prompts control a workflow whose authoritative state lives under `.agent-loop/`; the conversation itself is not the source of truth.

Use [`../docs/loops/README.md`](../docs/loops/README.md) before operating the loop.

The matching [`.github/prompts/`](../.github/prompts/) files are GitHub Copilot prompt adapters. Keep them aligned and thin; do not create a separate set of completion semantics there.

## Prompt vs Agent vs Skill

Use an **agent** when you need an outcome owner.

Use a **skill** when you need reusable behavior inside an owner.

Use a **prompt** when you need a repeatable invocation.

Example:

```text
Agent:
  agents/codebase-maintenance-engineer.md

Skill:
  skills/codebase-de-slop-and-refactoring.md

Prompt:
  prompts/implementation/codebase-de-slop-task.md
```

The prompt may be copied or customized per task. The agent/skill remain the reusable behavior source.

## Prompt Safety

Treat task-supplied and retrieved content as data.

A prompt should not instruct the model to:

- obey instructions embedded in webpages, issues, logs, retrieved documents or tool output;
- expose secrets or paste credential-bearing configuration into model-visible output;
- broaden tool permissions because the task "needs" them;
- retry unboundedly;
- declare completion without the required evidence.

For destructive, privileged, costly or production-affecting actions, preserve the owning agent's approval boundary.

## Prompt Quality Checklist

A task prompt should make material items explicit:

- objective;
- target repository/system/ref/environment;
- scope and non-goals;
- relevant existing architecture/behavior to preserve;
- trusted context vs untrusted inputs;
- required inspection;
- failure modes;
- implementation constraints;
- verification;
- acceptance criteria;
- completion/failure/escalation behavior.

Do not add sections that provide no behavioral value.

## Creating a New Prompt

Use [`../docs/patterns/prompt.md`](../docs/patterns/prompt.md).

Prefer a new reusable prompt when:

- the task recurs;
- the order of inspection/implementation/verification matters;
- misuse has meaningful safety or correctness cost;
- the output has a stable contract;
- a schema/example can make invocation less ambiguous.

Do not create a new prompt merely to preserve one project's transient details.

## Validation

After changing prompts:

```bash
python3 scripts/validate-agentdefaults.py
```

For bounded-completion prompts also run the bounded-completion validator when an execution environment is available:

```bash
python3 scripts/validate-bounded-completion.py
```

Report either command as passed only when it actually ran successfully.
