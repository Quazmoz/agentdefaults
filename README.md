<div align="center">

# AgentDefaults

**Reusable defaults for AI agents, skills, prompts, wrappers, examples, and benchmarkable token-efficiency workflows.**

![Markdown](https://img.shields.io/badge/content-Markdown-blue)
![Agent UX](https://img.shields.io/badge/focus-agent%20UX-purple)
![Token Efficiency](https://img.shields.io/badge/token%20efficiency-benchmarked-brightgreen)
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
| Use a local repo-aware coding CLI | [`docs/quickstarts/cli.md`](docs/quickstarts/cli.md) |
| Use Claude-style repo instructions | [`docs/quickstarts/claude.md`](docs/quickstarts/claude.md) |
| Use Gemini-style repo instructions | [`docs/quickstarts/gemini.md`](docs/quickstarts/gemini.md) |
| Use editor rule files | [`docs/quickstarts/editor.md`](docs/quickstarts/editor.md) |
| Use repository assistant profile wrappers | [`docs/quickstarts/repo-assistant.md`](docs/quickstarts/repo-assistant.md) |
| Use Palmier Pro through MCP | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| Add a new reusable default | [`docs/patterns/default.md`](docs/patterns/default.md) |
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
| Docs | [`docs/`](docs/) | Quickstarts, integration guides, patterns, tool maps, and benchmarks. |
| Examples | [`examples/`](examples/) | Practical copy-paste recipes. |
| Manifest | [`agentdefaults.manifest.json`](agentdefaults.manifest.json) | Machine-readable repo summary. |

Rule: **update canonical content first, then keep wrappers thin and discoverable.**

## Recommended Stacks

### Palmier Pro MCP Video Editing Stack

Use when you want an agent to operate Palmier Pro through MCP for timeline edits, story assembly, transcript cleanup, captions, b-roll, generation approval workflows, and exports.

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
prompts/palmierpro/story-assembly-from-project-media.md
prompts/palmierpro/full-edit-pass.md
examples/palmierpro-mcp-workflow.md
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
| Any chat/local model | [`agents/`](agents/), [`skills/`](skills/), [`prompts/`](prompts/) | Copy-paste the smallest useful stack. |

## Available Defaults

| Type | Name | Path |
|---|---|---|
| Agent | Palmier Pro MCP Video Editor | [`agents/palmierpro-mcp-video-editor-agent.md`](agents/palmierpro-mcp-video-editor-agent.md) |
| Agent | Token Economy Orchestrator | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| Agent | Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) |
| Agent | Terse Technical Coding Agent | [`agents/terse-technical-coding-agent.md`](agents/terse-technical-coding-agent.md) |
| Agent | Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) |
| Agent | Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) |
| Agent | SEO and AI Search Optimization Agent | [`agents/seo-ai-search-optimization-agent.md`](agents/seo-ai-search-optimization-agent.md) |
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
| Prompt | Palmier Pro Story Assembly From Project Media | [`prompts/palmierpro/story-assembly-from-project-media.md`](prompts/palmierpro/story-assembly-from-project-media.md) |
| Prompt | Palmier Pro Full Edit Pass | [`prompts/palmierpro/full-edit-pass.md`](prompts/palmierpro/full-edit-pass.md) |
| Prompt | Palmier Pro Transcript Cleanup Pass | [`prompts/palmierpro/transcript-cleanup-pass.md`](prompts/palmierpro/transcript-cleanup-pass.md) |
| Prompt | Palmier Pro Short-Form Social Cutdown | [`prompts/palmierpro/short-form-social-cutdown.md`](prompts/palmierpro/short-form-social-cutdown.md) |
| Prompt | Common Task Token Efficiency Benchmark | [`prompts/token-efficiency/common-task-benchmark.md`](prompts/token-efficiency/common-task-benchmark.md) |
| Prompt | Compare Models for Token Efficiency | [`prompts/token-efficiency/compare-models.md`](prompts/token-efficiency/compare-models.md) |

For the full list, use [`INDEX.md`](INDEX.md).

## Examples

| Recipe | Use |
|---|---|
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

- Required files exist.
- Markdown defaults include `## Purpose`.
- Local Markdown links resolve.

## Benchmark Evidence

| Artifact | Result | Scope |
|---|---:|---|
| [`docs/benchmarks/token-efficiency-smoke-test.md`](docs/benchmarks/token-efficiency-smoke-test.md) | 38.8% average output savings | Initial local IDE-agent smoke test. |
| [`docs/benchmarks/token-efficiency-fresh-2026-06-25.md`](docs/benchmarks/token-efficiency-fresh-2026-06-25.md) | 35.4% average output savings | Fresh third-pass local benchmark after validation micro-examples. |

These are repo-internal validation artifacts, not public benchmark claims. For stronger evidence, run [`prompts/token-efficiency/compare-models.md`](prompts/token-efficiency/compare-models.md) across multiple model classes with exact provider token counts.

## Repository Map

```text
agentdefaults/
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── agentdefaults.manifest.json
├── scripts/
│   └── validate-agentdefaults.py
├── docs/
│   ├── user-guide.md
│   ├── ux-roadmap.md
│   ├── palmierpro-mcp-tool-map.md
│   ├── quickstarts/
│   ├── patterns/
│   └── benchmarks/
├── examples/
├── agents/
├── skills/
├── prompts/
├── .github/
├── .cursor/
├── .windsurfrules
├── INDEX.md
└── README.md
```

## Token Efficiency Philosophy

- Compress language, not meaning.
- Reduce input/context, tool-result, and output waste.
- Preserve exact technical identifiers and safety rules.
- Benchmark quality separately from token savings.
- Keep prompts usable across hosted frontier models, coding agents, local LLMs, and MCP tools.

## Contributing

Before adding a new default, ask:

1. Is this reusable across more than one project?
2. Is the expected output clear?
3. Does it define enough context for an agent to perform well?
4. Are safety boundaries and destructive-action limits explicit?
5. Can another engineer quickly adapt it?
6. Can token-efficiency claims be measured or honestly estimated?

Use [`docs/patterns/default.md`](docs/patterns/default.md) for new reusable content.

## Status

Usable cross-tool scaffold with benchmarked token-efficiency defaults, Palmier Pro MCP video-editing defaults, tool wrappers, quickstarts, examples, patterns, and validation tooling.

## License

License to be added.
