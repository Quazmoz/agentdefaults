# Automation Platform Decision Framework

## Purpose

Provide a repeatable, category-aware method for selecting automation capabilities and products without reducing the decision to incumbent familiarity, vendor preference, or file syntax.

## When To Use

Use for new automation requests, architecture reviews, migrations, platform-consolidation discussions, and cases where existing logic may live in the wrong tool.

## Inputs Needed

- business outcome
- target systems
- current and desired state
- lifecycle actions
- trigger, frequency, and control loop
- source of truth
- target count and inventory model
- state, drift, reconciliation, artifact, and workflow-history needs
- source-control, cloud, and deployment platforms
- hosting, network, connectivity, and privilege constraints
- secrets, identity, approvals, and audit evidence
- rollback, retry, resume, compensation, and recovery expectations
- existing products, editions, licenses, content, and support model
- migration tolerance and budget
- candidate policy

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

Create one automation unit for each independently owned lifecycle. A unit should have one authoritative source of truth and one primary platform owner.

### 3. Classify the capability and control loop

Use `automation-platform-capability-taxonomy.md`.

Capability classes:

```text
infrastructure_as_code
configuration_management
ci_cd
GitOps_continuous_delivery
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
- source code and modules
- artifacts and provenance
- workflow or pipeline history
- approvals and audit evidence
- secrets and credentials

### 5. Apply category hard-fit rules

- Persistent provider-managed resource lifecycle defaults to the IaC category.
- Configuration or operation of existing targets defaults to configuration management or runbook automation.
- Triggered build, test, approval, artifact, promotion, or delivery sequencing defaults to CI/CD.
- Continuous Kubernetes reconciliation from version-controlled desired state defaults to GitOps CD.
- Operator-facing parameterized procedures default to runbook automation.
- Long-running stateful workflows with durable timers, retries, signals, or compensation default to durable workflow orchestration.
- Managed execution layers are evaluated separately from the underlying engine.
- A platform can execute a command without being the correct authoritative owner.

### 6. Discover viable products

Use `automation-platform-candidate-discovery.md`.

Choose a candidate policy:

```text
current_stack_only
current_stack_plus_alternatives
open_market
```

Start with incumbents. Add alternatives only when a concrete requirement makes them relevant.

### 7. Apply mandatory elimination gates

Eliminate candidates that fail a non-negotiable requirement such as:

- target, provider, operating-system, architecture, or resource coverage
- SaaS, self-hosted, hybrid, or air-gapped deployment
- source-control integration
- private-network reachability
- runner, agent, or controller topology
- identity, audit, approval, policy, or separation of duties
- data residency, evidence retention, or support lifecycle
- open-source, licensing, procurement, or vendor constraints
- state import, compatibility, or migration requirements
- recovery when the control plane is unavailable

Do not score disqualified products.

### 8. Score viable products

Score 0 to 5 and multiply by weight.

| Criterion | Weight | Question |
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

Do not let a weighted score override category mismatch or a mandatory gate.

### 9. Define boundaries

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

### 10. Challenge the recommendation

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
- Is migration value greater than migration and operating cost?

## Expected Output

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

## Weighted Matrix
| Criterion | Weight | Candidate 1 | Candidate 2 | Candidate 3 | Evidence |
|---|---:|---:|---:|---:|---|

## Boundaries
| Unit | Owner | Caller | Artifact | Durable State or History | Recovery |
|---|---|---|---|---|---|

## Migration and Operations Impact

## Risks and Unknowns

## Proof-of-Fit Pilot
```

## Quality Checks

- The request is decomposed and classified before products are scored.
- Every unit has exactly one authoritative owner.
- Products from different capability classes are not directly compared without decomposition.
- Mandatory gates are applied before weighting.
- Execution capability is not confused with state ownership.
- Exact product edition and hosting assumptions are visible.
- Rejected products receive evidence-based explanations.
- Security, supply chain, failure recovery, platform operations, migration, and total cost are included.
- Official product documentation and evidence dates support version-sensitive claims.
- The result can recommend composition, retention of the incumbent, migration, or no suitable product.
