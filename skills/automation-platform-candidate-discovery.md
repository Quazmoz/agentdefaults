# Automation Platform Candidate Discovery

## Purpose

Build a current, evidence-backed shortlist of automation products after the workload has been classified by capability. The skill expands beyond the incumbent Terraform, Ansible, and Jenkins stack without turning the result into an unbounded product catalog.

## When To Use

Use when:

- the current products are not an obvious fit
- the user explicitly wants alternatives
- a platform consolidation or migration is being considered
- hosting, source-control, cloud, compliance, licensing, or operational constraints may favor another product
- a category such as GitOps, runbook automation, or durable workflows is required

## Inputs Needed

- capability class for each automation unit
- incumbent products and maturity
- source-control and cloud platforms
- SaaS, self-hosted, hybrid, and air-gapped requirements
- runner, agent, controller, and target connectivity requirements
- operating systems, Kubernetes, network devices, and cloud targets
- compliance, approval, audit, and separation-of-duties requirements
- licensing, support, procurement, and budget constraints
- team skills and support ownership
- migration tolerance and deadline
- open-source or vendor requirements

## Candidate Policy

Use one of these modes:

```text
current_stack_only
  Compare only explicitly approved incumbent products.

current_stack_plus_alternatives
  Start with incumbents and add materially relevant alternatives.

open_market
  Build the shortlist from the capability class and constraints without favoring incumbents.
```

Default to `current_stack_plus_alternatives` unless the brief says otherwise.

## Discovery Process

### 1. Start with the capability class

Do not search for products until the automation unit has been classified using `automation-platform-capability-taxonomy.md`.

### 2. Build a longlist

Use the category catalog as a starting point, not as an exhaustive or permanently current list.

```text
Infrastructure as Code
  Terraform, OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane

Configuration Management
  Ansible/AAP/AWX, Puppet, Chef Infra, Salt, PowerShell DSC

CI/CD
  Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, Tekton

GitOps CD
  Argo CD, Flux

Runbook Automation
  Rundeck, AAP/AWX, Azure Automation

Managed IaC Execution
  HCP Terraform/Terraform Enterprise, Spacelift, env0, Scalr, Pulumi Cloud

Durable Workflow Orchestration
  Temporal, Argo Workflows, Airflow where data workflows dominate
```

Add another product only when it belongs to the correct capability class and a concrete workload constraint makes it relevant.

### 3. Apply elimination gates

Eliminate candidates that fail a mandatory requirement before weighted scoring.

Mandatory gates may include:

- required self-hosted, SaaS, hybrid, or air-gapped deployment model
- supported source-control provider
- runner or agent support for target operating systems and architectures
- private-network and outbound-connectivity model
- Kubernetes-native requirement
- Windows, network-device, or mainframe support
- required cloud or provider coverage
- approval, audit, identity, and separation-of-duties controls
- data residency or evidence-retention requirements
- open-source, licensing, procurement, or vendor-support constraints
- required API, plugin, module, provider, action, or collection maturity
- recovery requirements when the control plane is unavailable

### 4. Verify current product facts

For every shortlisted product:

1. Use official product documentation first.
2. Record the product or edition name.
3. Record documentation access date and relevant version when available.
4. Separate open-source, hosted, enterprise, and add-on capabilities.
5. Verify plan- or edition-specific features such as approvals, private runners, environments, policy, SSO, audit logs, and retention.
6. Mark unresolved pricing, licensing, roadmap, or support claims as unknown.
7. Do not rely on comparison blogs for definitive capability claims when official documentation exists.

Current facts that always require verification include:

- product availability and edition names
- supported hosting models
- runner or agent support
- approval and environment controls
- limits and quotas
- security and identity integrations
- licensing and pricing
- support lifecycle
- migration compatibility

### 5. Shortlist only viable products

Keep the final shortlist small:

```text
2 to 4 products per capability class by default
5 maximum when the decision is genuinely close
```

Include the incumbent even if it is weak when migration cost is material, then label it accurately.

### 6. Compare implementation and operating models

Product fit includes both workload capability and sustainable operation.

Evaluate:

- authoring model and language
- control-plane hosting
- runner, agent, or reconciliation model
- state, inventory, artifact, and history ownership
- ecosystem maturity
- testing and local-development experience
- secrets and identity integration
- policy, approvals, and auditability
- observability and failure diagnosis
- upgrade and plugin dependency burden
- scalability and concurrency
- portability and lock-in
- migration complexity
- total operational cost, not only license cost

## Product-Affinity Signals

These are candidate-generation signals, not automatic decisions.

### Source-control affinity

- GitHub-centered repositories and governance may favor GitHub Actions.
- Azure Repos, Azure Boards, Azure Artifacts, or existing Azure DevOps governance may favor Azure Pipelines.
- GitLab-centered source control and security workflows may favor GitLab CI/CD.
- mixed or legacy source-control estates may preserve a case for Jenkins or another independent orchestrator.

### Cloud affinity

- Azure-native resource authoring may justify Bicep.
- AWS-native stacks may justify CloudFormation.
- multi-cloud or SaaS-heavy estates may favor Terraform, OpenTofu, or Pulumi.
- Kubernetes control-plane reconciliation may justify Crossplane for selected resource classes.

### Operating-model affinity

- agentless push automation may favor Ansible.
- continuous agent-based configuration enforcement may favor Puppet, Chef, Salt, or DSC depending on the estate.
- pull-based Kubernetes reconciliation may favor Argo CD or Flux.
- deep pipeline customization and heterogeneous self-hosting may preserve a Jenkins use case despite its operating burden.

## Required Output

```markdown
## Candidate Policy

## Product Longlist
| Product | Capability Class | Why Considered | Mandatory Gate Status |
|---|---|---|---|

## Eliminated Candidates
| Product | Failed Requirement | Evidence | Reconsider If |
|---|---|---|---|

## Shortlist
| Product | Edition / Hosting | Strongest Fit | Main Tradeoff | Migration Impact | Evidence Date |
|---|---|---|---|---|---|

## Unknowns Requiring Verification

## Official Sources Checked
```

## Guardrails

- Do not recommend a product because it is popular or already known to the agent.
- Do not manufacture a feature matrix from memory.
- Do not compare a product's enterprise edition with another product's free edition without labeling the difference.
- Do not treat an action, plugin, module, provider, or marketplace listing as maintained without checking.
- Do not produce ten shallow candidates when three viable candidates are enough.
- Do not recommend migration when the incumbent meets requirements and migration value is weak.
- Do not hide procurement, licensing, support, or control-plane operations from total-cost analysis.

## Quality Bar

- Candidate generation follows capability classification.
- Mandatory constraints eliminate products before scoring.
- The shortlist is current, small, and evidence-backed.
- Edition and hosting differences are explicit.
- The incumbent is compared fairly against migration cost.
- Unknowns are visible and tied to a verification action.
