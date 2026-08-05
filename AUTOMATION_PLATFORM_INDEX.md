# Automation Platform Selection Index

## Purpose

Provide a focused entrypoint for classifying automation capabilities, comparing incumbent and alternative products, measuring evidence quality, modeling migration economics, and composing platforms with clear ownership, state, lifecycle, control-loop, recovery, and governance boundaries.

## Start Here

```text
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
```

## Output Depth

```text
quick_triage
  Compact capability decision, blockers, recommendation posture, strongest alternative, confidence, and next validation step.

standard
  Evidence-backed shortlist, ownership boundaries, migration posture, and pilot. Default.

full_architecture_review
  Complete evidence ledger, confidence-adjusted scoring, economics, handoffs, recovery, migration waves, and ADR-ready decision.
```

## Canonical Stack

### Agent

| Path | Use |
|---|---|
| [`agents/automation-platform-selection-advisor.md`](agents/automation-platform-selection-advisor.md) | Category-aware decision agent with product discovery, evidence, confidence, economics, composition, and output contracts. |

### Core Skills

| Path | Use |
|---|---|
| [`skills/automation-platform-capability-taxonomy.md`](skills/automation-platform-capability-taxonomy.md) | Canonical capability identifiers and control-loop classification. |
| [`skills/automation-platform-decision-framework.md`](skills/automation-platform-decision-framework.md) | Decompose work, validate constraints, apply hard-fit and mandatory gates, and compare viable products. |
| [`skills/automation-platform-candidate-discovery.md`](skills/automation-platform-candidate-discovery.md) | Build a current, edition-aware longlist and shortlist from incumbents and alternatives. |
| [`skills/automation-platform-evidence-and-confidence.md`](skills/automation-platform-evidence-and-confidence.md) | Build the evidence ledger, separate fit from confidence, calculate coverage, and handle effective ties. |
| [`skills/automation-platform-migration-and-economics.md`](skills/automation-platform-migration-and-economics.md) | Compare retain, optimize, augment, migrate, and pilot-first using total cost, reversibility, and migration waves. |
| [`skills/automation-platform-composition-and-boundaries.md`](skills/automation-platform-composition-and-boundaries.md) | Compose products with one authoritative owner per unit and typed handoff contracts. |
| [`skills/automation-platform-selection-orchestrator.md`](skills/automation-platform-selection-orchestrator.md) | Run the complete classification, discovery, evidence, comparison, economics, challenge, and pilot workflow. |

### Incumbent Fit Skills

| Path | Use |
|---|---|
| [`skills/terraform-workload-fit-analysis.md`](skills/terraform-workload-fit-analysis.md) | Evaluate Terraform resource lifecycle, state, drift, and plan/apply controls. |
| [`skills/ansible-workload-fit-analysis.md`](skills/ansible-workload-fit-analysis.md) | Evaluate Ansible configuration, deployment, inventory-driven operations, and day-two automation. |
| [`skills/jenkins-workload-fit-analysis.md`](skills/jenkins-workload-fit-analysis.md) | Evaluate Jenkins triggers, agents, CI/CD, artifacts, approvals, plugins, and pipeline recovery. |

### Alternative Analysis Skills

| Path | Use |
|---|---|
| [`skills/infrastructure-as-code-platform-alternatives-analysis.md`](skills/infrastructure-as-code-platform-alternatives-analysis.md) | Compare Terraform, OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane, and managed execution layers. |
| [`skills/configuration-management-platform-alternatives-analysis.md`](skills/configuration-management-platform-alternatives-analysis.md) | Compare Ansible/AAP/AWX, Puppet, Chef Infra, Salt, and PowerShell DSC. |
| [`skills/ci-cd-platform-alternatives-analysis.md`](skills/ci-cd-platform-alternatives-analysis.md) | Compare Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, and Tekton. |
| [`skills/gitops-runbook-and-workflow-platform-analysis.md`](skills/gitops-runbook-and-workflow-platform-analysis.md) | Evaluate Argo CD, Flux, runbook platforms, and durable workflow engines. |

### Prompts

| Path | Use |
|---|---|
| [`prompts/planning/select-automation-platform.md`](prompts/planning/select-automation-platform.md) | Select a new architecture with configurable output depth, evidence coverage, and migration economics. |
| [`prompts/review/challenge-automation-platform-choice.md`](prompts/review/challenge-automation-platform-choice.md) | Review an existing implementation, separate product limits from implementation defects, and produce the smallest safe correction. |

### Structured Inputs and Validation

| Path | Use |
|---|---|
| [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) | Brief contract with canonical enums, hosting consistency, output depth, risk, horizon, evidence, and scoring controls. |
| [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Full worked input with incumbents, alternatives, content inventory, operating burden, evidence threshold, and custom weights. |
| [`docs/automation-platform-selection-acceptance-tests.md`](docs/automation-platform-selection-acceptance-tests.md) | Twenty-five behavioral, architecture, evidence, economics, and output-discipline scenarios. |
| [`.github/agents/automation-platform-selection-advisor.agent.md`](.github/agents/automation-platform-selection-advisor.agent.md) | Thin GitHub Copilot custom-agent wrapper. |

## Canonical Capability Identifiers

```text
infrastructure_as_code
configuration_management
ci_cd
gitops_continuous_delivery
runbook_automation
managed_iac_execution
durable_workflow_orchestration
verification_and_reporting
adjacent_capability
unsupported_capability
```

Use these exact identifiers in briefs, schemas, reports, and validation.

## Capability-First Rules

```text
Persistent provider-managed resource lifecycle
  -> infrastructure_as_code

Configuration or operation of existing targets
  -> configuration_management or runbook_automation

Triggered build, test, artifact, approval, promotion, or delivery flow
  -> ci_cd

Continuous reconciliation of version-controlled Kubernetes desired state
  -> gitops_continuous_delivery

Approved parameterized operator procedures
  -> runbook_automation

Long-running state, timers, retries, signals, or compensation
  -> durable_workflow_orchestration

Governed plans, applies, policy, state, approvals, and drift around an IaC engine
  -> managed_iac_execution
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

## Decision Rules

- Validate contradictory constraints before analysis.
- Decompose and classify before selecting products.
- Assign one authoritative owner per automation unit.
- Apply mandatory gates before weighted scoring.
- Compare exact editions and hosting models.
- Keep each capability shortlist to two to four viable candidates by default.
- Use observed configuration and official current documentation for version-sensitive claims.
- Keep raw fit, evidence confidence, and unknowns separate.
- Do not score unknowns as zero or include non-applicable criteria in the denominator.
- Treat candidates within 5 percent as effectively tied unless a hard requirement or material operating difference decides the result.
- Do not confuse execution, orchestration, reconciliation, governance, and state ownership.
- Do not duplicate desired state between products.
- Keep native domain logic outside pipeline YAML and shell blocks.
- Do not call push-based deployment GitOps.
- Treat actions, plugins, providers, modules, collections, cookbooks, and images as supply-chain dependencies.
- Compare retain, optimize, augment, migrate, and pilot-first against the do-nothing baseline.
- Include one-time cost, recurring burden, dual running, reversibility, and exit strategy.
- Challenge the recommendation with a proof-of-fit pilot, rollback, and stopping rule.

## Reference Architectures

### CI/CD plus IaC and configuration

```text
selected CI/CD product
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

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Use standard output depth. Decompose and classify the workload, compare incumbents with a small set of justified alternatives, verify exact editions through official sources, apply mandatory gates before scoring, keep fit separate from confidence, compare migration economics and reversibility, define ownership and handoffs, and produce a proof-of-fit pilot with a stopping rule.
```
