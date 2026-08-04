# Terraform Workload Fit Analysis

## Purpose

Determine whether Terraform should be the authoritative owner of an automation unit and identify misuse patterns before implementation.

## When To Use

Use when a request creates, changes, imports, replaces, reconciles, or destroys persistent infrastructure or platform resources.

## Inputs Needed

- resource types and providers
- desired lifecycle
- current ownership and import state
- environment boundaries
- state-backend requirements
- drift expectations
- dependencies
- plan and approval controls
- secrets and credentials
- rollback and recovery expectations

## Strong Fit Signals

- The target is represented by a maintained Terraform provider.
- The resource persists after the run.
- Create, update, replacement, import, drift, and destroy behavior matter.
- Reviewable plan output is valuable.
- Reusable modules and environment promotion are needed.
- A remote state backend, locking, and controlled apply process can be supported.
- The desired configuration should remain authoritative across repeated runs.

## Weak Fit Signals

- The main task is running remote commands.
- The main task is configuring packages, files, services, users, or application internals.
- The workflow is dominated by build, test, artifacts, approvals, and release promotion.
- Provider coverage is missing, incomplete, or less reliable than the target API requires.
- The operation is a procedural incident runbook with no durable desired state.
- The resource is intentionally ephemeral and fully scoped to one pipeline execution.

## Analysis Procedure

1. List each resource and the provider expected to own it.
2. Confirm whether the provider models create, read, update, and delete behavior adequately.
3. Identify import requirements and pre-existing ownership.
4. Define the state backend, locking, workspace or repository boundaries, and recovery process.
5. Identify attributes that force replacement and the resulting blast radius.
6. Define plan review, policy, approval, apply, and post-apply verification.
7. Separate post-provision configuration for Ansible when appropriate.
8. Separate trigger and pipeline flow for Jenkins when appropriate.
9. Reject provisioners as the default configuration-management design.
10. Propose a small proof of fit using non-production resources.

## Decision Questions

- Does the provider expose the full lifecycle required?
- Who owns state, locking, backup, and state recovery?
- Can the resource be imported safely?
- What does drift mean for this resource?
- Can concurrent runs conflict?
- Which changes force replacement?
- How are secrets prevented from leaking into configuration, plans, logs, or state?
- Is destroy allowed, protected, or prohibited?
- Is the plan meaningful enough for human review?
- Is the resource lifecycle independent from host configuration?

## Anti-Patterns

- Terraform as a remote shell runner.
- Large `local-exec` or `remote-exec` workflows.
- Configuration duplicated in Terraform and Ansible.
- One state file for unrelated environments or excessive blast radius.
- Local state for shared production automation.
- Unreviewed automatic apply for high-impact changes.
- Treating a successful apply as complete without service-level verification.
- Hiding imperative retry loops inside configuration.

## Expected Output

```markdown
## Terraform Fit
- Verdict: strong | conditional | weak | disqualified
- Confidence:
- Authoritative resources:
- Provider coverage:
- State design:
- Drift model:
- Plan and approval path:
- Replacement and destroy risks:
- Configuration handed to Ansible:
- Orchestration handed to Jenkins:
- Pilot:
```

## Quality Bar

- Provider and lifecycle coverage are explicit.
- State ownership and recovery are defined.
- Replacement and destroy risks are visible.
- Provisioners are not used as a substitute for configuration management.
- The recommendation distinguishes Terraform ownership from Jenkins orchestration.
