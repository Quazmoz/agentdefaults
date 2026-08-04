# AgentDefaults Index

## Purpose

Provide fast lookup for agents, skills, prompts, wrappers, quickstarts, schemas, examples, validation, browser-research workflows, automation-platform architecture, MCP workflows, and benchmark artifacts.

Use [`README.md`](README.md) for the human-facing overview, [`docs/user-guide.md`](docs/user-guide.md) for guided selection, and [`agentdefaults.manifest.json`](agentdefaults.manifest.json) as the machine-readable stack registry.

## Quick Selection

| Need | Start With | Add / Use |
|---|---|---|
| Select or challenge an automation platform architecture | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) | Automation advisor, taxonomy, candidate discovery, fit-analysis skills, prompts, schema, and acceptance tests |
| New user onboarding | [`docs/user-guide.md`](docs/user-guide.md) | `README.md`, this index, selected stack quickstart |
| Generic repo-level agent instructions | [`AGENTS.md`](AGENTS.md) | Selected `agents/` and `skills/` files |
| Local repo-aware coding CLI | [`docs/quickstarts/cli.md`](docs/quickstarts/cli.md) | `AGENTS.md`, selected stack |
| Claude / Claude Code usage | [`docs/quickstarts/claude.md`](docs/quickstarts/claude.md) | `CLAUDE.md`, `AGENTS.md`, selected stack |
| Gemini / Gemini CLI usage | [`docs/quickstarts/gemini.md`](docs/quickstarts/gemini.md) | `GEMINI.md`, `AGENTS.md`, selected stack |
| Editor rule usage | [`docs/quickstarts/editor.md`](docs/quickstarts/editor.md) | Cursor and Windsurf wrappers |
| Repository assistant profiles | [`docs/quickstarts/repo-assistant.md`](docs/quickstarts/repo-assistant.md) | `.github/copilot-instructions.md`, `.github/agents/*.agent.md` |
| Palmier Pro MCP video editing | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) | Palmier agent, skills, prompts, and tool map |
| Browser-based app-market research | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) | App-market agent, browser skills, schema, and example |
| Validate an app idea using community history | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) | Community validation agent, forum skills, and prompt |
| Google Play growth / ASO optimization | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) | Growth agent, skills, schema, and example |
| Build or fix a Wear OS app | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) | Wear OS developer agent and screen-edge skill |
| Prepare a Wear OS app for Play release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) | Wear OS release agent and readiness skills |
| Plan a US-to-Europe trip | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) | Travel advisor, research skill, prompt, and example |
| Reduce GitHub Copilot token spend | [`skills/copilot-token-efficiency.md`](skills/copilot-token-efficiency.md) | Token budgeting and measurement skills |
| Manage agent context and output budgets | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) | Context pruning, output budgeting, and measurement |
| Add a reusable default | [`docs/patterns/default.md`](docs/patterns/default.md) | Skill, prompt, and benchmark patterns |
| Validate the repository | [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) | Run `python3 scripts/validate-agentdefaults.py` |

## Domain Sub-Indexes

| Domain | Path | Use |
|---|---|---|
| Automation Platform Architecture | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) | Classify capabilities and compare IaC, configuration management, CI/CD, GitOps, runbook, managed execution, and durable workflow products |
| Wear OS Development | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) | Build or repair Wear OS features |
| Wear OS Release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) | Final Play Store release readiness |
| US-Europe Travel | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) | Current, source-backed travel preparation |

## Tool Entrypoints

| Tool / Runner | Path | Use |
|---|---|---|
| Generic agents / Codex-style tools | [`AGENTS.md`](AGENTS.md) | Broad repository-level behavior |
| Claude / Claude Code | [`CLAUDE.md`](CLAUDE.md) | Claude-oriented wrapper |
| Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md) | Gemini-oriented wrapper |
| GitHub Copilot repository instructions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Repository-wide Copilot behavior |
| GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) | Selectable thin agent wrappers |
| Cursor | [`.cursor/rules/agentdefaults.mdc`](.cursor/rules/agentdefaults.mdc) | Cursor rule wrapper |
| Windsurf | [`.windsurfrules`](.windsurfrules) | Windsurf wrapper |
| Any chat or local model | [`examples/local-model.md`](examples/local-model.md) | Copy the smallest applicable agent and skill stack |

