# Agents

## Purpose

Explain how canonical agent profiles under `agents/` are intended to be selected, composed, and operated without treating every profile as interchangeable or loading the entire directory into context.

An **agent owns an outcome**. Its profile should define scope, non-goals, authority, workflow, failure/recovery behavior, output expectations, and objective stop conditions. Skills may specialize how the agent works, but they do not become independent authorities.

For the full repository routing layer, also see [`../ENGINEERING_AGENTS_INDEX.md`](../ENGINEERING_AGENTS_INDEX.md) and [`../INDEX.md`](../INDEX.md).

## Selection Rule

Choose the **smallest correct owner** for the primary risk and outcome.

Do not select a broader agent merely because the task touches adjacent technology. Examples:

- Hosting an AI service on Kubernetes is usually DevOps-owned unless model/RAG/agent behavior also requires material change.
- Finding a security issue during maintenance does not make the maintenance agent the security owner.
- Producing infrastructure documentation does not authorize infrastructure mutation.
- Adding bounded completion does not replace the selected domain owner.

A useful routing sequence is:

```text
What outcome is required?
        ↓
What domain owns the main correctness/safety risk?
        ↓
Choose the narrowest agent that owns that domain
        ↓
Load only task-relevant skills
        ↓
Add bounded completion only if durable iterative review/gating is justified
```

## Principal Engineering Owners

Use these when the task is broad within a core engineering discipline.

| Agent | Owns | Use when | Quickstart |
|---|---|---|---|
| [`principal-devops-engineer.md`](principal-devops-engineer.md) | Infrastructure, platform, CI/CD, reliability, cloud, containers, IaC, automation operations | The primary change/risk is DevOps/platform behavior | [`../docs/quickstarts/principal-devops-engineer.md`](../docs/quickstarts/principal-devops-engineer.md) |
| [`principal-ai-engineer.md`](principal-ai-engineer.md) | LLM apps, agents, RAG, evals, inference, model/tool integration | The primary change/risk is AI-system behavior | [`../docs/quickstarts/principal-ai-engineer.md`](../docs/quickstarts/principal-ai-engineer.md) |
| [`principal-ai-devops-engineer.md`](principal-ai-devops-engineer.md) | Materially cross-domain AI + platform systems | Both AI application behavior and platform/deployment behavior require material engineering | [`../docs/quickstarts/principal-ai-devops-engineer.md`](../docs/quickstarts/principal-ai-devops-engineer.md) |

Prefer a specialist below when it owns the task more precisely.

## Engineering Specialists

| Agent | Owns | Use when | Operator guide |
|---|---|---|---|
| [`agent-architect-builder.md`](agent-architect-builder.md) | Reusable agent architecture, contracts, skills, tools, permissions, evaluation, stop behavior | Designing, building, or auditing another agent | [`../docs/quickstarts/agent-builder.md`](../docs/quickstarts/agent-builder.md) |
| [`codebase-maintenance-engineer.md`](codebase-maintenance-engineer.md) | Behavior-preserving de-slop, refactoring, comment reconciliation, dependency/config cleanup, maintenance efficiency | Code works but maintainability has drifted | [`../docs/quickstarts/codebase-maintenance-engineer.md`](../docs/quickstarts/codebase-maintenance-engineer.md) |
| [`devsecops-security-engineer.md`](devsecops-security-engineer.md) | Security of Terraform/OpenTofu, Ansible/AAP, Jenkins, CI/CD, GitOps, IAM, runners, secrets and supply chain | Security is the primary objective/risk | [`../docs/quickstarts/devsecops-security-engineer.md`](../docs/quickstarts/devsecops-security-engineer.md) |
| [`devops-documentation-engineer.md`](devops-documentation-engineer.md) | Evidence-backed documentation-as-code, runbooks, Markdown, Mermaid and diagrams | Documentation is the primary deliverable | [`../docs/quickstarts/devops-documentation-engineer.md`](../docs/quickstarts/devops-documentation-engineer.md) |
| [`kubernetes-homelab-engineer.md`](kubernetes-homelab-engineer.md) | `Quazmoz/K8SHomelab` Kubernetes/Flux GitOps, deployment, storage/networking and incidents | Work targets the K8SHomelab repository/runtime | [`../docs/quickstarts/kubernetes-homelab-engineer.md`](../docs/quickstarts/kubernetes-homelab-engineer.md) |
| [`automation-platform-selection-advisor.md`](automation-platform-selection-advisor.md) | Automation capability classification, product fit, architecture, evidence and migration economics | Choosing/challenging Terraform, Ansible, Jenkins, GitOps, workflow or adjacent platforms | [`../AUTOMATION_PLATFORM_INDEX.md`](../AUTOMATION_PLATFORM_INDEX.md) |
| [`wearos-app-developer.md`](wearos-app-developer.md) | Wear OS implementation and UI/runtime engineering | Building or fixing Wear OS functionality | [`../WEAROS_DEVELOPMENT_INDEX.md`](../WEAROS_DEVELOPMENT_INDEX.md) |
| [`android-wearos-release-engineer.md`](android-wearos-release-engineer.md) | Android/Wear OS release qualification and Play readiness | Final release-readiness work | [`../WEAROS_INDEX.md`](../WEAROS_INDEX.md) |

