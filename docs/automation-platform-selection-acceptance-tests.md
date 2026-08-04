# Automation Platform Selection Acceptance Tests

## Purpose

Validate that the automation platform selection stack chooses owners by workload semantics, preserves platform boundaries, and does not force Terraform, Ansible, or Jenkins into responsibilities they should not own.

## Test Method

For each scenario:

1. Run the canonical agent and orchestrator.
2. Confirm workload decomposition occurs before scoring.
3. Confirm each automation unit has one authoritative owner.
4. Confirm rejected alternatives are explained.
5. Confirm state, inventory, triggers, credentials, approvals, recovery, and evidence are addressed where applicable.
6. Confirm a falsifiable proof-of-fit pilot is included for uncertain cases.

## Required Scenarios

### 1. Persistent cloud infrastructure

Input:

```text
Create and manage virtual networks, subnets, route tables, security groups, and managed databases across three environments. Detect drift and support controlled destroy.
```

Expected:

- Terraform is the authoritative owner.
- State backend, locking, plan, approval, replacement, drift, and destroy controls are discussed.
- Jenkins may orchestrate but is not the source of truth.
- Ansible is limited to configuration outside provider-managed resource ownership.

### 2. Existing server configuration

Input:

```text
Install packages, manage configuration files, rotate certificates, restart services safely, and verify health across 500 existing Linux servers.
```

Expected:

- Ansible is the authoritative owner.
- Inventory, privilege, modules, idempotency, canaries, batching, partial failure, and verification are discussed.
- Jenkins may schedule or gate the run.
- Terraform is not selected merely because desired state exists.

### 3. Application CI/CD

Input:

```text
On every merge, build, test, scan, package, approve, and promote an immutable application artifact through test and production.
```

Expected:

- Jenkins is the authoritative pipeline owner.
- Artifact provenance, credentials, approvals, parallelism, concurrency, retries, and retained evidence are discussed.
- Infrastructure and target configuration are kept outside the Jenkinsfile.

### 4. Full-stack delivery

Input:

```text
Create cloud infrastructure, configure hosts, build an application, and deploy it to production.
```

Expected:

- The request is decomposed.
- Terraform owns infrastructure lifecycle.
- Ansible owns host and application configuration or deployment.
- Jenkins owns triggering, build, test, approvals, artifacts, and coordination.
- Handoff contracts are explicit.

### 5. Misplaced Jenkins shell automation

Input:

```text
A 1,500-line Jenkinsfile uses shell commands to create cloud resources, edit server configuration, build artifacts, and deploy them.
```

Expected:

- The review identifies misplaced responsibilities and hidden state.
- The target design moves infrastructure to Terraform and configuration or deployment to Ansible.
- Jenkins retains orchestration.
- The migration plan is phased and does not demand an unnecessary big-bang rewrite.

### 6. Terraform provisioner misuse

Input:

```text
Terraform creates virtual machines and uses remote-exec to install all middleware and deploy the application.
```

Expected:

- Terraform remains the infrastructure owner.
- Ansible is recommended for configuration and deployment.
- Provisioner risks, rerun behavior, secrets, and partial failure are explained.

### 7. Ansible cloud lifecycle overreach

Input:

```text
Ansible playbooks create and delete a large cloud estate, but no durable infrastructure state or drift process exists.
```

Expected:

- Terraform is recommended for provider-managed resource lifecycle when provider coverage is suitable.
- Ansible remains valid for configuration and day-2 operations.
- Import, state adoption, migration risk, and pilot scope are addressed.

### 8. None of the supported platforms fits

Input:

```text
Run a months-long human approval workflow with timers, external callbacks, compensation steps, and durable business-process state.
```

Expected:

- The result states `insufficient_supported_platforms`.
- It identifies the missing durable workflow or orchestration capability class.
- It does not force the workload into Jenkins merely because Jenkins supports pipelines.

### 9. Platform outage recovery

Input:

```text
Design an automated recovery process for the Jenkins controller itself.
```

Expected:

- The result identifies circular dependency risk.
- Terraform or Ansible ownership is evaluated by recovery unit.
- The recovery path is runnable independently of the failed controller.

### 10. Ambiguous request

Input:

```text
Automate database deployment.
```

Expected:

- The result separates managed database resource creation, schema migration, configuration, application delivery, and pipeline coordination.
- Assumptions and confidence are explicit.
- The agent does not select a tool based on the word `deployment` alone.

## Structural Checks

The output must include:

- executive decision
- workload decomposition
- hard-fit analysis
- ownership map
- platform boundaries
- execution flow
- security and governance
- failure recovery
- anti-patterns
- proof-of-fit pilot
- rejected alternatives
- unknowns

## Failure Conditions

Fail the stack if it:

- recommends one platform for an undecomposed compound request
- assigns two authoritative owners to the same state
- selects Jenkins as infrastructure or configuration source of truth
- selects Terraform primarily for remote commands
- selects Ansible for provider-managed lifecycle without addressing state and drift
- equates idempotency with rollback
- omits credentials, approvals, or recovery for high-impact work
- relies exclusively on the failed platform for its own recovery
- cannot state that the supported platform set is insufficient
- provides weighted scores without evidence

## Repository Validation

```bash
python3 scripts/validate-agentdefaults.py
```
