# GitHub Copilot Prompt Adapters

## Purpose

Explain `.github/prompts/*.prompt.md` as GitHub Copilot runtime adapters so they are not confused with canonical reusable prompts under [`../../prompts/`](../../prompts/).

## Canonical vs Runtime Prompt

Use this relationship:

```text
canonical task/review behavior under prompts/
        ↓
Copilot-specific invocation adapter under .github/prompts/
```

A `.github/prompts` file may add runtime-specific frontmatter or invocation wording, but should not become a competing source of workflow semantics.

## Bounded Completion Prompts

The current adapters support the persisted Bounded Completion workflow:

```text
start-bounded-completion.prompt.md
resume-bounded-completion.prompt.md
review-bounded-completion.prompt.md
```

Operator docs:

- [`../../docs/loops/QUICK_REFERENCE.md`](../../docs/loops/QUICK_REFERENCE.md)
- [`../../docs/loops/README.md`](../../docs/loops/README.md)
- [`../../docs/quickstarts/bounded-completion.md`](../../docs/quickstarts/bounded-completion.md)

Canonical prompts live under:

```text
prompts/orchestration/
prompts/review/bounded-completion-review.md
```

## Important Boundaries

Invoking a prompt does not by itself:

- initialize durable `.agent-loop/` state;
- create mutation authority;
- prove reviewer independence;
- satisfy an acceptance criterion;
- record approval;
- make verification current;
- pass the completion gate.

The deterministic control plane and actual repository evidence remain authoritative.

## Editing Rule

If a workflow's behavior changes:

1. update the canonical agent/skill/prompt/control-plane contract first;
2. update the Copilot adapter only as needed for runtime invocation;
3. keep names and routing aligned;
4. avoid copying large canonical prompt bodies unless the runtime requires self-contained content.

## Validation

After changing Copilot prompt adapters run:

```bash
python3 scripts/validate-agentdefaults.py
```

For bounded-completion behavior changes also run:

```bash
python3 scripts/validate-bounded-completion.py
```

Do not claim the prompt caused an external model/reviewer to run unless the runtime actually reports or the operator confirms it.