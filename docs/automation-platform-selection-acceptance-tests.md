# Automation Platform Selection Acceptance Tests

## Purpose

Validate that the automation platform selection stack classifies workloads before comparing products, preserves ownership boundaries, evaluates current alternatives fairly, and does not force Terraform, Ansible, or Jenkins into responsibilities they should not own.

## Test Method

For each scenario:

1. Run the canonical agent and orchestrator.
2. Confirm workload decomposition and capability classification occur before product scoring.
3. Confirm each automation unit has one authoritative owner.
4. Confirm mandatory gates are applied before weighted scoring.
5. Confirm the shortlist is limited to viable products in the correct capability class.
6. Confirm product edition, hosting model, and evidence date are visible for version-sensitive claims.
7. Confirm rejected alternatives and the runner-up are explained.
8. Confirm state, inventory, artifacts, workflow history, credentials, supply chain, approvals, recovery, migration, and evidence are addressed where applicable.
9. Confirm retain, optimize, augment, migrate, and pilot-first outcomes are considered.
10. Confirm a falsifiable proof-of-fit pilot is included for uncertain cases.

## Required Scenarios

### 1. Multi-cloud persistent infrastructure

Input:

```text
Create and manage networks, identity, managed databases, and SaaS resources across Azure and AWS. Existing Terraform modules and state are mature, but the organization wants OpenTofu and Pulumi evaluated.
```

Expected:

- The capability is infrastructure as code.
- Terraform, OpenTofu, and Pulumi are compared as IaC engines rather than against CI/CD products.
- Existing state, provider coverage, import, modules, language model, licensing, migration, and execution-layer requirements are discussed.
- Terraform may be retained when migration value is weak.
- OpenTofu compatibility is tested rather than assumed.
- Pulumi is not selected solely because developers prefer a general-purpose language.

### 2. Azure-native bounded infrastructure

Input:

```text
Manage only Azure Resource Manager resources for one Azure-native product team. The enterprise standard elsewhere is Terraform. Compare Terraform and Bicep.
```

Expected:

- The unit is explicitly bounded before a cloud-native option is considered.
- Bicep's Azure affinity and Terraform's enterprise consistency are compared.
- The result addresses state or deployment history, testing, policy, modules, skill reuse, and cross-team operating cost.
- The target being Azure does not automatically decide the result.

### 3. Existing server configuration

Input:

```text
Install packages, manage files, rotate certificates, restart services safely, and verify health across 500 existing Linux servers through operator-triggered maintenance windows.
```

Expected:

- The capability is configuration management or runbook automation.
- Ansible or Ansible Automation Platform is a strong candidate.
- Inventory, privilege, modules, idempotency, canaries, batching, partial failure, and verification are discussed.
- Puppet and Chef are not preferred unless continuous agent-based enforcement is required.
- CI/CD may schedule or gate the run but does not own target configuration.

### 4. Continuous configuration enforcement

Input:

```text
Continuously enforce baseline packages, services, security settings, and configuration across 5,000 stable Linux and Windows servers, with node reporting every 30 minutes.
```

Expected:

- The required control loop is continuous reconciliation.
- Puppet, Chef Infra, Salt, DSC, and Ansible-based scheduling are evaluated based on target coverage and topology.
- Agent, server, certificate, classification, reporting, upgrade, and support operations are included.
- Ansible is not selected automatically because it is the incumbent.
- The final shortlist remains small.

### 5. GitHub-centered CI/CD

Input:

```text
All repositories, pull requests, CODEOWNERS, and developer permissions are in GitHub Enterprise Cloud. Builds need Linux and Windows runners inside private networks, protected production environments, immutable artifacts, and reusable workflows. Compare Jenkins and GitHub Actions.
```

Expected:

- The capability is CI/CD.
- GitHub Actions and Jenkins are compared with exact hosting and runner assumptions.
- GitHub affinity is treated as a strong signal, not an automatic answer.
- Self-hosted runner isolation, action pinning, environment controls, controller operations, migration, and total cost are included.
- The result may recommend a pilot before migration.

### 6. Azure DevOps-centered CI/CD

Input:

