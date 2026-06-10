# AgentDefaults

Reusable defaults for building AI agents, skills, prompts, and instruction packs.

AgentDefaults is intended to be a practical library of agent-building patterns: system instructions, reusable skill definitions, task prompts, workflow templates, evaluation checklists, and implementation notes that can be copied into agentic coding tools, custom assistants, internal automation agents, or AI-enabled developer workflows.

## Purpose

Modern AI agents are only as good as the defaults they start with. This repository exists to collect well-structured, reusable defaults that help agents behave more consistently, produce higher-quality work, and follow clear operating constraints.

Use this repository as a starting point when you need to:

- Bootstrap a new coding, DevOps, automation, research, or product agent.
- Reuse proven prompts instead of rewriting instructions from scratch.
- Maintain consistent agent behavior across tools and projects.
- Build skill packs for repeatable workflows.
- Document best practices for prompting, context management, and agent handoff.
- Create reusable instruction layers for IDE agents, chat agents, MCP-based workflows, and custom applications.

## What This Repository Will Contain

AgentDefaults is organized around four main building blocks.

### Agents

Agent definitions describe the role, operating model, boundaries, expected behaviors, and tool-use style for a complete assistant.

Examples:

- Full-stack software engineering agent
- Rust backend review agent
- DevOps automation agent
- Kubernetes homelab engineer agent
- Token-efficient response agent
- Comet authenticated research agent
- Android / Wear OS release agent
- Product strategy agent
- Documentation and README generation agent

### Skills

Skills are reusable task modules that can be composed into larger agents. A skill should be narrow, repeatable, and easy to evaluate.

Examples:

- Kubernetes GitOps change management
- Kubernetes homelab troubleshooting
- Token-efficient response compression
- Comet authenticated research
- Comet local bridge safety
- Code review
- Repository audit
- Release readiness review
- README generation
- GitHub issue triage
- Terraform review
- CI/CD pipeline review
- Prompt refinement
- Test plan generation

### Prompts

Prompts are task-specific instructions that can be pasted into an AI coding assistant, agent runner, or chat model to complete a defined job.

Examples:

- "Deep dive into this repository and identify production-readiness gaps."
- "Refactor this module without changing public behavior."
- "Create a robust implementation plan for this feature."
- "Generate Play Store release notes from the latest changes."

### Instructions

Instructions define durable behavior rules for agents. These may include tone, safety boundaries, coding standards, tool-use rules, formatting preferences, testing expectations, and review criteria.

Examples:

- Engineering quality standards
- Security review expectations
- Documentation style guide
- Agent handoff format
- Prompt writing conventions
- Repository cleanup rules

## Recommended Repository Structure

This repository is intentionally simple at the start. A suggested structure is:

```text
agentdefaults/
├── agents/
│   ├── kubernetes-homelab-engineer.md
│   ├── token-efficient-response-agent.md
│   ├── comet-authenticated-research-agent.md
│   ├── software-engineer.md
│   ├── devops-engineer.md
│   ├── rust-engineer.md
│   └── product-strategist.md
├── skills/
│   ├── kubernetes-gitops-change-management.md
│   ├── kubernetes-homelab-troubleshooting.md
│   ├── token-efficient-response-compression.md
│   ├── comet-authenticated-research.md
│   ├── comet-local-bridge-safety.md
│   ├── code-review.md
│   ├── repo-audit.md
│   ├── release-readiness.md
│   └── documentation.md
├── prompts/
│   ├── implementation/
│   ├── review/
│   ├── planning/
│   └── marketing/
├── instructions/
│   ├── engineering-standards.md
│   ├── security-standards.md
│   ├── documentation-style.md
│   └── agent-handoff.md
├── examples/
│   └── README.md
└── README.md
```

The structure may evolve as the repository grows.

## Available Defaults

| Type | Name | Path | Purpose |
|------|------|------|---------|
| Agent | Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) | Tailored agent for Quinn's `Quazmoz/K8SHomelab` repo, including Flux CD, HelmRelease, Kustomize, SOPS/Age, Calico, MetalLB, NGINX Ingress, WireGuard, observability, AI tooling, and MCP infrastructure. |
| Agent | Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) | Streamlines assistant behavior for high-signal, low-token responses while preserving correctness, safety, validation, and actionable output. |
| Agent | Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) | Uses a local Comet browser session for authenticated, automation-hostile, or browser-only research while keeping credentials and session secrets private. |
| Skill | Kubernetes GitOps Change Management | [`skills/kubernetes-gitops-change-management.md`](skills/kubernetes-gitops-change-management.md) | Adds, modifies, and reviews Kubernetes resources safely in Flux/Kustomize/HelmRelease repositories. |
| Skill | Kubernetes Homelab Troubleshooting | [`skills/kubernetes-homelab-troubleshooting.md`](skills/kubernetes-homelab-troubleshooting.md) | Diagnoses Flux, DNS, ingress, MetalLB, Calico, WireGuard, scheduling, storage, and node issues with low-blast-radius steps. |
| Skill | Token-Efficient Response Compression | [`skills/token-efficient-response-compression.md`](skills/token-efficient-response-compression.md) | Compresses verbose findings, tool results, and implementation details into concise, safe, actionable responses. |
| Skill | Comet Authenticated Research | [`skills/comet-authenticated-research.md`](skills/comet-authenticated-research.md) | Runs safe human-in-the-loop authenticated research through Comet while avoiding credential/session exposure. |
| Skill | Comet Local Bridge Safety | [`skills/comet-local-bridge-safety.md`](skills/comet-local-bridge-safety.md) | Designs and reviews safe local Comet bridge command surfaces, confirmations, and threat controls. |

