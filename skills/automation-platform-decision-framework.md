# Automation Platform Decision Framework

## Purpose

Provide a repeatable, category-aware method for selecting automation capabilities and products without reducing the decision to incumbent familiarity, vendor preference, file syntax, or an unsupported weighted total.

## When To Use

Use for new automation requests, architecture reviews, migrations, platform-consolidation discussions, and cases where existing logic may live in the wrong tool.

## Inputs Needed

- business outcome and decision owner
- target systems and environments
- current and desired state
- lifecycle actions
- trigger, frequency, and control loop
- source of truth
- target count and inventory model
- state, drift, reconciliation, artifact, and workflow-history needs
- source-control, cloud, artifact, identity, and deployment platforms
- hosting, network, connectivity, and privilege constraints
- secrets, approvals, policy, audit, and evidence requirements
- rollback, retry, resume, compensation, and recovery expectations
- existing products, editions, licenses, content, maturity, and support model
- migration tolerance, decision horizon, risk tolerance, and budget
- candidate policy and output depth

## Output Depth

Use one mode:

```text
quick_triage
  Produce the capability classification, mandatory blockers, recommendation posture, top alternatives, confidence, and next validation step. Do not emit a large scoring matrix.

standard
  Produce a shortlist, evidence-backed comparison, ownership boundaries, migration posture, and pilot. This is the default.

full_architecture_review
  Include the complete evidence ledger, weighted model, economics, handoff contracts, recovery design, migration waves, and architecture decision record.
```

Do not produce full-review volume for a simple request unless the user asks for it or the risk justifies it.

## Instructions

### 1. Normalize the request

Rewrite the request as observable outcomes. Replace vague statements such as `automate the deployment` with units such as:

```text
create network resources
configure operating-system prerequisites
build application artifact
run tests
approve production release
publish immutable artifact
update deployment declaration
reconcile cluster state
verify health
record evidence
```

### 2. Decompose compound work

Create one automation unit for each independently owned lifecycle. A unit should have one authoritative source of truth and one primary product owner.

### 3. Classify capability and control loop

Use the exact identifiers in `automation-platform-capability-taxonomy.md`:

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

Control loops:

```text
one_shot
event_driven
scheduled
continuous_reconciliation
durable_workflow
```

### 4. Identify authoritative records

For every unit, identify the durable home of:

- desired state
- resource identity or state
- inventory and classification
- source code and reusable content
- artifacts and provenance
- workflow or pipeline history
- approvals and audit evidence
- secrets and credentials

### 5. Apply category hard-fit rules

- Persistent provider-managed resource lifecycle defaults to `infrastructure_as_code`.
- Configuration or operation of existing targets defaults to `configuration_management` or `runbook_automation`.
- Triggered build, test, approval, artifact, promotion, or delivery sequencing defaults to `ci_cd`.
- Continuous Kubernetes reconciliation from version-controlled desired state defaults to `gitops_continuous_delivery`.
- Operator-facing parameterized procedures default to `runbook_automation`.
- Long-running stateful workflows with durable timers, retries, signals, or compensation default to `durable_workflow_orchestration`.
- Managed execution layers are evaluated separately from the underlying engine.
- A platform can execute a command without being the correct authoritative owner.

### 6. Discover viable products

Use `automation-platform-candidate-discovery.md`.

Candidate policy:

```text
current_stack_only
current_stack_plus_alternatives
open_market
```

Start with incumbents. Add alternatives only when a concrete requirement makes them relevant.

### 7. Apply mandatory elimination gates

Eliminate candidates that fail a non-negotiable requirement such as:

- target, provider, operating-system, architecture, or resource coverage
- SaaS, self-hosted, hybrid, managed-private, or air-gapped deployment
- source-control integration
- private-network reachability
- runner, agent, or controller topology
- identity, audit, approval, policy, or separation of duties
- data residency, evidence retention, or support lifecycle
- open-source, licensing, procurement, or vendor constraints
- state import, compatibility, or migration requirements
- recovery when the control plane is unavailable

Do not score disqualified products. Treat unresolved mandatory gates as blockers, not as low scores.

### 8. Build the evidence ledger

Use `automation-platform-evidence-and-confidence.md`.

For every material product claim record:

```text
product and edition
hosting model
claim type
verification status
source and access date
applicable version, plan, or environment
```

Keep observed facts, official claims, derived values, inferences, proposals, and unknowns separate.

### 9. Score viable products

Score fit from 0 to 5 only after mandatory gates pass.

