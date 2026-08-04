# Jenkins Workload Fit Analysis

## Purpose

Determine whether Jenkins should own the trigger, pipeline, build, test, approval, release, or coordination layer for an automation unit.

## When To Use

Use when work begins from a source-control event, webhook, schedule, or manual request and must move through durable stages with logs, artifacts, gates, credentials, notifications, and promotion controls.

## Inputs Needed

- trigger type and frequency
- source repositories and branches
- build, test, scan, package, approval, deploy, and verify stages
- artifact repositories and promotion model
- controller, agent, and executor topology
- plugin and shared-library dependencies
- credentials and secret boundaries
- concurrency and locking needs
- timeout, retry, restart, and recovery expectations
- audit, retention, and notification requirements

## Strong Fit Signals

- CI, build, test, scan, package, artifact, or release stages are central.
- A webhook, schedule, or manual approval starts the workflow.
- Parallel stages, gates, locks, credentials, logs, notifications, and pipeline history matter.
- The workflow must coordinate Terraform plans/applies or Ansible deployments.
- Artifacts must be built once and promoted through environments.
- Stage-level restart or durable execution is valuable.

## Weak Fit Signals

- The main job is persistent infrastructure desired-state ownership.
- The main job is detailed configuration of hosts or network devices.
- Pipeline steps would become the only record of infrastructure or server configuration.
- The required recovery workflow depends on the same failed Jenkins controller.
- The job is a long-running business process better served by a dedicated workflow or event platform.

## Analysis Procedure

1. Define the trigger and expected pipeline completion condition.
2. Separate pipeline orchestration from Terraform and Ansible domain logic.
3. Define repository boundaries for Jenkinsfiles, shared libraries, Terraform, and Ansible.
4. Define immutable artifact creation and promotion where applicable.
5. Define controller, agent, label, workspace, container, and toolchain requirements.
6. Define credentials, masking, rotation, and least-privilege execution identities.
7. Define approvals, locks, concurrency, timeouts, retries, and abort behavior.
8. Define what can restart from a stage and what must rerun from the beginning.
9. Define logs, test reports, artifacts, attestations, and retention.
10. Define failure notifications and human ownership.
11. Confirm that Terraform state and Ansible inventories remain outside Jenkins.

## Decision Questions

- What event starts the pipeline?
- What is built, tested, scanned, approved, promoted, or deployed?
- Which stages can run in parallel?
- Which stages are safe to retry?
- Is the artifact immutable across environments?
- Which credentials are needed per stage?
- How are concurrent deployments prevented?
- What happens if the controller restarts?
- Can an operator reconstruct the decision from retained evidence?
- Which platform owns post-deployment desired state?

## Anti-Patterns

- Infrastructure definitions embedded directly in Jenkinsfiles.
- Large inline shell scripts acting as an undocumented automation platform.
- Server configuration expressed as pipeline steps instead of Ansible roles or playbooks.
- Terraform state stored in workspaces.
- Long-lived secrets injected globally across unrelated stages.
- Rebuilding a different artifact for each environment.
- Automatic production changes without gates or protected credentials.
- Plugin sprawl with no ownership, pinning, testing, or upgrade process.
- A recovery pipeline that cannot run when Jenkins is impaired.

## Expected Output

```markdown
## Jenkins Fit
- Verdict: strong | conditional | weak | disqualified
- Confidence:
- Trigger:
- Pipeline stages:
- Artifacts and promotion:
- Controller and agents:
- Credentials:
- Concurrency and approvals:
- Restart and recovery:
- Terraform calls:
- Ansible calls:
- Logic that must stay outside Jenkins:
- Pilot:
```

## Quality Bar

- Trigger, stages, artifacts, and completion criteria are explicit.
- Jenkins orchestrates rather than replacing Terraform or Ansible.
- Credentials, concurrency, retries, and recovery are designed.
- Artifact promotion avoids environment-specific rebuilds when possible.
- Pipeline ownership and plugin maintenance are assigned.
