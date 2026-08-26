# Documentation Guide

## Purpose

Provide a human navigation layer for AgentDefaults documentation so users can find operating instructions without reading every canonical agent, skill, prompt, schema, and validator.

Canonical behavior still lives in the relevant [`../agents/`](../agents/), [`../skills/`](../skills/), [`../prompts/`](../prompts/), schemas, and executable control-plane code. Documentation explains how to use those artifacts; it should not silently fork their semantics.

## Start by Intent

| I need to... | Read |
|---|---|
| Understand agent loops and when to use them | [`loops/README.md`](loops/README.md) |
| Operate Bounded Completion day to day | [`loops/QUICK_REFERENCE.md`](loops/QUICK_REFERENCE.md) |
| Start/resume bounded completion in VS Code/Copilot | [`quickstarts/bounded-completion.md`](quickstarts/bounded-completion.md) |
| Choose a canonical agent | [`../agents/README.md`](../agents/README.md) |
| Understand skill composition | [`../skills/README.md`](../skills/README.md) |
| Find task prompts | [`../prompts/README.md`](../prompts/README.md) |
| Use authenticated Comet browser research safely | [`quickstarts/comet-authenticated-research.md`](quickstarts/comet-authenticated-research.md) |
| Reduce context/tool/output token waste | [`quickstarts/token-economy.md`](quickstarts/token-economy.md) |
| Understand structured contracts/state | [`../schemas/README.md`](../schemas/README.md) |
| Adapt repository examples safely | [`../examples/README.md`](../examples/README.md) |
| Understand bounded-loop defaults | [`../config/README.md`](../config/README.md) |
| Run validators/control-plane commands | [`../scripts/README.md`](../scripts/README.md) |
| Understand Claude project hooks/Graft integration | [`../.claude/README.md`](../.claude/README.md) |
| Understand Copilot prompt adapters | [`../.github/prompts/README.md`](../.github/prompts/README.md) |
| Understand cross-tool integration | [`tool-integration-guide.md`](tool-integration-guide.md) |
| Use AgentDefaults generally | [`user-guide.md`](user-guide.md) |
| Browse featured stacks | [`../INDEX.md`](../INDEX.md) |

## Quickstarts

Quickstarts explain **how to operate a stack**. They are the right starting point when setup, composition, runtime behavior, authority or verification is not obvious.

Current quickstarts include:

- [`quickstarts/agent-builder.md`](quickstarts/agent-builder.md)
- [`quickstarts/bounded-completion.md`](quickstarts/bounded-completion.md)
- [`quickstarts/codebase-maintenance-engineer.md`](quickstarts/codebase-maintenance-engineer.md)
- [`quickstarts/principal-devops-engineer.md`](quickstarts/principal-devops-engineer.md)
- [`quickstarts/principal-ai-engineer.md`](quickstarts/principal-ai-engineer.md)
- [`quickstarts/principal-ai-devops-engineer.md`](quickstarts/principal-ai-devops-engineer.md)
- [`quickstarts/kubernetes-homelab-engineer.md`](quickstarts/kubernetes-homelab-engineer.md)
- [`quickstarts/devsecops-security-engineer.md`](quickstarts/devsecops-security-engineer.md)
- [`quickstarts/devops-documentation-engineer.md`](quickstarts/devops-documentation-engineer.md)
- [`quickstarts/automation-platform-selection.md`](quickstarts/automation-platform-selection.md)
- [`quickstarts/app-market-research.md`](quickstarts/app-market-research.md)
- [`quickstarts/community-app-validation.md`](quickstarts/community-app-validation.md)
- [`quickstarts/comet-authenticated-research.md`](quickstarts/comet-authenticated-research.md)
- [`quickstarts/google-play-growth.md`](quickstarts/google-play-growth.md)
- [`quickstarts/palmierpro-mcp.md`](quickstarts/palmierpro-mcp.md)
- [`quickstarts/token-economy.md`](quickstarts/token-economy.md)
- [`quickstarts/codex.md`](quickstarts/codex.md)
- [`quickstarts/claude.md`](quickstarts/claude.md)
- [`quickstarts/gemini.md`](quickstarts/gemini.md)
- [`quickstarts/editor.md`](quickstarts/editor.md)
- [`quickstarts/cli.md`](quickstarts/cli.md)
- [`quickstarts/repo-assistant.md`](quickstarts/repo-assistant.md)

A quickstart should not duplicate the full canonical profile. If behavior conflicts, inspect the canonical artifact and runtime implementation before editing the quickstart.

## Agent Loops

[`loops/README.md`](loops/README.md) is the complete operator-level guide for repeated agent workflows. [`loops/QUICK_REFERENCE.md`](loops/QUICK_REFERENCE.md) is the compact command/order reference for active Bounded Completion work.

The full guide distinguishes:

