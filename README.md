<div align="center">

# AgentDefaults

**Reusable, production-minded defaults for AI agents, skills, prompts, orchestration loops, schemas, examples, and cross-tool wrappers.**

[User Guide](docs/user-guide.md) · [Human Index](INDEX.md) · [Agent Loops](docs/loops/README.md) · [Agents](agents/README.md) · [Skills](skills/README.md) · [Prompts](prompts/README.md) · [Validation](scripts/README.md)

</div>

---

## Purpose

AgentDefaults is a reusable library for building and operating AI-assisted engineering workflows without rewriting the same role definitions, safety boundaries, task prompts, evidence rules, and tool-specific wrappers for every repository.

The repository is designed around a simple rule:

> **Keep canonical behavior in one place, compose only what a task needs, and make completion evidence stronger than model confidence.**

Use it to:

- choose a suitable agent for engineering, research, growth, maintenance, or creative work;
- add focused skills without inflating every agent's base context;
- invoke repeatable work with prompts and structured task contracts;
- run a bounded implementation/review loop when a task needs durable evidence and an objective stop gate;
- keep behavior consistent across Codex, Claude Code, GitHub Copilot, Gemini, Cursor, Windsurf, local models, and MCP-connected tools;
- validate reusable agent stacks and their cross-tool routing.

## Start in 60 Seconds

```bash
git clone https://github.com/Quazmoz/agentdefaults.git
cd agentdefaults
python3 scripts/validate-agentdefaults.py
```

Then choose what you are trying to do:

