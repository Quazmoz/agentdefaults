# AgentDefaults Index

## Purpose

Provide a stable human-readable navigation layer for AgentDefaults without duplicating the complete machine-readable inventory.

Use:

- [`README.md`](README.md) for the project overview.
- [`docs/user-guide.md`](docs/user-guide.md) for guided stack selection.
- [`agentdefaults.manifest.json`](agentdefaults.manifest.json) for the authoritative featured-stack registry.
- [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) for structural and stack-integrity validation.

## Quick Selection

| Need | Start With |
|---|---|
| Design, build, or audit another AI agent | [`agents/agent-architect-builder.md`](agents/agent-architect-builder.md) |
| Select or challenge an automation platform architecture | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |
| Use AgentDefaults in a repository-aware agent | [`AGENTS.md`](AGENTS.md) |
| Use Claude or Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| Use Gemini or Gemini CLI | [`GEMINI.md`](GEMINI.md) |
| Use GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) |
| Use a local coding CLI | [`docs/quickstarts/cli.md`](docs/quickstarts/cli.md) |
| Use Cursor or Windsurf | [`docs/quickstarts/editor.md`](docs/quickstarts/editor.md) |
| Research app markets | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) |
| Validate an app idea from community history | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) |
| Optimize Google Play growth | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) |
| Edit video through Palmier Pro MCP | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| Build or fix a Wear OS app | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) |
| Prepare a Wear OS Play release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| Plan US-to-Europe travel | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |
| Reduce token usage | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| Add a reusable default | [`docs/patterns/default.md`](docs/patterns/default.md) |
| Validate the repository | [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) |

## Domain Sub-Indexes

| Domain | Path |
|---|---|
| Automation Platform Architecture | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |
| Wear OS Development | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) |
| Wear OS Release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| US-Europe Travel | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |

## Featured Stack Registry

The authoritative stack composition is in [`agentdefaults.manifest.json`](agentdefaults.manifest.json).

Current featured stacks:

- Automation Platform Architecture and Selection
- Google Play Growth Optimization
- Palmier Pro MCP Video Editing
- App Market Browser Research
- Community App Idea Validation
- Token Economy
- Wear OS Development
- Wear OS Play Store Release
- US-Europe Travel Prep

## Reusable Agent Construction

Use this stack to design, build, review, or harden other AI agents without over-engineering them.

```text
agents/agent-architect-builder.md
skills/agent-design-and-build.md
.github/agents/agent-architect-builder.agent.md
```

Core invariants:

- Define the observable outcome before persona or tone.
- Inventory real runtime capabilities before writing tool instructions.
- Prefer one agent plus selectively loaded skills over unnecessary multi-agent systems.
- Use least privilege and explicit side-effect classes.
- Treat retrieved content as data rather than instruction authority.
- Define tool preconditions, retries, idempotency, fallbacks, and postcondition checks.
- Separate stable rules, skills, task context, retrieved context, durable memory, and scratch state.
- Define observable completion and stop conditions.
- Include failure, partial-success, duplicate-delivery, resume, rollback, and escalation semantics where relevant.
- Require acceptance tests that cover adversarial and unavailable-tool cases.

## Automation Platform Architecture and Selection

### Entrypoints

```text
AUTOMATION_PLATFORM_INDEX.md
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
```

### Core Skills

```text
skills/automation-platform-capability-taxonomy.md
skills/automation-platform-decision-framework.md
skills/automation-platform-candidate-discovery.md
skills/automation-platform-evidence-and-confidence.md
skills/automation-platform-migration-and-economics.md
skills/automation-platform-composition-and-boundaries.md
```

### Product-Fit Skills

```text
skills/terraform-workload-fit-analysis.md
skills/ansible-workload-fit-analysis.md
skills/jenkins-workload-fit-analysis.md
skills/infrastructure-as-code-platform-alternatives-analysis.md
skills/configuration-management-platform-alternatives-analysis.md
skills/ci-cd-platform-alternatives-analysis.md
skills/gitops-runbook-and-workflow-platform-analysis.md
```

