# Ansible Workload Fit Analysis

## Purpose

Determine whether Ansible should own configuration convergence, application deployment, fleet operations, or day-2 automation for an automation unit.

## When To Use

Use when the targets already exist and the main job is to configure, deploy to, operate, patch, remediate, or verify them through inventory-driven automation.

## Inputs Needed

- target inventory and grouping
- connectivity and transport
- privilege-escalation requirements
- desired configuration or operational outcome
- supported modules and collections
- idempotency expectations
- execution-environment requirements
- secrets and credentials
- maintenance windows and concurrency limits
- rollback, canary, and verification expectations

## Strong Fit Signals

- Package, file, service, user, certificate, policy, middleware, or application configuration is the main job.
- Existing hosts or network devices must converge to a known state.
- Inventory groups, variables, roles, and reusable collections map naturally to the estate.
- Agentless execution is valuable or required.
- Patching, rotation, remediation, deployment, and operational runbooks are needed.
- Serial execution, canaries, handlers, check mode, and post-task validation can reduce risk.

## Weak Fit Signals

- The main job is authoritative lifecycle management of provider-managed cloud or SaaS resources.
- The main job is source-triggered build, test, artifact creation, approval, and promotion.
- The operation needs a durable event engine or long-running workflow state beyond the supported execution model.
- Required target access, privilege, or Python/runtime support cannot be established safely.
- The desired outcome depends primarily on imperative shell behavior with no reliable idempotency guard.

## Analysis Procedure

1. Define inventories, groups, variables, and ownership boundaries.
2. Confirm target connectivity, transport, privilege, and runtime prerequisites.
3. Prefer maintained modules and collections over command or shell tasks.
4. Classify each task as convergent, operational, deployment, or verification work.
5. Define idempotency expectations and changed-state semantics.
6. Design roles, collections, execution environments, and dependency pinning.
7. Define check mode, linting, molecule or integration tests where practical.
8. Define serial, batch, canary, maintenance-window, and failure-percentage controls.
9. Define rollback or compensating actions. Do not imply that idempotency equals rollback.
10. Separate persistent infrastructure lifecycle for Terraform.
11. Separate triggers, gates, artifacts, and stage orchestration for Jenkins.

## Decision Questions

- Is the target already present, and who creates it?
- Can the automation converge safely on a second run?
- Which tasks cannot support check mode, and why?
- Are command or shell tasks guarded and justified?
- How is inventory generated and kept current?
- How are host variables, group variables, and secrets separated?
- What is the maximum safe batch size?
- What happens after a partial fleet failure?
- Can the operation be tested against representative targets?
- Which outputs must Jenkins consume or archive?

## Anti-Patterns

- Ansible as the untracked lifecycle owner for large provider-managed resource estates.
- Dynamic infrastructure creation with no authoritative state model.
- Large playbooks composed mainly of shell commands.
- `changed_when: false` used to hide non-idempotent behavior.
- One inventory with uncontrolled production blast radius.
- Secrets stored in plaintext variables or logs.
- Assuming check mode proves production safety.
- Treating successful task execution as service verification.
- Duplicating infrastructure desired state already owned by Terraform.

## Expected Output

```markdown
## Ansible Fit
- Verdict: strong | conditional | weak | disqualified
- Confidence:
- Target inventory:
- Configuration or operation owned:
- Connectivity and privilege:
- Idempotency model:
- Modules and collections:
- Execution environment:
- Canary and concurrency controls:
- Recovery or compensation:
- Infrastructure handed to Terraform:
- Orchestration handed to Jenkins:
- Pilot:
```

## Quality Bar

- Inventory, connectivity, and privilege are explicit.
- Module-first design is preferred over shell execution.
- Idempotency is tested rather than assumed.
- Rollback and partial failure are addressed separately from convergence.
- Terraform and Jenkins boundaries are clear.
