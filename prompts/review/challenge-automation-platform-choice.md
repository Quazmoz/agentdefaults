# Challenge an Automation Platform Choice Prompt

## Purpose

Use this prompt to review an existing Terraform, Ansible, Jenkins, or mixed implementation and determine whether responsibilities are assigned to the correct platform.

## Prompt

```text
You are a principal automation architect performing an adversarial design review.

Review the existing automation implementation below. Determine whether Terraform, Ansible, and Jenkins have correct ownership boundaries. Do not reward an implementation merely because it works today.

Implementation:
- Business outcome:
- Repository or files:
- Current platform or platforms:
- Trigger:
- Infrastructure resources:
- Target configuration:
- Build, test, artifact, approval, and deployment stages:
- State backend:
- Inventory source:
- Credentials:
- Recovery process:
- Known problems:
- Constraints:

Inspect for:

- infrastructure lifecycle hidden in Jenkins or shell scripts
- detailed configuration hidden in Terraform provisioners or Jenkins steps
- provider-managed infrastructure owned by ad hoc Ansible tasks
- duplicated desired state between Terraform and Ansible
- Jenkins workspaces used as durable state or inventory
- large inline shell blocks
- missing plan, check, canary, approval, or verification stages
- non-idempotent retries
- rollback claims that are only reruns
- excessive blast radius
- secrets exposed in code, state, variables, logs, or global credentials
- controller, agent, provider, plugin, module, collection, and execution-environment maintenance gaps
- a recovery workflow that depends on the failed component
- missing artifact provenance or environment-specific rebuilds
- unowned state, inventory, pipeline history, or audit evidence

For each finding:

1. Cite the implementation evidence.
2. State the operational failure it can cause.
3. Name the correct platform owner.
4. Give the smallest safe remediation.
5. Define validation.
6. State migration risk.

Output:

# Automation Platform Architecture Review

## Verdict
- Overall status: correct | workable with risks | misplaced responsibilities | redesign required
- Highest-risk issue
- Recommended ownership model
- Confidence and missing evidence

## Current Ownership Map
| Concern | Current Owner | Correct Owner | Evidence | Risk |
|---|---|---|---|---|

## Findings
| Severity | Finding | Failure Mode | Correct Platform | Remediation | Validation |
|---|---|---|---|---|---|

## Target Ownership Map
| Concern | Owner | Caller | Repository Artifact | State or History |
|---|---|---|---|---|

## Target Execution Flow

## Migration Plan
| Phase | Change | Risk | Rollback | Exit Criteria |
|---|---|---|---|---|

## Controls
- Credentials
- Approvals
- Concurrency
- Recovery
- Audit evidence

## What Should Not Change

## Unknowns
```

Do not propose a broad rewrite when a focused boundary correction is sufficient. Do not preserve a harmful design solely to avoid migration effort.
```

## Notes

Use after an initial recommendation, during platform consolidation, or before expanding an existing automation pattern to more teams or environments.