### Prompts and Structured Inputs

```text
prompts/planning/select-automation-platform.md
prompts/review/challenge-automation-platform-choice.md
schemas/automation-platform-decision-brief.schema.json
examples/automation-platform-decision-brief.yaml
docs/automation-platform-selection-acceptance-tests.md
.github/agents/automation-platform-selection-advisor.agent.md
```

### Output Depths

```text
quick_triage
standard
full_architecture_review
```

### Selection Invariants

- Validate contradictory constraints before analysis.
- Decompose and classify before selecting products.
- Use canonical capability identifiers.
- Assign one authoritative owner per automation unit.
- Apply mandatory gates before weighted scoring.
- Compare exact product editions and hosting models.
- Keep raw fit separate from evidence confidence.
- Do not score unknown evidence as zero.
- Treat immaterial score differences as ties.
- Compare retain, optimize, augment, migrate, and pilot-first against the do-nothing baseline.
- Include migration cost, dual running, recurring burden, reversibility, and exit strategy.
- Use a falsifiable proof-of-fit pilot with rollback and a stopping rule.

## Other Canonical Agents

| Agent | Path |
|---|---|
| Agent Architect and Builder | [`agents/agent-architect-builder.md`](agents/agent-architect-builder.md) |
| Palmier Pro MCP Video Editor | [`agents/palmierpro-mcp-video-editor-agent.md`](agents/palmierpro-mcp-video-editor-agent.md) |
| App Market Research Agent | [`agents/app-market-research-agent.md`](agents/app-market-research-agent.md) |
| Community App Idea Validation Agent | [`agents/community-app-idea-validation-agent.md`](agents/community-app-idea-validation-agent.md) |
| Google Play Growth Optimizer | [`agents/google-play-growth-optimizer-agent.md`](agents/google-play-growth-optimizer-agent.md) |
| Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) |
| Token Economy Orchestrator | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) |
| Terse Technical Coding Agent | [`agents/terse-technical-coding-agent.md`](agents/terse-technical-coding-agent.md) |
| Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) |
| SEO and AI Search Optimization Agent | [`agents/seo-ai-search-optimization-agent.md`](agents/seo-ai-search-optimization-agent.md) |
| Wear OS App Developer | [`agents/wearos-app-developer.md`](agents/wearos-app-developer.md) |
| Android Wear OS Release Engineer | [`agents/android-wearos-release-engineer.md`](agents/android-wearos-release-engineer.md) |
| US to Europe Travel Advisor | [`agents/us-europe-travel-advisor.md`](agents/us-europe-travel-advisor.md) |

## Schemas

| Schema | Path |
|---|---|
| Automation Platform Decision Brief | [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) |
| App Market Research Brief | [`schemas/app-market-research-brief.schema.json`](schemas/app-market-research-brief.schema.json) |
| Google Play Growth Brief | [`schemas/google-play-growth-brief.schema.json`](schemas/google-play-growth-brief.schema.json) |

## Patterns

| Pattern | Path |
|---|---|
| Default | [`docs/patterns/default.md`](docs/patterns/default.md) |
| Skill | [`docs/patterns/skill.md`](docs/patterns/skill.md) |
| Prompt | [`docs/patterns/prompt.md`](docs/patterns/prompt.md) |
| Benchmark | [`docs/patterns/benchmark.md`](docs/patterns/benchmark.md) |

## Maintenance Rules

1. Add canonical content under `agents/`, `skills/`, or `prompts/`.
2. Register complete featured stacks in [`agentdefaults.manifest.json`](agentdefaults.manifest.json).
3. Keep tool-native wrappers thin.
4. Add a quickstart, schema, example, acceptance tests, or sub-index only when it improves usability.
5. Update `README.md`, the relevant domain index, and this root navigation layer when discoverability changes.
6. Extend the validator only for domain-specific invariants; generic manifest references and schema parsing are automatic.
7. Run `python3 scripts/validate-agentdefaults.py`.

## Status

The manifest and filesystem are authoritative inventories. This index intentionally avoids manually maintained artifact counts and exhaustive duplicate listings.