# Automation Platform Selection Acceptance Tests

## Purpose

Validate that the automation-platform stack classifies workloads before comparing products, preserves ownership boundaries, applies mandatory gates, distinguishes fit from evidence confidence, compares migration economics fairly, and does not force Terraform, Ansible, Jenkins, or a newer alternative into responsibilities they should not own.

## Test Method

For each scenario:

1. Run the canonical agent and orchestrator at the requested output depth.
2. Confirm brief contradictions are surfaced before analysis.
3. Confirm decomposition and canonical capability classification occur before product scoring.
4. Confirm each automation unit has one authoritative owner.
5. Confirm mandatory gates are applied before weighted scoring.
6. Confirm the shortlist contains only viable products in the correct capability class.
7. Confirm exact product edition, hosting model, evidence status, and evidence date are visible for version-sensitive claims.
8. Confirm raw fit, evidence confidence, adjusted points, and unknowns are distinct.
9. Confirm retain, optimize, augment, migrate, pilot-first, and the do-nothing baseline are considered where applicable.
10. Confirm a falsifiable proof-of-fit pilot includes rollback and a stopping rule when material uncertainty remains.

## Required Scenarios

### 1. Multi-cloud persistent infrastructure

Input: Manage Azure, AWS, SaaS, identity, networks, and databases with mature Terraform state while evaluating OpenTofu and Pulumi.

Expected:

- Classify as `infrastructure_as_code`.
- Compare Terraform, OpenTofu, and Pulumi as engines, not against CI/CD products.
- Address provider coverage, state, import, modules, language, licensing, migration, and execution layers.
- Retaining Terraform remains valid when migration value is weak.

### 2. Azure-native bounded infrastructure

Input: Manage only Azure Resource Manager resources for one Azure-native team while Terraform remains the enterprise standard.

Expected:

- Bound the unit before comparing Terraform and Bicep.
- Treat Azure affinity as a signal, not an automatic answer.
- Include consistency, state or deployment history, testing, policy, modules, skill reuse, and operating cost.

### 3. Existing server configuration

Input: Install packages, manage files, rotate certificates, restart services, and verify 500 Linux servers during maintenance windows.

Expected:

- Classify as `configuration_management` or `runbook_automation`.
- Ansible or AAP is a strong candidate.
- Address inventory, privilege, idempotency, canaries, batching, partial failure, and verification.
- CI/CD may call the work but does not own target configuration.

### 4. Continuous configuration enforcement

Input: Continuously enforce baselines and report node state every 30 minutes across 5,000 Linux and Windows servers.

Expected:

- Control loop is `continuous_reconciliation`.
- Evaluate Puppet, Chef Infra, Salt, DSC, and Ansible-based approaches by topology and target coverage.
- Include agent, server, certificate, reporting, upgrade, and support operations.

### 5. GitHub-centered CI/CD

Input: GitHub Enterprise Cloud owns repositories and governance; builds need private Linux and Windows runners, protected environments, immutable artifacts, and reusable workflows.

Expected:

- Classify as `ci_cd`.
- Compare Jenkins and GitHub Actions with exact runner and hosting assumptions.
- Include action pinning, isolation, approvals, controller operations, migration, evidence, and total cost.
- GitHub affinity is not an automatic decision.

### 6. Azure DevOps-centered CI/CD

Input: Azure Repos, Boards, Artifacts, service connections, environments, and private Windows agents are established while Jenkins performs delivery.

Expected:

- Compare Jenkins and Azure Pipelines because the operating model is relevant.
- Address protected resources, agent pools, permissions, traceability, YAML versus classic behavior, migration, and evidence.
- Azure as a target alone does not decide the result.

### 7. GitLab integrated delivery

Input: GitLab owns source, merge requests, registry, security scanning, and issues while Jenkins is connected by webhooks.

Expected:

- Shortlist GitLab CI/CD based on verified platform integration.
- Address runners, reusable components, downstream pipelines, environments, approvals, edition limits, and migration.
- Explain why the runner-up lost.

### 8. Kubernetes GitOps

Input: Build and deploy 40 services to six clusters using pull-based reconciliation, drift visibility, health, and Git-based promotion.

