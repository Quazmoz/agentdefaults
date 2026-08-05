# Automation Platform Migration and Economics

## Purpose

Compare retaining, optimizing, augmenting, or replacing an automation platform using explicit migration risk, reversibility, operating burden, and total-cost assumptions. This skill prevents migrations driven by novelty, license price alone, or shallow feature parity.

## When To Use

Use when:

- an incumbent product already exists
- platform consolidation or replacement is proposed
- a managed service is being compared with self-hosting
- licensing, support, staffing, upgrade burden, or control-plane operations may affect the decision
- the recommendation could require content conversion, state migration, retraining, or production cutover

## Inputs Needed

- incumbent products, editions, maturity, and ownership
- current repositories, modules, pipelines, playbooks, roles, cookbooks, manifests, integrations, and state
- candidate products and editions
- expected decision horizon
- license and infrastructure assumptions
- engineering and operations labor assumptions
- migration deadline and tolerance
- compliance, support, procurement, and availability requirements
- rollback and exit requirements
- expected benefits and measurable success criteria

## Decision Postures

Evaluate all applicable postures:

```text
retain
  Keep the incumbent because it meets requirements and replacement value is weak.

optimize
  Keep the incumbent and improve architecture, governance, reliability, or maintainability.

augment
  Keep the incumbent for its owned capability and add another product for a missing capability.

migrate
  Replace the incumbent because the target product provides material, durable value that exceeds migration and operating cost.

pilot_first
  Run a bounded proof of fit before committing to a posture.
```

Do not use `migrate` as the default outcome of a product comparison.

## Cost Model

Estimate costs over the requested horizon, using ranges when exact data is unavailable.

### One-time costs

- discovery and architecture
- procurement and legal review
- platform installation or tenant setup
- content conversion or rewrite
- state, inventory, artifact, credential, and history migration
- integration development
- testing and parallel operation
- training and documentation
- production cutover and rollback preparation
- temporary dual-platform support

### Recurring costs

- licenses and usage
- control-plane infrastructure
- runners, agents, controllers, storage, and network egress
- backups, disaster recovery, observability, and security operations
- plugin, provider, action, module, collection, cookbook, and dependency maintenance
- upgrades and compatibility testing
- platform engineering and support labor
- compliance evidence and audit administration
- incident response and downtime exposure
- vendor support

### Benefits

- reduced platform administration
- shorter lead time
- higher deployment frequency
- lower failure rate
- faster recovery
- improved policy, audit, or separation of duties
- reduced custom code or plugin burden
- improved developer or operator experience
- better target, cloud, or ecosystem fit
- lower concentration or lock-in risk

Do not monetize benefits without a stated method and baseline.

## Comparison Metrics

Use ranges and assumptions rather than false precision.

```text
total_cost = one_time_cost + recurring_cost_over_horizon + risk_allowance

net_value = quantified_benefit_over_horizon - total_cost

break_even_month = first month cumulative_benefit >= cumulative_cost
```

When benefits cannot be credibly monetized, use a qualitative benefit score and keep it separate from cost.

## Migration Complexity

Score each dimension as low, medium, high, or critical:

- content rewrite
- state or resource adoption
- history and evidence retention
- credential and identity migration
- integration replacement
- runner, agent, or controller topology change
- policy and approval recreation
- operator and developer retraining
- parallel-run requirement
- production cutover risk
- rollback feasibility
- vendor or format lock-in

A high feature score does not override critical migration risk.

## Reversibility and Exit Strategy

For every proposed target platform define:

- exportable source artifacts
- state, inventory, history, and evidence portability
- proprietary syntax or API dependencies
- rollback point
- coexistence period
- data retention after exit
- replacement path if the vendor, product, or edition becomes unavailable
- ownership of migration tooling

Prefer reversible pilots that do not strand production state or credentials.

## Migration Waves

Use phased migration:

```text
wave 0  inventory, baselines, and acceptance criteria
wave 1  low-risk representative workload
wave 2  shared integrations and reusable patterns
wave 3  medium-risk production workloads
wave 4  high-impact or exceptional workloads
wave 5  decommission, evidence retention, and cost verification
```

Define entry and exit criteria for every wave. Do not create a big-bang migration unless a hard deadline or platform failure makes it unavoidable.

## Option Comparison

| Posture | One-Time Cost | Recurring Cost | Risk | Benefit | Reversibility | Recommended When |
|---|---:|---:|---|---|---|---|
| Retain | | | | | | |
| Optimize | | | | | | |
| Augment | | | | | | |
| Migrate | | | | | | |
| Pilot First | | | | | | |

Include the do-nothing baseline. Its cost includes known operational burden and risk, not zero.

## Decision Rules

- Retain when requirements are met and migration does not create material strategic or operating value.
- Optimize when the largest gaps are implementation problems rather than product limitations.
- Augment when another capability class is missing but the incumbent remains appropriate for its owned state.
- Migrate when mandatory requirements cannot be met, support or lifecycle risk is unacceptable, or durable benefits exceed migration and operating cost.
- Pilot first when evidence, scale, usability, integration, recovery, or cost assumptions remain material.
- Reject a migration whose success depends on unowned rewrite work or unavailable operational capacity.

## Required Output

```markdown
## Decision Horizon and Baseline
- Horizon:
- Current annual operating burden:
- Current risk and known failure cost:
- Assumptions:

## Posture Comparison
| Posture | One-Time Cost Range | Recurring Cost Range | Benefits | Risks | Reversibility | Confidence |
|---|---:|---:|---|---|---|---|

## Migration Complexity
| Dimension | Rating | Evidence | Mitigation |
|---|---|---|---|

## Break-Even and Sensitivity
- Base case:
- Optimistic case:
- Pessimistic case:
- Variables with greatest impact:

## Migration Waves
| Wave | Scope | Entry Criteria | Exit Criteria | Rollback |
|---|---|---|---|---|

## Exit Strategy

## Recommended Posture
```

## Guardrails

- Do not treat license cost as total cost.
- Do not assume SaaS removes all operations work.
- Do not assign zero cost to retaining a fragile incumbent.
- Do not count speculative productivity gains as certain savings.
- Do not ignore dual-running cost.
- Do not migrate production state without a tested rollback or recovery path.
- Do not recommend replacement when focused optimization or augmentation solves the actual gap.

## Quality Bar

- The do-nothing baseline is explicit.
- Costs and benefits use ranges and stated assumptions.
- Migration complexity and reversibility are visible.
- Retain, optimize, augment, migrate, and pilot-first options are compared fairly.
- The recommended posture has measurable exit criteria.
- The plan can be stopped or reversed without losing authoritative state.
