# Automation Platform Composition and Boundaries

## Purpose

Design workflows that use Terraform, Ansible, and Jenkins together without duplicating ownership or hiding domain logic in the orchestration layer.

## When To Use

Use when a request spans persistent infrastructure, target configuration, application delivery, and pipeline coordination.

## Boundary Model

```text
Terraform
  owns: provider-managed resource lifecycle and infrastructure desired state
  stores: configuration and state
  exposes: plan, apply outputs, resource identifiers

Ansible
  owns: target configuration, application deployment to existing targets, and day-2 operations
  stores: inventories, variables, roles, playbooks, and execution dependencies
  exposes: changed state, task results, verification outputs

Jenkins
  owns: triggers, stage sequencing, builds, tests, approvals, artifact promotion, coordination, and run history
  stores: Jenkinsfile or shared-library flow, logs, reports, and artifact references
  exposes: pipeline status, approvals, evidence, notifications
```

## Composition Rules

1. Assign one authoritative owner per automation unit.
2. Jenkins may invoke Terraform and Ansible, but their configurations stay in their native repositories or directories.
3. Terraform outputs may feed dynamic inventory or deployment inputs, but do not make Jenkins the durable inventory store.
4. Ansible may verify infrastructure attributes, but must not duplicate Terraform-owned desired state.
5. Build artifacts once, then promote the same immutable artifact through environments when possible.
6. Use explicit handoff contracts between stages.
7. Make every handoff typed, versioned, validated, and auditable.
8. Keep credentials scoped to the stage and platform that needs them.
9. Use approvals before high-impact applies or production deployments.
10. Separate rollback from retry. A rerun is not automatically a rollback.
11. Design recovery paths that do not depend exclusively on the component being recovered.
12. Avoid circular ownership, such as Terraform creating Jenkins which is the only system able to recover Terraform state.

## Common Patterns

### Infrastructure then configuration

```text
Jenkins trigger
-> Terraform fmt, validate, test, and plan
-> human or policy approval
-> Terraform apply
-> publish validated outputs
-> generate or refresh Ansible inventory
-> Ansible check or canary
-> Ansible converge
-> service verification
-> archive evidence
```

### Application delivery to existing infrastructure

```text
Jenkins trigger
-> build and test
-> scan and package immutable artifact
-> approval
-> Ansible deploy to canary
-> verify
-> Ansible deploy in batches
-> verify
-> promote release record
```

### Scheduled day-2 operation

```text
Jenkins schedule
-> load approved inventory
-> Ansible prechecks
-> approval when required
-> Ansible serial operation
-> postchecks
-> report and notify
```

### Infrastructure-only change

```text
Jenkins trigger or approved operator invocation
-> Terraform validate and plan
-> approval
-> Terraform apply
-> verification
```

Jenkins is optional if the organization has another controlled Terraform execution platform.

## Handoff Contract

For each boundary, define:

```yaml
producer: terraform | ansible | jenkins
consumer: terraform | ansible | jenkins
artifact_or_output:
format:
version:
validation:
classification:
retention:
secret_content: false
failure_behavior:
owner:
```

## Repository Layout Example

```text
automation/
  terraform/
    environments/
    modules/
    tests/
  ansible/
    inventories/
    roles/
    playbooks/
    execution-environment.yml
  jenkins/
    Jenkinsfile
    shared-library/
  contracts/
  docs/
```

Separate repositories are also valid when ownership, release cadence, or access controls differ.

## Anti-Patterns

- Terraform configuration generated ad hoc inside a Jenkinsfile.
- Ansible playbooks embedded as multiline pipeline strings.
- Jenkins workspaces used as Terraform state or durable inventory.
- Terraform and Ansible both managing the same resource attribute.
- Jenkins environment variables becoming the undocumented system of record.
- Unversioned output parsing between tools.
- Production credentials available to build stages.
- Re-running a partially failed pipeline without understanding non-idempotent stages.
- Deleting infrastructure as the default rollback for application failures.

## Expected Output

```markdown
## Platform Ownership Map
| Concern | Owner | Caller | Artifact | Durable State or History |
|---|---|---|---|---|

## Execution Flow

## Handoff Contracts
| Producer | Consumer | Data | Validation | Failure Behavior |
|---|---|---|---|---|

## Credentials and Approvals

## Retry, Resume, and Rollback

## Repository Boundaries

## Anti-Patterns Prevented
```

## Quality Bar

- Each concern has one owner.
- Cross-tool handoffs are explicit and validated.
- Jenkins coordinates but does not absorb Terraform or Ansible logic.
- State, inventory, artifacts, and run history have distinct durable homes.
- Credentials and approvals follow least privilege.
- Retry, resume, compensation, and rollback are not conflated.
