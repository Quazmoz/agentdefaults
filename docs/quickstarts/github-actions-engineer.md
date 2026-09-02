# GitHub Actions Engineer Quickstart

## Purpose

Provide the shortest safe path to using the GitHub Actions Engineer for workflow/action implementation, debugging, hardening, release automation, and qualification.

## Canonical Stack

```text
agents/github-actions-engineer.md
skills/github-actions-engineering.md
docs/github-actions-engineer-acceptance-tests.md
.github/agents/github-actions-engineer.agent.md
```

## Upstream Reference

The specialist was informed by GitHub's public `github/awesome-copilot` `github-actions-expert.agent.md`, then adapted to AgentDefaults' canonical-agent architecture and hardened against current GitHub Actions trust-boundary and reliability failure modes.

Use current official GitHub Actions documentation as authority for changing platform behavior.

## Use It For

- `.github/workflows/*.yml` / `.yaml`
- reusable workflows
- composite, JavaScript, and Docker actions
- CI and release pipelines implemented with GitHub Actions
- `GITHUB_TOKEN` permissions
- secrets and environments
- OIDC federation
- action/reusable-workflow pinning
- GitHub-hosted and self-hosted runners
- caches and artifacts
- `pull_request`, `pull_request_target`, `workflow_run`, and other trigger trust boundaries
- matrices, concurrency, retries, timeouts, and CI cost
- release/package/deployment automation
- artifact provenance, attestations, and SBOM integration

## Do Not Use It For

- broad infrastructure/platform architecture where Actions is incidental: use [`principal-devops-engineer.md`](principal-devops-engineer.md)
- security work spanning several DevOps platforms: use [`devsecops-security-engineer.md`](devsecops-security-engineer.md)
- choosing whether Actions is the right automation platform: use [`../../AUTOMATION_PLATFORM_INDEX.md`](../../AUTOMATION_PLATFORM_INDEX.md)

## Fast Start

Give the agent:

```text
Repository: owner/repo
Branch/ref: current main or explicit target
Mode: investigate | review | design | implement | incident | release
Goal: observable outcome
Scope: workflow/action files or failing run
Authority: observe | propose | mutate_reversible | mutate_irreversible
Constraints: runner, environment, security, quota/cost, release requirements
Acceptance: measurable completion criteria
```

When debugging, include the workflow run/job/step identifiers or logs when available. The agent should inspect authoritative run evidence rather than guessing from YAML.

## Mandatory First Pass

Before mutation, establish:

```text
trigger actor/trust
workflow revision
checkout/download source
GITHUB_TOKEN permissions
secrets/OIDC identity
runner boundary
cache/artifact flow
external side effects
concurrency/retry behavior
postcondition evidence
```

## High-Risk Shapes

Escalate scrutiny for:

- `pull_request_target` or other privileged events
- `workflow_run` consuming artifacts produced by untrusted PR workflows
- self-hosted runners processing fork/PR code
- broad write permissions
- cloud/deployment credentials
- mutable third-party action tags/branches
- release/package/tag creation
- production deployment
- cache sharing across different trust levels
- shell commands containing event/PR/issue expressions

## Permission Model

```text
observe
propose
mutate_reversible
mutate_irreversible
```

Repository write access does not automatically authorize publishing, deploying, credential/OIDC changes, protection changes, destructive cleanup, or unsafe reruns.

## Verification Baseline

Apply what is relevant:

```text
YAML/parser validation
actionlint
workflow/action-specific static checks
GitHub Actions security analysis when available
custom-action tests
shell/static checks
permission audit
trigger/trust-boundary audit
full-SHA provenance audit
representative Actions run
failure/rerun/cancellation tests
artifact/release/deployment postcondition verification
```

A local runner/emulator is useful for limited step logic but is not proof of GitHub token, secret, event, cache, environment, or runner semantics.

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
