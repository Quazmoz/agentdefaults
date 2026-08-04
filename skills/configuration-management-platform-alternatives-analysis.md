# Configuration Management Platform Alternatives Analysis

## Purpose

Compare platforms that configure and continuously manage existing systems, including Ansible, Red Hat Ansible Automation Platform or AWX, Puppet, Chef Infra, Salt, and PowerShell Desired State Configuration.

## When To Use

Use when an automation unit owns operating-system, middleware, application, endpoint, or network-device configuration; fleet remediation; patching; policy enforcement; deployment to existing targets; or recurring day-2 operations.

## Candidate Set

Generate a shortlist from products justified by the estate:

```text
Ansible
Red Hat Ansible Automation Platform / AWX
Puppet
Chef Infra
Salt
PowerShell Desired State Configuration
```

Do not treat the open-source engine, community controller, and commercial enterprise platform as identical products.

## Hard Requirements

Evaluate before scoring:

- push, pull, agentless, agent-based, or hybrid control model
- target operating systems, network devices, endpoints, and middleware
- required continuous enforcement interval
- inventory, classification, facts, and targeting model
- private-network reachability and outbound-connectivity constraints
- privilege escalation and credential isolation
- disconnected or air-gapped operation
- scale, batching, maintenance windows, and concurrency
- desired-state reporting and compliance evidence
- module, collection, cookbook, formula, or resource ecosystem
- testing and promotion model
- operator self-service, approvals, scheduling, and RBAC
- controller, server, database, certificate, and agent operations
- commercial support, licensing, and procurement requirements

## Control-Model Decision

Use the required control loop as a major discriminator:

```text
operator-triggered push or runbook execution
  -> Ansible, AAP/AWX, Rundeck plus an execution engine, or Salt execution patterns may fit

continuous agent-based desired-state enforcement
  -> Puppet, Chef Infra, Salt, or DSC may fit

Windows-native configuration with PowerShell resource alignment
  -> DSC may fit for bounded Windows workloads

mixed network and server automation with agentless access
  -> Ansible or AAP/AWX may fit
```

A product can support more than one mode, but the dominant operating model should drive selection.

## Product Fit Profiles

These are starting hypotheses. Verify current official documentation, supported editions, and target compatibility.

### Ansible

Strong fit when:

- agentless push execution is valuable
- SSH, WinRM, APIs, or network connections reach targets safely
- playbooks, roles, inventories, and collections fit the work
- operator-triggered deployment, remediation, and day-2 workflows dominate

Primary tradeoffs:

- continuous enforcement requires scheduling or a controller rather than a persistent node agent
- large inventory, credentials, concurrency, and evidence need deliberate controller architecture
- imperative modules and shell tasks can weaken idempotency

### Red Hat Ansible Automation Platform / AWX

Strong fit when:

- centralized RBAC, inventories, credentials, execution environments, schedules, workflows, surveys, and audit history are required around Ansible
- self-service or governed enterprise execution is needed
- existing Ansible content should remain the execution engine

Primary tradeoffs:

- controller, execution-node, database, upgrade, and high-availability operations
- AWX and commercial AAP support and lifecycle expectations differ
- governance value depends on disciplined content, credentials, and inventory ownership

### Puppet

Strong fit when:

- declarative continuous desired-state enforcement through an agent-server model is required
- large, stable server fleets benefit from regular catalog application and reporting
- node classification, facts, modules, and centralized policy are strategic

Primary tradeoffs:

- agents, servers, certificates, code deployment, and classification infrastructure must be operated
- event-driven ad hoc runbooks may require additional capabilities or enterprise features
- migration from procedural playbooks can require substantial remodeling

### Chef Infra

Strong fit when:

- cookbook and policy-based configuration with node clients fits the organization
- Ruby-based infrastructure code and Chef testing tools are established
- centralized configuration data, policy distribution, and recurring client runs are desired

Primary tradeoffs:

- server, client, cookbook, dependency, and policy operations
- Ruby and Chef-specific ecosystem skills
- migration cost from simpler push-based automation

### Salt

Consider when:

- fast remote execution and configuration management are both needed
- its master, minion, proxy, or masterless topology fits target connectivity
- event-driven automation capabilities are materially relevant

Verify current supported editions, architecture, security model, and ecosystem before shortlisting.

### PowerShell Desired State Configuration

Consider when:

- Windows is the dominant target
- PowerShell and DSC resource coverage are strong
- a Windows-native desired-state model is strategically preferable

Primary tradeoffs:

- cross-platform and non-Windows coverage may require another platform
- resource maturity and the chosen DSC implementation must be verified
- enterprise reporting and orchestration may require adjacent services

## Comparison Matrix

| Criterion | Weight |
|---|---:|
| Target and resource coverage | 5 |
| Control-loop fit | 5 |
| Inventory and classification | 4 |
| Desired-state and idempotency | 4 |
| Continuous enforcement and drift reporting | 4 |
| Connectivity and privilege model | 4 |
| Scale, batching, and concurrency | 3 |
| Testing and content promotion | 3 |
| RBAC, approvals, and self-service | 3 |
| Audit and compliance evidence | 4 |
| Controller, server, and agent operations | 4 |
| Ecosystem and maintainability | 3 |
| Migration complexity | 3 |
| Licensing and support fit | 3 |

Mandatory target, connectivity, privilege, or hosting gaps are disqualifiers.

## Required Analysis

For each finalist, state:

- exact product and edition
- push, pull, agent, and controller topology
- inventory or node-classification source of truth
- credential and privilege architecture
- content repository and promotion flow
- convergence schedule or trigger
- canary, batching, and maintenance-window controls
- reporting and audit evidence
- high-availability and recovery design
- migration path from current content
- operational owner

## Anti-Patterns

- selecting an agent-based platform without budgeting certificate and agent lifecycle operations
- selecting Ansible for continuous enforcement without designing schedules, drift evidence, and controller availability
- selecting Puppet or Chef solely because the estate is large
- selecting DSC for non-Windows targets without decomposition
- assuming modules, cookbooks, or resources are maintained without verification
- embedding extensive shell logic instead of using testable native resources
- allowing two platforms to own the same configuration attribute
- conflating successful convergence with rollback

## Expected Output

```markdown
## Configuration-Management Shortlist
| Product | Edition / Topology | Best Fit | Main Gap | Mandatory Gates |
|---|---|---|---|---|

## Control-Loop and Connectivity Design

## Inventory, Classification, and Credential Ownership

## Weighted Comparison

## Migration and Operations Plan

## Recommendation
```

## Quality Bar

- The push, pull, and reconciliation model matches the workload.
- Target reachability and privilege are validated.
- Controller, server, agent, and certificate operations are included.
- Product edition and support differences are explicit.
- Migration reuses valuable content only when semantics remain correct.
- The recommendation states why the runner-up lost.
