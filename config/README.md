# Configuration

## Purpose

Explain repository-owned runtime configuration under `config/`. Configuration files set bounded control-plane defaults; they do not replace canonical agent/skill contracts or grant runtime authority.

## Current Configuration

The directory currently contains:

```text
bounded-completion.json
```

It configures default behavior for the persisted Bounded Completion control plane implemented by `scripts/bounded-completion.py`.

Operator guides:

- [`../docs/loops/QUICK_REFERENCE.md`](../docs/loops/QUICK_REFERENCE.md)
- [`../docs/loops/README.md`](../docs/loops/README.md)
- [`../docs/quickstarts/bounded-completion.md`](../docs/quickstarts/bounded-completion.md)

## `bounded-completion.json`

The file currently defines:

```text
version
require_distinct_reviewer_model
limits
preferred_model_labels
```

### Limits

Limits bound behaviors such as:

- full implementation/review iterations;
- unchanged repeated failures;
- plan/final review rounds;
- verification/subagent timeouts;
- retained verification logs;
- unchanged-state iterations;
- Stop-hook continuations.

Task-specific overrides may only tighten limits where the control plane permits them. Do not use a task contract to silently widen repository safety ceilings.

### Preferred model labels

Preferred model labels are human/operator routing hints. They are **not qualified provider model identifiers** and are not proof that a runtime used that model.

Distinct-model evidence counts only when the operator or runtime actually confirms reviewer identity according to the control-plane contract.

## Editing Rules

When changing configuration:

1. Check the canonical lead/reviewer/orchestration contract.
2. Check the executable control-plane semantics in `scripts/bounded_completion/`.
3. Preserve bounded recovery and stop behavior.
4. Do not add secrets, credentials, tokens, or environment-specific private data.
5. Do not loosen a safety bound merely to make a stuck task complete.
6. Update operator docs when a user-visible field or limit meaning changes.
7. Add/regress tests for material semantic changes.

## Configuration Is Not Approval

A config value cannot grant:

- production deployment authority;
- destructive mutation authority;
- credential access;
- release/publish approval;
- permission to bypass target-repository controls.

The user/task and selected owning agent remain the authority boundary.

## Validation

After changing bounded-completion configuration run:

```bash
python3 scripts/validate-bounded-completion.py
python3 scripts/validate-agentdefaults.py
```

Do not report either validator as passed unless it actually ran successfully.