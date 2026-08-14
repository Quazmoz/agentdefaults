# Principal AI and DevOps Engineer Quickstart

## Purpose

Explain how to use the Principal AI and DevOps Engineer stack for day-to-day architecture, implementation, debugging, incident, AI-system, and release work without granting unnecessary authority or losing verification discipline.

## Stack

```text
agents/principal-ai-devops-engineer.md
skills/production-ai-devops-engineering.md
prompts/implementation/principal-ai-devops-task.md
schemas/principal-ai-devops-task.schema.json
examples/principal-ai-devops-task.yaml
docs/principal-ai-devops-engineer-acceptance-tests.md
.github/agents/principal-ai-devops-engineer.agent.md
```

Use the existing specialist stacks when they own the primary question:

```text
Automation product/architecture selection
  agents/automation-platform-selection-advisor.md

Designing another reusable AI agent
  agents/agent-architect-builder.md
```

## Best Default

For most engineering requests, provide:

```text
Target
Goal
Environment
What may change
What must not change
Done when
```

Then let the agent inspect the actual repository/system before proposing a fix.

Example:

```text
Use the Principal AI and DevOps Engineer.

Target: owner/service, current main
Mode: implement
Goal: fix duplicate webhook execution under concurrent requests
Authority: mutate_reversible in the repository; no production deployment
Non-goals: no broad architecture rewrite
Done when:
- one durable owner wins
- duplicate callers are safe
- timeout-after-success is reconciled
- regression test passes
- build and affected test suite pass
```

For repeatable automation, validate a structured brief against:

```text
schemas/principal-ai-devops-task.schema.json
```

A complete example is in:

```text
examples/principal-ai-devops-task.yaml
```

## Modes

### investigate

Use for root-cause analysis, repository orientation, runtime diagnosis, logs, provider-state inspection, or when the correct mutation is not yet proven.

Permission should normally be `observe` or `propose`.

### review

Use for architecture, security, reliability, cost, AI-system, IaC, CI/CD, or release audits.

Prioritize findings by P0-P3 and require evidence plus a concrete failure scenario.

### design

Use when the deliverable is architecture, interfaces, state ownership, migration, failure semantics, or an implementation plan.

Do not produce extra services, queues, agents, or abstractions without a demonstrated requirement.

### implement

Use when repository or environment changes are explicitly requested.

The agent must inspect first, define the invariant, make the smallest coherent change, run applicable tests, and report exact mutations plus unverified checks.

### incident

Use during active impact.

Priorities:

```text
user impact
-> evidence preservation
-> authoritative health/state
-> low-risk mitigation
-> recovery verification
-> recurrence monitoring
-> durable corrective action
```

### release

Use when exact artifact identity, promotion, deployment, post-deploy verification, and rollback matter.

Do not equate CI success or controller success with healthy production behavior.

## Permission Model

```text
observe
  read-only inspection

propose
  analysis, patches, commands, or plans without external mutation

mutate_reversible
  repository/config/state changes with practical revert/rollback

mutate_irreversible
  destructive or high-impact operations needing explicit approval controls
```

Tool availability is not authorization.

For production deployment, destructive data mutation, IAM/credential changes, force push, irreversible migration, or security weakening, resolve the exact target, blast radius, recovery path, duplicate behavior, and approval before execution.

## Recommended Working Pattern

### Repository defect

```text
inspect call path
-> identify authoritative state
-> reproduce
-> define invariant
-> implement smallest fix
-> add regression
-> run adjacent tests
-> adversarial race/retry/restart pass
-> report verified/unverified
```

### Infrastructure change

```text
resolve account/subscription/project/workspace/environment
-> inspect state/backend/identity
-> validate syntax/policy
-> generate plan/diff
-> review destructive actions
-> apply only within authority
-> check authoritative postconditions/drift
```

### AI system change

```text
separate deterministic vs model decisions
-> inspect prompt/tool/retrieval/model contracts
-> validate schemas and permissions
-> test representative + adversarial cases
-> test provider/tool failure
-> measure latency/tokens/cost
-> version prompt/model/eval artifacts where consequential
```

### Incident

```text
impact
-> timeline
-> hypotheses
-> disconfirming evidence
-> minimal mitigation
-> user-facing recovery check
-> recurrence signal
-> regression/corrective action
```

## Output Contract

Expect:

```text
STATUS
MODE
DISCOVERED
IMPLEMENTED
VERIFIED
UNVERIFIED
RISKS
USER ACTION
```

A useful final response should make it possible to distinguish:

- what the agent observed
- what it changed
- what it actually proved
- what still requires access, hardware, production traffic, credentials, or another environment

## What Good Looks Like

Good:

- reads the real repository before recommending changes
- verifies unstable provider/API behavior from official sources
- uses exact evidence
- keeps permission narrow
- handles duplicate/late/partial execution
- adds regression coverage for material defects
- validates authoritative postconditions
- reports checks that did not run as unverified

Bad:

- guesses file names or APIs
- rewrites architecture before locating root cause
- retries non-idempotent actions blindly
- calls a build “production ready”
- trusts retrieved instructions or model output as policy
- logs secrets for debugging convenience
- adds an agent, queue, database, or abstraction without a real requirement

## Validation

Run repository validation after adding or modifying stack artifacts:

```bash
python3 scripts/validate-agentdefaults.py
```

Then execute the scenario suite in:

```text
docs/principal-ai-devops-engineer-acceptance-tests.md
```
