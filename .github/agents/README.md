# GitHub Copilot Agent Adapters

## Purpose

Explain the role of `.github/agents/*.agent.md` so GitHub Copilot custom-agent files are not mistaken for separate canonical agent implementations.

Canonical reusable behavior lives in [`../../agents/`](../../agents/). These files are runtime adapters that may add Copilot-specific frontmatter, tool/delegation configuration, concise routing, or integration hooks.

## Rule

When changing behavior:

```text
canonical agent under agents/
        ↓
update skill/schema/quickstart if needed
        ↓
keep .github/agents wrapper aligned and thin
```

Do not copy an entire canonical profile here merely for convenience. Duplication makes tool-specific behavior drift.

## Bounded Completion

The bounded completion adapters are operationally important because the lead/reviewer workflow can use VS Code custom-agent delegation and a scoped Stop hook.

Read, in order:

1. [`../../docs/loops/README.md`](../../docs/loops/README.md)
2. [`../../docs/quickstarts/bounded-completion.md`](../../docs/quickstarts/bounded-completion.md)
3. [`../../agents/bounded-completion-lead.md`](../../agents/bounded-completion-lead.md)
4. [`../../agents/bounded-completion-reviewer.md`](../../agents/bounded-completion-reviewer.md)

The repository intentionally avoids guessed `model:` identifiers where exact qualified local registrations are not authoritative. Select/confirm models through the runtime and never claim distinct-model evidence unless the operator/runtime actually proves it.

## Authority

A Copilot adapter cannot widen the canonical agent's authority.

Tool availability, custom-agent selection, delegation, hooks, or prompt files do not create approval for production deployment, destructive mutation, credential access, release publishing, force-push, or other privileged operations.

## Validation

After changing an adapter:

```bash
python3 scripts/validate-agentdefaults.py
```

Cross-tool routing and specialist stack validators should remain aligned with the canonical profile.
