# GitOps, Runbook, and Workflow Platform Analysis

## Purpose

Identify when Terraform, Ansible, Jenkins, and conventional CI/CD products are not the correct primary platform because the workload instead requires GitOps reconciliation, operator-facing runbooks, or durable workflow orchestration.

## When To Use

Use when the workload includes:

- continuous Kubernetes reconciliation
- cluster drift detection and self-healing
- operator-triggered or scheduled maintenance procedures
- self-service operational jobs
- long-running, stateful, or event-driven workflows
- compensation, durable timers, or external waits
- data-oriented workflow scheduling

## Capability Routing

### GitOps Continuous Delivery

Consider:

```text
Argo CD
Flux
```

Use when version-controlled desired state must be continuously reconciled into Kubernetes clusters.

Hard requirements:

- Kubernetes is the deployment control plane
- Git or another supported source is authoritative
- pull-based reconciliation is desired
- cluster credentials remain with the controller rather than a central push runner
- drift visibility, health, sync, and rollback-through-Git semantics fit the operating model

Do not recommend GitOps merely because a CI pipeline runs `kubectl apply`.

### Runbook and Operational Automation

Consider:

```text
Rundeck
Red Hat Ansible Automation Platform / AWX
Azure Automation
Jenkins only when a pipeline model genuinely fits
```

Use when operators need approved, parameterized, repeatable jobs with RBAC, scheduling, target selection, logs, and evidence.

Hard requirements:

- operator or service-catalog entrypoint
- parameter validation and authorization
- target inventory or node selection
- controlled credentials and privilege
- maintenance-window and concurrency controls
- evidence retention and notification
- recovery when the automation controller is unavailable

### Durable Workflow Orchestration

Consider:

```text
Temporal
Argo Workflows
cloud-native workflow services
Apache Airflow when data pipelines dominate
```

Use when workflow state, retries, timers, compensation, or waits must survive worker and controller restarts.

Hard requirements:

- long-running or stateful execution
- durable workflow history
- explicit retry and compensation semantics
- event or message integration
- versioning of running workflows
- operational visibility into stuck or failed executions

A conventional CI/CD pipeline may still trigger a durable workflow, but should not own its durable business state.

## Product Fit Profiles

These profiles are starting hypotheses. Verify current official documentation and editions.

### Argo CD

Consider when:

- Kubernetes application delivery, health, synchronization, and multi-cluster visibility are central
- a UI, API, RBAC, application model, and sync controls are valuable
- GitOps reconciliation should be distinct from CI

### Flux

Consider when:

- composable Kubernetes controllers and APIs fit the platform architecture
- GitOps should be deeply Kubernetes-native and automation-oriented
- teams prefer a toolkit approach over a centralized application UI

### Rundeck

Consider when:

- operations teams need job definitions, forms, schedules, RBAC, node targeting, logs, and self-service
- existing scripts or tools need a governed runbook surface

Do not use Rundeck as the source of truth for infrastructure or configuration that belongs in an IaC or configuration-management engine.

### Ansible Automation Platform / AWX

Consider when:

- runbooks are already implemented as Ansible content
- centralized inventories, credentials, execution environments, workflows, surveys, schedules, and RBAC are required
- avoiding a separate job platform is valuable

### Azure Automation

Consider when:

- Azure-native operational automation, identity, scheduling, and hybrid execution fit the estate
- Microsoft platform integration is a hard requirement

Verify current runtime, worker, networking, and support constraints.

### Temporal

Consider when:

- application-level workflows require durable execution, retries, timers, signals, and compensation
- workflow history must survive process failure
- developers can own workflow code and worker operations

### Argo Workflows

Consider when:

- Kubernetes-native DAG or step workflows are required
- containerized tasks and cluster execution fit the workload
- the organization can operate the controller and workflow archive

Do not confuse Argo Workflows with Argo CD; they solve different control problems.

### Apache Airflow

Consider when:

- data pipelines, scheduled DAGs, and data-platform integrations dominate
- workflow semantics align with batch-oriented data orchestration

Do not recommend Airflow as a generic infrastructure or application deployment engine.

## Comparison Questions

For GitOps candidates:

- What source is authoritative?
- What reconciles continuously?
- How are drift, health, sync, promotion, and rollback represented?
- How are cluster credentials and multi-tenancy controlled?
- How does CI hand off immutable artifacts and desired-state changes?

For runbook candidates:

- Who may launch which job against which targets?
- How are inputs validated?
- Where do inventory, credentials, logs, and evidence live?
- Can operations run if the primary CI platform is unavailable?
- How are maintenance windows, concurrency, and partial failure handled?

For durable workflow candidates:

- What state must survive executor loss?
- How long can a workflow run or wait?
- What retries, timers, signals, and compensation are required?
- How are workflow code changes handled for in-flight executions?
- What is the recovery model for the workflow control plane?

## Composition Patterns

### CI plus GitOps

```text
CI platform
-> build, test, scan, sign, and publish immutable artifact
-> update version-controlled deployment declaration
-> GitOps controller reconciles cluster state
-> health and sync status feed release evidence
```

### Runbook plus Configuration Engine

```text
runbook platform
-> authorize operator and validate parameters
-> invoke versioned Ansible or other automation content
-> execute against approved inventory
-> verify and archive evidence
```

### CI plus Durable Workflow

```text
CI/CD platform
-> deploy workflow code and workers
-> trigger or publish an event
-> durable workflow engine owns runtime state, retries, timers, and compensation
```

## Anti-Patterns

- calling push-based manifest deployment GitOps
- using a GitOps controller to build application artifacts
- using a runbook UI as the durable source of desired configuration
- using Jenkins sleep loops for multi-day business workflows
- using Airflow for generic server configuration
- selecting a Kubernetes-native workflow engine when Kubernetes operation is not strategic
- making incident recovery depend solely on the failed CI controller

## Expected Output

```markdown
## Missing Capability Detection

## Candidate Category and Shortlist
| Product | Capability | Best Fit | Main Gap | Mandatory Gates |
|---|---|---|---|---|

## Control Plane and Source of Truth

## Composition with IaC, Configuration, and CI/CD

## Failure and Recovery Model

## Recommendation
```

## Quality Bar

- GitOps, runbook, and durable workflow needs are distinguished.
- The primary control loop and durable state are explicit.
- CI/CD remains responsible only for appropriate build and release concerns.
- Product recommendations include control-plane recovery and operational ownership.
- The recommendation states when a current-stack product remains sufficient.
