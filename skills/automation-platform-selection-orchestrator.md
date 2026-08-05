# Automation Platform Selection Orchestrator

## Purpose

Coordinate workload intake, capability classification, candidate discovery, evidence validation, product-fit analysis, migration economics, composition design, proof-of-fit validation, and a final recommendation across incumbent and alternative automation platforms.

## When To Use

Use for a complete platform-selection exercise, architecture review, consolidation decision, or migration from automation that has accumulated in the wrong tool.

## Required Inputs

Prefer `schemas/automation-platform-decision-brief.schema.json`.

At minimum:

- requested outcome and decision owner
- targets and environments
- current implementation and products
- lifecycle actions
- triggers, frequency, and control-loop requirements
- systems of record
- source-control, cloud, identity, artifact, and deployment platforms
- hosting, runner, agent, controller, network, and privilege constraints
- credentials, approvals, policy, supply chain, and audit requirements
- rollback, resume, compensation, and recovery expectations
- organizational ownership
- licensing, support, procurement, migration, and budget constraints
- decision horizon, risk tolerance, candidate policy, and output depth

## Canonical Sequence

```text
1. validate the brief and reject contradictory constraints
2. restate the outcome, decision owner, horizon, risk tolerance, candidate policy, and output depth
3. decompose into automation units
4. classify capability and control loop for each unit
5. identify sources of truth and durable state or history
6. apply category hard-fit rules
7. build a product longlist from incumbents and justified alternatives
8. verify current product, edition, hosting, licensing, and lifecycle facts
9. create the evidence ledger
10. apply mandatory elimination gates
11. run incumbent Terraform, Ansible, and Jenkins fit analysis where applicable
12. run category-specific alternative analysis where applicable
13. score only viable products and keep fit separate from evidence confidence
14. calculate evidence coverage and identify effective ties
15. compare retain, optimize, augment, migrate, and pilot-first economics
16. identify disqualifiers, category errors, anti-patterns, and circular dependencies
17. define product ownership boundaries
18. design handoff contracts and execution or reconciliation flow
19. define credentials, supply-chain controls, approvals, evidence, and recovery
20. challenge the recommendation for scale, outage, stricter governance, stale evidence, cost, and reversibility
21. define a proof-of-fit pilot with a stopping rule
22. produce the recommendation, migration posture, and backlog at the selected output depth
```

## Skill Routing

Use:

- [`automation-platform-capability-taxonomy.md`](automation-platform-capability-taxonomy.md) for canonical capability identifiers and control-loop classification.
- [`automation-platform-decision-framework.md`](automation-platform-decision-framework.md) for decomposition, hard-fit rules, output depth, elimination gates, and scoring.
- [`automation-platform-candidate-discovery.md`](automation-platform-candidate-discovery.md) for longlist generation, current evidence, elimination, and shortlisting.
- [`automation-platform-evidence-and-confidence.md`](automation-platform-evidence-and-confidence.md) for evidence ledgers, freshness, confidence, coverage, and tie handling.
- [`automation-platform-migration-and-economics.md`](automation-platform-migration-and-economics.md) for retain, optimize, augment, migrate, pilot-first, total cost, migration waves, and reversibility.
- [`terraform-workload-fit-analysis.md`](terraform-workload-fit-analysis.md) for incumbent Terraform resource-lifecycle analysis.
- [`ansible-workload-fit-analysis.md`](ansible-workload-fit-analysis.md) for incumbent Ansible configuration and operations analysis.
- [`jenkins-workload-fit-analysis.md`](jenkins-workload-fit-analysis.md) for incumbent Jenkins pipeline analysis.
- [`infrastructure-as-code-platform-alternatives-analysis.md`](infrastructure-as-code-platform-alternatives-analysis.md) for Terraform, OpenTofu, Pulumi, cloud-native IaC, Crossplane, and managed execution comparisons.
- [`configuration-management-platform-alternatives-analysis.md`](configuration-management-platform-alternatives-analysis.md) for Ansible, AAP/AWX, Puppet, Chef, Salt, and DSC comparisons.
- [`ci-cd-platform-alternatives-analysis.md`](ci-cd-platform-alternatives-analysis.md) for Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, and Tekton comparisons.
- [`gitops-runbook-and-workflow-platform-analysis.md`](gitops-runbook-and-workflow-platform-analysis.md) for Argo CD, Flux, runbook platforms, and durable workflow engines.
- [`automation-platform-composition-and-boundaries.md`](automation-platform-composition-and-boundaries.md) when more than one product is justified.

## Output Depth

```text
quick_triage
  Return the capability, mandatory blockers, recommended posture and product, strongest alternative, confidence, and next validation step.

standard
  Return the shortlist, evidence-backed comparison, ownership boundaries, migration posture, and pilot. Default.

full_architecture_review
  Return the full evidence ledger, confidence-adjusted scoring, economics, handoff contracts, recovery design, migration waves, and ADR-ready decision.
```

Do not emit unused sections. Preserve high-risk controls even in a shorter mode.

## Candidate Policies

```text
current_stack_only
  Evaluate only explicitly approved incumbents.

current_stack_plus_alternatives
  Evaluate incumbents and add materially relevant products. Default.

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
evidence_coverage
```

A composed recommendation must still assign one authoritative owner to each unit.

## Confidence Model