## Featured Stack Registry

The canonical machine-readable registry is [`agentdefaults.manifest.json`](agentdefaults.manifest.json). It currently registers:

- Automation Platform Architecture and Selection
- Google Play Growth Optimization
- Palmier Pro MCP Video Editing
- App Market Browser Research
- Community App Idea Validation
- Token Economy
- Wear OS Development
- Wear OS Play Store Release
- US-Europe Travel Prep

## Automation Platform Architecture and Selection

### Entrypoints

```text
AUTOMATION_PLATFORM_INDEX.md
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
```

### Core Skills

| Skill | Path | Use |
|---|---|---|
| Capability Taxonomy | [`skills/automation-platform-capability-taxonomy.md`](skills/automation-platform-capability-taxonomy.md) | Classify IaC, configuration management, CI/CD, GitOps, runbooks, managed execution, and durable workflows |
| Decision Framework | [`skills/automation-platform-decision-framework.md`](skills/automation-platform-decision-framework.md) | Decompose work, apply category hard-fit rules and mandatory gates, then score viable products |
| Candidate Discovery | [`skills/automation-platform-candidate-discovery.md`](skills/automation-platform-candidate-discovery.md) | Build a current, edition-aware, evidence-backed shortlist |
| Composition and Boundaries | [`skills/automation-platform-composition-and-boundaries.md`](skills/automation-platform-composition-and-boundaries.md) | Assign one owner per unit and define typed handoffs |
| Selection Orchestrator | [`skills/automation-platform-selection-orchestrator.md`](skills/automation-platform-selection-orchestrator.md) | Run the complete classification, comparison, migration, and pilot workflow |

### Incumbent Fit Skills

| Skill | Path | Use |
|---|---|---|
| Terraform Fit | [`skills/terraform-workload-fit-analysis.md`](skills/terraform-workload-fit-analysis.md) | Persistent provider-managed resource lifecycle |
| Ansible Fit | [`skills/ansible-workload-fit-analysis.md`](skills/ansible-workload-fit-analysis.md) | Target configuration, deployment, and day-two operations |
| Jenkins Fit | [`skills/jenkins-workload-fit-analysis.md`](skills/jenkins-workload-fit-analysis.md) | Triggered pipelines, builds, artifacts, approvals, and coordination |

### Alternative Analysis Skills

| Skill | Path | Candidate Coverage |
|---|---|---|
| IaC Alternatives | [`skills/infrastructure-as-code-platform-alternatives-analysis.md`](skills/infrastructure-as-code-platform-alternatives-analysis.md) | Terraform, OpenTofu, Pulumi, CloudFormation, Bicep, Crossplane, managed IaC execution |
| Configuration Management Alternatives | [`skills/configuration-management-platform-alternatives-analysis.md`](skills/configuration-management-platform-alternatives-analysis.md) | Ansible/AAP/AWX, Puppet, Chef Infra, Salt, PowerShell DSC |
| CI/CD Alternatives | [`skills/ci-cd-platform-alternatives-analysis.md`](skills/ci-cd-platform-alternatives-analysis.md) | Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, CircleCI, Buildkite, Tekton |
| GitOps, Runbook, and Workflow | [`skills/gitops-runbook-and-workflow-platform-analysis.md`](skills/gitops-runbook-and-workflow-platform-analysis.md) | Argo CD, Flux, Rundeck, AAP/AWX, Azure Automation, Temporal, Argo Workflows, Airflow |

### Prompts, Schema, Example, and Tests