- normal single-agent execution;
- iterative agent workflows such as codebase maintenance;
- the formal persisted Bounded Completion loop.

Read the full guide before changing loop semantics, state ownership, Stop-hook behavior, reviewer independence, approval rules, or escalation policy. Use the quick reference for routine start/status/verify/findings/final-gate operation.

## Acceptance Tests

`*-acceptance-tests.md` files describe behavior and adversarial cases expected from complex stacks.

Use them when:

- changing an agent's authority or workflow;
- changing a schema;
- changing a validator/control plane;
- adding retry/recovery behavior;
- changing how wrappers route work;
- fixing a defect that should not regress.

Representative suites include:

- [`agent-builder-acceptance-tests.md`](agent-builder-acceptance-tests.md)
- [`bounded-completion-acceptance-tests.md`](bounded-completion-acceptance-tests.md)
- [`codebase-maintenance-engineer-acceptance-tests.md`](codebase-maintenance-engineer-acceptance-tests.md)
- [`automation-platform-selection-acceptance-tests.md`](automation-platform-selection-acceptance-tests.md)
- [`devsecops-security-engineer-acceptance-tests.md`](devsecops-security-engineer-acceptance-tests.md)
- [`devops-documentation-engineer-acceptance-tests.md`](devops-documentation-engineer-acceptance-tests.md)
- [`kubernetes-homelab-engineer-acceptance-tests.md`](kubernetes-homelab-engineer-acceptance-tests.md)

These documents define intended cases; run the corresponding executable validators/tests when available before claiming verification.

## Patterns

[`patterns/`](patterns/) contains authoring patterns for new reusable artifacts:

- [`patterns/agent.md`](patterns/agent.md)
- [`patterns/skill.md`](patterns/skill.md)
- [`patterns/prompt.md`](patterns/prompt.md)
- [`patterns/default.md`](patterns/default.md)
- [`patterns/benchmark.md`](patterns/benchmark.md)

Use them to keep new defaults consistent without creating boilerplate sections that do not constrain behavior.

## Benchmarks

[`benchmarks/`](benchmarks/) contains repository-internal evidence for token-efficiency work.

Benchmarks should distinguish:

- exact provider token counts vs estimates;
- baseline vs candidate;
- quality preservation vs simple size reduction;
- model/provider/version;
- prompt/config version;
- known limitations.

Do not convert internal smoke-test results into stronger public claims than the evidence supports.

## Tool and Integration Documentation

- [`tool-integration-guide.md`](tool-integration-guide.md): how canonical content maps to Codex, Claude, Copilot, Gemini, Cursor, Windsurf and related runtimes.
- [`../.claude/README.md`](../.claude/README.md): Claude Code project settings plus optional Graft hook/status-line adapter behavior.
- [`../.github/agents/README.md`](../.github/agents/README.md): GitHub Copilot custom-agent adapters versus canonical agents.
- [`../.github/prompts/README.md`](../.github/prompts/README.md): GitHub Copilot prompt adapters versus canonical prompts.
- [`palmierpro-mcp-tool-map.md`](palmierpro-mcp-tool-map.md): Palmier Pro MCP tool/operation mapping.
- [`chatgpt-project-google-play-marketing-instructions.md`](chatgpt-project-google-play-marketing-instructions.md): focused ChatGPT project instructions for Google Play marketing use.

Tool documentation does not grant access merely because a tool is described.

## Examples and Configuration

- [`../examples/README.md`](../examples/README.md) explains how to adapt structured examples without inheriting fake approvals, example verification commands, or environment-specific values.
- [`../config/README.md`](../config/README.md) explains repository-owned Bounded Completion defaults and why model labels/configuration do not create authority or reviewer proof.

## Source-of-Truth Order

When documentation and implementation disagree, investigate rather than blindly choosing the prose.

Use this precedence for repository behavior:

```text
explicit current user/task instruction
        ↓
authoritative target repository/runtime evidence
        ↓
canonical AgentDefaults agent/skill/schema/control-plane contract
        ↓
quickstart/operator documentation
        ↓
examples
        ↓
generic convention/assumption
```

Runtime-specific wrappers may add syntax or integration constraints but should not fork core authority or safety behavior.

## Documentation Quality Rule

Add documentation where it reduces real operator ambiguity.

High-value documentation explains:

- which artifact to select;
- how artifacts compose;
- required setup/preconditions;
- authority and approval boundaries;
- state ownership;
- failure/recovery behavior;
- how to verify completion;
- common misuse and troubleshooting.

Avoid duplicating long canonical instructions across several files; duplicated docs become another source of drift.

## Validation

After documentation changes, run:

```bash
python3 scripts/validate-agentdefaults.py
```

The validator checks local Markdown links among other repository invariants. Report validation as unverified if the command could not actually be executed.
