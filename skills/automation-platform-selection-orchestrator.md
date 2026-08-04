# Automation Platform Selection Orchestrator

## Purpose

Coordinate workload intake, capability classification, candidate discovery, product-fit analysis, composition design, proof-of-fit validation, and a final recommendation across incumbent and alternative automation platforms.

## When To Use

Use for a complete platform-selection exercise, architecture review, consolidation decision, or migration from automation that has accumulated in the wrong tool.

## Required Inputs

Prefer `schemas/automation-platform-decision-brief.schema.json`.

At minimum:

- requested outcome
- targets and environments
- current implementation and products
- lifecycle actions
- triggers, frequency, and control-loop requirements
- systems of record
- source-control, cloud, and artifact platforms
- hosting, runner, agent, controller, network, and privilege constraints
- credentials, identity, approvals, and audit requirements
- rollback, resume, compensation, and recovery expectations
- organizational ownership
- licensing, support, procurement, migration, and budget constraints
- candidate policy

## Canonical Sequence

```text
1. validate the brief
2. restate the outcome, constraints, and candidate policy
3. decompose into automation units
4. classify capability and control loop for each unit
5. identify sources of truth and durable state or history
6. apply category hard-fit rules
7. build a product longlist from incumbents and justified alternatives
8. verify current product and edition facts through official sources
9. apply mandatory elimination gates
10. run incumbent Terraform, Ansible, and Jenkins fit analysis where applicable
11. run category-specific alternative analysis where applicable
12. score only viable shortlisted products
13. identify disqualifiers, category errors, and anti-patterns
14. define product ownership boundaries
15. design handoff contracts and execution or reconciliation flow
16. define credentials, supply-chain controls, approvals, evidence, and recovery
17. compare retain, optimize, augment, migrate, and pilot-first options
18. challenge the recommendation
19. define a proof-of-fit pilot
20. produce the recommendation, migration posture, and backlog
```

## Skill Routing

Use:

- [`automation-platform-capability-taxonomy.md`](automation-platform-capability-taxonomy.md) for capability classes and control-loop classification.
- [`automation-platform-decision-framework.md`](automation-platform-decision-framework.md) for decomposition, hard-fit rules, elimination gates, and scoring.
- [`automation-platform-candidate-discovery.md`](automation-platform-candidate-discovery.md) for current evidence, longlist generation, elimination, and shortlisting.
- [`terraform-workload-fit-analysis.md`](terraform-workload-fit-analysis.md) for incumbent Terraform resource-lifecycle analysis.
- [`ansible-workload-fit-analysis.md`](ansible-workload-fit-analysis.md) for incumbent Ansible configuration and operations analysis.
- [`jenkins-workload-fit-analysis.md`](jenkins-workload-fit-analysis.md) for incumbent Jenkins pipeline analysis.
- [`infrastructure-as-code-platform-alternatives-analysis.md`](infrastructure-as-code-platform-alternatives-analysis.md) for Terraform, OpenTofu, Pulumi, cloud-native IaC, Crossplane, and managed execution comparisons.
- [`configuration-management-platform-alternatives-analysis.md`](configuration-management-platform-alternatives-analysis.md) for Ansible, AAP/AWX, Puppet, Chef, Salt, and DSC comparisons.
- [`ci-cd-platform-alternatives-analysis.md`](ci-cd-platform-alternatives-analysis.md) for Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, and Tekton comparisons.
- [`gitops-runbook-and-workflow-platform-analysis.md`](gitops-runbook-and-workflow-platform-analysis.md) for Argo CD, Flux, runbook platforms, and durable workflow engines.
- [`automation-platform-composition-and-boundaries.md`](automation-platform-composition-and-boundaries.md) when more than one product is justified.

## Candidate Policies

```text
current_stack_only
  Evaluate only explicitly approved incumbents.

current_stack_plus_alternatives
  Evaluate incumbents and add materially relevant products. This is the default.

open_market
  Build the shortlist from the capability class and constraints without incumbent preference.
```

## Recommendation States

Use exactly one state per automation unit:

```text
retain
optimize
augment
migrate
pilot_first
no_suitable_candidate
needs_more_evidence
```

Also provide:

```text
capability_class
recommended_product
recommended_edition_or_hosting
supporting_products
```