### Codebase maintenance vs domain engineering

The Codebase Maintenance agent is intentionally broad in what it may **inspect**, but narrow in what it owns. It should preserve product semantics and compatibility by default.

Use it for:

```text
stale comments/docs
duplicate helpers
dead residue
abstraction inflation
weak failure handling
test slop
dependency/config drift
generated-artifact drift
maintainability-oriented efficiency work
```

Hand off when the required fix becomes primarily:

```text
security architecture
production incident response
AI-system semantics
database/data migration ownership
platform architecture
new feature/product behavior
```

Its normal inspect → change → verify → second-pass cycle is an iterative workflow, not the repository's persisted `.agent-loop/` control plane. See [`../docs/loops/README.md`](../docs/loops/README.md).

## Bounded Completion Roles

These are **orchestration roles**, not normal domain owners.

| Agent | Role |
|---|---|
| [`bounded-completion-lead.md`](bounded-completion-lead.md) | Sole Integration Owner for the bounded loop, coordinating implementation, evidence, verification, findings, final diff review and deterministic gating. |
| [`bounded-completion-reviewer.md`](bounded-completion-reviewer.md) | Independent adversarial reviewer for plan challenge, diagnosis, findings, visual review where applicable and final completion challenge. |

Use them only after choosing the appropriate domain owner for the work.

The model is:

```text
selected domain owner
        ↓ behavior/authority
Bounded Completion Lead
        ↔ independent challenge
Bounded Completion Reviewer
        ↓
fresh verification + gate
```

The lead/reviewer overlay cannot add production access, mutation authority, approvals, or permissions that the selected owner/task does not already have.

Operator guide: [`../docs/loops/README.md`](../docs/loops/README.md)

Quickstart: [`../docs/quickstarts/bounded-completion.md`](../docs/quickstarts/bounded-completion.md)

## Research, Growth, Product and Creative Agents

