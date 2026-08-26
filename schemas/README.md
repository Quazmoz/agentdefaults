# Schemas

## Purpose

Explain the machine-readable contracts under `schemas/` and how they relate to agents, prompts, examples and runtime state.

Schemas reduce ambiguity for workflows whose inputs or evidence need stable identifiers and deterministic validation. They do not grant permissions and do not prove that a task was executed correctly.

## What the Schemas Represent

Most schemas define **task contracts**:

- [`agent-build-brief.schema.json`](agent-build-brief.schema.json)
- [`app-market-research-brief.schema.json`](app-market-research-brief.schema.json)
- [`automation-platform-decision-brief.schema.json`](automation-platform-decision-brief.schema.json)
- [`codebase-maintenance-task.schema.json`](codebase-maintenance-task.schema.json)
- [`devops-documentation-task.schema.json`](devops-documentation-task.schema.json)
- [`devsecops-security-task.schema.json`](devsecops-security-task.schema.json)
- [`google-play-growth-brief.schema.json`](google-play-growth-brief.schema.json)
- [`principal-ai-devops-task.schema.json`](principal-ai-devops-task.schema.json)
- [`principal-ai-engineer-task.schema.json`](principal-ai-engineer-task.schema.json)
- [`principal-devops-task.schema.json`](principal-devops-task.schema.json)

The bounded-completion stack additionally has runtime/evidence contracts:

- [`bounded-completion-task.schema.json`](bounded-completion-task.schema.json): operator-authored task contract.
- [`bounded-completion-state.schema.json`](bounded-completion-state.schema.json): durable loop state.
- [`bounded-completion-findings.schema.json`](bounded-completion-findings.schema.json): structured reviewer findings/dispositions.

## Task Contract vs Runtime State

Keep these concepts separate.

```text
task contract
  what must be accomplished and verified

runtime state
  where the current workflow is in its lifecycle

findings/evidence
  what was observed, challenged, accepted, rejected or resolved

repository/runtime
  the actual system being changed; remains authoritative for real behavior
```

For bounded completion, do not manually edit `.agent-loop/current/state.json` or findings when an equivalent [`../scripts/bounded-completion.py`](../scripts/bounded-completion.py) command exists.

## Stable Identifiers

Use stable criterion/finding identifiers when a workflow must:

- resume across conversations;
- reconcile reviewer findings;
- invalidate stale evidence;
- prove which acceptance criterion a check supports;
- distinguish resolved findings from newly observed ones.

Avoid relying on list position or prose similarity as identity.

## Security and Data Hygiene

Structured does not mean safe.

Do not put secrets, tokens, private keys, passwords, credential-store dumps or unrelated sensitive data into task contracts, findings or evidence.

Validate both syntax and semantics:

- identifiers refer to the intended target;
- paths/URLs are within allowed scope;
- required commands are real and appropriate;
- approval fields have trusted provenance;
- limits do not widen repository defaults;
- enum values do not disguise an unsupported state.

## Examples

Most task schemas have a companion example under [`../examples/`](../examples/).

Examples are starting points, not defaults that should be copied unchanged. Replace targets, acceptance criteria and verification with evidence appropriate to the real task.

## Changing a Schema

Treat schema evolution as a contract change.

Before changing one:

1. identify agents, prompts, examples, scripts and validators that consume it;
2. preserve backward compatibility when required or explicitly version/migrate;
3. update examples and validation together;
4. test malformed, missing, boundary and adversarial inputs;
5. do not relax validation merely to accept an existing invalid artifact.

The bounded-completion state/findings schemas are control-plane contracts; changes require especially careful regression testing with [`../scripts/validate-bounded-completion.py`](../scripts/validate-bounded-completion.py).

## Validation

Canonical validation parses every schema and checks local references:

```bash
python3 scripts/validate-agentdefaults.py
```

Schema validity is only one layer. The target workflow still needs semantic and runtime verification.