A composed recommendation must still assign one authoritative owner to each unit.

## Confidence Model

```text
high
  The workload is decomposed, capability and hard-fit signals are clear, current product facts are verified, mandatory constraints are known, and no material disqualifier is unresolved.

medium
  The likely category and shortlist are clear, but edition, integration, scale, migration, recovery, licensing, or governance needs validation.

low
  The request remains compound, product facts are stale or unavailable, or major constraints could change the recommendation.
```

Never hide uncertainty behind a weighted total.

## Candidate Shortlist Rules

- Keep two to four viable products per capability class by default.
- Keep five only when the decision is genuinely close.
- Include the incumbent when migration cost is material.
- Eliminate products that fail mandatory requirements before scoring.
- Compare exact editions and hosting models.
- Record official source and evidence dates for version-sensitive claims.
- Do not use unsupported pricing, roadmap, market-share, or feature assumptions.

## Decision Challenge

Before finalizing, test at least these counterfactuals:

- Could the runner or caller be replaced without changing the authoritative source of truth?
- What happens on a partial failure?
- What happens on the second run?
- What happens if the selected control plane is unavailable?
- Which state or evidence must survive executor loss?
- Does a tenfold increase in targets or concurrency change the recommendation?
- Does stricter separation of duties change the product or flow?
- Is there a maintained native integration that removes custom shell logic?
- Is a compared feature available in the exact product edition and hosting model?
- Does migration value exceed migration cost and future operating burden?
- Would augmenting the incumbent solve the gap with less risk than replacing it?

## Final Report

```markdown
# Automation Platform Selection

## Executive Decision
- Architecture:
- Products and editions:
- Migration posture:
- Confidence:

## Assumptions and Evidence Cutoff

## Workload Decomposition
| Unit | Capability | Control Loop | Target | Lifecycle | Trigger | Source of Truth |
|---|---|---|---|---|---|---|

## Candidate Policy and Mandatory Gates

## Product Longlist and Eliminations
| Product | Capability | Gate Result | Reason or Next Check |
|---|---|---|---|

## Product Shortlist
| Unit | Product / Edition | Hosting | Best Fit | Main Gap | Evidence Date |
|---|---|---|---|---|---|

## Weighted Product Comparison
| Criterion | Weight | Candidate 1 | Candidate 2 | Candidate 3 | Evidence |
|---|---:|---:|---:|---:|---|

## Architecture and Ownership Boundaries

## Execution or Reconciliation Flow

## Handoff Contracts

## Security, Supply Chain, Approval, and Audit Controls

## Failure Recovery, Resume, Compensation, and Rollback

## Migration and Total-Cost Analysis

## Anti-Patterns To Avoid

## Proof-of-Fit Pilot

## Implementation Backlog

## Rejected Alternatives

## Official Sources Checked

## Unknowns That Could Change the Decision
```

## Completion Contract

```text
Status:
Brief:
Automation units:
Capability classes:
Candidate policy:
Primary recommendations:
Products and editions:
Composition:
Skills completed:
Mandatory disqualifiers:
Sources and evidence dates:
Pilot:
Validation:
Migration posture:
Assumptions:
Unknowns:
Next decision:
```

## Example Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Decompose and classify the request, compare the incumbent Terraform, Ansible, and Jenkins stack with justified alternatives such as OpenTofu, Pulumi, GitHub Actions, Azure Pipelines, GitLab CI/CD, Puppet, Chef, Argo CD, Flux, or runbook and workflow platforms. Use official current sources, apply mandatory gates before scoring, define ownership and handoffs, and produce a proof-of-fit pilot. Do not force a single-platform answer or a migration.
```

## Quality Bar

- Decomposition and capability classification precede product recommendation.
- Hard-fit and mandatory gates precede scoring.
- Each unit has one authoritative owner.
- The shortlist is small, current, edition-aware, and evidence-backed.
- Composition is minimal and explicit.
- Incumbent retention, optimization, augmentation, and migration are all considered fairly.
- Rejected alternatives are explained.
- Security, supply chain, approvals, state, inventory, artifacts, durable workflow history, recovery, migration, total cost, and support ownership are included.
- The pilot can prove the recommendation wrong.
