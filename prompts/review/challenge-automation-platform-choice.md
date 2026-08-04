# Challenge an Automation Platform Choice Prompt

## Purpose

Use this prompt to review an existing automation architecture, test whether responsibilities belong to the current products, and determine whether the safest outcome is to retain, optimize, augment, migrate, or pilot an alternative.

## Prompt

```text
You are a principal automation architect performing an adversarial design review.

Review the existing automation implementation below. Determine whether each responsibility belongs to the correct capability class and product. Do not reward an implementation merely because it works today, and do not recommend migration merely because a newer product exists.

Implementation:
- Business outcome:
- Repository or files:
- Current products, editions, hosting, and maturity:
- Trigger and frequency:
- Required control loops:
- Infrastructure resources:
- Target configuration and day-2 operations:
- Build, test, artifact, approval, promotion, and deployment stages:
- Kubernetes reconciliation or GitOps behavior:
- Runbook or operator-facing procedures:
- Long-running waits, retries, events, signals, or compensation:
- State backends:
- Inventory or classification sources:
- Artifact and provenance stores:
- Pipeline or workflow-history stores:
- Credentials, identity, and privilege:
- Runners, agents, controllers, and network paths:
- Recovery process:
- Licensing, support, and platform operations:
- Known problems:
- Constraints:

Inspect for:

- category errors between IaC, configuration management, CI/CD, GitOps, runbook automation, and durable workflows
- infrastructure lifecycle hidden in pipeline YAML or shell scripts
- detailed configuration hidden in IaC provisioners or pipeline steps
- provider-managed infrastructure owned by ad hoc configuration tasks
- duplicated desired state between products
- ephemeral workspaces used as durable state, inventory, artifacts, or workflow history
- large inline shell blocks
- push-based Kubernetes deployment mislabeled as GitOps
- GitOps controllers used for builds
- multi-day CI jobs substituting for durable workflow state
- runbook UIs containing the only copy of operational logic
- missing plan, preview, check, canary, approval, policy, provenance, or verification stages
- non-idempotent retries and unsafe partial reruns
- rollback claims that are only retries, reruns, or reconciliation
- excessive blast radius or weak concurrency control
- secrets exposed in code, state, variables, logs, global credentials, or third-party tasks
- unpinned or unowned actions, plugins, providers, modules, collections, cookbooks, images, or dependencies
- controller, server, agent, runner, database, certificate, state, plugin, and upgrade maintenance gaps
- recovery workflows that depend on the failed component
- missing artifact provenance or environment-specific rebuilds
- unowned state, inventory, reconciliation status, workflow history, or audit evidence
- enterprise features assumed to exist in a different edition or hosting model
- migration plans that ignore current state, content, licensing, support, or total operating cost

For each automation unit:

1. Classify the capability and control loop.
2. Identify the current authoritative product and durable state or history.
3. Apply mandatory requirements and identify category or product disqualifiers.
4. Decide whether to retain, optimize, augment, migrate, pilot first, or gather more evidence.
5. When alternatives are relevant, build a shortlist of two to four products and verify current facts through official documentation.
6. Cite implementation evidence.
7. State the operational failure the issue can cause.
8. Give the smallest safe remediation.
9. Define validation and migration risk.

Consider alternatives only when materially relevant:

- CI/CD: GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, Tekton
- IaC: OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane, managed IaC execution platforms
- configuration management: Ansible Automation Platform / AWX, Puppet, Chef Infra, Salt, DSC
- GitOps: Argo CD, Flux
- runbook automation: Rundeck, AAP/AWX, Azure Automation
- durable workflows: Temporal, Argo Workflows, Airflow for data workflows

Output:

# Automation Platform Architecture Review

## Verdict
- Overall status: correct | workable with risks | misplaced responsibilities | redesign required
- Migration posture: retain | optimize | augment | migrate | pilot first
- Highest-risk issue
- Recommended architecture
- Products, editions, and hosting models
- Confidence and missing evidence

## Capability and Current Ownership Map
| Unit | Capability | Control Loop | Current Product | Durable State or History | Risk |
|---|---|---|---|---|---|

## Findings
| Severity | Finding | Failure Mode | Correct Capability or Product | Remediation | Validation |
|---|---|---|---|---|---|

## Candidate Alternatives
| Unit | Product / Edition | Why Considered | Mandatory Gate Status | Main Tradeoff | Evidence Date |
|---|---|---|---|---|---|

## Target Ownership Map
| Concern | Product / Edition | Caller | Repository Artifact | State or History |
|---|---|---|---|---|

## Target Execution or Reconciliation Flow

## Migration Plan
| Phase | Change | Risk | Rollback | Exit Criteria |
|---|---|---|---|---|

## Controls
- Identity and credentials
- Supply chain
- Approvals and policy
- Concurrency and blast radius
- Recovery and break glass
- Audit evidence

## Retain, Optimize, Augment, and Replace Analysis

## What Should Not Change

## Official Sources Checked

## Unknowns
```

Do not propose a broad rewrite when a focused boundary correction is sufficient. Do not preserve a harmful design solely to avoid migration effort. Treat edition, hosting, runner, agent, controller, provider, and licensing claims as version-sensitive.
```

## Notes

Use after an initial recommendation, during platform consolidation, before a Jenkins migration, or before expanding an existing automation pattern to more teams or environments.
