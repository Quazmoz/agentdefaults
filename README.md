# AgentDefaults

Reusable defaults for building AI agents, skills, prompts, instruction packs, and tool-specific agent wrappers.

AgentDefaults is a practical library of agent-building patterns that can be copied into agentic coding tools, custom assistants, internal automation agents, IDE agents, MCP workflows, or local model runners.

For fast agent discovery and stack selection, see [`INDEX.md`](INDEX.md).

## Purpose

Modern AI agents need reliable defaults: system instructions, reusable skills, task prompts, context rules, benchmark prompts, and tool-specific wrappers.

Use this repository to:

- Bootstrap coding, DevOps, automation, research, product, or documentation agents.
- Reuse proven prompts instead of rewriting instructions from scratch.
- Maintain consistent behavior across Claude, Gemini, GitHub Copilot, Cursor, Windsurf, Codex-style agents, and custom tools.
- Build composable skill packs for repeatable workflows.
- Reduce context, tool-result, and output token waste without sacrificing correctness or safety.
- Benchmark whether concise prompts actually improve common task performance.

## Compatibility Targets

| Tool / Runner | Primary Files | Purpose |
|---|---|---|
| Generic agents / Codex-style agents | [`AGENTS.md`](AGENTS.md), [`INDEX.md`](INDEX.md) | Broad repository-level instructions and stack selection. |
| Claude / Claude Code | [`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md), [`INDEX.md`](INDEX.md) | Claude-oriented entrypoint with shared generic rules. |
| Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md), [`AGENTS.md`](AGENTS.md), [`INDEX.md`](INDEX.md) | Gemini-oriented entrypoint with shared generic rules. |
| GitHub Copilot repository instructions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Repo-wide Copilot behavior and maintenance rules. |
| GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) | Selectable Copilot agent profile wrappers. |
| Cursor | [`.cursor/rules/agentdefaults.mdc`](.cursor/rules/agentdefaults.mdc) | Cursor rule wrapper pointing back to canonical files. |
| Windsurf | [`.windsurfrules`](.windsurfrules) | Windsurf rule wrapper pointing back to canonical files. |
| Any chat model | `agents/`, `skills/`, `prompts/` | Copy-paste reusable agent stacks. |

For setup details, see [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md).

## Repository Model

AgentDefaults separates **canonical reusable content** from **tool-specific wrappers**.

Canonical content:

```text
agents/   complete reusable agent profiles
skills/   composable behavior/task modules
prompts/  copy-paste task prompts and benchmarks
```

Tool wrappers:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
.github/copilot-instructions.md
.github/agents/*.agent.md
.cursor/rules/agentdefaults.mdc
.windsurfrules
docs/tool-integration-guide.md
```

Rule: update canonical content first, then keep wrappers thin and discoverable.

## Recommended Repository Structure

```text
agentdefaults/
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── .github/
│   ├── copilot-instructions.md
│   └── agents/
│       ├── token-economy-orchestrator.agent.md
│       ├── terse-technical-coding.agent.md
│       └── token-efficiency-benchmark.agent.md
├── .cursor/
│   └── rules/
│       └── agentdefaults.mdc
├── .windsurfrules
├── agents/
│   ├── kubernetes-homelab-engineer.md
│   ├── token-efficient-response-agent.md
│   ├── token-economy-orchestrator.md
│   ├── terse-technical-coding-agent.md
│   ├── comet-authenticated-research-agent.md
│   └── seo-ai-search-optimization-agent.md
├── skills/
│   ├── token-efficient-response-compression.md
│   ├── context-budgeting-and-pruning.md
│   ├── token-output-budgeting.md
│   ├── prompt-and-memory-compression.md
│   ├── token-efficiency-measurement.md
│   ├── kubernetes-gitops-change-management.md
│   ├── kubernetes-homelab-troubleshooting.md
│   ├── comet-authenticated-research.md
│   └── comet-local-bridge-safety.md
├── prompts/
│   └── token-efficiency/
│       ├── common-task-benchmark.md
│       ├── agent-retrofit.md
│       ├── compress-memory-file.md
│       └── compare-models.md
├── docs/
│   └── tool-integration-guide.md
├── INDEX.md
└── README.md
```

## Available Defaults

| Type | Name | Path | Purpose |
|---|---|---|---|
| Entrypoint | Generic Agent Instructions | [`AGENTS.md`](AGENTS.md) | Broad tool-agnostic entrypoint for AI coding agents. |
| Entrypoint | Claude Instructions | [`CLAUDE.md`](CLAUDE.md) | Claude-oriented repo instructions that reference shared generic rules. |
| Entrypoint | Gemini Instructions | [`GEMINI.md`](GEMINI.md) | Gemini-oriented repo instructions that reference shared generic rules. |
| Copilot | Copilot Instructions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Repository-wide GitHub Copilot behavior. |
| Copilot Agent | Token Economy Orchestrator | [`.github/agents/token-economy-orchestrator.agent.md`](.github/agents/token-economy-orchestrator.agent.md) | Copilot wrapper for token economy work. |
| Copilot Agent | Terse Technical Coding Agent | [`.github/agents/terse-technical-coding.agent.md`](.github/agents/terse-technical-coding.agent.md) | Copilot wrapper for terse coding and repo maintenance. |
| Copilot Agent | Token Efficiency Benchmark Agent | [`.github/agents/token-efficiency-benchmark.agent.md`](.github/agents/token-efficiency-benchmark.agent.md) | Copilot wrapper for token benchmark reports. |
| Agent | Kubernetes Homelab Engineer | [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) | Kubernetes homelab and GitOps specialist. |
| Agent | Token-Efficient Response Agent | [`agents/token-efficient-response-agent.md`](agents/token-efficient-response-agent.md) | High-signal, low-token behavior layer. |
| Agent | Token Economy Orchestrator | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) | Manages input, tool, and output token budgets. |
| Agent | Terse Technical Coding Agent | [`agents/terse-technical-coding-agent.md`](agents/terse-technical-coding-agent.md) | Senior-engineer coding behavior with focused diffs. |
| Agent | Comet Authenticated Research Agent | [`agents/comet-authenticated-research-agent.md`](agents/comet-authenticated-research-agent.md) | Safe authenticated/browser research workflow. |
| Agent | SEO and AI Search Optimization Agent | [`agents/seo-ai-search-optimization-agent.md`](agents/seo-ai-search-optimization-agent.md) | Classic SEO and AI-search visibility reviews. |
| Skill | Token-Efficient Response Compression | [`skills/token-efficient-response-compression.md`](skills/token-efficient-response-compression.md) | Compresses verbose output safely. |
| Skill | Context Budgeting and Pruning | [`skills/context-budgeting-and-pruning.md`](skills/context-budgeting-and-pruning.md) | Reduces input/context token usage. |
| Skill | Token Output Budgeting | [`skills/token-output-budgeting.md`](skills/token-output-budgeting.md) | Applies verbosity modes and compact response templates. |
| Skill | Prompt and Memory Compression | [`skills/prompt-and-memory-compression.md`](skills/prompt-and-memory-compression.md) | Compresses reusable prompt/memory files. |
| Skill | Token Efficiency Measurement | [`skills/token-efficiency-measurement.md`](skills/token-efficiency-measurement.md) | Measures savings and quality regressions. |
| Prompt | Common Task Token Efficiency Benchmark | [`prompts/token-efficiency/common-task-benchmark.md`](prompts/token-efficiency/common-task-benchmark.md) | Benchmarks baseline vs candidate prompts. |
| Prompt | Token Efficiency Agent Retrofit | [`prompts/token-efficiency/agent-retrofit.md`](prompts/token-efficiency/agent-retrofit.md) | Adds token-efficiency behavior to existing agents. |
| Prompt | Compress Memory or Instruction File | [`prompts/token-efficiency/compress-memory-file.md`](prompts/token-efficiency/compress-memory-file.md) | Compresses recurring instruction files. |
| Prompt | Compare Models for Token Efficiency | [`prompts/token-efficiency/compare-models.md`](prompts/token-efficiency/compare-models.md) | Tests prompt behavior across models. |
| Guide | Tool Integration Guide | [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) | Explains usage by tool and wrapper type. |

