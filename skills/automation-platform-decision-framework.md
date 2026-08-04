# Automation Platform Decision Framework

## Purpose

Provide a repeatable method for choosing between Terraform, Ansible, Jenkins, or a composed workflow without reducing the decision to team familiarity or file syntax.

## When To Use

Use for new automation requests, architecture reviews, migrations, platform-consolidation discussions, and cases where existing logic may live in the wrong tool.

## Inputs Needed

- business outcome
- target systems
- current and desired state
- lifecycle actions
- trigger and frequency
- source of truth
- target count and inventory model
- state, drift, and reconciliation needs
- connectivity and privilege constraints
- secrets and credentials
- approvals and audit evidence
- artifacts and promotion flow
- rollback and recovery expectations
- team ownership and support model

## Instructions

### 1. Normalize the request

Rewrite the request as observable outcomes. Replace vague statements such as "automate the deployment" with units such as:

```text
create network resources
configure operating-system prerequisites
build application artifact
run tests
approve production release
deploy artifact to existing hosts
verify health
record evidence
```

### 2. Decompose compound work

Create one automation unit for each independently owned lifecycle. A unit should have one authoritative source of truth and one primary platform owner.

### 3. Classify each unit

Use these classes:

```text
infrastructure_lifecycle
configuration_convergence
application_deployment
day_two_operation
build_and_test
pipeline_orchestration
approval_and_promotion
verification_and_reporting
unsupported_capability
```

### 4. Apply hard-fit rules

- Persistent provider-managed resource lifecycle defaults to Terraform.
- Configuration or operation of existing targets defaults to Ansible.
- Triggered build, test, approval, delivery, or coordination defaults to Jenkins.
- Compound workflows are split and composed.
- A platform can execute a command without being the correct authoritative owner.

### 5. Identify disqualifiers

Examples:

- Terraform provider coverage is absent or dangerously incomplete.
- Ansible cannot reach targets or obtain required privilege safely.
- Jenkins is unavailable during the recovery scenario it is expected to execute.
- The workload requires a durable event engine, queue, or long-running workflow model beyond the supported set.
- State ownership would be duplicated across tools.
- Required rollback cannot be expressed or tested.

### 6. Score viable options

Score 0 to 5 and multiply by weight.

| Criterion | Weight | Question |
|---|---:|---|
| Domain ownership | 5 | Is this platform naturally responsible for the unit? |
| Desired-state fit | 4 | Can repeated execution converge safely? |
| State and drift | 4 | Can it represent and reconcile the required state? |
| Trigger and workflow | 3 | Does it fit the event, schedule, gate, or sequence? |
| Inventory and scale | 3 | Does its target model fit the estate? |
| Recovery | 3 | Can failures be retried, resumed, rolled back, or compensated? |
| Security | 3 | Are credentials and privilege boundaries supportable? |
| Auditability | 2 | Can it produce the required evidence and approvals? |
| Maintainability | 3 | Can logic be tested, reviewed, reused, and owned? |
| Operating model | 2 | Does the organization have a sustainable support model? |

Do not let a weighted score override a hard ownership mismatch.

### 7. Define boundaries

For each unit, record:

```text
primary owner
caller or trigger
repository artifact
state or history store
credentials used
approval point
verification method
recovery method
```

### 8. Challenge the recommendation

Ask:

- What breaks if this tool is unavailable?
- What state is lost or duplicated?
- Can a second run safely converge?
- Can a failed run resume without manual archaeology?
- Does rollback restore the prior state or only stop further change?
- Is business logic hidden in shell steps?
- Could a maintained provider, module, collection, or plugin replace custom code?
- Does the recommendation still hold at ten times the target count?

## Expected Output

```markdown
## Decision Summary

## Workload Units
| Unit | Class | Source of Truth | Lifecycle | Trigger |
|---|---|---|---|---|

## Hard-Fit Result
| Unit | Default Owner | Disqualifiers | Final Owner |
|---|---|---|---|

## Weighted Matrix
| Criterion | Weight | Terraform | Ansible | Jenkins | Evidence |
|---|---:|---:|---:|---:|---|

## Boundaries
| Unit | Owner | Caller | Artifact | State or History | Recovery |
|---|---|---|---|---|---|

## Risks and Unknowns

## Proof-of-Fit Pilot
```

## Quality Checks

- The request is decomposed before scoring.
- Every unit has exactly one authoritative owner.
- Execution capability is not confused with state ownership.
- Rejected platforms receive evidence-based explanations.
- Security, failure recovery, and operational support are included.
- The result can recommend a composition or state that none of the supported tools fits.