```text
The organization uses Azure Repos, Boards, Artifacts, service connections, environments, and private Windows agents. Jenkins currently performs builds and releases. Compare Jenkins and Azure Pipelines.
```

Expected:

- Azure Pipelines is evaluated because the broader Azure DevOps operating model is relevant.
- Environments, approvals or checks, protected resources, agent pools, traceability, permissions, and migration are discussed.
- Azure as a deployment target alone is not used as the deciding reason.
- Classic and YAML capability differences are not conflated.

### 7. GitLab integrated delivery

Input:

```text
Source control, merge requests, container registry, security scanning, and issue tracking are in GitLab. Jenkins triggers scripts through GitLab webhooks. Compare Jenkins and GitLab CI/CD.
```

Expected:

- GitLab CI/CD is shortlisted based on platform integration.
- Runners, reusable components, parent or downstream pipelines, environments, approvals, edition limits, and migration are checked.
- Existing Jenkins customization and operating cost are included.
- The recommendation states why the runner-up lost.

### 8. Kubernetes GitOps

Input:

```text
Build and deploy 40 services to six Kubernetes clusters. Teams require pull-based reconciliation, drift visibility, health status, and promotion through reviewed Git changes. Compare GitHub Actions, Azure Pipelines, Argo CD, and Flux.
```

Expected:

- The request is decomposed into CI and GitOps units.
- CI/CD products own build, test, signing, artifact publication, and desired-state change proposals.
- Argo CD or Flux owns cluster reconciliation.
- CI/CD and GitOps products are not scored as if they own the same unit.
- Cluster credentials, multi-tenancy, health, drift, sync, recovery, and controller operations are discussed.

### 9. Full-stack delivery

Input:

```text
Create cloud infrastructure, configure hosts, build an application, and deploy it to Kubernetes and virtual machines.
```

Expected:

- The request is decomposed into IaC, configuration management, CI/CD, and possibly GitOps units.
- Incumbent and alternative candidates are generated per capability class.
- Each unit receives one authoritative owner.
- Handoff contracts are explicit.
- The result does not force a single product.

### 10. Misplaced Jenkins shell automation

Input:

```text
A 1,500-line Jenkinsfile uses shell commands to create cloud resources, edit server configuration, build artifacts, deploy manifests, and wait for a manual callback for three days.
```

Expected:

- The review identifies IaC, configuration, CI/CD, deployment, and durable workflow category errors.
- The target design moves domain responsibilities to native engines.
- Jenkins or an alternative CI/CD product retains only appropriate orchestration.
- The multi-day callback is evaluated for a durable workflow engine.
- The migration plan is phased and avoids an unnecessary big-bang rewrite.

### 11. Terraform provisioner misuse

Input:

```text
Terraform creates virtual machines and uses remote-exec to install all middleware and deploy the application.
```

Expected:

- The IaC engine remains the infrastructure owner.
- A configuration-management product is recommended for target convergence.
- Provisioner risks, rerun behavior, secrets, and partial failure are explained.
- Terraform, OpenTofu, and Pulumi are not compared unless engine migration is materially relevant.

### 12. Ansible cloud lifecycle overreach

Input:

```text
Ansible playbooks create and delete a large cloud estate, but no durable infrastructure state or drift process exists.
```

Expected:

- The capability is reclassified as IaC.
- A viable IaC shortlist is produced based on provider, state, hosting, and migration requirements.
- Ansible remains valid for configuration and day-2 operations.
- Import, state adoption, migration risk, and pilot scope are addressed.

### 13. Managed IaC governance

Input:

```text
Terraform code is sound, but Jenkins stores plans, applies with shared credentials, has weak policy controls, and cannot schedule drift detection. Compare HCP Terraform, Terraform Enterprise, Spacelift, env0, Scalr, and retaining Jenkins.
```

Expected:

- The IaC engine decision is separated from the managed execution decision.
- The shortlist is reduced using hosting, private execution, policy, state, approval, identity, support, and procurement gates.
- Jenkins may be retained for CI while a managed platform owns Terraform execution.
- Exact editions and official evidence dates are included.

### 14. Runbook automation

Input:

```text
Operations needs a self-service catalog for approved service restarts, certificate rotation, database failover checks, and targeted remediation with forms, RBAC, schedules, logs, and maintenance windows.
```

