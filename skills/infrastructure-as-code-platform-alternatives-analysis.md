# Infrastructure as Code Platform Alternatives Analysis

## Purpose

Compare infrastructure-as-code products that can own persistent resource lifecycle, including Terraform, OpenTofu, Pulumi, AWS CloudFormation, Azure Bicep, Crossplane, and managed execution layers around those engines.

## When To Use

Use when an automation unit creates, imports, changes, replaces, reconciles, or destroys provider-managed infrastructure or platform resources.

## Candidate Set

Generate a shortlist from:

```text
Terraform
OpenTofu
Pulumi
AWS CloudFormation
Azure Bicep
Crossplane
```

Evaluate managed execution separately when required:

```text
HCP Terraform / Terraform Enterprise
Spacelift
env0
Scalr
Pulumi Cloud
```

A managed execution platform is not automatically a replacement for the underlying IaC engine or language.

## Hard Requirements

Evaluate before scoring:

- required cloud, SaaS, identity, network, Kubernetes, and on-prem provider coverage
- resource import and migration requirements
- state ownership, locking, encryption, backup, and recovery
- plan or preview behavior
- drift detection and reconciliation model
- policy, approval, and separation-of-duties requirements
- module, package, component, or template reuse model
- supported authoring languages and team maintainability
- offline, private-network, and air-gapped operation
- testing and local development
- existing state and module compatibility
- licensing, support, procurement, and vendor constraints
- control-plane availability and disaster recovery

## Product Fit Profiles

These profiles are hypotheses. Verify current official documentation, edition boundaries, provider coverage, and migration behavior.

### Terraform

Strong fit when:

- HCL, providers, modules, state-backed planning, and broad ecosystem coverage fit the estate
- existing Terraform state and modules are mature
- multi-cloud and SaaS resources require one common lifecycle model
- HCP Terraform, Terraform Enterprise, or another execution layer satisfies governance needs

Primary tradeoffs:

- state and provider lifecycle must be operated carefully
- licensing and distribution requirements must be evaluated for the intended edition and usage
- provider behavior and version upgrades can create migration work

### OpenTofu

Strong fit when:

- Terraform-style configuration and workflow compatibility are valuable
- Linux Foundation stewardship or the project's licensing and governance model is preferred
- existing configuration and providers can be validated for compatibility

Primary tradeoffs:

- compatibility must be tested rather than assumed indefinitely
- provider, module, tooling, and managed-platform support must be verified
- migration requires state backup, version testing, and rollback planning

### Pulumi

Strong fit when:

- general-purpose languages and their testing ecosystems materially improve infrastructure engineering
- component abstractions, packages, and programming-language reuse are strategic
- the team can govern application-language complexity in infrastructure code
- Pulumi state and optional Pulumi Cloud capabilities fit operations

Primary tradeoffs:

- infrastructure code can become overly imperative or architecturally complex
- language runtime, package, and dependency management become part of the IaC platform
- migration from HCL modules and state may be substantial

### AWS CloudFormation

Strong fit when:

- AWS is the dominant or exclusive platform
- AWS-native lifecycle integration and support are more important than multi-cloud portability
- stack and change-set behavior fits the deployment model

Primary tradeoffs:

- AWS-specific authoring and portability
- coverage and ergonomics vary across resource types and release timing
- cross-cloud or broad SaaS management requires additional tools

### Azure Bicep

Strong fit when:

- Azure Resource Manager is the primary lifecycle target
- Azure-native authoring, deployment scopes, and integration are strategic
- multi-cloud abstraction is not required for the unit

Primary tradeoffs:

- Azure-specific lifecycle ownership
- non-Azure and SaaS resource management requires another engine
- organization-wide consistency may suffer if other clouds use a different IaC model

### Crossplane

Strong fit when:

- Kubernetes APIs and reconciliation are explicitly desired as the infrastructure control plane
- platform teams need composite resources and self-service abstractions
- continuous reconciliation is preferable to run-based plans and applies
- the organization can operate and secure the Kubernetes control plane and providers

Primary tradeoffs:

- Kubernetes becomes a critical infrastructure control plane
- provider maturity and resource semantics require careful validation
- plan, approval, and change-review patterns differ from conventional IaC
- operational complexity is high when Kubernetes-native control is not already strategic

## Engine Versus Execution Layer

Separate these decisions:

```text
1. Which engine or language owns resource lifecycle?
2. Where are plans, applies, state, policies, approvals, and drift runs executed?
```

Possible architectures include:

```text
Terraform + HCP Terraform
OpenTofu + self-hosted CI
OpenTofu + compatible managed orchestration
Pulumi + Pulumi Cloud
Terraform or OpenTofu + Spacelift, env0, or Scalr
Bicep + Azure Pipelines or GitHub Actions
CloudFormation + AWS-native pipeline services
Crossplane + GitOps controller
```

Verify current product support before recommending a pairing.

## Comparison Matrix

| Criterion | Weight |
|---|---:|
| Required resource and provider coverage | 5 |
| State, identity, and import fit | 5 |
| Plan, preview, drift, and reconciliation model | 4 |
| Language and maintainability | 3 |
| Module or component ecosystem | 3 |
| Testing and developer experience | 3 |
| Policy, approval, and audit | 4 |
| Security and secret boundaries | 4 |
| Offline and private-network fit | 3 |
| Existing-state compatibility | 4 |
| Migration complexity | 3 |
| Operational burden | 3 |
| Licensing and support fit | 3 |
| Portability and lock-in | 2 |

Mandatory provider, state, security, or hosting gaps are disqualifiers regardless of score.

## Required Analysis

For each finalist, state:

- engine and version or edition assumptions
- execution and state architecture
- provider coverage validation
- import or migration approach
- plan, approval, and apply flow
- drift and reconciliation behavior
- state recovery and break-glass process
- module or component strategy
- testing strategy
- policy and audit controls
- largest lock-in and operational risks

## Anti-Patterns

- choosing a language before verifying provider coverage
- choosing OpenTofu solely as a drop-in replacement without compatibility tests
- choosing Pulumi solely because developers prefer a programming language
- choosing a cloud-native engine for a multi-cloud unit without decomposition
- placing state in CI workspaces
- confusing a managed execution platform with the IaC engine
- allowing multiple engines to own the same resource attributes
- claiming declarative authoring guarantees safe rollback

## Expected Output

```markdown
## IaC Shortlist
| Product | Engine / Execution Model | Best Fit | Main Gap | Mandatory Gates |
|---|---|---|---|---|

## State and Control-Plane Architecture

## Provider and Migration Evidence

## Weighted Comparison

## Recommendation
```

## Quality Bar

- Engine selection and execution-layer selection are separated.
- Provider and import compatibility are evidenced.
- State recovery is designed before adoption.
- Existing state and modules are treated as migration assets and liabilities.
- Cloud-native products are recommended only for appropriately bounded units.
- The recommendation states why the runner-up lost.
