# DevOps Documentation Engineer Quickstart

## Purpose

Provide the shortest reliable path for using the DevOps Documentation Engineer to create or reconcile Markdown, Mermaid, runbooks, architecture documentation, and diagram assets from authoritative Terraform, Ansible/AAP, Azure, Jenkins, GitHub, and GitOps evidence.

## Use This Stack

```text
agents/devops-documentation-engineer.md
skills/devops-documentation-engineering.md
prompts/implementation/devops-documentation-task.md
schemas/devops-documentation-task.schema.json
examples/devops-documentation-task.yaml
docs/devops-documentation-engineer-acceptance-tests.md
.github/agents/devops-documentation-engineer.agent.md
```

## Best-Fit Tasks

- reconcile a documentation repo against current DevOps implementation
- document Jenkins or Ansible GitOps flows
- document Terraform/Azure ownership and dependencies
- create or update runbooks and operational references
- build evidence-backed Mermaid architecture, sequence, or lifecycle diagrams
- audit stale Markdown, broken links, image references, or misleading diagrams
- maintain docs-as-code without modifying the underlying platform

## Start With Evidence

Before writing, identify:

```text
documentation target
source repositories/systems
current-state versus target-state intent
audience
allowed documentation mutations
existing Markdown/Mermaid/image conventions
validation commands or site build
```

For a complex GitOps flow, require evidence for:

```text
desired-state source
review/approval
trigger
validation
controller/orchestrator
execution identity
target
authoritative state
success/failure signals
retry/reconciliation
promotion
rollback
```

## Example Invocation

Use [`../../prompts/implementation/devops-documentation-task.md`](../../prompts/implementation/devops-documentation-task.md), or adapt [`../../examples/devops-documentation-task.yaml`](../../examples/devops-documentation-task.yaml) for a structured request.

A concise task can be:

```text
Use the DevOps Documentation Engineer.

Target: <documentation repo/path>
Mode: implement
Goal: Reconcile the current Jenkins and Ansible GitOps documentation against the implementation repositories.
Sources: <repos/systems>
State intent: current_state
Authority: documentation files only
Diagrams: update embedded Mermaid; preserve opaque image diagrams that have no editable source and report them.
Done when: material claims are evidence-backed, links/diagrams validate where tooling exists, and unverified items are explicit.
```

## Diagram Policy

### Mermaid

Prefer Mermaid for logical architecture and workflow diagrams when the repository already supports it or the task explicitly requests it. Every edge is a technical claim and must be reconciled against source evidence.

### Existing images

Determine whether each image is:

```text
editable source
rendered derivative
opaque image only
```

Update editable source first. Do not overwrite an opaque PNG/JPG with an inferred reconstruction when the source is unavailable.

## Scope Boundary

This agent may inspect Terraform, Ansible/AAP, Jenkins, Azure, GitHub, and runtime evidence but its normal mutation scope is documentation only.

If the documentation task exposes an implementation defect, report it under `HANDOFF` and route actual platform changes to `agents/principal-devops-engineer.md`.

## Validation

For AgentDefaults stack changes run:

```bash
python3 scripts/validate-agentdefaults.py
```

For a real documentation repository run its own applicable Markdown/site/link/Mermaid validation and reconcile material claims against source evidence. Do not treat a successful site build as proof that technical content is correct.

## Completion

A documentation task is complete only when the requested documents exist or the requested review is delivered, material claims are traceable to inspected evidence, current/target state is correctly represented, diagram limitations are explicit, no sensitive data is introduced, and every unrun check remains `UNVERIFIED`.