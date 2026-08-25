# Bounded Completion Review

## Purpose

Run a focused independent adversarial review against the current bounded-completion evidence.

## Prompt

Review the active task contract, `.agent-loop/current/state.json`, `.agent-loop/current/findings.json`, latest verification log, current Git diff/workspace changes, relevant tests, and any required visual artifacts. Challenge assumptions, missing criteria, regressions, error/security boundaries, disabled or weakened validation, placeholders, and incomplete integration. Return stable structured findings using the contract in `agents/bounded-completion-reviewer.md`. Separate evidence-backed defects from hypotheses and blocking issues from suggestions. Do not edit implementation files by default and do not approve visual criteria without inspecting an actual artifact.
