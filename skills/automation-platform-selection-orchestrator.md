# Automation Platform Selection Orchestrator

## Purpose

Coordinate workload intake, decomposition, platform-fit analysis, composition design, proof-of-fit validation, and a final recommendation across Terraform, Ansible, and Jenkins.

## When To Use

Use for a complete platform-selection exercise, an architecture review, or a migration from automation that has accumulated in the wrong tool.

## Required Inputs

Prefer `schemas/automation-platform-decision-brief.schema.json`.

At minimum:

- requested outcome
- targets and environments
- current implementation
- lifecycle actions
- triggers and frequency
- systems of record
- credentials and privilege constraints
- approvals and audit requirements
- rollback and recovery expectations
- organizational ownership

## Canonical Sequence

```text
1. validate the brief
2. restate the outcome and constraints
3. decompose into automation units
4. classify each unit
5. identify source of truth and lifecycle owner
6. apply hard-fit rules
7. run Terraform fit analysis where applicable
8. run Ansible fit analysis where applicable
9. run Jenkins fit analysis where applicable
10. score viable options
11. identify disqualifiers and anti-patterns
12. define platform ownership boundaries
13. design handoff contracts and execution flow
14. define credentials, approvals, evidence, and recovery
15. challenge the recommendation
16. define a proof-of-fit pilot
17. produce the recommendation and backlog
```

## Skill Routing

Use:

- [`automation-platform-decision-framework.md`](automation-platform-decision-framework.md) for decomposition, classification, hard-fit rules, and scoring.
- [`terraform-workload-fit-analysis.md`](terraform-workload-fit-analysis.md) for persistent provider-managed resource lifecycle.
- [`ansible-workload-fit-analysis.md`](ansible-workload-fit-analysis.md) for configuration, deployment, fleet operations, and day-2 work.
- [`jenkins-workload-fit-analysis.md`](jenkins-workload-fit-analysis.md) for triggers, CI/CD, approvals, artifacts, and stage coordination.
- [`automation-platform-composition-and-boundaries.md`](automation-platform-composition-and-boundaries.md) when more than one platform is justified.

## Recommendation States

Use exactly one state per automation unit:

```text
terraform
ansible
jenkins
composed
insufficient_supported_platforms
needs_more_evidence
```

A composed recommendation must still assign one owner to each unit.

## Confidence Model

```text
high
  The workload is decomposed, hard-fit signals are clear, major constraints are known, and no material disqualifier is unresolved.

medium
  The likely owner is clear, but provider coverage, inventory, connectivity, scale, recovery, or governance needs validation.

low
  The request remains compound or major constraints could change the recommendation.
```

Never hide uncertainty behind a weighted total.

## Decision Challenge

Before finalizing, test at least these counterfactuals:

- Could the runner be replaced without changing the authoritative source of truth?
- What happens on a partial failure?
- What happens on the second run?
- What happens if the selected platform is unavailable?
- Which state or evidence must survive executor loss?
- Does a tenfold increase in targets change the recommendation?
- Does a stricter separation-of-duties requirement change the flow?
- Is there a maintained native integration that removes custom shell logic?

## Final Report

```markdown
# Automation Platform Selection

## Executive Decision

## Assumptions and Confidence

## Workload Decomposition
| Unit | Class | Target | Lifecycle | Trigger | Source of Truth |
|---|---|---|---|---|---|

## Platform Fit
| Unit | Terraform | Ansible | Jenkins | Owner | Reason |
|---|---|---|---|---|---|

## Weighted Matrix
| Criterion | Weight | Terraform | Ansible | Jenkins | Evidence |
|---|---:|---:|---:|---:|---|

## Architecture and Ownership Boundaries

## Execution Flow

## Handoff Contracts

## Security, Approval, and Audit Controls

## Failure Recovery and Rollback

## Anti-Patterns To Avoid

## Proof-of-Fit Pilot

## Implementation Backlog

## Rejected Alternatives

## Unknowns That Could Change the Decision
```

## Completion Contract

```text
Status:
Brief:
Automation units:
Primary recommendations:
Composition:
Skills completed:
Disqualifiers:
Pilot:
Validation:
Assumptions:
Unknowns:
Next decision:
```

## Example Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Decompose the request, decide which units belong in Terraform, Ansible, and Jenkins, define the ownership and handoff boundaries, challenge the recommendation, and produce a proof-of-fit pilot. Do not force a single-platform answer.
```

## Quality Bar

- Decomposition precedes recommendation.
- Hard-fit rules precede scoring.
- Each unit has one owner.
- Composition is minimal and explicit.
- Rejected alternatives are explained.
- Security, approvals, state, inventory, artifacts, recovery, and support ownership are included.
- The pilot can prove the recommendation wrong.
