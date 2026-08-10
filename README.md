<div align="center">

# AgentDefaults

**Reusable defaults for AI agents, skills, prompts, wrappers, browser research, examples, and benchmarkable token-efficiency workflows.**

![Markdown](https://img.shields.io/badge/content-Markdown-blue)
![Agent UX](https://img.shields.io/badge/focus-agent%20UX-purple)
![Token Efficiency](https://img.shields.io/badge/token%20efficiency-self--tested%20(estimated)-informational)
![Self Hosted Friendly](https://img.shields.io/badge/local%20models-friendly-orange)
![MCP Ready](https://img.shields.io/badge/MCP-video%20editing-cyan)

[Start with the User Guide](docs/user-guide.md) · [Browse the Index](INDEX.md) · [Run Validation](scripts/validate-agentdefaults.py) · [View Benchmarks](docs/benchmarks/token-efficiency-fresh-2026-06-25.md)

</div>

---

## Why This Exists

Modern AI engineering work needs reusable defaults: agent roles, behavior skills, task prompts, tool-specific instruction wrappers, validation checks, and benchmark artifacts.

AgentDefaults helps you:

- Bootstrap coding, DevOps, automation, research, product, documentation, or creative-production agents.
- Keep behavior consistent across repo-aware coding tools, chat models, local models, IDE assistants, and MCP-connected apps.
- Reduce input/context/output token waste without sacrificing correctness or validation.
- Benchmark concise-agent behavior instead of assuming shorter prompts are better.
- Reuse proven instruction stacks instead of rewriting the same agent setup every time.

## Start In 60 Seconds

```bash
git clone https://github.com/Quazmoz/agentdefaults.git
cd agentdefaults
python3 scripts/validate-agentdefaults.py
```

Then choose a path:

| I want to... | Start here |
|---|---|
| Pick the right files quickly | [`docs/user-guide.md`](docs/user-guide.md) |
| Design, build, or audit another AI agent | [`docs/quickstarts/agent-builder.md`](docs/quickstarts/agent-builder.md) |
| Select or challenge an automation platform architecture | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |
| Use a local repo-aware coding CLI | [`docs/quickstarts/cli.md`](docs/quickstarts/cli.md) |
| Use Claude-style repo instructions | [`docs/quickstarts/claude.md`](docs/quickstarts/claude.md) |
| Use Gemini-style repo instructions | [`docs/quickstarts/gemini.md`](docs/quickstarts/gemini.md) |
| Use editor rule files | [`docs/quickstarts/editor.md`](docs/quickstarts/editor.md) |
| Use repository assistant profile wrappers | [`docs/quickstarts/repo-assistant.md`](docs/quickstarts/repo-assistant.md) |
| Use Palmier Pro through MCP | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| Research Google Play, Wear OS, forums, and Play Console | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) |
| Validate an app idea using subreddit or community history | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) |
| Optimize Google Play growth / ASO | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) |
| Build or release a Wear OS app | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) |
| Plan a US-to-Europe trip | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |
| Add a reusable agent | [`docs/patterns/agent.md`](docs/patterns/agent.md) |
| Add another reusable default | [`docs/patterns/default.md`](docs/patterns/default.md) |
| Copy a ready-made example | [`examples/`](examples/) |

## The Core Model

AgentDefaults separates **canonical reusable content** from **thin tool wrappers**.

| Layer | Folder / File | Purpose |
|---|---|---|
| Entrypoints | [`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), [`GEMINI.md`](GEMINI.md) | Broad repo-level instructions for supported tools. |
| Tool wrappers | [`.github/copilot-instructions.md`](.github/copilot-instructions.md), [`.github/agents/`](.github/agents/) | Tool-native profiles that point back to canonical files. |
| Editor rules | [`.cursor/rules/agentdefaults.mdc`](.cursor/rules/agentdefaults.mdc), [`.windsurfrules`](.windsurfrules) | Thin editor integration files. |
| Agents | [`agents/`](agents/) | Full reusable agent profiles. |
| Skills | [`skills/`](skills/) | Composable behavior and task modules. |
| Prompts | [`prompts/`](prompts/) | Copy-paste benchmark and task prompts. |
| Schemas | [`schemas/`](schemas/) | Machine-readable contracts for structured workflows. |
| Docs | [`docs/`](docs/) | Quickstarts, integration guides, patterns, tool maps, and benchmarks. |
| Examples | [`examples/`](examples/) | Practical copy-paste recipes. |
| Manifest | [`agentdefaults.manifest.json`](agentdefaults.manifest.json) | Machine-readable repo summary. |

Rule: **update canonical content first, then keep wrappers thin and discoverable.**

## Recommended Stacks

### Agent Architect and Builder Stack

Use when turning a goal, prompt, or existing agent into a reusable production-quality agent with explicit scope, verified runtime capabilities, least-privilege tools, trust boundaries, modular skills, context strategy, recovery semantics, objective completion, stop conditions, and adversarial acceptance tests.

```text
docs/quickstarts/agent-builder.md
agents/agent-architect-builder.md
skills/agent-design-and-build.md
schemas/agent-build-brief.schema.json
examples/agent-build-brief.yaml
prompts/planning/build-ai-agent.md
docs/agent-builder-acceptance-tests.md
docs/patterns/agent.md
.github/agents/agent-architect-builder.agent.md
```

The stack defaults to one agent plus selectively loaded skills. It introduces multiple agents only when permission isolation, independent specialist context, parallel execution with reconciliation, independent verification, separate durable control loops, or fault isolation provides a concrete benefit. A skill, retrieved document, tool output, or sub-agent cannot broaden the parent agent's authority.

### Automation Platform Architecture and Selection Stack

Use when deciding which automation capability and product should own a workload, reviewing an existing architecture, or comparing an incumbent Terraform, Ansible, and Jenkins stack with alternatives.

The stack classifies work before comparing products across:

```text
infrastructure as code
configuration management
CI/CD
GitOps continuous delivery
runbook automation
managed IaC execution
durable workflow orchestration
```

It can recommend or compare products such as Terraform, OpenTofu, Pulumi, Ansible, Puppet, Chef Infra, Jenkins, GitHub Actions, Azure Pipelines, GitLab CI/CD, Argo CD, Flux, Rundeck, Temporal, and other justified candidates. It applies mandatory hosting, target, network, identity, governance, licensing, and support gates before scoring.

```text
AUTOMATION_PLATFORM_INDEX.md
docs/quickstarts/automation-platform-selection.md
agents/automation-platform-selection-advisor.md
skills/automation-platform-capability-taxonomy.md
skills/automation-platform-decision-framework.md
skills/automation-platform-candidate-discovery.md
skills/infrastructure-as-code-platform-alternatives-analysis.md
skills/configuration-management-platform-alternatives-analysis.md
skills/ci-cd-platform-alternatives-analysis.md
skills/gitops-runbook-and-workflow-platform-analysis.md
skills/automation-platform-composition-and-boundaries.md
skills/automation-platform-selection-orchestrator.md
prompts/planning/select-automation-platform.md
prompts/review/challenge-automation-platform-choice.md
schemas/automation-platform-decision-brief.schema.json
examples/automation-platform-decision-brief.yaml
```

### Palmier Pro MCP Video Editing Stack

Use when you want an agent to operate Palmier Pro through MCP for timeline edits, story assembly, YouTube Shorts, transcript cleanup, captions, b-roll, generation approval workflows, and exports.

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
prompts/palmierpro/story-assembly-from-project-media.md
prompts/palmierpro/youtube-short-from-long-form.md
prompts/palmierpro/full-edit-pass.md
examples/palmierpro-mcp-workflow.md
```

### App Market Browser Research Stack

Use when you want a browser-capable agent to research Google Play autocomplete, competitors, listings, Reddit, XDA, public forums, and approved Play Console data with resumable checkpoints and secure human authentication.

```text
docs/quickstarts/app-market-research.md
agents/app-market-research-agent.md
skills/browser-research-foundations.md
skills/authenticated-browser-handoff.md
skills/play-store-autocomplete-research.md
skills/play-store-competitor-discovery.md
skills/play-store-listing-teardown.md
skills/forum-demand-mining.md
skills/play-console-search-term-analysis.md
skills/market-opportunity-clustering.md
skills/app-market-research-orchestrator.md
schemas/app-market-research-brief.schema.json
examples/app-market-research-brief.yaml
```

### Community App Idea Validation Stack

Use when the core question is whether one app idea has appeared before in a subreddit or public community, which solutions were recommended, what remains unresolved, and whether a new validation post would add useful evidence.

```text
docs/quickstarts/community-app-validation.md
agents/community-app-idea-validation-agent.md
skills/browser-research-foundations.md
skills/forum-demand-mining.md
skills/subreddit-app-idea-validation.md
prompts/research/validate-app-idea-in-community.md
.github/agents/community-app-idea-validator.agent.md
```

The stack searches exact concepts, problem-first language, workarounds, dissatisfaction, competitor launches, and comments. It separates community demand from medical, scientific, legal, financial, or regulatory validity in sensitive domains.

### Google Play Growth Stack

Use when you want to improve Google Play discovery, listing conversion, app quality, web/AEO visibility, and AI-recommendation readiness for an Android or Wear OS app.

```text
docs/quickstarts/google-play-growth.md
agents/google-play-growth-optimizer-agent.md
skills/google-play-growth-orchestrator.md
skills/google-play-aso-foundations.md
skills/google-play-keyword-and-metadata-optimization.md
skills/google-play-creative-conversion-optimization.md
skills/google-play-quality-and-retention-signals.md
skills/app-web-seo-and-entity-optimization.md
skills/ai-agent-recommendation-readiness.md
skills/app-growth-experimentation-and-measurement.md
schemas/google-play-growth-brief.schema.json
examples/google-play-growth-brief.yaml
```

### Wear OS Stacks

Use the development stack while building or fixing features, and the release stack for final Play Store readiness. See [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) and [`WEAROS_INDEX.md`](WEAROS_INDEX.md).

```text
# Development
agents/wearos-app-developer.md
skills/wearos-screen-edge-safety.md
prompts/implementation/wearos-app-development.md

# Release readiness
agents/android-wearos-release-engineer.md
skills/wearos-playstore-readiness.md
prompts/review/wearos-release-readiness-review.md
```

### US-Europe Travel Prep Stack

Use when preparing for a trip from the US to one or more European countries, with current, source-backed baggage, customs, entry, money, and outlet guidance. See [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md).

```text
agents/us-europe-travel-advisor.md
skills/us-europe-baggage-packing-research.md
prompts/planning/us-europe-trip-prep.md
examples/stacks/us-europe-travel-prep.md
```

### GitHub Copilot Cost-Reduction Stack

Use when a team wants to lower GitHub Copilot spend (usage-based AI Credits) without losing quality.

```text
.github/copilot-instructions.md   (drop-in from examples/copilot-token-efficiency.md)
skills/copilot-token-efficiency.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficiency-measurement.md
```

### Token Economy Stack

Use when you want smaller outputs, narrower context, and measurable savings.

```text
AGENTS.md
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

### Terse Coding Stack

Use when you want focused implementation work with compact status reporting.

```text
AGENTS.md
agents/terse-technical-coding-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Benchmark Stack

Use when you want to measure baseline vs candidate behavior.

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
docs/benchmarks/token-efficiency-smoke-test.md
docs/benchmarks/token-efficiency-fresh-2026-06-25.md
```

## Tool Compatibility

| Tool / Runner | Primary file(s) | Notes |
|---|---|---|
| Generic repo-aware agents | [`AGENTS.md`](AGENTS.md) | Base instruction file for broad compatibility. |
| Claude / Claude Code | [`CLAUDE.md`](CLAUDE.md) | Claude-oriented wrapper, delegates shared rules to `AGENTS.md`. |
| Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md) | Gemini-oriented wrapper, delegates shared behavior to `AGENTS.md`. |
| GitHub Copilot repo instructions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Repo-wide behavior and maintenance rules. |
| GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) | Selectable profile wrappers. |
| Cursor | [`.cursor/rules/agentdefaults.mdc`](.cursor/rules/agentdefaults.mdc) | Thin rule wrapper pointing back to canonical files. |
| Windsurf | [`.windsurfrules`](.windsurfrules) | Thin wrapper pointing back to canonical files. |
| MCP-connected apps | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) | Palmier Pro video-editing workflow over local MCP. |
| Browser-capable agents | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md), [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) | Broad market research or focused community-history validation. |
| Any chat/local model | [`agents/`](agents/), [`skills/`](skills/), [`prompts/`](prompts/) | Copy-paste the smallest useful stack. |

## Available Defaults

| Type | Name | Path |
|---|---|---|
| Agent | Agent Architect and Builder | [`agents/agent-architect-builder.md`](agents/agent-architect-builder.md) |
| Agent | Automation Platform Selection Advisor | [`agents/automation-platform-selection-advisor.md`](agents/automation-platform-selection-advisor.md) |
| Agent | Palmier Pro MCP Video Editor | [`agents/palmierpro-mcp-video-editor-agent.md`](agents/palmierpro-mcp-video-editor-agent.md) |
| Agent | App Market Research Agent | [`agents/app-market-research-agent.md`](agents/app-market-research-agent.md) |
| Agent | Community App Idea Validation Agent | [`agents/community-app-idea-validation-agent.md`](agents/community-app-idea-validation-agent.md) |
| Agent | Token Economy Orchestrator | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| Agent | Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) |
| Agent | Terse Technical Coding Agent | [`agents/terse-technical-coding-agent.md`](agents/terse-technical-coding-agent.md) |
| Agent | Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) |
| Agent | Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) |
| Agent | SEO and AI Search Optimization Agent | [`agents/seo-ai-search-optimization-agent.md`](agents/seo-ai-search-optimization-agent.md) |
| Agent | Google Play Growth Optimizer | [`agents/google-play-growth-optimizer-agent.md`](agents/google-play-growth-optimizer-agent.md) |
| Agent | Wear OS App Developer | [`agents/wearos-app-developer.md`](agents/wearos-app-developer.md) |
| Agent | Android Wear OS Release Engineer | [`agents/android-wearos-release-engineer.md`](agents/android-wearos-release-engineer.md) |
| Agent | US to Europe Travel Advisor | [`agents/us-europe-travel-advisor.md`](agents/us-europe-travel-advisor.md) |
| Skill | Agent Design and Build | [`skills/agent-design-and-build.md`](skills/agent-design-and-build.md) |
| Skill | Automation Platform Capability Taxonomy | [`skills/automation-platform-capability-taxonomy.md`](skills/automation-platform-capability-taxonomy.md) |
| Skill | Automation Platform Candidate Discovery | [`skills/automation-platform-candidate-discovery.md`](skills/automation-platform-candidate-discovery.md) |
| Skill | CI/CD Platform Alternatives Analysis | [`skills/ci-cd-platform-alternatives-analysis.md`](skills/ci-cd-platform-alternatives-analysis.md) |
| Skill | IaC Platform Alternatives Analysis | [`skills/infrastructure-as-code-platform-alternatives-analysis.md`](skills/infrastructure-as-code-platform-alternatives-analysis.md) |
| Skill | Configuration Management Alternatives Analysis | [`skills/configuration-management-platform-alternatives-analysis.md`](skills/configuration-management-platform-alternatives-analysis.md) |
| Skill | GitOps, Runbook, and Workflow Platform Analysis | [`skills/gitops-runbook-and-workflow-platform-analysis.md`](skills/gitops-runbook-and-workflow-platform-analysis.md) |
| Skill | Browser Research Foundations | [`skills/browser-research-foundations.md`](skills/browser-research-foundations.md) |
| Skill | Authenticated Browser Handoff | [`skills/authenticated-browser-handoff.md`](skills/authenticated-browser-handoff.md) |
| Skill | Play Store Autocomplete Research | [`skills/play-store-autocomplete-research.md`](skills/play-store-autocomplete-research.md) |
| Skill | Play Store Competitor Discovery | [`skills/play-store-competitor-discovery.md`](skills/play-store-competitor-discovery.md) |
| Skill | Play Store Listing Teardown | [`skills/play-store-listing-teardown.md`](skills/play-store-listing-teardown.md) |
| Skill | Forum Demand Mining | [`skills/forum-demand-mining.md`](skills/forum-demand-mining.md) |
| Skill | Subreddit App Idea Validation | [`skills/subreddit-app-idea-validation.md`](skills/subreddit-app-idea-validation.md) |
| Skill | Play Console Search Term Analysis | [`skills/play-console-search-term-analysis.md`](skills/play-console-search-term-analysis.md) |
| Skill | Market Opportunity Clustering | [`skills/market-opportunity-clustering.md`](skills/market-opportunity-clustering.md) |
| Skill | App Market Research Orchestrator | [`skills/app-market-research-orchestrator.md`](skills/app-market-research-orchestrator.md) |
| Skill | Palmier Pro MCP Setup and Safety | [`skills/palmierpro-mcp-setup-and-safety.md`](skills/palmierpro-mcp-setup-and-safety.md) |
| Skill | Palmier Pro Timeline Editing | [`skills/palmierpro-timeline-editing.md`](skills/palmierpro-timeline-editing.md) |
| Skill | Palmier Pro Transcript Cuts and Captions | [`skills/palmierpro-transcript-cuts-and-captions.md`](skills/palmierpro-transcript-cuts-and-captions.md) |
| Skill | Palmier Pro AI Generation Workflow | [`skills/palmierpro-ai-generation-workflow.md`](skills/palmierpro-ai-generation-workflow.md) |
| Skill | GitHub Copilot Token Efficiency | [`skills/copilot-token-efficiency.md`](skills/copilot-token-efficiency.md) |
| Skill | Context Budgeting and Pruning | [`skills/context-budgeting-and-pruning.md`](skills/context-budgeting-and-pruning.md) |
| Skill | Token Output Budgeting | [`skills/token-output-budgeting.md`](skills/token-output-budgeting.md) |
| Skill | Token-Efficient Response Compression | [`skills/token-efficient-response-compression.md`](skills/token-efficient-response-compression.md) |
| Skill | Prompt and Memory Compression | [`skills/prompt-and-memory-compression.md`](skills/prompt-and-memory-compression.md) |
| Skill | Token Efficiency Measurement | [`skills/token-efficiency-measurement.md`](skills/token-efficiency-measurement.md) |
| Skill | Kubernetes GitOps Change Management | [`skills/kubernetes-gitops-change-management.md`](skills/kubernetes-gitops-change-management.md) |
| Skill | Kubernetes Homelab Troubleshooting | [`skills/kubernetes-homelab-troubleshooting.md`](skills/kubernetes-homelab-troubleshooting.md) |
| Skill | Comet Authenticated Research | [`skills/comet-authenticated-research.md`](skills/comet-authenticated-research.md) |
| Skill | Comet Local Bridge Safety | [`skills/comet-local-bridge-safety.md`](skills/comet-local-bridge-safety.md) |
| Skill | Google Play Growth Orchestrator | [`skills/google-play-growth-orchestrator.md`](skills/google-play-growth-orchestrator.md) |
| Skill | Google Play ASO Foundations | [`skills/google-play-aso-foundations.md`](skills/google-play-aso-foundations.md) |
| Skill | Google Play Keyword and Metadata Optimization | [`skills/google-play-keyword-and-metadata-optimization.md`](skills/google-play-keyword-and-metadata-optimization.md) |
| Skill | Google Play Creative Conversion Optimization | [`skills/google-play-creative-conversion-optimization.md`](skills/google-play-creative-conversion-optimization.md) |
| Skill | Google Play Quality and Retention Signals | [`skills/google-play-quality-and-retention-signals.md`](skills/google-play-quality-and-retention-signals.md) |
| Skill | App Web SEO and Entity Optimization | [`skills/app-web-seo-and-entity-optimization.md`](skills/app-web-seo-and-entity-optimization.md) |
| Skill | AI Agent Recommendation Readiness | [`skills/ai-agent-recommendation-readiness.md`](skills/ai-agent-recommendation-readiness.md) |
| Skill | App Growth Experimentation and Measurement | [`skills/app-growth-experimentation-and-measurement.md`](skills/app-growth-experimentation-and-measurement.md) |
| Skill | Wear OS Play Store Readiness | [`skills/wearos-playstore-readiness.md`](skills/wearos-playstore-readiness.md) |
| Skill | Wear OS Screen Edge Safety | [`skills/wearos-screen-edge-safety.md`](skills/wearos-screen-edge-safety.md) |
| Skill | US-Europe Baggage and Packing Research | [`skills/us-europe-baggage-packing-research.md`](skills/us-europe-baggage-packing-research.md) |
| Prompt | Build a Production-Quality AI Agent | [`prompts/planning/build-ai-agent.md`](prompts/planning/build-ai-agent.md) |
| Prompt | Select the Right Automation Platform | [`prompts/planning/select-automation-platform.md`](prompts/planning/select-automation-platform.md) |
| Prompt | Challenge an Automation Platform Choice | [`prompts/review/challenge-automation-platform-choice.md`](prompts/review/challenge-automation-platform-choice.md) |
| Prompt | Validate an App Idea in a Community | [`prompts/research/validate-app-idea-in-community.md`](prompts/research/validate-app-idea-in-community.md) |
| Prompt | Palmier Pro Story Assembly From Project Media | [`prompts/palmierpro/story-assembly-from-project-media.md`](prompts/palmierpro/story-assembly-from-project-media.md) |
| Prompt | Palmier Pro YouTube Short From Long-Form | [`prompts/palmierpro/youtube-short-from-long-form.md`](prompts/palmierpro/youtube-short-from-long-form.md) |
| Prompt | Palmier Pro Full Edit Pass | [`prompts/palmierpro/full-edit-pass.md`](prompts/palmierpro/full-edit-pass.md) |
| Prompt | Palmier Pro Transcript Cleanup Pass | [`prompts/palmierpro/transcript-cleanup-pass.md`](prompts/palmierpro/transcript-cleanup-pass.md) |
| Prompt | Palmier Pro Short-Form Social Cutdown | [`prompts/palmierpro/short-form-social-cutdown.md`](prompts/palmierpro/short-form-social-cutdown.md) |
| Prompt | Common Task Token Efficiency Benchmark | [`prompts/token-efficiency/common-task-benchmark.md`](prompts/token-efficiency/common-task-benchmark.md) |
| Prompt | Compare Models for Token Efficiency | [`prompts/token-efficiency/compare-models.md`](prompts/token-efficiency/compare-models.md) |

For the full list, use [`INDEX.md`](INDEX.md).

## Examples

| Recipe | Use |
|---|---|
| [`examples/agent-build-brief.yaml`](examples/agent-build-brief.yaml) | Ready-to-adapt structured brief for building a repository maintenance agent with explicit runtime and authority boundaries. |
| [`examples/automation-platform-decision-brief.yaml`](examples/automation-platform-decision-brief.yaml) | Category-aware automation selection brief with incumbents, alternatives, hosting, licensing, migration, and evidence controls. |
| [`examples/app-market-research-brief.yaml`](examples/app-market-research-brief.yaml) | Ready-to-adapt Wear OS market-research brief. |
| [`examples/palmierpro-mcp-workflow.md`](examples/palmierpro-mcp-workflow.md) | Copy-paste Palmier Pro MCP editing workflows. |
| [`examples/copilot-token-efficiency.md`](examples/copilot-token-efficiency.md) | Drop-in `.github` files + habits to lower GitHub Copilot cost. |
| [`examples/coding.md`](examples/coding.md) | Build a compact coding workflow. |
| [`examples/benchmark.md`](examples/benchmark.md) | Run a token-efficiency benchmark. |
| [`examples/compression.md`](examples/compression.md) | Compress prompt, memory, or instruction files. |
| [`examples/handoff.md`](examples/handoff.md) | Create compact continuation handoffs. |
| [`examples/local-model.md`](examples/local-model.md) | Use AgentDefaults with a chat/local model. |
| [`examples/repository-profile.md`](examples/repository-profile.md) | Use a thin repository profile wrapper. |

## Patterns For New Defaults

| Pattern | Use |
|---|---|
| [`docs/patterns/agent.md`](docs/patterns/agent.md) | New canonical agent profile structure. |
| [`docs/patterns/default.md`](docs/patterns/default.md) | Generic reusable default structure. |
| [`docs/patterns/skill.md`](docs/patterns/skill.md) | New skill structure. |
| [`docs/patterns/prompt.md`](docs/patterns/prompt.md) | New prompt structure. |
| [`docs/patterns/benchmark.md`](docs/patterns/benchmark.md) | New benchmark artifact structure. |

## Validation

Run the reusable validator instead of copying long snippets from the README:

```bash
python3 scripts/validate-agentdefaults.py
```

It checks:

- Core, Agent Architect and Builder, and automation-platform required files exist.
- Markdown defaults include `## Purpose`.
- Every JSON manifest and schema parses and local schema references resolve.
- Manifest metadata and featured-stack references are valid.
- The Agent Architect and Builder stack preserves canonical build modes, architecture choices, permission classes, runtime-capability fields, required contract terms, and all 22 acceptance scenarios.
- The automation platform stack preserves its canonical capability, evidence, economics, and acceptance-test invariants.
- Local Markdown links resolve.

## Benchmark Evidence

| Artifact | Result | Scope |
|---|---:|---|
| [`docs/benchmarks/token-efficiency-smoke-test.md`](docs/benchmarks/token-efficiency-smoke-test.md) | ~38.8% average output savings (estimated, chars/4) | Initial local IDE-agent smoke test. |
| [`docs/benchmarks/token-efficiency-fresh-2026-06-25.md`](docs/benchmarks/token-efficiency-fresh-2026-06-25.md) | ~35.4% average output savings (estimated, chars/4) | Fresh local benchmark after validation micro-examples. |

These are repo-internal validation artifacts, not public benchmark claims. For stronger evidence, run [`prompts/token-efficiency/compare-models.md`](prompts/token-efficiency/compare-models.md) across multiple model classes with exact provider token counts.

## Repository Map

```text
agentdefaults/
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── AUTOMATION_PLATFORM_INDEX.md
├── agentdefaults.manifest.json
├── scripts/
│   └── validate-agentdefaults.py
├── schemas/
│   ├── agent-build-brief.schema.json
│   ├── automation-platform-decision-brief.schema.json
│   └── app-market-research-brief.schema.json
├── docs/
│   ├── agent-builder-acceptance-tests.md
│   ├── automation-platform-selection-acceptance-tests.md
│   ├── user-guide.md
│   ├── ux-roadmap.md
│   ├── palmierpro-mcp-tool-map.md
│   ├── app-market-research-acceptance-tests.md
│   ├── quickstarts/
│   │   ├── agent-builder.md
│   │   ├── automation-platform-selection.md
│   │   └── community-app-validation.md
│   ├── patterns/
│   │   └── agent.md
│   └── benchmarks/
├── examples/
│   ├── agent-build-brief.yaml
│   └── automation-platform-decision-brief.yaml
├── agents/
│   ├── agent-architect-builder.md
│   ├── automation-platform-selection-advisor.md
│   └── community-app-idea-validation-agent.md
├── skills/
│   ├── agent-design-and-build.md
│   ├── automation-platform-capability-taxonomy.md
│   ├── automation-platform-candidate-discovery.md
│   ├── ci-cd-platform-alternatives-analysis.md
│   ├── infrastructure-as-code-platform-alternatives-analysis.md
│   ├── configuration-management-platform-alternatives-analysis.md
│   ├── gitops-runbook-and-workflow-platform-analysis.md
│   └── subreddit-app-idea-validation.md
├── prompts/
│   ├── planning/
│   │   ├── build-ai-agent.md
│   │   └── select-automation-platform.md
│   ├── review/
│   │   └── challenge-automation-platform-choice.md
│   └── research/
│       └── validate-app-idea-in-community.md
├── .github/
│   └── agents/
│       ├── agent-architect-builder.agent.md
│       ├── automation-platform-selection-advisor.agent.md
│       └── community-app-idea-validator.agent.md
├── .cursor/
├── .windsurfrules
├── INDEX.md
├── WEAROS_INDEX.md
├── WEAROS_DEVELOPMENT_INDEX.md
├── TRAVEL_INDEX.md
└── README.md
```

## Token Efficiency Philosophy

- Compress language, not meaning.
- Reduce input/context, tool-result, and output waste.
- Preserve exact technical identifiers and safety rules.
- Benchmark quality separately from token savings.
- Keep prompts usable across hosted frontier models, coding agents, local LLMs, browser agents, and MCP tools.

## Contributing

Before adding a new default, ask:

1. Is this reusable across more than one project?
2. Is the expected output clear?
3. Does it define enough context for an agent to perform well?
4. Are safety boundaries and destructive-action limits explicit?
5. Can another engineer quickly adapt it?
6. Can token-efficiency claims be measured or honestly estimated?

Use [`docs/patterns/agent.md`](docs/patterns/agent.md) for new agent profiles and [`docs/patterns/default.md`](docs/patterns/default.md) for other reusable content.

## Status

Usable cross-tool scaffold with reusable agent-construction defaults, category-aware automation platform architecture and selection, token-efficiency defaults, browser-based app-market research, focused subreddit/community app-idea validation, Palmier Pro MCP video-editing defaults, Google Play growth tooling, Wear OS development and release stacks, travel research, tool wrappers, quickstarts, examples, schemas, patterns, and validation tooling.

## License

License to be added.
