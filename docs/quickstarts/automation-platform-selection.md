# Automation Platform Selection Quickstart

## Purpose

Show how to use AgentDefaults to classify an automation workload and select the right products across infrastructure as code, configuration management, CI/CD, GitOps, runbook automation, managed IaC execution, and durable workflows.

Terraform, Ansible, and Jenkins are anchor products, not mandatory answers.

## Stack

```text
Agent:
  agents/automation-platform-selection-advisor.md

Orchestrator:
  skills/automation-platform-selection-orchestrator.md

Core decision skills:
  skills/automation-platform-capability-taxonomy.md
  skills/automation-platform-decision-framework.md
  skills/automation-platform-candidate-discovery.md
  skills/automation-platform-composition-and-boundaries.md

Incumbent fit skills:
  skills/terraform-workload-fit-analysis.md
  skills/ansible-workload-fit-analysis.md
  skills/jenkins-workload-fit-analysis.md

Alternative analysis skills:
  skills/infrastructure-as-code-platform-alternatives-analysis.md
  skills/configuration-management-platform-alternatives-analysis.md
  skills/ci-cd-platform-alternatives-analysis.md
  skills/gitops-runbook-and-workflow-platform-analysis.md

Brief:
  schemas/automation-platform-decision-brief.schema.json
  examples/automation-platform-decision-brief.yaml

Prompts:
  prompts/planning/select-automation-platform.md
  prompts/review/challenge-automation-platform-choice.md

Copilot wrapper:
  .github/agents/automation-platform-selection-advisor.agent.md

Acceptance tests:
  docs/automation-platform-selection-acceptance-tests.md
```

## Setup

1. Copy the agent, orchestrator, taxonomy, decision framework, and candidate-discovery skills into the target context.
2. Add only the category-specific fit skills needed for the workload.
3. Fill in [`../../examples/automation-platform-decision-brief.yaml`](../../examples/automation-platform-decision-brief.yaml).
4. Validate it against [`../../schemas/automation-platform-decision-brief.schema.json`](../../schemas/automation-platform-decision-brief.schema.json).
5. Choose a candidate policy: incumbent only, incumbent plus alternatives, or open market.
6. Decompose and classify the request before comparing products.
7. Apply mandatory gates before weighted scoring.
8. Verify product editions, hosting models, limits, licensing, and support through official current documentation.
9. Assign one authoritative owner to each automation unit.
10. Define handoff contracts if multiple products are required.
11. Compare retain, optimize, augment, migrate, and pilot-first outcomes.
12. Challenge the recommendation and run a proof-of-fit pilot.

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md.

Validate examples/automation-platform-decision-brief.yaml. Decompose and classify the request before selecting products. Start with the existing Terraform, Ansible, and Jenkins investments, then add only materially relevant alternatives such as OpenTofu, Pulumi, GitHub Actions, Azure Pipelines, GitLab CI/CD, Puppet, Chef, Argo CD, Flux, Rundeck, or a durable workflow engine.

Use official current documentation. Compare exact editions and hosting models. Apply mandatory hosting, target, provider, network, identity, governance, licensing, and support gates before scoring. Keep each capability shortlist to two to four viable products.

Produce:
- workload decomposition and capability classification
- candidate policy
- product longlist, mandatory gates, and eliminations
- product shortlist with editions and hosting models
- weighted decision matrix
- ownership boundaries
- execution or reconciliation flow and handoff contracts
- security, supply-chain, approval, audit, and recovery controls
- migration and total-cost analysis
- anti-patterns to avoid
- proof-of-fit pilot
- implementation backlog
- rejected alternatives, official sources, and unknowns

Do not force a single-tool answer or a migration.
```

## Minimal Invocation

```text
For this automation request, classify the capability first, then recommend the best product or bounded composition. Compare the incumbent with up to three viable alternatives, apply mandatory gates before scoring, explain why the runner-up lost, and give me a small pilot.
```

## Jenkins Alternatives Invocation

```text
Compare the current Jenkins implementation with GitHub Actions, Azure Pipelines, and GitLab CI/CD. Verify current editions and hosting models. Evaluate SCM affinity, private runners or agents, network access, environments and approvals, reusable workflows, artifacts, supply-chain governance, controller operations, migration complexity, and total cost. Recommend retain, optimize, augment, migrate, or pilot first.
```

## Configuration Management Invocation

```text
Compare Ansible or Ansible Automation Platform with Puppet, Chef Infra, Salt, and PowerShell DSC for this estate. Determine whether the workload needs agentless push execution, governed runbooks, or continuous agent-based desired-state enforcement. Include target coverage, inventory or classification, credentials, batching, reporting, controller and agent operations, migration, and support.
```

## IaC Invocation

```text
Compare Terraform with OpenTofu, Pulumi, and any justified cloud-native option. Separate the IaC engine from the managed execution layer. Verify provider coverage, state and import compatibility, plan or preview behavior, drift, policy, private execution, migration, licensing, and recovery.
```

## GitOps and Workflow Invocation

```text
Determine whether this Kubernetes deployment needs conventional CI/CD, Argo CD, Flux, or a composition. If the workflow includes long waits, durable retries, timers, signals, or compensation, also evaluate a durable workflow engine rather than using long-running CI jobs.
```

## Example Decisions

### GitHub-hosted application with private deployment targets

```text
GitHub Actions may own CI/CD when GitHub governance, reusable workflows, environment protection, and private self-hosted runners satisfy requirements.
Terraform or another IaC engine still owns infrastructure lifecycle.
Ansible or another configuration platform still owns host convergence.
```

### Azure DevOps enterprise estate

```text
Azure Pipelines may be stronger than Jenkins when Azure Repos, Boards, Artifacts, service connections, protected resources, environments, and private agents already form the operating model.
The target being Azure alone is not sufficient reason to choose it.
```

### Large continuously enforced server fleet

```text
Puppet or Chef may outrank Ansible when recurring agent-based desired-state enforcement and node reporting are mandatory.
Ansible may remain the better runbook or deployment tool, producing a bounded composition.
```

### Kubernetes GitOps delivery

```text
CI builds, tests, signs, and publishes the artifact.
A Git change updates the deployment declaration.
Argo CD or Flux reconciles the cluster.
```

### Long-running operational process

```text
CI/CD may deploy and trigger the workflow.
A durable workflow engine owns multi-day state, retries, timers, signals, and compensation.
```

## Approval Boundaries

A recommendation or design does not automatically authorize:

- IaC apply, destroy, import, state move, repair, or backend migration.
- Configuration execution against production targets.
- CI/CD job, credential, plugin, runner, agent, controller, environment, or organization changes.
- GitOps synchronization or cluster registration.
- Runbook execution or privilege escalation.
- Workflow-engine deployment or production workflow start.
- Production deployment or rollback.
- Product purchase, license change, or migration.

## Validation

Use [`../automation-platform-selection-acceptance-tests.md`](../automation-platform-selection-acceptance-tests.md).

Repository validation:

```bash
python3 scripts/validate-agentdefaults.py
```

## Known Limitations

- Product capabilities, editions, limits, licensing, pricing, and support lifecycles change and must be verified.
- A maintained provider, module, action, plugin, collection, cookbook, controller, or integration can change the best path.
- Weighted scoring cannot override category mismatch or a mandatory requirement.
- Source-control or cloud affinity is not an automatic decision.
- Migration value must exceed migration and future operating cost.
- A proof-of-fit pilot is still required for uncertain integration, compatibility, connectivity, scale, governance, or recovery behavior.
