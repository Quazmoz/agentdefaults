# Bounded Completion Pipeline Quickstart

## Purpose

Operate the reusable two-agent VS Code/GitHub Copilot completion pipeline with Qwen3 Coder Next Q6 as Integration Owner and Qwen 3.6 35B Vision as independent adversarial reviewer.

## Prerequisites

- Open the repository root in VS Code.
- Ensure both local models are already available in the VS Code model picker.
- Do not add guessed `model:` frontmatter. This repository has no authoritative qualified identifiers for the user's local model registrations.
- Use Python 3. The repository canonical validation command is `python3 scripts/validate-agentdefaults.py` on macOS/Linux and CI.
- To enable the lead's agent-scoped Stop hook, set `chat.useCustomAgentHooks` to `true`. Agent-scoped hooks are currently Preview; if disabled/unavailable, use the manual gate command.

## Start a New Task

1. Copy `examples/bounded-completion-task.json` or create a contract conforming to `schemas/bounded-completion-task.schema.json`.
2. Fill stable acceptance-criterion IDs, initial `PENDING` status, and real verification argv. Do not invent checks.
3. In VS Code select custom agent `Bounded Completion Lead`.
4. Select `Qwen3 Coder Next Q6` from the model picker.
5. Run `/start-bounded-completion` or paste the canonical start prompt.
6. The lead initializes state with:

```bash
python3 scripts/bounded-completion.py init --contract <contract.json>
```

7. Before major implementation, obtain the reviewer plan challenge. Native subagent invocation is supported by the lead adapter, but may inherit the lead model because no exact reviewer model ID is committed.
8. For a review that must count as distinct-model evidence, use the `Review with Qwen Vision` handoff, select `Qwen 3.6 35B Vision`, and only record distinct-model confirmation when the operator or runtime actually confirms it.

## Runtime Files

The control plane keeps conversationally durable but Git-ignored evidence under:

```text
.agent-loop/current/task-contract.json
.agent-loop/current/state.json
.agent-loop/current/findings.json
.agent-loop/logs/
.agent-loop/archive/
```

Do not commit secrets in the task contract, findings, logs, or visual artifacts. Verification logs preserve command output, so canonical and required checks must not intentionally print credentials or unrelated secret-store contents.

## Normal Loop

Use these commands from the repository root as evidence is produced:

```bash
python3 scripts/bounded-completion.py advance --description "implemented coherent slice"
python3 scripts/bounded-completion.py verify
python3 scripts/bounded-completion.py criterion --id AC-1 --status SATISFIED --evidence "<evidence>"
python3 scripts/bounded-completion.py record-diff --summary "<current diff inspection>"
python3 scripts/bounded-completion.py record-integrity --summary "<audit>" \
  --no-unrelated-destructive-change \
  --no-validation-weakening \
  --no-unjustified-test-disabling \
  --no-placeholder-implementation
python3 scripts/bounded-completion.py gate
```

Use `record-review`, `add-finding`, `dispose-finding`, `resolve-finding`, and `record-visual` for reviewer evidence. Required approvals are recorded only with trusted provenance, for example:

```bash
python3 scripts/bounded-completion.py approve \
  --name production-change \
  --source operator-confirmed \
  --evidence "User explicitly approved this named operation"
```

An agent statement is not approval. `subagent_timeout_seconds` is an orchestration ceiling: if the current VS Code subagent runtime does not expose an enforceable per-subagent timeout, the lead must use a bounded manual handoff or escalate rather than claim the timeout was enforced. Run `python3 scripts/bounded-completion.py --help` for exact arguments.

## Visual Tasks

A required visual criterion is blocked unless a real artifact exists inside the workspace and is recorded after actual inspection:

```bash
python3 scripts/bounded-completion.py record-visual \
  --criterion AC-UI-1 \
  --artifact artifacts/screenshot.png \
  --inspected-by "Qwen 3.6 35B Vision" \
  --review "No clipping at required viewport"
```

Changing the workspace after the screenshot makes that review stale, forcing regeneration/review.

## Stop Hook

The lead adapter uses a scoped `Stop` hook. The hook checks the deterministic completion gate and emits only valid JSON on stdout. It checks `stop_hook_active`; it can block at most the configured number of continuations and then records `ESCALATED` rather than recursively continuing.

Windows uses the hook's `py -3` override; macOS/Linux use `python3`. If Python is unavailable, the hook cannot prove completion and the operator must use the manual gate once the supported runtime is installed/configured.

## Resume

Select the lead agent with Qwen3 Coder Next Q6 and run `/resume-bounded-completion`. Do not reinitialize state.

## Safe New-Task Reset

Use:

```bash
python3 scripts/bounded-completion.py init --contract <new-contract.json> --replace-active
```

This archives current state rather than deleting it.

## Escalation Format

An escalation reports:

1. current task status;
2. exact incomplete criteria;
3. active blockers;
4. verification failures and logs;
5. attempted actions;
6. why more autonomous attempts are not justified;
7. smallest required user decision/input;
8. safe options;
9. whether state can resume without reset.

## Canonical Start Prompt

```text
Start a new bounded completion loop for the active task contract. Initialize or safely reset current loop state while preserving prior task history. Map each acceptance criterion to concrete evidence. Ask the Bounded Completion Reviewer to challenge the plan before major implementation begins. Act as Integration Owner. Implement in coherent increments, run deterministic canonical verification, request independent review, disposition every finding, and resolve all blocking findings. Continue until the objective completion gate passes or a documented escalation condition occurs. Never weaken validation, bypass tests, claim unsupported visual review, or declare completion based only on agent confidence.
```

## Canonical Resume Prompt

```text
Resume the active bounded completion loop. Read the active task contract, durable state, current findings, latest verification log, and current Git diff. Confirm recorded state against repository evidence before continuing. Proceed from the recorded next action. If the same failure repeated without material progress, request an independent diagnosis from the Bounded Completion Reviewer before another similar change. Continue until the completion gate passes or an escalation condition occurs. Do not reset active state or discard unresolved findings.
```
