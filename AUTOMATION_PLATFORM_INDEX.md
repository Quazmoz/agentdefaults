# Automation Platform Selection Index

## Purpose

Provide a focused entrypoint for selecting and composing Terraform, Ansible, and Jenkins based on workload ownership, state, lifecycle, triggers, recovery, and governance.

## Start Here

```text
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
```

## Canonical Stack

### Agent

| Path | Use |
|---|---|
| [`agents/automation-platform-selection-advisor.md`](agents/automation-platform-selection-advisor.md) | Full decision agent, doctrine, workflow, scoring model, and output contract. |

### Skills

| Path | Use |
|---|---|
| [`skills/automation-platform-decision-framework.md`](skills/automation-platform-decision-framework.md) | Decompose work, classify automation units, apply hard-fit rules, and score viable platforms. |
| [`skills/terraform-workload-fit-analysis.md`](skills/terraform-workload-fit-analysis.md) | Evaluate persistent provider-managed infrastructure lifecycle, state, drift, and plan/apply controls. |
| [`skills/ansible-workload-fit-analysis.md`](skills/ansible-workload-fit-analysis.md) | Evaluate configuration convergence, deployment, inventory-driven operations, and day-2 automation. |
| [`skills/jenkins-workload-fit-analysis.md`](skills/jenkins-workload-fit-analysis.md) | Evaluate CI/CD, triggers, stages, artifacts, approvals, credentials, and pipeline recovery. |
| [`skills/automation-platform-composition-and-boundaries.md`](skills/automation-platform-composition-and-boundaries.md) | Compose tools with explicit ownership and handoff contracts. |
| [`skills/automation-platform-selection-orchestrator.md`](skills/automation-platform-selection-orchestrator.md) | Run the complete selection, challenge, pilot, and recommendation workflow. |

### Prompts

| Path | Use |
|---|---|
| [`prompts/planning/select-automation-platform.md`](prompts/planning/select-automation-platform.md) | Select a platform architecture for a new request. |
| [`prompts/review/challenge-automation-platform-choice.md`](prompts/review/challenge-automation-platform-choice.md) | Review an existing implementation for misplaced responsibilities and migration needs. |

### Structured Inputs and Validation

| Path | Use |
|---|---|
| [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) | Machine-readable decision brief contract. |
| [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Full-stack worked input example. |
| [`docs/automation-platform-selection-acceptance-tests.md`](docs/automation-platform-selection-acceptance-tests.md) | Behavioral and architecture acceptance tests. |
| [`.github/agents/automation-platform-selection-advisor.agent.md`](.github/agents/automation-platform-selection-advisor.agent.md) | Thin GitHub Copilot custom-agent wrapper. |

## Fast Decision Rules

```text
Persistent provider-managed resource lifecycle
  -> Terraform

Configuration or operation of existing targets
  -> Ansible

Triggered build, test, approval, artifact, release, or coordination flow
  -> Jenkins

More than one responsibility
  -> Decompose and compose with one owner per unit

None fits
  -> State the missing capability instead of forcing a choice
```

## Reference Architecture

```text
Jenkins trigger and pipeline
  -> Terraform validate, plan, approval, apply
  -> validated Terraform outputs
  -> Ansible inventory, canary, converge, verify
  -> Jenkins archives evidence and reports status
```

This is a common composition, not a mandatory design. Jenkins is optional when another controlled execution platform already exists.

## Core Guardrails

- Decompose before selecting.
- Assign one authoritative owner per automation unit.
- Do not confuse execution capability with state ownership.
- Do not duplicate desired state between Terraform and Ansible.
- Keep Terraform and Ansible logic out of Jenkinsfiles.
- Do not use Terraform provisioners as the primary configuration system.
- Do not use Jenkins workspaces as durable state or inventory.
- Address credentials, approvals, retries, rollback, partial failure, and platform outage recovery.
- Challenge the recommendation with a proof-of-fit pilot.

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Decompose the workload, select Terraform, Ansible, Jenkins, or a bounded composition for each automation unit, define ownership and handoff contracts, challenge the design, and produce a proof-of-fit pilot.
```
