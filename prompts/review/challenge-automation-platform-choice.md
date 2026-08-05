# Challenge an Automation Platform Choice Prompt

## Purpose

Use this prompt to review an existing automation architecture, test whether responsibilities belong to the current products, distinguish product limitations from implementation defects, and determine whether the safest outcome is to retain, optimize, augment, migrate, or pilot an alternative.

## Prompt

```text
You are a principal automation architect performing an adversarial design review.

Review the existing implementation below. Determine whether each responsibility belongs to the correct capability class and product. Do not reward an implementation merely because it works today, and do not recommend migration merely because a newer product exists.

Implementation:
- Business outcome and decision owner:
- Output depth: quick_triage | standard | full_architecture_review
- Decision horizon and risk tolerance:
- Repository or files:
- Current products, editions, hosting, maturity, content inventory, and annual operating burden:
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
- Licensing, support, procurement, and platform operations:
- Evidence cutoff and required evidence coverage:
- Migration tolerance, reversibility, and exit requirements:
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
- product limitations confused with correctable implementation defects
- migration plans that ignore current state, content, dual running, training, licensing, support, reversibility, or total operating cost
- weighted scores built on stale, conflicting, or unknown evidence

For each automation unit:

1. Classify it with an exact canonical capability identifier and control loop.
2. Identify the current authoritative product and durable state or history.
3. Apply mandatory requirements and identify category or product disqualifiers.
4. Separate product limitations from implementation, governance, or operating-model problems.
5. Decide whether to retain, optimize, augment, migrate, pilot first, or gather more evidence.
6. When alternatives are relevant, build a shortlist of two to four exact products, editions, and hosting models.
7. Verify current facts through observed configuration and official documentation, recording source dates.
8. Keep raw fit and evidence confidence separate. Do not score unknowns as zero.
9. Treat candidates within 5 percent as effectively tied unless a hard requirement or material operating difference decides the result.
10. Compare the do-nothing baseline with migration cost, recurring burden, dual running, reversibility, and expected benefit over the decision horizon.
11. Cite implementation evidence and state the operational failure each finding can cause.
12. Give the smallest safe remediation and define validation.
13. Define a proof-of-fit pilot with rollback and a stopping rule where evidence remains incomplete.

Consider alternatives only when materially relevant:

- CI/CD: GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, Tekton
- IaC: OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane, managed IaC execution platforms
- configuration management: Ansible Automation Platform / AWX, Puppet, Chef Infra, Salt, DSC
- GitOps: Argo CD, Flux
- runbook automation: Rundeck, AAP/AWX, Azure Automation
- durable workflows: Temporal, Argo Workflows, Airflow for data workflows

Output only the sections required by the selected depth.

# Automation Platform Architecture Review

## Verdict
- Overall status: correct | workable_with_risks | misplaced_responsibilities | redesign_required
- Migration posture: retain | optimize | augment | migrate | pilot_first | needs_more_evidence
- Highest-risk issue
- Recommended architecture
- Products, editions, and hosting models
- Confidence and weighted evidence coverage

## Capability and Current Ownership Map
| Unit | Capability | Control Loop | Current Product | Durable State or History | Risk |
|---|---|---|---|---|---|

## Findings
| Severity | Finding | Product Limitation or Implementation Defect | Failure Mode | Remediation | Validation |
|---|---|---|---|---|---|

## Mandatory Gates and Evidence Quality

## Candidate Alternatives
| Unit | Product / Edition | Why Considered | Gate Status | Raw Fit | Evidence Confidence | Main Tradeoff |
|---|---|---|---|---:|---|---|

## Target Ownership Map
| Concern | Product / Edition | Caller | Repository Artifact | State or History |
|---|---|---|---|---|

## Target Execution or Reconciliation Flow

## Migration Economics and Reversibility
| Posture | One-Time Cost | Recurring Burden | Benefit | Risk | Reversibility |
|---|---:|---:|---|---|---|

## Migration Plan
| Wave | Change | Entry Criteria | Exit Criteria | Rollback |
|---|---|---|---|---|

## Controls
- Identity and credentials
- Supply chain
- Approvals and policy
- Concurrency and blast radius
- Recovery and break glass
- Audit evidence

## Proof-of-Fit Pilot

## What Should Not Change

## Evidence Ledger and Official Sources

## Unknowns
```

Do not propose a broad rewrite when a focused boundary correction is sufficient. Do not preserve a harmful design solely to avoid migration effort. Treat edition, hosting, runner, agent, controller, provider, licensing, and lifecycle claims as version-sensitive.
```

## Notes

Use after an initial recommendation, during platform consolidation, before a Jenkins migration, or before expanding an existing automation pattern to more teams or environments.
