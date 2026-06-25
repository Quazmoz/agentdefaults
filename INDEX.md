# AgentDefaults Index

Fast lookup for agents, skills, prompts, wrappers, quickstarts, examples, patterns, benchmark artifacts, and recommended stacks.

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
| Any chat/local model usage | `examples/local-model.md` | copy-paste selected stack |
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

## UX Guides

| Guide | Path | Use |
|---|---|---|
| User Guide | `docs/user-guide.md` | Choose the right entrypoint, stack, and validation path. |
| UX Roadmap | `docs/ux-roadmap.md` | Track follow-up usability improvements. |
| Tool Integration Guide | `docs/tool-integration-guide.md` | Practical tool-by-tool setup and maintenance guidance. |
| CLI Quickstart | `docs/quickstarts/cli.md` | Local repo-aware coding CLI usage. |
| Claude Quickstart | `docs/quickstarts/claude.md` | Claude-style usage. |
| Gemini Quickstart | `docs/quickstarts/gemini.md` | Gemini-style usage. |
| Editor Quickstart | `docs/quickstarts/editor.md` | Cursor/Windsurf-style editor rule usage. |
| Repository Assistant Quickstart | `docs/quickstarts/repo-assistant.md` | Repository-level assistant wrappers and profile files. |

## Canonical Agents

| Agent | Path | Use |
|---|---|---|
| Kubernetes Homelab Engineer | `agents/kubernetes-homelab-engineer.md` | Kubernetes homelab and GitOps specialist. |
| Token-Efficient Response Agent | `agents/token-efficient-response-agent.md` | High-signal, low-token behavior layer. |
| Token Economy Orchestrator | `agents/token-economy-orchestrator.md` | Manage input, context, tool-result, and output token budgets. |
| Terse Technical Coding Agent | `agents/terse-technical-coding-agent.md` | Senior-engineer coding workflows with focused diffs. |
| Comet Authenticated Research Agent | `agents/comet-authenticated-research-agent.md` | Human-in-the-loop authenticated/browser research workflow. |
| SEO and AI Search Optimization Agent | `agents/seo-ai-search-optimization-agent.md` | Classic SEO and AI-search visibility reviews. |

## Canonical Skills

| Skill | Path | Use |
|---|---|---|
| Token-Efficient Response Compression | `skills/token-efficient-response-compression.md` | Compress verbose output without losing correctness. |
| Context Budgeting and Pruning | `skills/context-budgeting-and-pruning.md` | Reduce input/context token usage. |
| Token Output Budgeting | `skills/token-output-budgeting.md` | Control response verbosity with explicit modes and validation micro-examples. |
| Prompt and Memory Compression | `skills/prompt-and-memory-compression.md` | Compress recurring prompt/memory/instruction files. |
| Token Efficiency Measurement | `skills/token-efficiency-measurement.md` | Measure savings and quality regressions. |
| Kubernetes GitOps Change Management | `skills/kubernetes-gitops-change-management.md` | Safely add/modify Kubernetes GitOps resources. |
| Kubernetes Homelab Troubleshooting | `skills/kubernetes-homelab-troubleshooting.md` | Diagnose Kubernetes homelab runtime issues. |
| Comet Authenticated Research | `skills/comet-authenticated-research.md` | Safe human-in-the-loop authenticated research. |
| Comet Local Bridge Safety | `skills/comet-local-bridge-safety.md` | Safe local browser bridge design/review. |

## Canonical Prompts

| Prompt | Path | Use |
|---|---|---|
| Common Task Token Efficiency Benchmark | `prompts/token-efficiency/common-task-benchmark.md` | Benchmark baseline vs candidate prompts across common tasks. |
| Token Efficiency Agent Retrofit | `prompts/token-efficiency/agent-retrofit.md` | Retrofit existing prompts/agents with token-efficient behavior. |
| Compress Memory or Instruction File | `prompts/token-efficiency/compress-memory-file.md` | Compress recurring instruction files with an audit report. |
| Compare Models for Token Efficiency | `prompts/token-efficiency/compare-models.md` | Compare prompt behavior across hosted/coding/local models. |

## Examples

| Example | Path | Use |
|---|---|---|
| Coding | `examples/coding.md` | Compact coding workflow. |
| Benchmark | `examples/benchmark.md` | Token-efficiency benchmark recipe. |
| Compression | `examples/compression.md` | Prompt, memory, or instruction compression. |
| Handoff | `examples/handoff.md` | Compact continuation handoff. |
| Local Model | `examples/local-model.md` | Chat/local model copy-paste usage. |
| Repository Profile | `examples/repository-profile.md` | Thin repository profile wrapper usage. |

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
| Token Efficiency Fresh Benchmark | `docs/benchmarks/token-efficiency-fresh-2026-06-25.md` | Fresh third-pass local benchmark after validation micro-examples. |

## Recommended Stacks

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

## Selection Rules

1. Choose the tool entrypoint first.
2. Choose one canonical agent or behavior layer.
3. Add only the skills needed for the task.
4. Prefer narrow context over whole-repo ingestion.
5. Preserve exact paths, commands, schemas, safety rules, and validation status.
6. For token-efficiency claims, use `skills/token-efficiency-measurement.md` or benchmark prompts.
7. When adding new discoverable files, update `README.md`, this `INDEX.md`, and the validation script.

## Maintenance Rules

When adding a new default:

1. Add canonical content under `agents/`, `skills/`, or `prompts/` when possible.
2. Add a wrapper only if a tool benefits from a native file location.
3. Keep wrappers thin; do not duplicate full canonical files everywhere.
4. Add a guide, example, or pattern when it materially improves UX.
5. Run `python3 scripts/validate-agentdefaults.py`.

## Status

Current index includes:

- 6 canonical agents
- 9 canonical skills
- 4 token-efficiency prompts
- 7 tool-specific integration entrypoints/wrappers
- 8 UX/integration guides
- 6 examples
- 4 reusable patterns
- 2 benchmark artifacts
- 1 machine-readable manifest
- 1 validation script