## Usage

Copy the relevant agent, skill, prompt, or instruction into your target tool.

General pattern:

```text
Base / entrypoint:
  AGENTS.md or tool-specific file

Behavior layer:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md

Task:
  <your task>
```

## Recommended Stacks

### Concise General Technical Agent

```text
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Terse Coding Agent

```text
agents/terse-technical-coding-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
```

### Prompt and Memory Compression

```text
skills/prompt-and-memory-compression.md
skills/token-efficiency-measurement.md
prompts/token-efficiency/compress-memory-file.md
prompts/token-efficiency/agent-retrofit.md
```

### Benchmark Token Improvements

```text
skills/token-efficiency-measurement.md
prompts/token-efficiency/common-task-benchmark.md
prompts/token-efficiency/compare-models.md
```

### GitHub Copilot Custom Agents

```text
.github/agents/token-economy-orchestrator.agent.md
.github/agents/terse-technical-coding.agent.md
.github/agents/token-efficiency-benchmark.agent.md
```

After committing these files to the default branch, refresh the Copilot/GitHub agent UI and check whether the descriptions appear.

## Testing the Defaults

This repository is mostly Markdown, so testing means validating three things:

1. Files are present, discoverable, and internally linked.
2. Each agent/skill/prompt has the required structure.
3. The token-efficiency pack reduces tokens without materially reducing answer quality.

### 1. Static Repository Check

From a local clone, run:

```bash
git clone https://github.com/Quazmoz/agentdefaults.git
cd agentdefaults

