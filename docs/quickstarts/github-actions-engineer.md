# GitHub Actions Engineer Quickstart

## Purpose

Provide the shortest safe path to using the GitHub Actions Engineer for workflow/action implementation, debugging, hardening, reusable-workflow design, release automation, and qualification.

## Canonical Stack

```text
agents/github-actions-engineer.md
skills/github-actions-engineering.md
prompts/implementation/github-actions-task.md
schemas/github-actions-task.schema.json
examples/github-actions-task.yaml
docs/github-actions-engineer-acceptance-tests.md
.github/agents/github-actions-engineer.agent.md
scripts/validate-github-actions-stack.py
```

## Upstream Reference

The specialist was informed by GitHub's public `github/awesome-copilot` `github-actions-expert.agent.md`, then adapted to AgentDefaults' canonical-agent architecture and hardened for trust-boundary, reliability, reusable-workflow, runner, provenance, and cost failure modes.

The upstream reference is not the runtime authority. Use current official GitHub documentation for changing platform behavior.

## Authoritative GitHub References

Start with the current GitHub documentation relevant to the task, especially:

- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [Securely using `pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Reusing workflow configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [OpenID Connect reference](https://docs.github.com/en/actions/reference/security/oidc)
- [Using OpenID Connect with reusable workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows)
- [Dependabot on GitHub Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions)

Verify provider-specific OIDC and release semantics from that provider's current official documentation as well.

## Use It For

- `.github/workflows/*.yml` / `.yaml`
- reusable workflows and `workflow_call`
- composite, JavaScript, and Docker actions
- CI and release pipelines implemented with GitHub Actions
- `GITHUB_TOKEN` permissions
- Actions, Dependabot, and environment secret boundaries
- OIDC federation and reusable-workflow identity
- action/reusable-workflow pinning and repository provenance
- GitHub-hosted and self-hosted runners
- caches, artifacts, packages, releases, attestations, and SBOMs
- `pull_request`, `pull_request_target`, `workflow_run`, Dependabot, and other trigger trust boundaries
- matrices, concurrency, cancellation, reruns, retries, timeouts, and CI cost
- release/package/deployment automation and artifact promotion

## Do Not Use It For

- broad infrastructure/platform architecture where Actions is incidental: use [`principal-devops-engineer.md`](principal-devops-engineer.md)
- defensive security spanning several DevOps platforms: use [`devsecops-security-engineer.md`](devsecops-security-engineer.md)
- choosing whether Actions is the right automation platform: use [`../../AUTOMATION_PLATFORM_INDEX.md`](../../AUTOMATION_PLATFORM_INDEX.md)

## Fast Start

For a normal interactive task provide:

```text
Repository: owner/repo
Branch/ref: current main or explicit target
Mode: investigate | review | design | implement | incident | release
Goal: observable outcome
Scope: workflow/action files, run IDs, or failing job/step
Trust: event actors, lower-trust inputs, privileged identities, runner boundary, artifact/cache boundary
Authority: observe | propose | mutate_reversible | mutate_irreversible
Constraints: runner, environment, security, quota/cost, compatibility, release requirements
Acceptance: measurable completion criteria
```

For a repeatable task copy [`../../prompts/implementation/github-actions-task.md`](../../prompts/implementation/github-actions-task.md). For machine-readable orchestration validate input against [`../../schemas/github-actions-task.schema.json`](../../schemas/github-actions-task.schema.json); start from [`../../examples/github-actions-task.yaml`](../../examples/github-actions-task.yaml).

## Mandatory First Pass

Before mutation establish:

```text
trigger actor/trust
workflow revision
source/ref/download origin
GITHUB_TOKEN permissions
Actions/Dependabot/environment secrets
OIDC/external identity
runner boundary
reusable-workflow call chain
cache/artifact producer -> consumer trust
external side effects
concurrency/cancellation/rerun behavior
authoritative postcondition
```

Inspect relevant repository/org Actions settings, rulesets, branch protection, environments, and runner-group policy; YAML alone does not prove those runtime controls.

## High-Risk Shapes

Escalate scrutiny for:

- `pull_request_target` or another privileged event
- `workflow_run` consuming artifacts produced by lower-trust PR workflows
- Dependabot workflows that fail because Actions secrets/write tokens are intentionally unavailable
- self-hosted runners processing fork/PR code
- broad write permissions
- cloud/deployment credentials or OIDC
- mutable third-party action/reusable-workflow tags/branches
- full SHAs copied from the wrong repository/fork
- release/package/tag creation
- production deployment
- cache sharing across different trust levels
- shell/program source containing event/PR/issue expressions
- reusable workflows that appear to require more permission than callers grant
- cancellation/rerun of non-idempotent external mutations

## Platform Semantics to Remember

Do not rely on these from memory when they are material; verify current docs first. The specialist explicitly models that:

- full commit SHA pinning is GitHub's immutable-reference control for actions, and the SHA must be verified against the intended repository;
- `pull_request_target` runs with elevated trust and must not execute lower-trust PR code;
- `workflow_run` does not make an artifact trustworthy merely by downloading it in a privileged run;
- Dependabot-triggered workflows have special token/secret restrictions;
- nested reusable-workflow `GITHUB_TOKEN` permissions can only be maintained or reduced, not elevated;
- OIDC can expose reusable-workflow identity claims such as `job_workflow_ref` / `job_workflow_sha` for provider trust designs;
- self-hosted runners are not guaranteed to be ephemeral or clean and require an explicit isolation/access model;
- non-SHA reusable-workflow references can complicate rerun identity, so consequential workflows should prefer immutable references.

## Permission Model

```text
observe
propose
mutate_reversible
mutate_irreversible
```

Repository write access does not automatically authorize publishing, deploying, credentials/OIDC mutation, repository/org protection changes, privileged runner changes, destructive cleanup, or unsafe reruns.

## Verification Baseline

Apply what is relevant:

```text
YAML/parser validation
actionlint
workflow/action-specific static/security checks
custom-action tests
shell/static checks
permission audit
trigger/trust-boundary audit
Dependabot/fork behavior audit
full-SHA + intended-repository provenance audit
reusable-workflow permission/secret/OIDC audit
representative GitHub Actions run
failure/rerun/cancellation/concurrency tests
artifact/release/deployment postcondition verification
```

A local runner/emulator is useful for limited step logic but is not proof of GitHub token, secret, Dependabot, event, environment, OIDC, cache, or hosted-runner semantics.

## Validation of This Stack

After modifying the specialist run:

```bash
python3 scripts/validate-github-actions-stack.py
python3 scripts/validate-agentdefaults.py
```

The stack-specific validator checks manifest registration, schema invariants, routing, canonical security/reliability concepts, the worked example, Copilot adapter references, and inclusion in the primary suite.

## Expected Delivery

```text
STATUS
MODE
DISCOVERED
TRUST BOUNDARY
IMPLEMENTED
VERIFIED
UNVERIFIED
RISKS
HANDOFF
USER ACTION
```

Never promote an unexecuted check into `VERIFIED`.