| Criterion | Default Weight | Question |
|---|---:|---|
| Capability ownership | 5 | Is this product naturally responsible for the unit? |
| Control-loop fit | 5 | Does its execution or reconciliation model match? |
| State and durable-history fit | 4 | Can it own the required state, inventory, artifacts, or workflow history? |
| Target and ecosystem coverage | 5 | Does it support the required targets through maintained integrations? |
| Hosting and execution topology | 4 | Does the control plane, runner, agent, or controller model fit? |
| Recovery | 4 | Can failures be retried, resumed, compensated, rolled back, or reconciled? |
| Security | 4 | Are identity, credentials, isolation, and privilege boundaries supportable? |
| Audit and governance | 3 | Can it produce approvals, policies, and evidence? |
| Maintainability | 3 | Can logic be tested, reviewed, reused, and owned? |
| Scale and concurrency | 3 | Does its target and execution model fit expected growth? |
| Platform operations | 4 | Can the organization sustainably operate it? |
| Existing operating model | 2 | Does it reuse valuable current investments? |
| Migration complexity | 3 | Can adoption or migration be performed safely? |
| Licensing and total cost | 3 | Are license, infrastructure, labor, and support sustainable? |
| Portability and lock-in | 2 | Is the coupling acceptable? |

Rules:

- Customize weights only when the brief states the business priority.
- Show raw fit and evidence confidence separately.
- Do not score `unknown` as zero.
- Exclude `not_applicable` criteria from the denominator.
- Use confidence-adjusted points only as described in `automation-platform-evidence-and-confidence.md`.
- Treat candidates within 5 percent of applicable points as effectively tied unless a mandatory requirement, migration difference, or operating-model advantage is decisive.
- Do not let a weighted score override a category mismatch or mandatory gate.

### 10. Compare decision postures and economics

Use `automation-platform-migration-and-economics.md`.

Evaluate:

```text
retain
optimize
augment
migrate
pilot_first
```

Include the do-nothing baseline, one-time migration cost, recurring operating cost, dual-running cost, reversibility, and decision horizon. Prefer ranges over false precision.

### 11. Define ownership boundaries

For each unit, record:

```text
primary product and edition
capability class
caller or trigger
repository artifact
state, inventory, artifact, or history store
credentials used
approval point
verification method
recovery method
operational owner
```

### 12. Challenge the recommendation

Ask:

- What breaks if the control plane, runner, agent, or controller is unavailable?
- What state, inventory, artifact, or evidence is lost or duplicated?
- Can a second run safely converge?
- Can a partial failure resume without manual archaeology?
- Does rollback restore the prior state or only stop further change?
- Is business logic hidden in shell steps or pipeline configuration?
- Could a maintained provider, module, action, task, collection, cookbook, or controller remove custom code?
- Does the recommendation still hold at ten times the scale?
- Does stricter separation of duties change the architecture?
- Is the compared feature available in the exact edition and hosting model?
- Is evidence coverage sufficient for the stated confidence?
- Is migration value greater than migration and operating cost?
- Is the target architecture reversible?

## Expected Output

### Quick triage

```markdown
## Decision
- Capability:
- Recommended posture and product:
- Confidence:
- Mandatory blockers:
- Strongest alternative:
- Next validation step:
```

### Standard or full review

```markdown
## Decision Summary

## Workload Units
| Unit | Capability | Control Loop | Source of Truth | Lifecycle | Trigger |
|---|---|---|---|---|---|

## Candidate Policy and Mandatory Gates

## Longlist and Eliminations
| Product | Capability | Gate Result | Reason |
|---|---|---|---|

## Shortlist
| Unit | Product / Edition | Hosting | Strongest Fit | Main Gap | Evidence Date |
|---|---|---|---|---|---|

## Evidence Quality

## Weighted Matrix
| Criterion | Weight | Raw Fit | Confidence | Adjusted Points | Evidence |
|---|---:|---:|---|---:|---|

## Boundaries
| Unit | Owner | Caller | Artifact | Durable State or History | Recovery |
|---|---|---|---|---|---|

## Migration and Economics

## Risks and Unknowns

## Proof-of-Fit Pilot
```

## Quality Checks

- The request is decomposed and classified before products are scored.
- Canonical capability identifiers are used consistently.
- Every unit has exactly one authoritative owner.
- Products from different capability classes are not directly compared without decomposition.
- Mandatory gates are applied before weighting.
- Exact product edition and hosting assumptions are visible.
- Unknown evidence is not converted into a false low score.
- Evidence coverage supports the stated confidence.
- Security, supply chain, failure recovery, platform operations, migration, reversibility, and total cost are included at the selected output depth.
- The result can recommend composition, retention, optimization, augmentation, migration, pilot-first, or no suitable product.