| Artifact | Path | Use |
|---|---|---|
| Selection Prompt | [`prompts/planning/select-automation-platform.md`](prompts/planning/select-automation-platform.md) | Select a new architecture using a small current shortlist |
| Architecture Review Prompt | [`prompts/review/challenge-automation-platform-choice.md`](prompts/review/challenge-automation-platform-choice.md) | Challenge an existing implementation and migration case |
| Decision Brief Schema | [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) | Validate candidate policy, hosting, migration, governance, and requested outputs |
| Worked Example | [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Example with Terraform, AAP, Jenkins, GitHub, Azure, AWS, and alternatives |
| Acceptance Tests | [`docs/automation-platform-selection-acceptance-tests.md`](docs/automation-platform-selection-acceptance-tests.md) | Twenty behavioral and architecture scenarios |
| Copilot Wrapper | [`.github/agents/automation-platform-selection-advisor.agent.md`](.github/agents/automation-platform-selection-advisor.agent.md) | Thin selectable GitHub Copilot profile |

## Canonical Agents

| Agent | Path | Use |
|---|---|---|
| Automation Platform Selection Advisor | [`agents/automation-platform-selection-advisor.md`](agents/automation-platform-selection-advisor.md) | Category-aware product selection, architecture review, composition, migration, and pilot design |
| Palmier Pro MCP Video Editor | [`agents/palmierpro-mcp-video-editor-agent.md`](agents/palmierpro-mcp-video-editor-agent.md) | Video editing through Palmier Pro MCP |
| App Market Research Agent | [`agents/app-market-research-agent.md`](agents/app-market-research-agent.md) | Resumable public and authenticated app-market research |
| Community App Idea Validation Agent | [`agents/community-app-idea-validation-agent.md`](agents/community-app-idea-validation-agent.md) | Focused subreddit and community-history validation |
| Google Play Growth Optimizer | [`agents/google-play-growth-optimizer-agent.md`](agents/google-play-growth-optimizer-agent.md) | ASO, conversion, quality, SEO/AEO, and recommendation readiness |
| Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) | Kubernetes homelab and GitOps work |
| Token Economy Orchestrator | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) | Context, tool-result, and output token budgets |
| Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) | High-signal, low-token response behavior |
| Terse Technical Coding Agent | [`agents/terse-technical-coding-agent.md`](agents/terse-technical-coding-agent.md) | Senior-engineer coding workflows with focused diffs |
| Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) | Human-in-the-loop authenticated browser research |
| SEO and AI Search Optimization Agent | [`agents/seo-ai-search-optimization-agent.md`](agents/seo-ai-search-optimization-agent.md) | Search and AI-discovery visibility reviews |
| Wear OS App Developer | [`agents/wearos-app-developer.md`](agents/wearos-app-developer.md) | Wear OS application implementation and repair |
| Android Wear OS Release Engineer | [`agents/android-wearos-release-engineer.md`](agents/android-wearos-release-engineer.md) | Wear OS Play release readiness |
| US to Europe Travel Advisor | [`agents/us-europe-travel-advisor.md`](agents/us-europe-travel-advisor.md) | Research-first travel preparation |

## Other Canonical Skill Groups

### App Market Research

```text
skills/browser-research-foundations.md
skills/authenticated-browser-handoff.md
skills/play-store-autocomplete-research.md
skills/play-store-competitor-discovery.md
skills/play-store-listing-teardown.md
skills/forum-demand-mining.md
skills/play-console-search-term-analysis.md
skills/market-opportunity-clustering.md
skills/app-market-research-orchestrator.md
```

### Google Play Growth

```text
skills/google-play-growth-orchestrator.md
skills/google-play-aso-foundations.md
skills/google-play-keyword-and-metadata-optimization.md
skills/google-play-creative-conversion-optimization.md
skills/google-play-quality-and-retention-signals.md
skills/app-web-seo-and-entity-optimization.md
skills/ai-agent-recommendation-readiness.md
skills/app-growth-experimentation-and-measurement.md
```

### Token Economy

```text
skills/copilot-token-efficiency.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/prompt-and-memory-compression.md
skills/token-efficiency-measurement.md
```

### Wear OS and Travel

```text
skills/wearos-screen-edge-safety.md
skills/wearos-playstore-readiness.md
skills/us-europe-baggage-packing-research.md
```

### Palmier Pro MCP

```text
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
```

## Schemas

