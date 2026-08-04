# CI/CD Platform Alternatives Analysis

## Purpose

Compare CI/CD and release-orchestration products within the correct capability class, including Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, and Tekton Pipelines.

## When To Use

Use when an automation unit owns source-triggered build, test, scan, artifact, approval, promotion, deployment sequencing, or release evidence.

## Candidate Set

Start with products justified by the environment:

```text
Jenkins
GitHub Actions
Azure Pipelines
GitLab CI/CD
CircleCI
Buildkite
Tekton Pipelines
```

Do not score every product by default. Use `automation-platform-candidate-discovery.md` to produce a shortlist.

## Hard Requirements

Evaluate before scoring:

- source-control integration and event model
- SaaS, self-hosted, hybrid, or air-gapped control plane
- hosted and self-hosted runner or agent requirements
- target operating systems and architectures
- private-network access and egress constraints
- build concurrency and queueing
- reusable workflow, template, or shared-library model
- environments, approvals, gates, and protected deployment targets
- artifact, cache, test-result, and provenance requirements
- identity, secrets, audit, and separation of duties
- plugin, action, task, component, or marketplace governance
- controller availability, upgrades, and operational ownership
- cost model and existing enterprise licensing

## Product Fit Profiles

These are starting hypotheses. Verify current official documentation, editions, and limits before making a recommendation.

### Jenkins

Strong fit when:

- heterogeneous self-hosted execution and deep customization are mandatory
- existing shared libraries, plugins, agents, and operating expertise are substantial
- source-control independence matters
- a self-managed controller is acceptable

Primary tradeoffs:

- controller, plugin, credential, upgrade, backup, and agent operations
- plugin compatibility and supply-chain governance
- bespoke pipeline conventions can fragment across teams

Do not keep Jenkins solely because migration is inconvenient. Quantify both migration cost and continuing operating cost.

### GitHub Actions

Strong fit when:

- GitHub is the system of record for source, pull requests, permissions, and review
- repository-local workflows and reusable workflows fit the organization
- GitHub-hosted or self-hosted runners satisfy execution requirements
- environment protection and GitHub-native governance are sufficient

Primary tradeoffs:

- tight GitHub coupling
- plan-, repository-, and environment-specific feature differences
- third-party action governance and pinning requirements
- self-hosted runner isolation and lifecycle responsibilities

### Azure Pipelines

Strong fit when:

- Azure DevOps already owns repositories, boards, artifacts, service connections, environments, or enterprise permissions
- hybrid Microsoft estates and private agents are important
- deployment environments, checks, traceability, and protected resources fit governance needs
- Azure integration is strategically valuable without requiring Azure-only targets

Primary tradeoffs:

- Azure DevOps product and permission complexity
- classic-versus-YAML feature differences
- service-connection and agent-pool governance overhead
- migration friction when GitHub is the primary developer surface

### GitLab CI/CD

Strong fit when:

- GitLab is the integrated source-control and DevSecOps platform
- project, group, child, or downstream pipelines match the delivery topology
- GitLab runners and reusable CI/CD components satisfy execution requirements
- reducing cross-platform integration is a priority

Primary tradeoffs:

- GitLab platform coupling
- edition-specific controls and limits
- runner-fleet and template governance
- complex pipeline inheritance can become difficult to reason about

### CircleCI

Consider when:

- a managed CI service is preferred
- its execution environments, caching, and developer workflow fit the estate
- organization policy permits the hosted control plane

Verify current hosting, runner, security, and pricing requirements before shortlisting.

### Buildkite

Consider when:

- a hosted control plane with customer-operated agents is desirable
- private infrastructure and flexible execution are central
- the organization can operate and secure the agent fleet

Verify current governance, deployment, and pricing capabilities before shortlisting.

### Tekton Pipelines

Consider when:

- Kubernetes-native pipeline custom resources and execution are explicit requirements
- the organization can operate the Kubernetes control plane and surrounding developer experience
- portability within Kubernetes matters more than a turnkey CI/CD user interface

Do not recommend Tekton merely because workloads deploy to Kubernetes.

## Comparison Matrix

Score only viable shortlisted products from 0 to 5.

| Criterion | Weight |
|---|---:|
| Source-control and developer-workflow fit | 4 |
| Runner or agent topology | 4 |
| Environment and approval controls | 4 |
| Reuse and platform standardization | 3 |
| Artifact, test, and provenance handling | 3 |
| Security and identity model | 4 |
| Auditability and evidence | 3 |
| Private-network and target reachability | 4 |
| Scalability and concurrency | 3 |
| Reliability and recovery | 3 |
| Platform operations burden | 4 |
| Migration complexity | 2 |
| Total cost and licensing fit | 3 |
| Portability and lock-in | 2 |

Mandatory gates override scores.

## Required Analysis

For each finalist, state:

- exact product and edition or deployment model
- workflow-authoring model
- runner or agent model
- environment and approval design
- secrets and identity boundary
- artifact and evidence path
- reuse and governance model
- controller or SaaS availability assumptions
- migration approach
- operational owner
- largest residual risk

## Anti-Patterns

- selecting GitHub Actions only because code is hosted on GitHub without checking runner and governance requirements
- retaining Jenkins without accounting for controller and plugin operations
- selecting Azure Pipelines only because the target is Azure
- selecting Tekton only because the target is Kubernetes
- comparing hosted pricing while omitting self-hosted infrastructure and labor
- using CI/CD variables as the durable source of infrastructure or configuration truth
- allowing unpinned third-party tasks, actions, or plugins in privileged pipelines

## Expected Output

```markdown
## CI/CD Shortlist
| Product | Edition / Hosting | Best Fit | Main Gap | Mandatory Gates |
|---|---|---|---|---|

## Weighted Comparison

## Runner and Network Architecture

## Governance and Supply-Chain Controls

## Migration and Operating Cost

## Recommendation
```

## Quality Bar

- The shortlist reflects the actual SCM, hosting, runner, network, and governance environment.
- Product-edition differences are explicit.
- Existing investments and migration costs are considered without becoming automatic vetoes.
- Controller and runner operations are included in total cost.
- The recommendation states why the runner-up lost.