Expected:

- Split `ci_cd` from `gitops_continuous_delivery`.
- CI owns build, test, signing, artifact publication, and desired-state change proposals.
- Argo CD or Flux owns reconciliation.
- Do not score CI/CD and GitOps products as direct substitutes.

### 9. Full-stack delivery

Input: Create cloud infrastructure, configure hosts, build an application, and deploy to Kubernetes and virtual machines.

Expected:

- Decompose into IaC, configuration, CI/CD, and possibly GitOps units.
- Generate candidates per capability.
- Assign one owner per unit and explicit handoffs.
- Do not force one product.

### 10. Misplaced Jenkins shell automation

Input: A 1,500-line Jenkinsfile creates cloud resources, edits server configuration, builds artifacts, deploys manifests, and waits three days for a callback.

Expected:

- Identify IaC, configuration, CI/CD, deployment, and durable-workflow category errors.
- Move domain logic to native engines.
- Evaluate a durable workflow engine for the callback.
- Use a phased migration, not a big-bang rewrite.

### 11. Terraform provisioner misuse

Input: Terraform creates VMs and uses remote-exec for all middleware and application deployment.

Expected:

- IaC remains infrastructure owner.
- Configuration management owns target convergence.
- Explain rerun, secret, and partial-failure risks.
- Do not introduce engine migration without material relevance.

### 12. Ansible cloud lifecycle overreach

Input: Ansible creates and deletes a large cloud estate without durable infrastructure state or drift management.

Expected:

- Reclassify resource lifecycle as `infrastructure_as_code`.
- Produce an IaC shortlist based on provider, state, hosting, and migration requirements.
- Keep Ansible for configuration and day-two operations.

### 13. Managed IaC governance

Input: Terraform code is sound, but Jenkins holds plans, shared credentials, approvals, and drift scheduling.

Expected:

- Separate the IaC engine from `managed_iac_execution`.
- Compare viable managed execution products using hosting, private execution, policy, state, identity, support, and procurement gates.
- Jenkins may remain CI while another product owns Terraform execution.

### 14. Runbook automation

Input: Operations needs a self-service catalog for restarts, certificate rotation, failover checks, and remediation with forms, RBAC, schedules, logs, and maintenance windows.

Expected:

- Classify as `runbook_automation`.
- Distinguish execution engine from operator surface.
- Consider Rundeck, AAP/AWX, Azure Automation, or incumbents only when environment fit justifies them.
- Address operation during CI-platform failure.

### 15. Durable business workflow

Input: Run a months-long workflow with timers, callbacks, signals, compensation, and durable business state.

Expected:

- Classify as `durable_workflow_orchestration`.
- Do not force Jenkins, GitHub Actions, or Azure Pipelines into the role.
- Address workflow state, versioning, retries, compensation, worker failure, and recovery.

### 16. Air-gapped environment

Input: Automate infrastructure, configuration, and CI/CD with no SaaS control plane or public marketplace access.

Expected:

- Eliminate SaaS-only candidates before scoring.
- Require exact self-hosted or air-gapped editions.
- Address dependency mirroring, updates, certificates, supply-chain evidence, and support.

### 17. Incumbent remains best fit

Input: Jenkins is well maintained, uses isolated ephemeral agents, approved plugins, tested libraries, reliable backups, and low operating cost; GitHub hosts few repositories.

Expected:

- Retain or optimize Jenkins may be correct.
- Do not manufacture a migration case.
- Provide reevaluation triggers and measurable pilot criteria.

### 18. Platform outage recovery

Input: Design automated recovery for the primary CI/CD controller.

Expected:

- Identify circular dependency risk.
- Decompose IaC, configuration, backup, credential, and bootstrap units.
- Recovery must run independently of the failed controller.

### 19. Ambiguous database deployment

Input: Automate database deployment.

Expected:

- Separate managed database lifecycle, schema migration, configuration, data movement, application delivery, and pipeline coordination.
- State assumptions and confidence.
- Do not select based on the word `deployment`.

### 20. Edition and pricing discipline

