# Automation Platform Capability Taxonomy

## Purpose

Classify an automation workload by the control model and lifecycle it requires before comparing products. This prevents category errors such as comparing a configuration-management controller directly with a CI runner or using a pipeline engine as the source of truth for infrastructure.

## When To Use

Use at the start of every automation-platform selection, architecture review, consolidation exercise, or migration analysis.

## Inputs Needed

- desired business outcome
- target systems and environments
- current and desired state
- lifecycle actions
- trigger and frequency
- source of truth
- state, inventory, artifact, and history requirements
- failure, retry, resume, rollback, and reconciliation expectations
- hosting, connectivity, security, and governance constraints

## Capability Classes

### Infrastructure as Code and Resource Lifecycle

Owns the declared lifecycle of persistent provider-managed resources.

Typical responsibilities:

- create, read, update, replace, import, and destroy resources
- maintain resource identity and state
- preview or plan changes
- detect or reconcile drift
- compose reusable infrastructure modules or components

Representative products:

```text
Terraform
OpenTofu
Pulumi
AWS CloudFormation
Azure Bicep
Crossplane
```

### Configuration Management and Fleet Convergence

Owns the desired configuration or operational state of existing machines, devices, middleware, applications, or endpoints.

Typical responsibilities:

- package, file, service, user, policy, and certificate management
- inventory-driven execution
- recurring desired-state enforcement
- patching, remediation, deployment, and day-2 operations
- node classification and configuration reporting

Representative products:

```text
Ansible / Red Hat Ansible Automation Platform / AWX
Puppet
Chef Infra
Salt
PowerShell Desired State Configuration
```

### Continuous Integration and Delivery Orchestration

Owns triggered build, test, scan, package, approval, promotion, and deployment-stage sequencing.

Typical responsibilities:

- source-control, webhook, schedule, API, or manual triggers
- jobs, stages, matrices, fan-out, and dependencies
- runner or agent scheduling
- artifact and test-result handling
- deployment environments, approvals, and run history

Representative products:

```text
Jenkins
GitHub Actions
Azure Pipelines
GitLab CI/CD
CircleCI
Buildkite
Tekton Pipelines
```

### GitOps Continuous Delivery and Reconciliation

Owns continuous reconciliation of deployed state from version-controlled desired state, most commonly for Kubernetes.

Typical responsibilities:

- pull-based reconciliation
- drift detection and self-healing
- cluster and application deployment status
- promotion through Git changes
- declarative rollback through version control

Representative products:

```text
Argo CD
Flux
```

Do not classify ordinary CI pipelines as GitOps merely because they apply manifests from Git.

### Runbook and Operational Job Automation

Owns controlled, repeatable, operator-facing execution of operational procedures.

Typical responsibilities:

- approved self-service jobs
- scheduled maintenance
- incident and remediation runbooks
- inventory-aware execution
- operator permissions, forms, logs, and evidence

Representative products:

```text
Rundeck
Red Hat Ansible Automation Platform / AWX
Azure Automation
Jenkins, only when the workflow genuinely fits a pipeline model
```

### Managed IaC Execution and Governance

Provides controlled execution, policy, state, approvals, drift, and organizational workflows around infrastructure-as-code engines.

Typical responsibilities:

- remote plans and applies
- state and workspace governance
- policy enforcement
- run approvals and audit evidence
- drift scheduling and private runners or agents

Representative products:

```text
HCP Terraform / Terraform Enterprise
Spacelift
env0
Scalr
Pulumi Cloud
```

These platforms do not automatically replace the underlying IaC language or resource ownership model.

### Durable Workflow and Event Orchestration

Owns long-running, stateful, resumable workflows whose lifetime or failure semantics exceed a conventional CI/CD pipeline.

Typical responsibilities:

- durable timers and retries
- compensation and saga patterns
- event-driven business workflows
- long waits for external systems or human actions
- workflow state that survives worker or controller restarts

Representative products:

```text
Temporal
Argo Workflows
Apache Airflow for data-oriented workflows
cloud-native workflow services
```

Do not recommend a CI/CD platform merely because it can wait or retry if durable workflow state is the central requirement.

### Policy, Secrets, Scheduling, and Service Management

These are adjacent capability classes that may be required but should not be mistaken for the primary automation owner.

Examples:

```text
policy as code
secrets management
enterprise schedulers
IT service management
artifact repositories
observability and incident management
```

## Classification Method

For each automation unit, record:

```text
capability_class
control_loop: one_shot | event_driven | scheduled | continuous_reconciliation | durable_workflow
authoritative_source_of_truth
durable_state_or_history
target_model
execution_location
failure_semantics
approval_model
```

Use the control loop as a major discriminator:

- `one_shot` favors direct execution or runbook tools.
- `event_driven` favors CI/CD or workflow orchestration.
- `scheduled` may fit CI/CD, runbook, or scheduler platforms.
- `continuous_reconciliation` favors IaC drift workflows, configuration agents, or GitOps controllers.
- `durable_workflow` favors a workflow engine rather than a conventional pipeline.

## Category Error Checks

Reject or challenge recommendations that:

- use a CI/CD runner as the authoritative infrastructure state store
- use an IaC provisioner as the main configuration-management system
- call a push-based deployment pipeline GitOps without continuous reconciliation
- use a configuration-management controller as a general build system
- use a short-lived pipeline for a long-running business workflow without durable state
- recommend a managed execution service without naming the underlying automation engine
- compare products from different capability classes without first decomposing the workload

## Expected Output

```markdown
## Capability Classification
| Unit | Capability Class | Control Loop | Source of Truth | Durable State or History | Candidate Category |
|---|---|---|---|---|---|

## Category Boundaries

## Adjacent Capabilities Required

## Category Errors Avoided
```

## Quality Bar

- Every unit is classified before products are scored.
- Product comparisons stay within the correct capability class unless composition is being designed.
- The control loop and durable-state requirements are explicit.
- Adjacent services are identified without being promoted to authoritative owners.
- The taxonomy can express that no current category or product is sufficient.