```text
high
  Hard-fit signals are clear, all mandatory gates are resolved, material product claims are current and verified, and weighted evidence coverage is at least 80 percent.

medium
  The category and shortlist are clear, but edition, integration, scale, migration, recovery, licensing, cost, or governance needs validation.

low
  The request remains compound, evidence is stale or conflicting, coverage is weak, or major constraints could change the recommendation.
```

Never hide uncertainty behind a weighted total. Use `needs_more_evidence` or `pilot_first` when an unresolved gate or material unknown controls the decision.

## Shortlist and Scoring Rules

- Keep two to four viable products per capability class by default.
- Keep five only when the decision is genuinely close.
- Include the incumbent when migration cost is material.
- Eliminate products that fail mandatory requirements before scoring.
- Compare exact editions and hosting models.
- Record official source and evidence dates for version-sensitive claims.
- Keep raw fit and evidence confidence separate.
- Do not score unknowns as zero or include non-applicable criteria in the denominator.
- Treat candidates within 5 percent of applicable points as effectively tied unless a hard requirement, migration difference, or operating-model advantage decides the result.
- Do not use unsupported pricing, roadmap, market-share, or feature assumptions.

## Constraint Consistency Checks

Before analysis, reject or resolve contradictions such as:

- `air_gapped_required: true` without `air_gapped` in allowed hosting models
- `self_hosted_required: true` while only SaaS is allowed
- the same product in both allowed and excluded lists
- `current_stack_only` with an allowed-product list that excludes every incumbent
- `migration_tolerance: none` with a requested `migrate`-only output
- a required capability class excluded from the allowed capability classes

Do not silently reinterpret contradictory constraints.

## Decision Challenge

Before finalizing, test at least these counterfactuals:

- Could the runner or caller be replaced without changing the authoritative source of truth?
- What happens on a partial failure and on the second run?
- What happens if the selected control plane is unavailable?
- Which state or evidence must survive executor loss?
- Does a tenfold increase in targets or concurrency change the recommendation?
- Does stricter separation of duties change the product or flow?
- Is there a maintained native integration that removes custom shell logic?
- Is each compared feature available in the exact edition and hosting model?
- Does evidence coverage support the stated confidence?
- Does migration value exceed migration cost and future operating burden?
- Would optimization or augmentation solve the gap with less risk?
- Can the pilot and target architecture be reversed without losing authoritative state?

## Final Report

### Quick triage

```markdown
# Automation Platform Triage

## Decision
- Capability:
- Recommended posture and product:
- Confidence:
- Mandatory blockers:
- Strongest alternative:
- Next validation step:

## Assumptions
```

### Standard or full review

```markdown
# Automation Platform Selection

## Executive Decision
- Architecture:
- Products and editions:
- Migration posture:
- Confidence and evidence coverage:

## Assumptions, Decision Horizon, and Evidence Cutoff

## Workload Decomposition
| Unit | Capability | Control Loop | Target | Lifecycle | Trigger | Source of Truth |
|---|---|---|---|---|---|---|

## Mandatory Gates

## Product Longlist and Eliminations
| Product | Capability | Gate Result | Reason or Next Check |
|---|---|---|---|

## Product Shortlist
| Unit | Product / Edition | Hosting | Best Fit | Main Gap | Evidence Date |
|---|---|---|---|---|---|

## Evidence Quality

## Confidence-Aware Product Comparison
| Criterion | Weight | Candidate | Raw Fit | Confidence | Adjusted Points | Source IDs |
|---|---:|---|---:|---|---:|---|

## Architecture and Ownership Boundaries

## Execution or Reconciliation Flow

## Handoff Contracts

## Security, Supply Chain, Approval, and Audit Controls

## Failure Recovery, Resume, Compensation, and Rollback

## Migration Economics and Reversibility

## Proof-of-Fit Pilot

## Implementation Backlog

## Rejected Alternatives

## Evidence Ledger and Official Sources

## Unknowns That Could Change the Decision
```

## Completion Contract

```text
Status:
Output depth:
Decision owner and horizon:
Brief:
Automation units:
Capability classes:
Candidate policy:
Primary recommendations:
Products and editions:
Composition:
Migration posture:
Evidence coverage:
Mandatory disqualifiers:
Pilot:
Validation:
Assumptions:
Unknowns:
Next decision:
```

## Example Invocation

```text
Load agents/automation-platform-selection-advisor.md and skills/automation-platform-selection-orchestrator.md. Validate examples/automation-platform-decision-brief.yaml. Decompose and classify the request, compare the incumbent Terraform, Ansible, and Jenkins stack with justified alternatives, use official current evidence, apply mandatory gates before scoring, keep fit separate from confidence, compare migration economics and reversibility, define ownership and handoffs, and produce a proof-of-fit pilot. Use standard output depth unless the request needs only triage or a full architecture review.
```

## Quality Bar

- Contradictory constraints are surfaced before analysis.
- Decomposition and capability classification precede product recommendation.
- Canonical capability identifiers are used.
- Hard-fit and mandatory gates precede scoring.
- Each unit has one authoritative owner.
- The shortlist is small, current, edition-aware, and evidence-backed.
- Unknown evidence is not scored as product failure.
- Confidence is supported by evidence coverage.
- Composition is minimal and explicit.
- Retain, optimize, augment, migrate, and pilot-first are considered fairly.
- Security, supply chain, state, inventory, artifacts, workflow history, recovery, migration cost, recurring burden, reversibility, and support ownership are included at the selected depth.
- The pilot can prove the recommendation wrong.
