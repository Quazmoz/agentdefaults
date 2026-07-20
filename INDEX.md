# AgentDefaults Index

## Purpose

Provide fast lookup for agents, skills, prompts, wrappers, quickstarts, examples, schemas, benchmark artifacts, MCP workflows, browser-research workflows, and recommended stacks.

Use this file when an AI agent needs to quickly determine which defaults exist and how to compose them. Use [`README.md`](README.md) for the human-facing overview and [`docs/user-guide.md`](docs/user-guide.md) for guided selection.

## Quick Selection

| Need | Start With | Add / Use |
|---|---|---|
| New user onboarding | `docs/user-guide.md` | `README.md`, `INDEX.md` |
| Generic repo-level agent instructions | `AGENTS.md` | `INDEX.md`, `README.md` |
| Local repo-aware coding CLI | `docs/quickstarts/cli.md` | `AGENTS.md`, selected `agents/` + `skills/` |
| Claude / Claude Code usage | `docs/quickstarts/claude.md` | `CLAUDE.md`, `AGENTS.md`, selected stack |
| Gemini / Gemini CLI usage | `docs/quickstarts/gemini.md` | `GEMINI.md`, `AGENTS.md`, selected stack |
| Editor rule usage | `docs/quickstarts/editor.md` | `.cursor/rules/agentdefaults.mdc`, `.windsurfrules` |
| Repository assistant profiles | `docs/quickstarts/repo-assistant.md` | `.github/copilot-instructions.md`, `.github/agents/*.agent.md` |
| Palmier Pro MCP video editing | `docs/quickstarts/palmierpro-mcp.md` | `agents/palmierpro-mcp-video-editor-agent.md`, Palmier skills/prompts |
| Browser-based app-market research | `docs/quickstarts/app-market-research.md` | `agents/app-market-research-agent.md`, browser-research skills, brief schema |
| Google Play growth / ASO optimization | `docs/quickstarts/google-play-growth.md` | `agents/google-play-growth-optimizer-agent.md`, Google Play growth skills, growth brief schema |
| Build or fix a Wear OS app | `WEAROS_DEVELOPMENT_INDEX.md` | `agents/wearos-app-developer.md`, `skills/wearos-screen-edge-safety.md` |
| Prepare a Wear OS app for Play release | `WEAROS_INDEX.md` | `agents/android-wearos-release-engineer.md`, `skills/wearos-playstore-readiness.md` |
| Plan a US-to-Europe trip | `TRAVEL_INDEX.md` | `agents/us-europe-travel-advisor.md`, `skills/us-europe-baggage-packing-research.md` |
| Palmier Pro story assembly | `prompts/palmierpro/story-assembly-from-project-media.md` | Inspect all project video media, infer intent, extract main points, and assemble a YouTube story arc. |
| YouTube Short from long-form Palmier project | `prompts/palmierpro/youtube-short-from-long-form.md` | Create a 9:16 Short with facecam/screenshare placement and mobile-readable captions. |
| Any chat/local model usage | `examples/local-model.md` | copy-paste selected stack |
| Reduce GitHub Copilot spend (AI Credits) | `skills/copilot-token-efficiency.md` | `examples/copilot-token-efficiency.md`, `skills/context-budgeting-and-pruning.md` |
| Make any agent more concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md`, `skills/token-output-budgeting.md` |
| Manage context/tool/output token budgets | `agents/token-economy-orchestrator.md` | `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md`, `skills/token-efficiency-measurement.md` |
| Make a coding agent terse and senior-engineer focused | `examples/coding.md` | `agents/terse-technical-coding-agent.md`, token-output skills |
| Compress reusable prompts or memory files | `examples/compression.md` | `skills/prompt-and-memory-compression.md`, `prompts/token-efficiency/compress-memory-file.md` |
| Measure token savings for common tasks | `examples/benchmark.md` | `skills/token-efficiency-measurement.md`, benchmark prompts |
| Review existing benchmark evidence | `docs/benchmarks/token-efficiency-fresh-2026-06-25.md` | compare with historical smoke test |
| Add new reusable content | `docs/patterns/default.md` | `docs/patterns/skill.md`, `docs/patterns/prompt.md`, `docs/patterns/benchmark.md` |
| Validate repository UX | `scripts/validate-agentdefaults.py` | run `python3 scripts/validate-agentdefaults.py` |

## Tool Entrypoints

| Tool / Runner | Path | Use |
|---|---|---|
| Generic agents / Codex-style agents | `AGENTS.md` | Broad repository-level instruction file for generic repo-aware agents. |
| Claude | `CLAUDE.md` | Claude-oriented entrypoint that references shared generic rules. |
| Gemini | `GEMINI.md` | Gemini-oriented entrypoint that delegates shared behavior to `AGENTS.md`. |
| GitHub Copilot repository instructions | `.github/copilot-instructions.md` | Repository-wide assistant behavior and maintenance rules. |
| GitHub Copilot custom agent profiles | `.github/agents/*.agent.md` | Selectable profile wrappers that point back to canonical files. |
| Cursor | `.cursor/rules/agentdefaults.mdc` | Thin editor rule wrapper. |
| Windsurf | `.windsurfrules` | Thin editor wrapper. |
| Palmier Pro MCP | `docs/quickstarts/palmierpro-mcp.md` | Video-editing workflow through Palmier Pro's local MCP server. |
| Browser-capable agent | `docs/quickstarts/app-market-research.md` | App-market research with adapter-based browser control and human authentication. |

## UX Guides

| Guide | Path | Use |
|---|---|---|
| User Guide | `docs/user-guide.md` | Choose the right entrypoint, stack, and validation path. |
| UX Roadmap | `docs/ux-roadmap.md` | Track follow-up usability improvements. |
| Tool Integration Guide | `docs/tool-integration-guide.md` | Practical tool-by-tool setup and maintenance guidance. |
| Palmier Pro MCP Quickstart | `docs/quickstarts/palmierpro-mcp.md` | Connect and use Palmier Pro through MCP. |
| App Market Research Quickstart | `docs/quickstarts/app-market-research.md` | Run public and authenticated app-market research. |
| Google Play Growth Quickstart | `docs/quickstarts/google-play-growth.md` | Run the Google Play growth / ASO optimization workflow. |
| App Market Research Acceptance Tests | `docs/app-market-research-acceptance-tests.md` | Validate browser adapters, resume behavior, privacy, and consequential-action safety. |
| Palmier Pro MCP Tool Map | `docs/palmierpro-mcp-tool-map.md` | Choose the right Palmier MCP tool by editing intent. |
| CLI Quickstart | `docs/quickstarts/cli.md` | Local repo-aware coding CLI usage. |
| Claude Quickstart | `docs/quickstarts/claude.md` | Claude-style usage. |
| Gemini Quickstart | `docs/quickstarts/gemini.md` | Gemini-style usage. |
| Editor Quickstart | `docs/quickstarts/editor.md` | Cursor/Windsurf-style editor rule usage. |
| Repository Assistant Quickstart | `docs/quickstarts/repo-assistant.md` | Repository-level assistant wrappers and profile files. |

## Domain Sub-Indexes

Focused root-level indexes for the larger domain packs:

| Sub-Index | Path | Use |
|---|---|---|
| Wear OS Development | `WEAROS_DEVELOPMENT_INDEX.md` | Building or fixing Wear OS app features. |
| Wear OS Release | `WEAROS_INDEX.md` | Final Wear OS Play Store release readiness. |
| US-Europe Travel | `TRAVEL_INDEX.md` | US-to-Europe travel-prep pack. |

## Canonical Agents

| Agent | Path | Use |
|---|---|---|
| Palmier Pro MCP Video Editor | `agents/palmierpro-mcp-video-editor-agent.md` | Video editing, transcript cleanup, captions, approved generation, and export workflows in Palmier Pro over MCP. |
| App Market Research Agent | `agents/app-market-research-agent.md` | Resumable Google Play, Wear OS, public-community, and approved Play Console research. |
| Kubernetes Homelab Engineer | `agents/kubernetes-homelab-engineer.md` | Kubernetes homelab and GitOps specialist. |
| Token-Efficient Response Agent | `agents/token-efficient-response-agent.md` | High-signal, low-token behavior layer. |
| Token Economy Orchestrator | `agents/token-economy-orchestrator.md` | Manage input, context, tool-result, and output token budgets. |
| Terse Technical Coding Agent | `agents/terse-technical-coding-agent.md` | Senior-engineer coding workflows with focused diffs. |
| Comet Authenticated Research Agent | `agents/comet-authenticated-research-agent.md` | Human-in-the-loop authenticated/browser research workflow. |
| SEO and AI Search Optimization Agent | `agents/seo-ai-search-optimization-agent.md` | Classic SEO and AI-search visibility reviews. |
| Google Play Growth Optimizer | `agents/google-play-growth-optimizer-agent.md` | ASO, listing conversion, quality, SEO/AEO, and AI-recommendation readiness for Android/Wear OS apps. |
| Wear OS App Developer | `agents/wearos-app-developer.md` | Build/fix Wear OS apps with round-screen safety and Play quality guardrails. |
| Android Wear OS Release Engineer | `agents/android-wearos-release-engineer.md` | Final Play Store release readiness, packaging, listing, privacy, and watch-face format checks. |
| US to Europe Travel Advisor | `agents/us-europe-travel-advisor.md` | Research-first US-to-Europe trip prep: baggage, customs, entry, money, and outlets. |

## Canonical Skills

| Skill | Path | Use |
|---|---|---|
| Browser Research Foundations | `skills/browser-research-foundations.md` | Shared navigation, provenance, checkpoint, privacy, and failure-handling rules. |
| Authenticated Browser Handoff | `skills/authenticated-browser-handoff.md` | Secure login, CAPTCHA, MFA, consent, takeover, resume, and consequential-action protection. |
| Play Store Autocomplete Research | `skills/play-store-autocomplete-research.md` | Collect visible suggestions with locale, rank, normalization, and checkpoints. |
| Play Store Competitor Discovery | `skills/play-store-competitor-discovery.md` | Find direct competitors and substitutes while verifying device support. |
| Play Store Listing Teardown | `skills/play-store-listing-teardown.md` | Analyze positioning, screenshots, monetization, reviews, and update themes. |
| Forum Demand Mining | `skills/forum-demand-mining.md` | Mine public communities for unmet needs, app-search intent, and workarounds. |
| Play Console Search Term Analysis | `skills/play-console-search-term-analysis.md` | Parse approved official exports with human-controlled authentication. |
| Market Opportunity Clustering | `skills/market-opportunity-clustering.md` | Produce evidence-linked opportunity clusters and transparent scoring. |
| App Market Research Orchestrator | `skills/app-market-research-orchestrator.md` | Validate briefs, sequence sources, pause for auth, resume, and generate manifests. |
| Palmier Pro MCP Setup and Safety | `skills/palmierpro-mcp-setup-and-safety.md` | Connect safely, read state, and protect against unintended paid/destructive actions. |
| Palmier Pro Timeline Editing | `skills/palmierpro-timeline-editing.md` | Frame-accurate timeline edits, b-roll, overlays, sync, properties, and verification. |
| Palmier Pro Transcript Cuts and Captions | `skills/palmierpro-transcript-cuts-and-captions.md` | Filler removal, retake cleanup, dead-air reduction, and caption creation. |
| Palmier Pro AI Generation Workflow | `skills/palmierpro-ai-generation-workflow.md` | Approved image/video/audio generation, upscaling, prompts, references, and organization. |
| GitHub Copilot Token Efficiency | `skills/copilot-token-efficiency.md` | Cut Copilot spend via model selection, context scoping, modes, and `.github` files. |
| Token-Efficient Response Compression | `skills/token-efficient-response-compression.md` | Compress verbose output without losing correctness. |
| Context Budgeting and Pruning | `skills/context-budgeting-and-pruning.md` | Reduce input/context token usage. |
| Token Output Budgeting | `skills/token-output-budgeting.md` | Control response verbosity with explicit modes and validation micro-examples. |
| Prompt and Memory Compression | `skills/prompt-and-memory-compression.md` | Compress recurring prompt/memory/instruction files. |
| Token Efficiency Measurement | `skills/token-efficiency-measurement.md` | Measure savings and quality regressions. |
| Kubernetes GitOps Change Management | `skills/kubernetes-gitops-change-management.md` | Safely add/modify Kubernetes GitOps resources. |
| Kubernetes Homelab Troubleshooting | `skills/kubernetes-homelab-troubleshooting.md` | Diagnose Kubernetes homelab runtime issues. |
| Comet Authenticated Research | `skills/comet-authenticated-research.md` | Safe human-in-the-loop authenticated research. |
| Comet Local Bridge Safety | `skills/comet-local-bridge-safety.md` | Safe local browser bridge design/review. |
| Google Play Growth Orchestrator | `skills/google-play-growth-orchestrator.md` | Validate a growth brief, sequence the growth skills, and produce a prioritized plan. |
| Google Play ASO Foundations | `skills/google-play-aso-foundations.md` | Core Play ranking/conversion factors and policy-safe ASO principles. |
| Google Play Keyword and Metadata Optimization | `skills/google-play-keyword-and-metadata-optimization.md` | Title, short/long description, and keyword work within field limits and policy. |
| Google Play Creative Conversion Optimization | `skills/google-play-creative-conversion-optimization.md` | Icon, screenshots, feature graphic, and store-listing experiments. |
| Google Play Quality and Retention Signals | `skills/google-play-quality-and-retention-signals.md` | Android vitals, ratings/reviews, retention, and quality as growth work. |
| App Web SEO and Entity Optimization | `skills/app-web-seo-and-entity-optimization.md` | Crawlable product pages, canonical entity facts, and AEO for apps. |
| AI Agent Recommendation Readiness | `skills/ai-agent-recommendation-readiness.md` | Make an app safely quotable/recommendable by AI assistants; crawler controls. |
| App Growth Experimentation and Measurement | `skills/app-growth-experimentation-and-measurement.md` | Experiment design, metrics, and honest measurement for app growth. |
| Wear OS Play Store Readiness | `skills/wearos-playstore-readiness.md` | Pre-submission Wear OS release, listing, screenshot, and privacy review. |
| Wear OS Screen Edge Safety | `skills/wearos-screen-edge-safety.md` | Prevent/fix clipped text/controls, overlap, font-scaling, and missing scroll indicators. |
| US-Europe Baggage and Packing Research | `skills/us-europe-baggage-packing-research.md` | Baggage, customs, packing, money, outlet, and return-to-US research workflow. |

## Canonical Prompts

| Prompt | Path | Use |
|---|---|---|
| Palmier Pro Story Assembly From Project Media | `prompts/palmierpro/story-assembly-from-project-media.md` | Inspect all relevant project video assets, infer intent, extract main points, and build a YouTube story arc for an AI-engineering creator. |
| Palmier Pro YouTube Short From Long-Form | `prompts/palmierpro/youtube-short-from-long-form.md` | Create a 9:16 YouTube Short from long-form footage with facecam/screenshare placement and mobile-safe captions. |
| Palmier Pro Full Edit Pass | `prompts/palmierpro/full-edit-pass.md` | Run a complete first-pass Palmier timeline edit. |
| Palmier Pro Transcript Cleanup Pass | `prompts/palmierpro/transcript-cleanup-pass.md` | Clean speech without broader timeline restructuring. |
| Palmier Pro Short-Form Social Cutdown | `prompts/palmierpro/short-form-social-cutdown.md` | Create a short-form social clip from a longer Palmier project. |
| Common Task Token Efficiency Benchmark | `prompts/token-efficiency/common-task-benchmark.md` | Benchmark baseline vs candidate prompts across common tasks. |
| Token Efficiency Agent Retrofit | `prompts/token-efficiency/agent-retrofit.md` | Retrofit existing prompts/agents with token-efficient behavior. |
| Compress Memory or Instruction File | `prompts/token-efficiency/compress-memory-file.md` | Compress recurring instruction files with an audit report. |
| Compare Models for Token Efficiency | `prompts/token-efficiency/compare-models.md` | Compare prompt behavior across hosted/coding/local models. |
| Wear OS App Development | `prompts/implementation/wearos-app-development.md` | One-shot implementation prompt for building/fixing a Wear OS feature. |
| Wear OS Release Readiness Review | `prompts/review/wearos-release-readiness-review.md` | One-shot prompt to review and fix a Wear OS repo for Play release. |
| US-Europe Trip Prep | `prompts/planning/us-europe-trip-prep.md` | One-shot US-to-Europe trip-prep guide prompt. |

## Schemas

| Schema | Path | Use |
|---|---|---|
| App Market Research Brief | `schemas/app-market-research-brief.schema.json` | Validate markets, seeds, sources, outputs, and scoring options before browsing. |
| Google Play Growth Brief | `schemas/google-play-growth-brief.schema.json` | Validate app, markets, objectives, sources, and outputs for a growth engagement. |

## Examples

| Example | Path | Use |
|---|---|---|
| App Market Research Brief | `examples/app-market-research-brief.yaml` | Copy-paste Wear OS research brief for GB and US sources. |
| Palmier Pro MCP Workflow | `examples/palmierpro-mcp-workflow.md` | Copy-paste Palmier Pro MCP editing workflows. |
| GitHub Copilot Token Efficiency | `examples/copilot-token-efficiency.md` | Drop-in `.github` files + habits to lower GitHub Copilot cost. |
| Coding | `examples/coding.md` | Compact coding workflow. |
| Benchmark | `examples/benchmark.md` | Token-efficiency benchmark recipe. |
| Compression | `examples/compression.md` | Prompt, memory, or instruction compression. |
| Handoff | `examples/handoff.md` | Compact continuation handoff. |
| Local Model | `examples/local-model.md` | Chat/local model copy-paste usage. |
| Repository Profile | `examples/repository-profile.md` | Thin repository profile wrapper usage. |
| Google Play Growth Brief | `examples/google-play-growth-brief.yaml` | Copy-paste Wear OS Google Play growth brief. |
| US-Europe Travel Prep Stack | `examples/stacks/us-europe-travel-prep.md` | Composed travel-prep stack (agent, skill, behavior layer, prompt). |
| Wear OS Play Store Release Stack | `examples/stacks/wearos-playstore-release.md` | Composed Wear OS release stack. |
| Wear OS Tool Configs | `examples/tool-configs/wearos-CLAUDE.md`, `examples/tool-configs/wearos-codex-AGENTS.md` | Copy-in `CLAUDE.md` / `AGENTS.md` for a Wear OS app repo. |
| Travel Tool Configs | `examples/tool-configs/travel-CLAUDE.md`, `examples/tool-configs/travel-codex-AGENTS.md` | Copy-in `CLAUDE.md` / `AGENTS.md` for a travel-prep workspace. |

## Patterns

| Pattern | Path | Use |
|---|---|---|
| Default Pattern | `docs/patterns/default.md` | Generic reusable default structure. |
| Skill Pattern | `docs/patterns/skill.md` | Structure for new skills. |
| Prompt Pattern | `docs/patterns/prompt.md` | Structure for new prompts. |
| Benchmark Pattern | `docs/patterns/benchmark.md` | Structure for benchmark artifacts. |

## Benchmark Artifacts

| Artifact | Path | Use |
|---|---|---|
| Token Efficiency Smoke Test | `docs/benchmarks/token-efficiency-smoke-test.md` | Initial local IDE-agent smoke-test result using estimated token counts. |
| Token Efficiency Fresh Benchmark | `docs/benchmarks/token-efficiency-fresh-2026-06-25.md` | Fresh local benchmark after validation micro-examples. |

## Recommended Stacks

### App Market Browser Research Stack

```text
Entrypoint:
  docs/quickstarts/app-market-research.md

Agent:
  agents/app-market-research-agent.md

Skills:
  skills/browser-research-foundations.md
  skills/authenticated-browser-handoff.md
  skills/play-store-autocomplete-research.md
  skills/play-store-competitor-discovery.md
  skills/play-store-listing-teardown.md
  skills/forum-demand-mining.md
  skills/play-console-search-term-analysis.md
  skills/market-opportunity-clustering.md
  skills/app-market-research-orchestrator.md

Schema:
  schemas/app-market-research-brief.schema.json

Example:
  examples/app-market-research-brief.yaml

Acceptance tests:
  docs/app-market-research-acceptance-tests.md
```

### Palmier Pro MCP Video Editing Stack

```text
Entrypoint:
  docs/quickstarts/palmierpro-mcp.md

Agent:
  agents/palmierpro-mcp-video-editor-agent.md

Skills:
  skills/palmierpro-mcp-setup-and-safety.md
  skills/palmierpro-timeline-editing.md
  skills/palmierpro-transcript-cuts-and-captions.md
  skills/palmierpro-ai-generation-workflow.md

Tool map:
  docs/palmierpro-mcp-tool-map.md

Prompts:
  prompts/palmierpro/story-assembly-from-project-media.md
  prompts/palmierpro/youtube-short-from-long-form.md
  prompts/palmierpro/full-edit-pass.md
  prompts/palmierpro/transcript-cleanup-pass.md
  prompts/palmierpro/short-form-social-cutdown.md

Example:
  examples/palmierpro-mcp-workflow.md
```

### GitHub Copilot Cost-Reduction Stack

```text
Entrypoint:
  .github/copilot-instructions.md (drop-in from examples/copilot-token-efficiency.md)

Skill:
  skills/copilot-token-efficiency.md

Supporting skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficiency-measurement.md

Example:
  examples/copilot-token-efficiency.md
```

### Cross-Tool Token Economy Stack

```text
Entrypoint:
  AGENTS.md or tool-specific wrapper

Behavior layers:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md
  skills/token-efficiency-measurement.md
```

### Terse Coding Stack

```text
Entrypoint:
  AGENTS.md, CLAUDE.md, GEMINI.md, or .github/agents/terse-technical-coding.agent.md

Agent:
  agents/terse-technical-coding-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md
```

### Benchmark Stack

```text
Agent wrapper:
  .github/agents/token-efficiency-benchmark.agent.md

Skills:
  skills/token-efficiency-measurement.md

Prompts:
  prompts/token-efficiency/common-task-benchmark.md
  prompts/token-efficiency/compare-models.md

Artifacts:
  docs/benchmarks/token-efficiency-smoke-test.md
  docs/benchmarks/token-efficiency-fresh-2026-06-25.md
```

### Google Play Growth Stack

```text
Entrypoint:
  docs/quickstarts/google-play-growth.md

Agent:
  agents/google-play-growth-optimizer-agent.md

Skills:
  skills/google-play-growth-orchestrator.md
  skills/google-play-aso-foundations.md
  skills/google-play-keyword-and-metadata-optimization.md
  skills/google-play-creative-conversion-optimization.md
  skills/google-play-quality-and-retention-signals.md
  skills/app-web-seo-and-entity-optimization.md
  skills/ai-agent-recommendation-readiness.md
  skills/app-growth-experimentation-and-measurement.md

Schema:
  schemas/google-play-growth-brief.schema.json

Example:
  examples/google-play-growth-brief.yaml

Acceptance tests:
  docs/google-play-growth-acceptance-tests.md
```

### Wear OS Development Stack

```text
Sub-index:
  WEAROS_DEVELOPMENT_INDEX.md

Agent:
  agents/wearos-app-developer.md

Skills:
  skills/wearos-screen-edge-safety.md
  skills/token-efficient-response-compression.md

Prompt:
  prompts/implementation/wearos-app-development.md
```

### Wear OS Play Store Release Stack

```text
Sub-index:
  WEAROS_INDEX.md

Agent:
  agents/android-wearos-release-engineer.md

Skills:
  skills/wearos-playstore-readiness.md
  skills/wearos-screen-edge-safety.md

Prompt:
  prompts/review/wearos-release-readiness-review.md

Example:
  examples/stacks/wearos-playstore-release.md
```

### US-Europe Travel Prep Stack

```text
Sub-index:
  TRAVEL_INDEX.md

Agent:
  agents/us-europe-travel-advisor.md

Skills:
  skills/us-europe-baggage-packing-research.md
  skills/token-efficient-response-compression.md

Prompt:
  prompts/planning/us-europe-trip-prep.md

Example:
  examples/stacks/us-europe-travel-prep.md
```

## Selection Rules

1. Choose the tool entrypoint first.
2. Choose one canonical agent or behavior layer.
3. Add only the skills needed for the task.
4. Prefer narrow context over whole-repo ingestion.
5. Preserve exact paths, commands, schemas, safety rules, and validation status.
6. For MCP tools, treat live tool output as the source of truth over static docs.
7. For browser research, treat visible source evidence and approved exports as the source of truth.
8. For token-efficiency claims, use `skills/token-efficiency-measurement.md` or benchmark prompts.
9. When adding new discoverable files, update `README.md`, this `INDEX.md`, and the validation script.

## Maintenance Rules

When adding a new default:

1. Add canonical content under `agents/`, `skills/`, or `prompts/` when possible.
2. Add a wrapper only if a tool benefits from a native file location.
3. Keep wrappers thin; do not duplicate full canonical files everywhere.
4. Add a guide, example, schema, or pattern when it materially improves UX.
5. Run `python3 scripts/validate-agentdefaults.py`.

## Status

Current index includes:

- 12 canonical agents
- 34 canonical skills
- 12 canonical prompts
- 11 tool integration files (6 entrypoint/rule files + 5 Copilot agent profiles)
- 3 domain sub-indexes (Wear OS development, Wear OS release, US-Europe travel)
- 8 quickstarts plus UX/integration guides, acceptance tests, and tool maps
- 16 examples
- 4 reusable patterns
- 2 benchmark artifacts
- 2 machine-readable workflow schemas
- 1 machine-readable manifest
