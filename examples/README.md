# Examples

## Purpose

Explain how to use `examples/` as concrete starting material without mistaking example values for canonical policy, validated target configuration, or universal defaults.

## What Examples Are

Examples translate reusable contracts into something easy to copy and adapt.

Typical flow:

```text
quickstart / canonical agent
        ↓
schema or prompt contract
        ↓
copy a matching example
        ↓
replace illustrative values with real task data
        ↓
validate / execute through the owning stack
```

Examples do not outrank canonical agents, skills, schemas, target-repository evidence, or current user instructions.

## Structured Task Examples

Representative structured briefs include:

- [`agent-build-brief.yaml`](agent-build-brief.yaml)
- [`bounded-completion-task.json`](bounded-completion-task.json)
- [`codebase-maintenance-task.yaml`](codebase-maintenance-task.yaml)
- [`automation-platform-decision-brief.yaml`](automation-platform-decision-brief.yaml)
- [`devops-documentation-task.yaml`](devops-documentation-task.yaml)
- [`devsecops-security-task.yaml`](devsecops-security-task.yaml)
- [`google-play-growth-brief.yaml`](google-play-growth-brief.yaml)
- [`app-market-research-brief.yaml`](app-market-research-brief.yaml)

When a schema exists under [`../schemas/`](../schemas/), treat the schema as the machine-readable contract and the example as one valid/adaptable shape.

## Workflow and Stack Examples

Markdown recipes such as these show practical composition:

- [`coding.md`](coding.md)
- [`local-model.md`](local-model.md)
- [`handoff.md`](handoff.md)
- [`compression.md`](compression.md)
- [`benchmark.md`](benchmark.md)
- [`copilot-token-efficiency.md`](copilot-token-efficiency.md)
- [`palmierpro-mcp-workflow.md`](palmierpro-mcp-workflow.md)
- [`stacks/`](stacks/)

These recipes may intentionally be smaller than a production task contract.

## Safe Adaptation Rules

Before using an example:

1. Confirm it matches the correct agent/stack.
2. Replace repository, branch, environment, account, model, URL, and acceptance-criterion values with real task values.
3. Remove example approvals that were not actually granted.
4. Replace illustrative verification commands with commands that really exist in the target repository.
5. Do not carry example credentials/secrets; examples should not contain any.
6. Re-check mutation/production authority independently of the example.
7. Validate against the schema or owning workflow when available.

An example passing schema validation does not prove its target system or task is correct.

## Bounded Completion Example

For the persisted loop, start with:

```text
examples/bounded-completion-task.json
schemas/bounded-completion-task.schema.json
docs/loops/QUICK_REFERENCE.md
docs/loops/README.md
```

Do not reuse acceptance criteria or verification commands from the example unless they are genuinely correct for the target repository.

## Adding an Example

Add an example when it meaningfully reduces setup ambiguity for a reusable contract or stack.

Good examples are:

- valid or explicitly labeled illustrative;
- small enough to understand;
- realistic enough to adapt;
- free of secrets/private identifiers;
- linked to the owning quickstart/schema/agent;
- not another copy of canonical policy prose.

## Validation

After adding/changing repository examples run:

```bash
python3 scripts/validate-agentdefaults.py
```

Run task/schema-specific validation when available. Do not claim an example represents a successful real-world run unless that run actually occurred.