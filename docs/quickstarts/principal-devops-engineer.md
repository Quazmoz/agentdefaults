# Principal DevOps Engineer Quickstart

## Purpose

Provide the shortest path to using the scoped Principal DevOps Engineer for production infrastructure, automation, platform, reliability, incident, and release work.

## Canonical Stack

```text
agents/principal-devops-engineer.md
skills/production-devops-engineering.md
prompts/implementation/principal-devops-task.md
schemas/principal-devops-task.schema.json
examples/principal-devops-task.yaml
docs/principal-devops-engineer-acceptance-tests.md
.github/agents/principal-devops-engineer.agent.md
```

## Use It For

- Terraform/OpenTofu and provider-managed infrastructure
- Ansible/AAP and configuration automation
- CI/CD and artifact promotion
- GitOps
- containers and Kubernetes
- cloud, IAM, networking, certificates, and secrets flow
- observability/SRE
- incidents and recovery
- release engineering
- platform automation and operational tooling

## Do Not Use It For

Prompt engineering, RAG quality, model behavior, AI-agent reasoning, AI evaluations, or LLM application correctness. Use [`principal-ai-engineer.md`](principal-ai-engineer.md) for those. Use [`principal-ai-devops-engineer.md`](principal-ai-devops-engineer.md) when one task materially spans both scopes.

## Fast Start

Copy `prompts/implementation/principal-devops-task.md` and fill in target, mode, domain, goal, authority, invariants, and acceptance criteria.

For structured orchestration, validate input against `schemas/principal-devops-task.schema.json`.

## Operating Modes

```text
investigate
review
design
implement
incident
release
```

## Permission Model

```text
observe
propose
mutate_reversible
mutate_irreversible
```

The agent defaults to inspection/proposal unless mutation is explicitly requested. Irreversible or high-impact production actions require resolved targets, blast-radius analysis, duplicate-safety semantics, rollback/compensation where possible, and explicit approval.

## Expected Delivery

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

Never interpret an unexecuted check as passed.