Input: Recommend the cheapest product with approvals, private runners, audit logs, and one-year evidence retention.

Expected:

- Require exact editions, hosting, limits, licensing, and official evidence dates.
- Mark unresolved pricing or procurement as unknown.
- Do not confuse license price with total cost.

### 21. Contradictory hosting constraints

Input: `self_hosted_required: true`, `air_gapped_required: true`, but `allowed_hosting_models` contains only `saas`.

Expected:

- Schema validation or intake consistency checks fail before product analysis.
- The advisor does not silently reinterpret the brief.
- The output identifies the exact contradiction and required correction.

### 22. Unknown evidence is not failure

Input: Two CI/CD products appear suitable, but private-runner limits and audit-retention behavior for one exact edition cannot be verified.

Expected:

- The missing facts are `unknown`, not score zero.
- Evidence coverage and confidence decrease.
- The result is `needs_more_evidence` or `pilot_first` when the unknown is material.
- Verification actions are prioritized by decision impact.

### 23. Effective scoring tie

Input: Two candidates are within 3 percent of applicable weighted points and both pass mandatory gates; the incumbent has lower migration cost.

Expected:

- Treat the products as effectively tied.
- Do not claim a decisive numeric winner.
- Prefer retaining or piloting unless a strategic or operating-model advantage justifies migration.

### 24. Migration economics reverse the feature winner

Input: A new CI/CD product scores slightly higher on features, but migration requires rewriting 300 pipelines, dual running for a year, retraining, and recreating seven years of audit evidence.

Expected:

- Compare retain, optimize, augment, migrate, and pilot-first over the decision horizon.
- Include one-time, recurring, dual-running, risk, and evidence-retention cost.
- The recommendation may retain or optimize the incumbent despite the higher raw feature score.
- Define reversibility and migration waves if a pilot proceeds.

### 25. Output-depth discipline

Input: A low-risk user asks only, “Should this scheduled certificate rotation be in Jenkins or Ansible?” and requests `quick_triage`.

Expected:

- Return a compact capability decision, blockers, strongest alternative, confidence, and next validation step.
- Do not emit a full product catalog, economics model, or large matrix.
- Preserve essential privilege, inventory, recovery, and audit caveats.

## Structural Checks

Standard and full-review outputs must include, as applicable:

- executive decision, output depth, decision owner, horizon, and migration posture
- workload decomposition with canonical capability identifiers
- control-loop classification and authoritative records
- candidate policy and mandatory gates
- small product shortlist with exact edition and hosting model
- evidence quality summary and weighted evidence coverage
- raw fit separated from confidence and adjusted points
- ownership map and platform boundaries
- execution or reconciliation flow
- security, supply chain, governance, and recovery controls
- migration economics, reversibility, and do-nothing baseline
- proof-of-fit pilot with rollback and stopping rule
- rejected alternatives and runner-up explanation
- evidence ledger, official sources, and unknowns

Quick-triage output must include only:

- capability
- recommended posture and product
- confidence
- mandatory blockers
- strongest alternative
- next validation step
- material assumptions

## Failure Conditions

Fail the stack if it:

- analyzes contradictory constraints without surfacing them
- recommends a product for an undecomposed compound request
- uses inconsistent capability identifiers
- compares products from different capability classes as direct substitutes
- assigns two authoritative owners to the same state
- scores a candidate that failed a mandatory requirement
- scores unknown evidence as zero
- includes non-applicable criteria in the denominator
- declares a decisive winner from an immaterial score difference
- produces an unfiltered product catalog
- selects CI/CD as infrastructure, configuration, or durable-workflow source of truth
- labels push-based deployment as GitOps
- equates idempotency, retry, rerun, or reconciliation with rollback
- omits credentials, supply chain, approvals, or recovery for high-impact work
- relies exclusively on the failed platform for its own recovery
- assumes enterprise features exist in another edition or hosting model
- recommends migration without comparing optimization, the do-nothing baseline, dual running, and reversibility
- uses stale or unofficial claims when current official documentation is available
- produces full-review volume for a requested quick triage

## Repository Validation

```bash
python3 scripts/validate-agentdefaults.py
```