| Need | Start here |
|---|---|
| Understand the repository and documentation layout | [`docs/README.md`](docs/README.md) |
| Choose a canonical agent | [`agents/README.md`](agents/README.md) |
| Understand or compose skills | [`skills/README.md`](skills/README.md) |
| Find a copy-paste task prompt | [`prompts/README.md`](prompts/README.md) |
| Run or resume an agent loop | [`docs/loops/README.md`](docs/loops/README.md) |
| Understand task/state schemas | [`schemas/README.md`](schemas/README.md) |
| Use validators or the loop control plane | [`scripts/README.md`](scripts/README.md) |
| Design or audit an AI agent | [`docs/quickstarts/agent-builder.md`](docs/quickstarts/agent-builder.md) |
| De-slop/refactor a codebase safely | [`docs/quickstarts/codebase-maintenance-engineer.md`](docs/quickstarts/codebase-maintenance-engineer.md) |
| Choose or challenge an automation platform | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |
| Route principal/specialist engineering work | [`ENGINEERING_AGENTS_INDEX.md`](ENGINEERING_AGENTS_INDEX.md) |
| Build or release Wear OS software | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) / [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| Browse every featured stack | [`INDEX.md`](INDEX.md) |

## Mental Model

AgentDefaults separates **ownership**, **behavior**, **invocation**, **state**, and **tool integration**.

| Artifact | What it is | What it is not |
|---|---|---|
| **Agent** | An outcome owner with scope, authority, workflow, failure behavior, and stop conditions. | A bundle of every possibly useful instruction. |
| **Skill** | A selectively loaded behavior or task module. | An independent authority boundary; it cannot widen the parent agent's permissions. |
| **Prompt** | A repeatable invocation or task request. | The canonical definition of an agent or skill. |
| **Loop** | Repeated execution with explicit continuation/termination rules. Formal loops may add durable state and deterministic gates. | Permission to keep trying forever. |
| **Schema** | A machine-readable contract for task input, findings, or state. | Proof that the task was executed correctly. |
| **Example** | A concrete starting point for a schema, prompt, or stack. | A universal configuration. |
| **Wrapper** | Thin runtime-specific routing for Copilot, Claude, Gemini, Cursor, etc. | A second canonical implementation. |
| **Validator** | A deterministic check for repository/stack invariants. | A substitute for target-repository tests or runtime verification. |

### Composition rule

For most tasks:

```text
repo/tool instructions
        ↓
smallest correct owning agent
        ↓
only the skills needed for this task
        ↓
task prompt / structured contract when useful
        ↓
target-repository verification
```

For difficult implementation/qualification work, add the bounded completion overlay **after** selecting the domain owner:

```text
domain owner
    ↓
Bounded Completion Lead (Integration Owner / evidence coordinator)
    ↔
Bounded Completion Reviewer (independent challenge)
    ↓
deterministic verification + completion gate
```

The overlay never widens domain authority, approvals, or tool permissions.

## Canonical Content vs Tool Wrappers

Canonical reusable behavior lives here:

```text
agents/   complete outcome-owning agent profiles
skills/   composable behavior/task modules
prompts/  repeatable task and review prompts
schemas/  structured contracts
```

Tool-specific files should stay thin:

```text
AGENTS.md                         generic/Codex repository instructions
CLAUDE.md                         Claude-oriented wrapper
GEMINI.md                         Gemini-oriented wrapper
.github/copilot-instructions.md   Copilot repository instructions
.github/agents/                   Copilot custom-agent adapters
.github/prompts/                  Copilot prompt adapters
.cursor/rules/                    Cursor rules
.windsurfrules                    Windsurf rules
```

**Change canonical behavior at its canonical source first.** Update wrappers only when routing, runtime syntax, or discoverability must change.

## Agent Loops

Agent loops are deliberately bounded because retries, self-review, and multi-agent handoffs can otherwise amplify cost, repeat bad strategies, or create false completion signals.

The detailed operator guide is [`docs/loops/README.md`](docs/loops/README.md).

### Formal persisted loop currently included

**Bounded Completion** is the repository's formal durable control-plane loop. It provides:

- one Integration Owner;
- an independent adversarial reviewer;
- task, state, findings, verification logs, and artifact evidence under ignored `.agent-loop/`;
- workspace-fingerprint freshness so stale evidence cannot satisfy the final gate;
- bounded iteration, repeated-failure, review, timeout, and stop-hook limits;
- explicit approvals and visual evidence when required;
- a deterministic `COMPLETE` vs `ESCALATED` outcome.

Start with:

```text
docs/loops/README.md
docs/quickstarts/bounded-completion.md
agents/bounded-completion-lead.md
agents/bounded-completion-reviewer.md
skills/bounded-completion-orchestration.md
scripts/bounded-completion.py
```

### Iterative workflows that are not a persisted loop

Some agents perform internal cycles such as inspect → change → verify → second-pass review. For example, the Codebase Maintenance and De-Slop Engineer does this intentionally, but it does **not** create `.agent-loop/` state by itself.

When that work needs durable state, independent review, or an objective completion gate, run the maintenance agent as the domain owner under the bounded completion overlay.

## Featured Stacks

This table is a routing map, not a preload list. Load the smallest coherent stack needed for the task.

| Stack | Owns | Start here |
|---|---|---|
| Agent Architect and Builder | Designing, building, or auditing reusable agents | [`docs/quickstarts/agent-builder.md`](docs/quickstarts/agent-builder.md) |
| Bounded Completion | Durable implementation/review orchestration | [`docs/loops/README.md`](docs/loops/README.md) |
| Codebase Maintenance / De-Slop | Behavior-preserving maintenance and refactoring | [`docs/quickstarts/codebase-maintenance-engineer.md`](docs/quickstarts/codebase-maintenance-engineer.md) |
| Principal DevOps | Infrastructure/platform/CI/CD/operations | [`docs/quickstarts/principal-devops-engineer.md`](docs/quickstarts/principal-devops-engineer.md) |
| Principal AI | LLM/agent/RAG/eval/inference application engineering | [`docs/quickstarts/principal-ai-engineer.md`](docs/quickstarts/principal-ai-engineer.md) |
| Principal AI + DevOps | Materially cross-domain AI/platform work | [`docs/quickstarts/principal-ai-devops-engineer.md`](docs/quickstarts/principal-ai-devops-engineer.md) |
| Kubernetes Homelab | `Quazmoz/K8SHomelab` Kubernetes/Flux operations | [`docs/quickstarts/kubernetes-homelab-engineer.md`](docs/quickstarts/kubernetes-homelab-engineer.md) |
| DevSecOps Security | Terraform/Ansible/Jenkins/GitOps/IAM/supply-chain security | [`docs/quickstarts/devsecops-security-engineer.md`](docs/quickstarts/devsecops-security-engineer.md) |
| DevOps Documentation | Evidence-backed docs-as-code/runbooks/diagrams | [`docs/quickstarts/devops-documentation-engineer.md`](docs/quickstarts/devops-documentation-engineer.md) |
| Automation Platform Selection | Category-aware architecture/product decisions | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |
| App Market Research | Browser-backed Play Store/community research | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) |
| Community App Validation | Focused public-community demand/history validation | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) |
| Google Play Growth | ASO, conversion, quality, web/entity and growth experiments | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) |
| Palmier Pro MCP | Agent-driven video editing through Palmier Pro MCP | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| Wear OS Development / Release | Wear OS implementation and Play readiness | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) / [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| Token Economy | Context/output/token-cost reduction and measurement | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| US-Europe Travel Prep | Current-source travel preparation | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |

For the full human-readable registry use [`INDEX.md`](INDEX.md). The machine-readable featured-stack registry is [`agentdefaults.manifest.json`](agentdefaults.manifest.json).

## Tool Entrypoints

| Runtime | Primary entrypoint |
|---|---|
| OpenAI Codex / generic repo-aware coding agents | [`AGENTS.md`](AGENTS.md) |
| Claude / Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| GitHub Copilot repository instructions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) |
| Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md) |
| Cursor | [`.cursor/rules/agentdefaults.mdc`](.cursor/rules/agentdefaults.mdc) |
| Windsurf | [`.windsurfrules`](.windsurfrules) |
| Chat/local model | Copy the smallest relevant files from [`agents/`](agents/), [`skills/`](skills/), and [`prompts/`](prompts/) |