required_files=(
  "AGENTS.md"
  "CLAUDE.md"
  "GEMINI.md"
  "INDEX.md"
  "README.md"
  ".github/copilot-instructions.md"
  ".github/agents/token-economy-orchestrator.agent.md"
  ".github/agents/terse-technical-coding.agent.md"
  ".github/agents/token-efficiency-benchmark.agent.md"
  ".cursor/rules/agentdefaults.mdc"
  ".windsurfrules"
  "docs/tool-integration-guide.md"
  "agents/token-efficient-response-agent.md"
  "agents/token-economy-orchestrator.md"
  "agents/terse-technical-coding-agent.md"
  "skills/token-efficient-response-compression.md"
  "skills/context-budgeting-and-pruning.md"
  "skills/token-output-budgeting.md"
  "skills/prompt-and-memory-compression.md"
  "skills/token-efficiency-measurement.md"
  "prompts/token-efficiency/common-task-benchmark.md"
  "prompts/token-efficiency/agent-retrofit.md"
  "prompts/token-efficiency/compress-memory-file.md"
  "prompts/token-efficiency/compare-models.md"
)

for file in "${required_files[@]}"; do
  test -f "$file" || { echo "missing: $file"; exit 1; }
done

echo "All required integration and token-efficiency files exist."
```

### 2. Markdown Structure Check

```bash
python3 - <<'PY'
from pathlib import Path

