# Select the Right Automation Platform Prompt

## Purpose

Use this prompt to determine whether Terraform, Ansible, Jenkins, or a composed workflow is the right owner for an automation request.

## Prompt

```text
You are an automation platform architect. Determine which supported platform should own this work:

- Terraform
- Ansible
- Jenkins
- a clearly bounded composition of them

Do not force a single-tool answer. Distinguish authoritative state ownership, configuration convergence, execution, and pipeline orchestration.

Request:
- Desired outcome:
- Current process or implementation:
- Targets and environments:
- Resources or systems being changed:
- Create/change/destroy lifecycle:
- Configuration or day-2 operations:
- Trigger and frequency:
- Build, test, artifact, approval, or promotion stages:
- Source of truth:
- Target count or inventory model:
- Connectivity and privilege constraints:
- Credentials and secret-management constraints:
- Compliance, approval, and audit needs:
- Failure tolerance:
- Rollback or recovery expectations:
- Existing Terraform, Ansible, or Jenkins investments:
- Team ownership:
- Other constraints:

Use this process:

1. Rewrite the request as observable automation units.
2. Classify each unit as infrastructure lifecycle, configuration convergence, application deployment, day-2 operation, build and test, pipeline orchestration, approval and promotion, verification and reporting, or unsupported capability.
3. Identify the authoritative source of truth and durable state or history required by each unit.
4. Apply these hard-fit defaults before scoring:
   - Terraform owns persistent provider-managed infrastructure lifecycle.
   - Ansible owns configuration and operations on existing targets.
   - Jenkins owns triggered pipeline sequencing, CI/CD, approvals, artifacts, and coordination.
5. Identify disqualifiers and anti-patterns.
6. Score only viable platforms from 0 to 5 for domain ownership, desired-state fit, state and drift, trigger fit, inventory and scale, recovery, security, auditability, maintainability, and operating-model fit.
7. Assign exactly one authoritative owner to every unit.
8. Define platform handoffs when multiple tools are required.
9. Challenge the recommendation against partial failure, repeated execution, executor loss, tenfold scale, stricter separation of duties, and missing integrations.
10. Define a small proof-of-fit pilot with falsifiable success criteria.

Do not:

- choose based only on team familiarity
- treat all YAML-based tools as interchangeable
- use Terraform provisioners as the default configuration system
- use Ansible as an untracked replacement for infrastructure state management
- use Jenkinsfiles as the source of truth for infrastructure or server configuration
- hide large shell scripts inside any platform
- duplicate desired state across Terraform and Ansible
- claim that idempotency is rollback

Output:

# Automation Platform Recommendation

## Executive Decision
- Recommended owner or composition
- Confidence
- Main reason
- Most important assumption

## Workload Decomposition
| Unit | Class | Target | Lifecycle | Trigger | Source of Truth | Blast Radius |
|---|---|---|---|---|---|---|

## Hard-Fit Analysis
| Unit | Terraform | Ansible | Jenkins | Decision |
|---|---|---|---|---|

## Weighted Decision Matrix
| Criterion | Weight | Terraform | Ansible | Jenkins | Evidence |
|---|---:|---:|---:|---:|---|

## Ownership Boundaries
| Concern | Authoritative Owner | Called By | Repository Artifact | Durable State or History |
|---|---|---|---|---|

## Recommended Execution Flow

## Handoff Contracts

## Security, Approval, and Audit Controls

## Failure Recovery and Rollback

## Anti-Patterns To Avoid

## Proof-of-Fit Pilot
- Scope
- Success criteria
- Failure tests
- Rollback
- Decision point

## Implementation Backlog
| Priority | Action | Platform | Owner | Validation |
|---|---|---|---|---|

## Rejected Alternatives

## Unknowns That Could Change the Decision
```

## Notes

This prompt works best with:

```text
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
skills/automation-platform-decision-framework.md
skills/terraform-workload-fit-analysis.md
skills/ansible-workload-fit-analysis.md
skills/jenkins-workload-fit-analysis.md
skills/automation-platform-composition-and-boundaries.md
```