## Suggested File Format

Each reusable agent, skill, prompt, or instruction should be written in Markdown and should be easy to copy into another tool.

A good template is:

```markdown
# Name

## Purpose

What this default is for.

## When To Use

The situations where this default is useful.

## Instructions

The actual reusable instruction text.

## Inputs Needed

Any context the user or calling system should provide.

## Expected Output

The response shape or deliverable the agent should produce.

## Quality Bar

How to evaluate whether the result is good.

## Notes

Known limitations, edge cases, or customization tips.
```

## Design Principles

The defaults in this repository should be:

- **Practical** — written for real workflows, not abstract demos.
- **Composable** — easy to combine into larger agent systems.
- **Specific** — clear enough to produce repeatable output.
- **Tool-aware** — explicit about when an agent should inspect files, search docs, run tests, or make changes.
- **Reviewable** — structured so humans can quickly audit the behavior being requested.
- **Safe by default** — conservative around destructive operations, secrets, credentials, production systems, and user data.
- **Outcome-focused** — optimized for useful deliverables rather than verbose reasoning.

## Usage

Copy the relevant agent, skill, prompt, or instruction into your agent configuration, IDE assistant, custom system prompt, or workflow runner.

For example:

```text
Use the Software Engineering Agent as the base role.
Add the Code Review skill.
Add the Repository Audit skill.
Apply the Engineering Standards instruction pack.
Provide the target repository, branch, and requested scope.
```

Then customize only the project-specific context instead of rewriting the full prompt stack.

## Example Agent Stack

```text
Base agent:
  agents/software-engineer.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/token-efficient-response-compression.md
  skills/code-review.md
  skills/repo-audit.md
  skills/test-plan-generation.md

Instructions:
  instructions/engineering-standards.md
  instructions/security-standards.md
  instructions/agent-handoff.md

Task prompt:
  prompts/review/deep-repository-review.md
```

For the Kubernetes homelab repo, start with:

```text
Base agent:
  agents/kubernetes-homelab-engineer.md

Optional behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/kubernetes-gitops-change-management.md
  skills/kubernetes-homelab-troubleshooting.md
  skills/token-efficient-response-compression.md

Target repo:
  Quazmoz/K8SHomelab

Expected workflow:
  Inspect AGENT_CONTEXT.md, README.md, apps/base/, clusters/my-homelab/, and relevant docs before proposing or making changes.
```

For authenticated or automation-hostile web research, start with:

```text
Base agent:
  agents/comet-authenticated-research-agent.md

Optional behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/comet-authenticated-research.md
  skills/comet-local-bridge-safety.md
  skills/token-efficient-response-compression.md

Expected workflow:
  Use Comet running on the user's machine for authenticated pages, human-in-the-loop login, MFA/SSO completion, and browser-only research that normal automation cannot handle safely.
```

## Best Practices

When adding new defaults:

1. Prefer clear instructions over clever wording.
2. State the expected output format.
3. Define the agent's scope and non-goals.
4. Include quality checks the agent should perform before finishing.
5. Avoid embedding secrets, private URLs, credentials, or environment-specific values.
6. Keep prompts modular so they can be reused across projects.
7. Update examples when adding a new pattern that others should follow.

## Initial Roadmap

Planned additions:

- Base software engineering agent profile
- DevOps / infrastructure agent profile
- Rust engineering agent profile
- Android / Wear OS agent profile
- Repository audit prompt pack
- Code review skill pack
- Documentation generation skill pack
- Release readiness checklist
- Prompt engineering conventions
- Agent handoff templates
- Example composed agent stacks

## Status

Early scaffold. The README defines the initial direction and structure for the repository. Content packs will be added over time.

## Contributing

Contributions should keep the repository practical, reusable, and easy to copy into real agent workflows.

Before adding a new default, ask:

- Is this reusable across more than one project?
- Is the expected output clear?
- Does it define enough context for an agent to perform well?
- Are safety boundaries and destructive-action limits explicit?
- Can another engineer quickly adapt it?

## License

License to be added.
