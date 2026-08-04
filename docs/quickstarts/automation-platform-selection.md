# Automation Platform Selection Quickstart

## Purpose

Show how to use AgentDefaults to decide whether Terraform, Ansible, Jenkins, or a bounded composition is the right tool for an automation workload.

## Stack

```text
Agent:
  agents/automation-platform-selection-advisor.md

Orchestrator:
  skills/automation-platform-selection-orchestrator.md

Core skills:
  skills/automation-platform-decision-framework.md
  skills/terraform-workload-fit-analysis.md
  skills/ansible-workload-fit-analysis.md
  skills/jenkins-workload-fit-analysis.md
  skills/automation-platform-composition-and-boundaries.md

Brief:
  schemas/automation-platform-decision-brief.schema.json
  examples/automation-platform-decision-brief.yaml

Prompts:
  prompts/planning/select-automation-platform.md
  prompts/review/challenge-automation-platform-choice.md

Copilot wrapper:
  .github/agents/automation-platform-selection-advisor.agent.md

Acceptance tests:
  docs/automation-platform-selection-acceptance-tests.md
```

## Setup

1. Copy the agent, orchestrator, and only the needed fit-analysis skills into the target context.
2. Fill in [`../../examples/automation-platform-decision-brief.yaml`](../../examples/automation-platform-decision-brief.yaml).
3. Validate it against [`../../schemas/automation-platform-decision-brief.schema.json`](../../schemas/automation-platform-decision-brief.schema.json).
4. Decompose compound requests before comparing tools.
5. Apply hard-fit rules before weighted scoring.
6. Assign one authoritative owner to each automation unit.
7. Define handoff contracts if multiple platforms are required.
8. Challenge the recommendation and run a proof-of-fit pilot.

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md.

Validate examples/automation-platform-decision-brief.yaml. Decompose the request into automation units. Determine which units should be owned by Terraform, Ansible, or Jenkins. Do not force a single-tool answer.

Use these ownership defaults:
- Terraform for persistent provider-managed infrastructure lifecycle.
- Ansible for configuration and operations on existing targets.
- Jenkins for triggered pipelines, CI/CD, approvals, artifacts, and coordination.

Produce:
- workload decomposition
- hard-fit analysis
- weighted decision matrix
- ownership boundaries
- execution flow and handoff contracts
- security, approval, audit, and recovery controls
- anti-patterns to avoid
- proof-of-fit pilot
- implementation backlog
- rejected alternatives and unknowns
```

## Minimal Invocation

```text
For this automation request, tell me whether Terraform, Ansible, Jenkins, or a composition should own it. Decompose the request first, assign one owner per unit, explain why the alternatives are weaker, and give me a small pilot.
```

## Existing-Implementation Review

```text
Load prompts/review/challenge-automation-platform-choice.md. Inspect the current Terraform, Ansible, Jenkins, and shell implementation. Find misplaced responsibilities, duplicated state, unsafe retries, missing approvals, recovery gaps, and logic that belongs in another platform. Produce the smallest safe migration plan.
```

## Example Decisions

### Provision a cloud network and configure hosts

```text
Terraform owns the network and compute resource lifecycle.
Ansible owns operating-system and application configuration.
Jenkins optionally validates, approves, and sequences both.
```

### Build and deploy an application to existing servers

```text
Jenkins owns build, test, artifact, approval, and promotion.
Ansible owns deployment and target convergence.
Terraform is not required unless infrastructure lifecycle changes.
```

### Rotate certificates across a server fleet

```text
Ansible owns inventory-driven rotation and verification.
Jenkins may schedule, approve, and archive evidence.
Terraform is used only for provider-managed certificate resources it already owns.
```

### Create a managed database

```text
Terraform owns database resource lifecycle when provider coverage is suitable.
Ansible may configure clients or applications.
Jenkins may run plan, approval, apply, and verification stages.
```

## Approval Boundaries

A recommendation or design does not automatically authorize:

- Terraform apply or destroy.
- State import, move, repair, or backend migration.
- Ansible execution against production inventory.
- Privilege escalation or credential changes.
- Jenkins job, credential, plugin, controller, or agent changes.
- Production deployment or rollback.

## Validation

Use [`../automation-platform-selection-acceptance-tests.md`](../automation-platform-selection-acceptance-tests.md).

Repository validation:

```bash
python3 scripts/validate-agentdefaults.py
```

## Known Limitations

- A maintained provider, module, collection, or plugin can change the best implementation path.
- Organizational controls may require an execution platform other than Jenkins.
- Some workloads need a dedicated event, workflow, scheduler, secrets, policy, or service-management platform beyond the current supported set.
- Weighted scoring cannot override a hard ownership mismatch.
- A proof-of-fit pilot is still required for uncertain provider coverage, connectivity, scale, or recovery behavior.