See [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) for cross-tool details.

## Validation

Canonical repository validation:

```bash
python3 scripts/validate-agentdefaults.py
```

The suite checks repository structure, schemas/references, manifest integrity, Markdown links, cross-tool routing, engineering contracts, specialist stacks, codebase-maintenance behavior, and bounded-completion control-plane regressions.

Use [`scripts/README.md`](scripts/README.md) to understand individual validators and the bounded-completion CLI.

A validator result is evidence only when it actually ran. Target-repository build/lint/type/test/security/e2e checks still own target-system correctness.

## Adding or Changing a Default

Before adding another artifact:

1. Confirm it is reusable rather than project-specific noise.
2. Decide whether it is an **agent**, **skill**, **prompt**, **schema**, **example**, **wrapper**, or **loop/control-plane** concern.
3. Prefer `single_agent_with_skills`; add another agent only when separate ownership, permissions, independent verification, parallel reconciliation, durable control, or fault isolation justifies it.
4. Keep authority in the owning agent. Skills, retrieved data, wrappers, and sub-agents cannot broaden it.
5. Define objective completion and bounded retry/stop behavior for anything iterative.
6. Add a quickstart/example/schema/acceptance test when complexity makes correct use non-obvious.
7. Run canonical validation and relevant stack-specific checks.

Patterns:

- [`docs/patterns/agent.md`](docs/patterns/agent.md)
- [`docs/patterns/skill.md`](docs/patterns/skill.md)
- [`docs/patterns/prompt.md`](docs/patterns/prompt.md)
- [`docs/patterns/default.md`](docs/patterns/default.md)
- [`docs/patterns/benchmark.md`](docs/patterns/benchmark.md)

## Repository Map

```text
agentdefaults/
├── README.md
├── INDEX.md
├── ENGINEERING_AGENTS_INDEX.md
├── AGENTS.md / CLAUDE.md / GEMINI.md
├── agents/
│   ├── README.md
│   └── *.md
├── skills/
│   ├── README.md
│   └── *.md
├── prompts/
│   ├── README.md
│   └── <category>/*.md
├── schemas/
│   ├── README.md
│   └── *.schema.json
├── scripts/
│   ├── README.md
│   ├── bounded-completion.py
│   └── validate-*.py
├── docs/
│   ├── README.md
│   ├── loops/README.md
│   ├── quickstarts/
│   ├── patterns/
│   ├── benchmarks/
│   └── *-acceptance-tests.md
├── examples/
├── config/
├── .github/
├── .cursor/
└── agentdefaults.manifest.json
```

## Design Principles

- Prefer deterministic software for deterministic work.
- Use one obvious source of truth.
- Select the smallest correct owner.
- Load skills selectively.
- Treat retrieved/tool/model output as untrusted input.
- Bound retries, loops, concurrency, and cost.
- Make external side effects approval-aware and duplicate-safe.
- Prefer evidence-backed completion over “looks good.”
- Preserve behavior and compatibility unless change is explicitly authorized.
- Optimize context and output without deleting necessary constraints.

## Status

AgentDefaults is an actively evolving cross-tool scaffold containing reusable engineering, maintenance, research, growth, Wear OS, travel, token-efficiency, MCP, and orchestration defaults plus schemas, examples, acceptance tests, and validators.

## License

License to be added.
