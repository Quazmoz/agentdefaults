# Automation Platform Composition and Boundaries

## Purpose

Design workflows that combine infrastructure lifecycle, configuration management, CI/CD, GitOps, runbook automation, managed execution, and durable workflow products without duplicating ownership or hiding domain logic in the orchestration layer.

## When To Use

Use when a request spans more than one capability class or when one product must trigger, govern, or consume outputs from another.

## Boundary Model

Every automation unit must have one authoritative owner.

```text
IaC engine
  owns: provider-managed resource lifecycle and infrastructure desired state
  stores: configuration, resource identity, and state
  exposes: plans or previews, outputs, resource identifiers, and change results

Configuration-management engine
  owns: target configuration, deployment to existing targets, and day-2 state
  stores: inventories or classification, variables or data, roles, modules, cookbooks, manifests, and policies
  exposes: changed state, convergence reports, task results, and verification outputs

CI/CD platform
  owns: triggers, build, test, scan, artifact, approval, promotion, stage coordination, and run history
  stores: workflow or pipeline definitions, logs, reports, and artifact references
  exposes: run status, approvals, evidence, and notifications

GitOps controller
  owns: continuous reconciliation of version-controlled deployment state
  stores: cluster-side reconciliation state and health observations
  consumes: Git revisions, manifests, packages, and immutable artifact references
  exposes: sync, drift, health, and reconciliation status

Runbook platform
  owns: authorized operator entrypoints, parameters, schedules, target selection, and job evidence
  stores: job definitions, execution logs, and operator history
  invokes: versioned automation content or APIs

Managed IaC execution platform
  owns: controlled plan and apply execution, approvals, policies, run history, and possibly state
  does not automatically own: the underlying IaC language or resource model

Durable workflow engine
  owns: long-running workflow state, retries, timers, signals, compensation, and execution history
  stores: durable workflow history
  invokes: activities, services, or automation platforms
```

## Composition Rules

1. Assign one authoritative owner per automation unit.
2. Keep domain logic in the native engine or repository.
3. Treat the caller, executor, reconciler, and source of truth as separate roles.
4. Pass typed, versioned, validated outputs between platforms.
5. Never use ephemeral workspaces as durable state, inventory, artifact truth, or workflow history.
6. Build artifacts once, then promote the same immutable artifact when possible.
7. Scope credentials to the platform, stage, environment, and target that require them.
8. Put approvals before consequential resource changes or production releases.
9. Separate retry, resume, reconciliation, compensation, and rollback.
10. Design recovery paths that do not depend exclusively on the failed component.
11. Avoid circular ownership and bootstrap traps.
12. Record control-plane, runner, agent, controller, state, database, certificate, plugin, and upgrade ownership.
13. Prefer the smallest composition that satisfies capability and governance requirements.

## Common Patterns

### CI/CD plus IaC plus configuration management

```text
CI/CD trigger
-> validate and test IaC
-> plan or preview
-> policy and human approval
-> IaC apply through an approved execution layer
-> publish validated outputs
-> refresh approved inventory or deployment inputs
-> configuration-management canary or check
-> converge targets
-> verify service health
-> archive evidence
```

### CI/CD plus GitOps

```text
CI/CD trigger
-> build, test, scan, sign, and publish immutable artifact
-> update version-controlled deployment declaration
-> review and merge desired-state change
-> GitOps controller reconciles cluster state
-> health and sync evidence feed release reporting
```

The CI/CD platform owns artifact creation and change proposal. The GitOps controller owns cluster reconciliation.

### Runbook platform plus configuration engine

```text
operator or service-catalog request
-> authorize user and validate parameters
-> select approved targets and maintenance window
-> invoke versioned configuration or remediation content
-> execute in batches
-> verify and archive evidence
```

The runbook platform owns the operator surface and execution record. The configuration engine owns target changes.

### Managed IaC execution

```text
source-control event
-> managed IaC platform loads versioned configuration
-> validate, test, and plan
-> policy checks and approval
-> apply with controlled credentials
-> store state, logs, and evidence
-> schedule drift detection
```

The managed platform governs execution. The IaC engine still defines resource lifecycle.

### CI/CD plus durable workflow

```text
CI/CD platform
-> build and deploy workflow code and workers
-> trigger workflow or publish event
-> durable workflow engine owns timers, retries, signals, compensation, and runtime state
-> outcome returns to release or operational reporting
```

## Handoff Contract

For each boundary, define:

```yaml
producer:
consumer:
capability_owner:
artifact_or_output:
format:
version:
validation:
classification:
retention:
secret_content: false
integrity_or_provenance:
failure_behavior:
retry_or_resume_owner:
owner:
```

## Repository Layout Example

```text
automation/
  iac/
    environments/
    modules-or-components/
    tests/
  configuration/
    inventories-or-classification/
    roles-modules-cookbooks-or-manifests/
    runbooks/
    tests/
  ci-cd/
    workflows-or-pipelines/
    reusable-components/
  gitops/
    applications/
    environments/
  workflow/
    definitions/
    workers/
  contracts/
  policy/
  docs/
```

Separate repositories are valid when ownership, release cadence, access control, or platform boundaries differ.

## Anti-Patterns

- IaC configuration generated ad hoc inside a pipeline.
- Configuration-management content embedded as multiline pipeline strings.
- CI/CD workspaces used as IaC state, durable inventory, or workflow state.
- Two engines managing the same resource or configuration attribute.
- CI/CD variables becoming the undocumented system of record.
- A pipeline applying Kubernetes manifests being described as GitOps without reconciliation.
- GitOps controllers building artifacts.
- Runbook UIs storing the only copy of operational logic.
- Multi-day CI jobs substituting for a durable workflow engine.
- Unversioned output parsing between tools.
- Production credentials available to build stages.
- Re-running a partial workflow without understanding non-idempotent activities.
- Deleting infrastructure as the default rollback for application failures.

## Expected Output

```markdown
## Platform Ownership Map
| Concern | Capability | Product / Edition | Caller | Artifact | Durable State or History |
|---|---|---|---|---|---|

## Execution and Reconciliation Flow

## Handoff Contracts
| Producer | Consumer | Data | Validation | Failure Behavior | Recovery Owner |
|---|---|---|---|---|---|

## Credentials, Policy, and Approvals

## Retry, Resume, Reconciliation, Compensation, and Rollback

## Repository Boundaries

## Control-Plane Recovery

## Anti-Patterns Prevented
```

## Quality Bar

- Each concern has one owner.
- Cross-platform handoffs are explicit, typed, versioned, and validated.
- Orchestration coordinates but does not absorb domain logic.
- State, inventory, artifacts, reconciliation status, and workflow history have distinct durable homes.
- Credentials and approvals follow least privilege and separation of duties.
- Retry, resume, reconciliation, compensation, and rollback are not conflated.
- The architecture can recover when a control plane or runner is unavailable.