Expected:

- The capability is runbook automation, not generic CI/CD.
- Rundeck, Ansible Automation Platform or AWX, Azure Automation, and the incumbent are considered only when environment fit justifies them.
- The execution engine and operator surface are distinguished.
- Recovery when the primary CI platform is unavailable is addressed.

### 15. Durable business workflow

Input:

```text
Run a months-long approval workflow with timers, external callbacks, compensation steps, signals, and durable business-process state.
```

Expected:

- The capability is durable workflow orchestration.
- Temporal, a cloud workflow service, or another justified durable engine may be considered.
- Jenkins, GitHub Actions, and Azure Pipelines are not forced into the role.
- Durable state, workflow versioning, retries, compensation, worker failure, and control-plane recovery are discussed.

### 16. Air-gapped environment

Input:

```text
Automate infrastructure, configuration, and CI/CD in a disconnected environment with no SaaS control plane or public marketplace access.
```

Expected:

- SaaS-only candidates are eliminated before scoring.
- Offline installation, dependency mirroring, update process, runner or agent topology, certificates, support, and supply-chain evidence are discussed.
- Product recommendations use exact self-hosted editions.

### 17. Incumbent is still the best fit

Input:

```text
Jenkins is well maintained, uses ephemeral isolated agents, approved plugins, tested shared libraries, reliable backups, and low operating cost. GitHub hosts only a minority of repositories. No material delivery problem exists.
```

Expected:

- The advisor may recommend retaining or optimizing Jenkins.
- It does not manufacture a migration case.
- Future reevaluation triggers and measurable pilot criteria are provided.

### 18. Platform outage recovery

Input:

```text
Design an automated recovery process for the primary CI/CD controller itself.
```

Expected:

- The result identifies circular dependency risk.
- IaC and configuration ownership are evaluated by recovery unit.
- The recovery path is runnable independently of the failed controller.
- Backup, state, credentials, runner bootstrap, and break-glass procedures are addressed.

### 19. Ambiguous request

Input:

```text
Automate database deployment.
```

Expected:

- The result separates managed database resource creation, schema migration, configuration, data movement, application delivery, and pipeline coordination.
- Assumptions and confidence are explicit.
- Products are not selected based on the word `deployment` alone.

### 20. Edition and evidence discipline

Input:

```text
Recommend the cheapest product with approvals, private runners, audit logs, and one-year evidence retention.
```

Expected:

- The advisor refuses to rely on product-name memory or vague pricing claims.
- Exact editions, hosting models, current limits, licensing, and official evidence dates are required.
- Unknown pricing or procurement details are marked unknown.
- License cost is not confused with total operational cost.

## Structural Checks

The output must include:

- executive decision and migration posture
- workload decomposition
- capability and control-loop classification
- candidate policy
- mandatory gates
- product longlist and eliminations
- small product shortlist with edition and hosting model
- weighted product comparison
- ownership map and platform boundaries
- execution or reconciliation flow
- security, supply-chain, and governance controls
- failure recovery, retry, resume, reconciliation, compensation, and rollback
- migration and total-cost analysis
- anti-patterns
- proof-of-fit pilot
- rejected alternatives and runner-up explanation
- official sources and evidence dates
- unknowns

## Failure Conditions

Fail the stack if it:

- recommends a product for an undecomposed compound request
- compares products from different capability classes as direct substitutes
- assigns two authoritative owners to the same state
- scores a candidate that failed a mandatory requirement
- produces an unfiltered product catalog
- selects a CI/CD product as infrastructure, configuration, or durable workflow source of truth
- selects an IaC engine primarily for remote commands
- selects configuration management for provider-managed lifecycle without addressing state and drift
- labels push-based deployment as GitOps
- equates idempotency, retry, rerun, or reconciliation with rollback
- omits credentials, supply chain, approvals, or recovery for high-impact work
- relies exclusively on the failed platform for its own recovery
- assumes enterprise features exist in another edition or hosting model
- recommends migration without comparing incumbent optimization and migration cost
- uses stale or unofficial product claims when official documentation is available
- provides weighted scores without evidence

## Repository Validation

```bash
python3 scripts/validate-agentdefaults.py
```
