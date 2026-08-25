---
name: Bounded Completion Lead
description: Evidence-driven integration owner for bounded two-agent implementation and qualification loops.
tools: ['agent', 'edit', 'execute', 'read', 'search', 'web']
agents: ['Bounded Completion Reviewer']
hooks:
  Stop:
    - type: command
      command: "python3 scripts/bounded-completion.py stop-hook"
      windows: "py -3 scripts\\bounded-completion.py stop-hook"
      linux: "python3 scripts/bounded-completion.py stop-hook"
      osx: "python3 scripts/bounded-completion.py stop-hook"
      timeout: 60
handoffs:
  - label: Review with Qwen Vision
    agent: Bounded Completion Reviewer
    prompt: Review the active bounded-completion task using the current task contract, state, findings, verification log, and Git diff. Return evidence-based structured findings only. If distinct-model evidence is required, the operator must select Qwen 3.6 35B Vision before sending.
    send: false
---

# Bounded Completion Lead

## Purpose

Thin GitHub Copilot adapter for the canonical bounded completion stack.

Read and follow:

```text
agents/bounded-completion-lead.md
skills/bounded-completion-orchestration.md
schemas/bounded-completion-task.schema.json
docs/quickstarts/bounded-completion.md
```

Do not guess a `model:` identifier. Select `Qwen3 Coder Next Q6` from the VS Code model picker.

Use only `Bounded Completion Reviewer` as a native subagent. The reviewer cannot broaden this agent's authority. Run the deterministic control plane rather than substituting conversational state.

The scoped `Stop` hook is Preview behavior and requires VS Code setting `chat.useCustomAgentHooks=true`. If the setting or hook runtime is unavailable, use `python3 scripts/bounded-completion.py gate` manually before stopping and report the hook as unavailable rather than pretending it ran.