| Schema | Path | Use |
|---|---|---|
| Automation Platform Decision Brief | [`schemas/automation-platform-decision-brief.schema.json`](schemas/automation-platform-decision-brief.schema.json) | Platform candidate, hosting, lifecycle, migration, and governance inputs |
| App Market Research Brief | [`schemas/app-market-research-brief.schema.json`](schemas/app-market-research-brief.schema.json) | Markets, seeds, sources, and research outputs |
| Google Play Growth Brief | [`schemas/google-play-growth-brief.schema.json`](schemas/google-play-growth-brief.schema.json) | App, markets, objectives, sources, constraints, and growth outputs |

## Examples

| Example | Path | Use |
|---|---|---|
| Automation Platform Decision Brief | [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Category-aware product-selection input |
| App Market Research Brief | [`examples/app-market-research-brief.yaml`](examples/app-market-research-brief.yaml) | Browser-research input |
| Google Play Growth Brief | [`examples/google-play-growth-brief.yaml`](examples/google-play-growth-brief.yaml) | Play growth engagement input |
| Palmier Pro MCP Workflow | [`examples/palmierpro-mcp-workflow.md`](examples/palmierpro-mcp-workflow.md) | Video-editing workflow examples |
| GitHub Copilot Token Efficiency | [`examples/copilot-token-efficiency.md`](examples/copilot-token-efficiency.md) | Drop-in Copilot behavior and cost controls |
| Coding | [`examples/coding.md`](examples/coding.md) | Compact coding workflow |
| Benchmark | [`examples/benchmark.md`](examples/benchmark.md) | Token-efficiency benchmark recipe |
| Compression | [`examples/compression.md`](examples/compression.md) | Prompt, memory, or instruction compression |
| Handoff | [`examples/handoff.md`](examples/handoff.md) | Compact continuation handoff |
| Local Model | [`examples/local-model.md`](examples/local-model.md) | Chat or local-model use |
| Repository Profile | [`examples/repository-profile.md`](examples/repository-profile.md) | Thin repository profile wrapper |

## Patterns and Validation

| Artifact | Path | Use |
|---|---|---|
| Default Pattern | [`docs/patterns/default.md`](docs/patterns/default.md) | Generic reusable default structure |
| Skill Pattern | [`docs/patterns/skill.md`](docs/patterns/skill.md) | New skill structure |
| Prompt Pattern | [`docs/patterns/prompt.md`](docs/patterns/prompt.md) | New prompt structure |
| Benchmark Pattern | [`docs/patterns/benchmark.md`](docs/patterns/benchmark.md) | New benchmark structure |
| Repository Validator | [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) | Required files, Markdown purpose sections, all schemas, manifest integrity, automation stack integrity, and local links |

## Selection Rules

1. Choose the domain or tool entrypoint first.
2. Load one canonical agent or orchestrator.
3. Add only the skills required for the task.
4. Prefer narrow context over whole-repository ingestion.
5. Preserve exact paths, commands, schemas, safety rules, evidence dates, and validation status.
6. For automation-product selection, classify capability before comparing products and apply mandatory gates before scoring.
7. For MCP tools, treat live tool output as the source of truth over static documentation.
8. For browser research, treat visible source evidence and approved exports as the source of truth.
9. For token-efficiency claims, use the measurement skill or benchmark prompts.

## Maintenance Rules

When adding a new default:

1. Add canonical content under `agents/`, `skills/`, or `prompts/` when possible.
2. Register complete stacks in [`agentdefaults.manifest.json`](agentdefaults.manifest.json).
3. Add a wrapper only when a tool benefits from a native file location.
4. Keep wrappers thin and point them to canonical content.
5. Add a quickstart, example, schema, acceptance tests, or sub-index when it materially improves usability.
6. Update `README.md` and this index.
7. Extend the validator only for domain-specific integrity rules; generic manifest references and schema parsing are automatic.
8. Run `python3 scripts/validate-agentdefaults.py`.

## Status

The index intentionally avoids manually maintained artifact counts. The manifest and filesystem are the authoritative inventories, while this file remains the human-readable navigation layer.
