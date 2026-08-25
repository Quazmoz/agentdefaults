# Bounded Completion Pipeline Implementation Plan

## Purpose

Record the repository-supported implementation plan for a bounded two-agent GitHub Copilot completion pipeline before broad implementation begins.

## Discovery Summary

- Canonical reusable behavior belongs in `agents/`, `skills/`, `prompts/`, and `schemas/`; GitHub Copilot files under `.github/` must remain thin adapters.
- Existing canonical repository verification is `python3 scripts/validate-agentdefaults.py`, run by `.github/workflows/validate.yml` on Python 3.13.
- The repository currently has Copilot custom agents, but no `.github/prompts/`, `.github/hooks/`, or `.vscode/` workspace customization files.
- No repository-accessible Qwen model identifier or provider binding is present. Do not commit guessed `model:` values.
- Current VS Code documentation supports custom-agent `agents` restrictions, the `agent` subagent tool, handoffs, prompt files, and agent-scoped `Stop` hooks. Agent-scoped hooks require `chat.useCustomAgentHooks`.
- Graft instructions exist in `AGENTS.md`, but a committed `graft/INDEX.md` is not available through the repository API, so repository files and current official VS Code documentation are the authoritative evidence for this change.

## Architecture

1. Add canonical lead and reviewer agent definitions plus one orchestration skill.
2. Add a generic JSON task contract, durable state/findings schemas, and one central limits configuration.
3. Add `scripts/bounded-completion.py` as the deterministic control plane for task initialization, verification, state/findings updates, completion gating, archival/reset, and the Stop-hook decision.
4. Store runtime state in ignored `.agent-loop/` state/history/log directories so state survives chat compaction without polluting commits.
5. Add thin Copilot custom-agent and prompt-file adapters. Permit native subagent delegation to the reviewer, but require manual model-picker selection when distinct Qwen-model identity cannot be proven by repository configuration.
6. Add an agent-scoped Stop hook for the lead only, with recursion protection and bounded continuation.
7. Extend the existing canonical AgentDefaults validator with a dedicated bounded-pipeline validator and controlled temporary-fixture tests.
8. Register the stack in the manifest and human indexes without changing unrelated routing.

## Verification Plan

- Validate JSON schemas/config and Markdown/link structure through the existing suite.
- Validate custom-agent frontmatter terms required by the current VS Code schema.
- Exercise task initialization and archive behavior in temporary fixtures.
- Exercise passing and failing verification, required-check failure, stale-verification detection, unresolved high/critical finding blocking, missing visual evidence blocking, stale final-review blocking, completion success, Stop-hook JSON validity, Stop-hook recursion guard, iteration escalation, and log retention.
- Run `python3 scripts/validate-agentdefaults.py` after the final change.
- Inspect the final commit diff and current `main` status before reporting completion.

## Compatibility Decision

Do not bind `Qwen3 Coder Next Q6` or `Qwen 3.6 35B Vision` in agent frontmatter until VS Code exposes the exact qualified local model identifiers in repository-accessible configuration. The operator selects the intended model from the VS Code model picker. Automatic reviewer subagent invocation remains supported, but its result only counts as distinct-model review when the runtime/model selection is independently confirmed; otherwise use the documented manual reviewer handoff.