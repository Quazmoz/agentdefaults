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
  skills/automation-platform-evidence-and-confidence.md
  skills/automation-platform-migration-and-economics.md
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

## Choose an Output Depth

```text
quick_triage
  Capability, blockers, recommended posture and product, strongest alternative, confidence, and next validation step.

standard
  Shortlist, evidence-backed comparison, ownership boundaries, migration posture, and pilot. Default.

full_architecture_review
  Evidence ledger, confidence-adjusted scoring, economics, handoffs, recovery, migration waves, and ADR-ready decision.
```

Use the smallest mode that satisfies the request. High-risk controls still apply in every mode.

## Setup

1. Copy the agent, orchestrator, taxonomy, decision framework, candidate-discovery, evidence, and economics skills into the target context.
2. Add only the category-specific fit skills needed for the workload.
3. Fill in [`../../examples/automation-platform-decision-brief.yaml`](../../examples/automation-platform-decision-brief.yaml).
4. Validate it against [`../../schemas/automation-platform-decision-brief.schema.json`](../../schemas/automation-platform-decision-brief.schema.json).
5. Resolve contradictory hosting, product, capability, and migration constraints before analysis.
6. Choose candidate policy and output depth.
7. Decompose and classify the request before comparing products.
8. Apply mandatory gates before weighted scoring.
9. Verify exact product editions, hosting models, limits, licensing, lifecycle, and support through official current documentation.
10. Keep raw fit, evidence confidence, and unknowns separate.
11. Assign one authoritative owner to each automation unit.
12. Define handoff contracts if multiple products are required.
13. Compare retain, optimize, augment, migrate, and pilot-first against the do-nothing baseline.
14. Include migration cost, dual running, recurring burden, reversibility, and exit strategy.
15. Challenge the recommendation and run a proof-of-fit pilot.

## Copy-Paste Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md.

Validate examples/automation-platform-decision-brief.yaml. Use standard output depth. Decompose and classify the request before selecting products. Start with the existing Terraform, Ansible, and Jenkins investments, then add only materially relevant alternatives such as OpenTofu, Pulumi, GitHub Actions, Azure Pipelines, GitLab CI/CD, Puppet, Chef, Argo CD, Flux, Rundeck, or a durable workflow engine.

Use official current documentation. Compare exact editions and hosting models. Apply mandatory hosting, target, provider, network, identity, governance, licensing, lifecycle, and support gates before scoring. Keep each capability shortlist to two to four viable products.

Keep raw fit and evidence confidence separate. Do not score unknowns as zero. Report evidence coverage, treat close scores as ties, and prefer pilot-first when a material gate or product fact is unresolved.

Compare retain, optimize, augment, migrate, and pilot-first against the do-nothing baseline. Include one-time migration cost, recurring operating burden, dual running, reversibility, and exit strategy over the decision horizon.

Produce the ownership boundaries, execution or reconciliation flow, controls, proof-of-fit pilot, implementation backlog, rejected alternatives, evidence ledger, and unknowns required by the selected output depth.

Do not force a single-tool answer or a migration.
```

## Minimal Invocation

```text
Use quick_triage output. Classify this automation request, identify mandatory blockers, recommend retain, optimize, augment, migrate, or pilot-first, compare the strongest alternative, state confidence, and give the next validation step.
```

## Full Review Invocation

```text
Use full_architecture_review output. Build an evidence ledger, calculate evidence coverage, compare exact product editions and hosting models, produce confidence-adjusted scoring, model retain/optimize/augment/migrate economics over 36 months, define reversibility and migration waves, and create an ADR-ready decision.
```

## Jenkins Alternatives Invocation

```text
Compare the current Jenkins implementation with GitHub Actions, Azure Pipelines, and GitLab CI/CD. Verify exact editions and hosting models. Evaluate SCM affinity, private runners or agents, network access, environments and approvals, reusable workflows, artifacts, supply-chain governance, controller operations, evidence quality, migration complexity, reversibility, and total cost. Recommend retain, optimize, augment, migrate, or pilot-first.
```

## Configuration Management Invocation

```text
Compare Ansible or Ansible Automation Platform with Puppet, Chef Infra, Salt, and PowerShell DSC for this estate. Determine whether the workload needs agentless push execution, governed runbooks, or continuous agent-based desired-state enforcement. Include target coverage, inventory or classification, credentials, batching, reporting, controller and agent operations, migration, evidence confidence, and support.
```

## IaC Invocation

```text
Compare Terraform with OpenTofu, Pulumi, and any justified cloud-native option. Separate the IaC engine from the managed execution layer. Verify provider coverage, state and import compatibility, plan or preview behavior, drift, policy, private execution, migration, licensing, recovery, evidence quality, and exit strategy.
```

## GitOps and Workflow Invocation

```text
Determine whether this Kubernetes deployment needs conventional CI/CD, Argo CD, Flux, or a composition. If the workflow includes long waits, durable retries, timers, signals, or compensation, also evaluate a durable workflow engine rather than using long-running CI jobs.
```

## Example Decisions

### GitHub-hosted application with private deployment targets

```text
GitHub Actions may own CI/CD when GitHub governance, reusable workflows, environment protection, and private self-hosted runners satisfy verified requirements.
Terraform or another IaC engine still owns infrastructure lifecycle.
Ansible or another configuration platform still owns host convergence.
```

### Azure DevOps enterprise estate

```text
Azure Pipelines may be stronger than Jenkins when Azure Repos, Boards, Artifacts, service connections, protected resources, environments, and private agents form the operating model.
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
- Evidence confidence and product fit are different dimensions.
- Migration value must exceed migration and future operating cost.
- A proof-of-fit pilot is still required for uncertain integration, compatibility, connectivity, scale, governance, recovery, economics, or usability behavior.
