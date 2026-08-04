# Automation Platform Selection Index

## Purpose

Provide a focused entrypoint for classifying automation capabilities, comparing incumbent and alternative products, and composing platforms with clear ownership, state, lifecycle, control-loop, recovery, migration, and governance boundaries.

## Start Here

```text
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
```

## Canonical Stack

### Agent

| Path | Use |
|---|---|
| [`agents/automation-platform-selection-advisor.md`](agents/automation-platform-selection-advisor.md) | Full category-aware decision agent, product discovery rules, scoring model, and output contract. |

### Core Skills

| Path | Use |
|---|---|
| [`skills/automation-platform-capability-taxonomy.md`](skills/automation-platform-capability-taxonomy.md) | Distinguish IaC, configuration management, CI/CD, GitOps, runbooks, managed execution, and durable workflows. |
| [`skills/automation-platform-decision-framework.md`](skills/automation-platform-decision-framework.md) | Decompose work, classify control loops, apply hard-fit and mandatory gates, and score viable products. |
| [`skills/automation-platform-candidate-discovery.md`](skills/automation-platform-candidate-discovery.md) | Build a current, edition-aware, evidence-backed longlist and shortlist from incumbents and alternatives. |
| [`skills/automation-platform-composition-and-boundaries.md`](skills/automation-platform-composition-and-boundaries.md) | Compose products with explicit ownership and typed handoff contracts. |
| [`skills/automation-platform-selection-orchestrator.md`](skills/automation-platform-selection-orchestrator.md) | Run the complete classification, discovery, comparison, challenge, migration, and pilot workflow. |

### Incumbent Fit Skills

| Path | Use |
|---|---|
| [`skills/terraform-workload-fit-analysis.md`](skills/terraform-workload-fit-analysis.md) | Evaluate Terraform resource lifecycle, state, drift, and plan/apply controls. |
| [`skills/ansible-workload-fit-analysis.md`](skills/ansible-workload-fit-analysis.md) | Evaluate Ansible configuration, deployment, inventory-driven operations, and day-2 automation. |
| [`skills/jenkins-workload-fit-analysis.md`](skills/jenkins-workload-fit-analysis.md) | Evaluate Jenkins triggers, agents, CI/CD, artifacts, approvals, plugins, and pipeline recovery. |

### Alternative Analysis Skills

| Path | Use |
|---|---|
| [`skills/infrastructure-as-code-platform-alternatives-analysis.md`](skills/infrastructure-as-code-platform-alternatives-analysis.md) | Compare Terraform, OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane, and managed IaC execution layers. |
| [`skills/configuration-management-platform-alternatives-analysis.md`](skills/configuration-management-platform-alternatives-analysis.md) | Compare Ansible/AAP/AWX, Puppet, Chef Infra, Salt, and PowerShell DSC. |
| [`skills/ci-cd-platform-alternatives-analysis.md`](skills/ci-cd-platform-alternatives-analysis.md) | Compare Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, and Tekton. |
| [`skills/gitops-runbook-and-workflow-platform-analysis.md`](skills/gitops-runbook-and-workflow-platform-analysis.md) | Evaluate Argo CD, Flux, runbook platforms, and durable workflow engines. |

### Prompts

| Path | Use |
|---|---|
| [`prompts/planning/select-automation-platform.md`](prompts/planning/select-automation-platform.md) | Select a platform architecture for a new request using current official evidence. |
| [`prompts/review/challenge-automation-platform-choice.md`](prompts/review/challenge-automation-platform-choice.md) | Review an existing implementation for category errors, misplaced ownership, and migration needs. |

### Structured Inputs and Validation

| Path | Use |
|---|---|
| [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) | Machine-readable decision brief with candidate policy, hosting, migration, and evidence controls. |
| [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Full worked input comparing incumbents with justified alternatives. |
| [`docs/automation-platform-selection-acceptance-tests.md`](docs/automation-platform-selection-acceptance-tests.md) | Behavioral, architecture, product-comparison, and validation tests. |
| [`.github/agents/automation-platform-selection-advisor.agent.md`](.github/agents/automation-platform-selection-advisor.agent.md) | Thin GitHub Copilot custom-agent wrapper. |

## Capability-First Rules

```text
Persistent provider-managed resource lifecycle
  -> infrastructure as code

Configuration or operation of existing targets
  -> configuration management or runbook automation

Triggered build, test, artifact, approval, promotion, or delivery flow
  -> CI/CD

Continuous reconciliation of version-controlled Kubernetes desired state
  -> GitOps continuous delivery

Approved parameterized operator procedures
  -> runbook automation

Long-running state, timers, retries, signals, or compensation
  -> durable workflow orchestration

Governed plans, applies, policy, state, approvals, and drift around an IaC engine
  -> managed IaC execution
```

Only after capability classification should the advisor compare products.

## Candidate Examples

```text
IaC
  Terraform, OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane

Configuration management
  Ansible/AAP/AWX, Puppet, Chef Infra, Salt, DSC

CI/CD
  Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, Tekton

GitOps
  Argo CD, Flux

Runbooks
  Rundeck, AAP/AWX, Azure Automation

Managed IaC execution
  HCP Terraform/Terraform Enterprise, Spacelift, env0, Scalr, Pulumi Cloud

Durable workflows
  Temporal, Argo Workflows, Airflow for data workflows
```

This is a candidate catalog, not a requirement to compare every product.

## Candidate Policies

```text
current_stack_only
current_stack_plus_alternatives
open_market
```

Default to `current_stack_plus_alternatives`.

## Reference Architectures

### CI/CD plus IaC and configuration

```text
GitHub Actions, Azure Pipelines, GitLab CI/CD, Jenkins, or another selected CI/CD platform
  -> IaC validate, plan or preview, policy, approval, apply
  -> validated outputs
  -> configuration-management check, canary, converge, verify
  -> CI/CD archives evidence and reports status
```

### CI/CD plus GitOps

```text
CI/CD builds, tests, scans, signs, and publishes artifact
  -> approved Git change updates deployment declaration
  -> Argo CD or Flux reconciles cluster state
```

### CI/CD plus durable workflow

```text
CI/CD deploys workflow code and workers
  -> durable workflow engine owns runtime state, timers, retries, signals, and compensation
```

These are patterns, not mandatory products.

## Core Guardrails

- Decompose and classify before selecting products.
- Assign one authoritative owner per automation unit.
- Apply mandatory gates before weighted scoring.
- Compare exact editions and hosting models.
- Keep each capability shortlist to two to four viable candidates by default.
- Use official current documentation for version-sensitive claims.
- Do not confuse execution, orchestration, reconciliation, and state ownership.
- Do not duplicate desired state between products.
- Keep native domain logic outside pipeline YAML and shell blocks.
- Do not call push-based deployment GitOps.
- Treat actions, plugins, providers, modules, collections, cookbooks, and images as supply-chain dependencies.
- Compare incumbent optimization and augmentation against migration cost.
- Address credentials, approvals, retries, resume, reconciliation, compensation, rollback, partial failure, and control-plane recovery.
- Challenge the recommendation with a proof-of-fit pilot.

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Decompose and classify the workload, compare incumbents with a small set of justified alternatives, verify current product editions through official sources, apply mandatory gates before scoring, define ownership and handoffs, compare retain/optimize/augment/migrate outcomes, and produce a proof-of-fit pilot.
```
