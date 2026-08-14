# Principal AI Engineer Quickstart

## Purpose

Provide the shortest path to using the scoped Principal AI Engineer for production LLM applications, agents, MCP, RAG, inference, prompts/context, evaluations, AI security, and AI observability.

## Canonical Stack

```text
agents/principal-ai-engineer.md
skills/production-ai-engineering.md
prompts/implementation/principal-ai-engineer-task.md
schemas/principal-ai-engineer-task.schema.json
examples/principal-ai-engineer-task.yaml
docs/principal-ai-engineer-acceptance-tests.md
.github/agents/principal-ai-engineer.agent.md
```

## Use It For

- LLM application architecture and debugging
- AI agents and tool orchestration
- MCP integrations and security
- RAG and knowledge systems
- prompt/context engineering
- structured outputs and validation
- evaluation harnesses and regression datasets
- inference/model/provider integration
- AI observability, latency, tokens, and cost
- prompt/model/retrieval release qualification
- AI-specific threat modeling and adversarial testing

## Do Not Use It For

Generic IaC, Ansible/AAP, CI/CD, GitOps, Kubernetes, cloud/IAM/networking, or SRE architecture. Use [`principal-devops-engineer.md`](principal-devops-engineer.md) for those. Use [`principal-ai-devops-engineer.md`](principal-ai-devops-engineer.md) when one task materially spans both scopes.

## Fast Start

Copy `prompts/implementation/principal-ai-engineer-task.md` and fill in target, mode, domain, goal, authority, invariants, eval requirements, and acceptance criteria.

For structured orchestration, validate input against `schemas/principal-ai-engineer-task.schema.json`.

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

The agent defaults to inspection/proposal unless mutation is explicitly requested. Consequential tools, production model/prompt/index rollout, destructive data changes, external sends, access-control changes, and autonomous spending require explicit authority and applicable approval gates.

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

AI quality is not established by a demo. Required tests/evals must actually run.