| Agent | Owns | Start here |
|---|---|---|
| [`app-market-research-agent.md`](app-market-research-agent.md) | Browser-backed market, Play Store, forum and approved Play Console research | [`../docs/quickstarts/app-market-research.md`](../docs/quickstarts/app-market-research.md) |
| [`community-app-idea-validation-agent.md`](community-app-idea-validation-agent.md) | Focused community-history/demand validation for an app idea | [`../docs/quickstarts/community-app-validation.md`](../docs/quickstarts/community-app-validation.md) |
| [`comet-authenticated-research-agent.md`](comet-authenticated-research-agent.md) | Authenticated browser research using the Comet/local-bridge safety model | Canonical profile + related skills |
| [`google-play-growth-optimizer-agent.md`](google-play-growth-optimizer-agent.md) | Google Play discovery, conversion, quality, web/entity visibility and growth experiments | [`../docs/quickstarts/google-play-growth.md`](../docs/quickstarts/google-play-growth.md) |
| [`seo-ai-search-optimization-agent.md`](seo-ai-search-optimization-agent.md) | SEO, entity and AI-search discoverability work | Canonical profile |
| [`palmierpro-mcp-video-editor-agent.md`](palmierpro-mcp-video-editor-agent.md) | Palmier Pro MCP timeline/video-editing workflows | [`../docs/quickstarts/palmierpro-mcp.md`](../docs/quickstarts/palmierpro-mcp.md) |
| [`us-europe-travel-advisor.md`](us-europe-travel-advisor.md) | Current-source US-Europe travel preparation | [`../TRAVEL_INDEX.md`](../TRAVEL_INDEX.md) |

## Efficiency and Response-Control Agents

These profiles alter how work is orchestrated or communicated. They generally should not replace a domain owner when domain expertise is required.

| Agent | Use |
|---|---|
| [`token-economy-orchestrator.md`](token-economy-orchestrator.md) | Manage context/output/tool-result budgets and measurable token efficiency. |
| [`token-efficient-response-agent.md`](token-efficient-response-agent.md) | Produce compact responses without deleting required constraints/evidence. |
| [`terse-technical-coding-agent.md`](terse-technical-coding-agent.md) | Focused coding with compact status reporting. |

When correctness conflicts with token savings, correctness wins.

## How Skills Relate to Agents

A normal composition looks like:

```text
agents/principal-ai-engineer.md
+ skills/production-ai-engineering.md
+ one or more narrowly relevant task skills
```

or:

```text
agents/kubernetes-homelab-engineer.md
+ skills/kubernetes-gitops-change-management.md
+ skills/kubernetes-homelab-troubleshooting.md
```

Do not load every skill "just in case." Selective loading reduces conflicting instructions and context cost.

See [`../skills/README.md`](../skills/README.md).

## Canonical Profiles vs `.github/agents`

Files in this directory are canonical reusable profiles.

Files under [`../.github/agents/`](../.github/agents/) are GitHub Copilot adapters. They may contain runtime-specific frontmatter, delegation hints, or concise routing, but they should not fork canonical behavior.

If the two disagree:

1. inspect whether the wrapper contains a runtime-only requirement;
2. correct canonical behavior here when the behavior itself is wrong;
3. keep the wrapper thin and aligned.

## When an Agent Needs a Quickstart

Add or strengthen a quickstart when any of these are true:

- setup/runtime selection is non-obvious;
- more than one agent/skill must be composed;
- there is a structured schema/contract;
- external tools or authentication are involved;
- the workflow is iterative or stateful;
- approvals or destructive-action boundaries are easy to misuse;
- completion requires evidence beyond a normal task response.

Do not duplicate the full agent profile into the quickstart. The quickstart should explain **how to operate it**.

## Building a New Agent

Use:

```text
docs/quickstarts/agent-builder.md
agents/agent-architect-builder.md
skills/agent-design-and-build.md
docs/patterns/agent.md
```

At minimum define:

- observable objective;
- use and non-use conditions;
- inputs/preconditions;
- actual runtime/tool capabilities;
- authoritative data/state;
- permission class and approval gates;
- trust boundaries;
- retries, timeouts, idempotency and partial failure;
- context/memory policy;
- output contract;
- objective completion and stop conditions;
- adversarial/negative acceptance tests where material.

Default to `single_agent_with_skills`. Multi-agent architecture needs a concrete technical justification such as permission isolation, independent verification, specialist context separation, parallel work with reconciliation, separate durable control loops, or fault isolation.

## Validation

After changing canonical agents, run:

```bash
python3 scripts/validate-agentdefaults.py
```

Run the relevant specialist validator/acceptance tests as well. A passing AgentDefaults validator does not replace build/test/runtime verification in a target repository.