required_sections = ["## Purpose"]
paths = [
    *Path("agents").glob("*.md"),
    *Path("skills").glob("*.md"),
    *Path("prompts/token-efficiency").glob("*.md"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("GEMINI.md"),
    Path(".github/copilot-instructions.md"),
    *Path(".github/agents").glob("*.agent.md"),
    Path("docs/tool-integration-guide.md"),
]
failures = []

for path in paths:
    text = path.read_text(encoding="utf-8")
    missing = [section for section in required_sections if section not in text]
    if missing:
        failures.append(f"{path}: missing {', '.join(missing)}")

if failures:
    print("Structure check failed:")
    print("\n".join(failures))
    raise SystemExit(1)

print(f"Structure check passed for {len(paths)} Markdown defaults and wrappers.")
PY
```

### 3. Link and Path Check

```bash
python3 - <<'PY'
import re
from pathlib import Path

failures = []
for md in Path(".").rglob("*.md"):
    text = md.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        if not any(target.endswith(ext) for ext in [".md", ".mdc", ".agent.md", ".windsurfrules"]):
            continue
        resolved = (md.parent / target).resolve()
        if not resolved.exists():
            failures.append(f"{md}: broken link -> {target}")

if failures:
    print("Broken links:")
    print("\n".join(failures))
    raise SystemExit(1)

print("Markdown link check passed.")
PY
```

### 4. Agent Smoke Test

Paste this into any model or IDE agent after adding the token-efficiency stack:

```text
Use the AgentDefaults token economy stack:
- agents/token-economy-orchestrator.md
- agents/token-efficient-response-agent.md
- skills/context-budgeting-and-pruning.md
- skills/token-output-budgeting.md
- skills/token-efficient-response-compression.md

Task:
Explain why a React component re-renders when a parent passes an inline object prop. Give the cause, fix, and validation check in under 120 words.
```

Expected result:

- Starts with the cause.
- Uses compact technical language.
- Gives a fix such as stable object identity, `useMemo`, or moving the object outside render.
- Includes a validation check.
- Avoids generic React background.

### 5. Token-Efficiency Benchmark

Use [`prompts/token-efficiency/common-task-benchmark.md`](prompts/token-efficiency/common-task-benchmark.md) to compare a baseline agent against a token-efficient candidate.

Minimum process:

```text
1. Run the same task with the baseline prompt.
2. Run the same task with the token-efficiency stack.
3. Count input and output tokens using API usage, model logs, tokenizer output, or approximate chars / 4.
4. Score quality from 1-5 using skills/token-efficiency-measurement.md.
5. Adopt only if output tokens drop and quality stays within the allowed threshold.
```

Suggested pass criteria:

```text
Average output-token reduction: >= 30%
Average net-token reduction:    >= 20% when input/tool tokens are counted
Average quality drop:           <= 0.5 points
Safety/production tasks:        no quality drop allowed
Validation/citations/risks:     preserved when required
```

### 6. Tool Compatibility Test

For each supported tool:

```text
Claude:  confirm CLAUDE.md and AGENTS.md are picked up or manually attached.
Gemini:  confirm GEMINI.md and AGENTS.md are picked up or manually attached.
Copilot: confirm .github/copilot-instructions.md applies and .github/agents/*.agent.md profiles appear.
Cursor:  confirm .cursor/rules/agentdefaults.mdc applies.
Windsurf: confirm .windsurfrules applies.
Generic: paste AGENTS.md + selected stack into the model.
```

Then run the Agent Smoke Test above.

## Token Efficiency Philosophy

- Compress language, not meaning.
- Reduce input/context, tool-result, and output waste.
- Preserve exact technical identifiers and safety rules.
- Benchmark quality separately from token savings.
- Keep prompts usable across hosted frontier models, coding agents, and local LLMs.

## Best Practices

When adding new defaults:

1. Prefer clear instructions over clever wording.
2. State the expected output format.
3. Define the agent's scope and non-goals.
4. Include quality checks.
5. Avoid embedding secrets, private URLs, credentials, or environment-specific values.
6. Keep prompts modular and reusable.
7. Update `README.md`, `INDEX.md`, and `docs/tool-integration-guide.md` when adding a new tool wrapper.
8. For token-efficiency defaults, include measurement guidance.

## Status

Early but usable scaffold for cross-tool agent defaults.

## Contributing

Before adding a new default, ask:

- Is this reusable across more than one project?
- Is the expected output clear?
- Does it define enough context for an agent to perform well?
- Are safety boundaries and destructive-action limits explicit?
- Can another engineer quickly adapt it?
- Can token-efficiency claims be measured or at least estimated honestly?

## License

License to be added.
