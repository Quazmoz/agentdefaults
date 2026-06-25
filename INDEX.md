# AgentDefaults Index

Fast lookup for agents, skills, prompts, wrappers, benchmark artifacts, and recommended stacks.

Use this file when an AI agent needs to quickly determine which defaults exist and how to compose them. Use `README.md` for the broader human-facing overview and `docs/tool-integration-guide.md` for tool-specific setup.

## Quick Selection

| Need | Start With | Add / Use |
|---|---|---|
| Generic repo-level agent instructions | `AGENTS.md` | `INDEX.md`, `README.md` |
| Claude / Claude Code usage | `CLAUDE.md` | `AGENTS.md`, `INDEX.md`, selected `agents/` + `skills/` |
| Gemini / Gemini CLI usage | `GEMINI.md` | `AGENTS.md`, `INDEX.md`, selected `agents/` + `skills/` |
| GitHub Copilot repo-wide behavior | `.github/copilot-instructions.md` | `AGENTS.md`, `INDEX.md` |
| GitHub Copilot selectable agents | `.github/agents/*.agent.md` | Commit to default branch, refresh Copilot/GitHub agent UI |
| Cursor usage | `.cursor/rules/agentdefaults.mdc` | `AGENTS.md`, `INDEX.md` |
| Windsurf usage | `.windsurfrules` | `AGENTS.md`, `INDEX.md` |
| Any chat/local model usage | `agents/`, `skills/`, `prompts/` | Copy-paste selected stack |
| Make any agent more concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md`, `skills/token-output-budgeting.md` |
| Manage context/tool/output token budgets | `agents/token-economy-orchestrator.md` | `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md`, `skills/token-efficiency-measurement.md` |
| Make a coding agent terse and senior-engineer focused | `agents/terse-technical-coding-agent.md` | `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md` |
| Compress reusable prompts or memory files | `skills/prompt-and-memory-compression.md` | `prompts/token-efficiency/compress-memory-file.md`, `prompts/token-efficiency/agent-retrofit.md` |
| Measure token savings for common tasks | `skills/token-efficiency-measurement.md` | `prompts/token-efficiency/common-task-benchmark.md`, `prompts/token-efficiency/compare-models.md` |
| Review existing benchmark evidence | `docs/benchmarks/token-efficiency-smoke-test.md` | Treat as an initial local smoke test, not a controlled public benchmark |
| Work on Quinn's Kubernetes homelab | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-gitops-change-management.md`, `skills/kubernetes-homelab-troubleshooting.md` |
| Research authenticated or automation-hostile sites with Comet | `agents/comet-authenticated-research-agent.md` | `skills/comet-authenticated-research.md`, `skills/comet-local-bridge-safety.md` |
| Improve classic SEO and AI search visibility | `agents/seo-ai-search-optimization-agent.md` | `skills/token-efficient-response-compression.md`, `skills/token-output-budgeting.md` |

## Tool Entrypoints

### Generic Agents / Codex-Style Agents

**Path:** `AGENTS.md`

Use as the broad repository-level instruction file for any tool that supports generic agent manifests or manual context attachment.

### Claude

**Path:** `CLAUDE.md`

Use as the Claude-oriented entrypoint. It references `AGENTS.md`, `INDEX.md`, and task-relevant canonical files while discouraging whole-repo context loading.

### Gemini

**Path:** `GEMINI.md`

Use as the Gemini-oriented entrypoint. It keeps Gemini-specific guidance thin and delegates shared behavior to `AGENTS.md`.

### GitHub Copilot Repository Instructions

**Path:** `.github/copilot-instructions.md`

Use for repository-wide Copilot behavior and maintenance rules.

### GitHub Copilot Custom Agent Profiles

**Paths:**

```text
.github/agents/token-economy-orchestrator.agent.md
.github/agents/terse-technical-coding.agent.md
.github/agents/token-efficiency-benchmark.agent.md
```

Use these as selectable Copilot custom-agent wrappers. They intentionally reference canonical files instead of duplicating the full library.

### Cursor

**Path:** `.cursor/rules/agentdefaults.mdc`

Use as a thin Cursor rule wrapper for this repository.

### Windsurf

**Path:** `.windsurfrules`

Use as a thin Windsurf wrapper for this repository.

### Cross-Tool Guide

**Path:** `docs/tool-integration-guide.md`

Use for practical tool-by-tool setup and maintenance guidance.

## Canonical Agents

### Kubernetes Homelab Engineer

**Path:** `agents/kubernetes-homelab-engineer.md`

Use for Quinn's `Quazmoz/K8SHomelab` repo and similar production-style Kubernetes homelab environments.

### Token-Efficient Response Agent

**Path:** `agents/token-efficient-response-agent.md`

Use as a behavior layer when responses should be concise, direct, and high-signal.

### Token Economy Orchestrator

**Path:** `agents/token-economy-orchestrator.md`

Use when the agent must manage input, context, tool-result, and output tokens across long-running workflows.

### Terse Technical Coding Agent

**Path:** `agents/terse-technical-coding-agent.md`

Use for senior-engineer coding workflows where the assistant should make focused changes and avoid excessive narration.

### Comet Authenticated Research Agent

**Path:** `agents/comet-authenticated-research-agent.md`

Use when research requires Comet running locally as a visible browser, especially for authenticated or automation-hostile pages.

### SEO and AI Search Optimization Agent

**Path:** `agents/seo-ai-search-optimization-agent.md`

Use for practical search visibility work across classic SEO, AI-search readiness, websites, app listings, GitHub repos, YouTube videos, Product Hunt pages, and landing pages.

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

## Benchmark Artifacts

| Artifact | Path | Use |
|---|---|---|
| Token Efficiency Smoke Test | `docs/benchmarks/token-efficiency-smoke-test.md` | Initial local IDE-agent smoke-test result using estimated token counts. |

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

### Prompt / Memory Compression Stack

```text
Skills:
  skills/prompt-and-memory-compression.md
  skills/token-efficiency-measurement.md

Prompts:
  prompts/token-efficiency/compress-memory-file.md
  prompts/token-efficiency/agent-retrofit.md
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
```

## Selection Rules

1. Choose the tool entrypoint first: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot, Cursor, Windsurf, or manual copy-paste.
2. Choose one canonical agent or behavior layer.
3. Add only the skills needed for the task.
4. Prefer narrow context over whole-repo ingestion.
5. Preserve exact paths, commands, schemas, safety rules, and validation status.
6. For token-efficiency claims, use `skills/token-efficiency-measurement.md` or `prompts/token-efficiency/common-task-benchmark.md`.
7. When adding a wrapper, update `README.md`, this `INDEX.md`, and `docs/tool-integration-guide.md`.

## Maintenance Rules

When adding a new default:

1. Add the canonical file under `agents/`, `skills/`, or `prompts/`.
2. Add a wrapper only if a tool benefits from a native file location.
3. Keep wrappers thin; do not duplicate full canonical files everywhere.
4. Update `README.md` and `INDEX.md`.
5. Add or update testing guidance if discoverability changes.

## Status

Current index includes:

- 6 canonical agents
- 9 canonical skills
- 4 token-efficiency prompts
- 7 tool-specific integration entrypoints/wrappers
- 1 cross-tool integration guide
- 1 benchmark artifact
