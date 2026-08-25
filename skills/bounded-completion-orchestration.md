# Bounded Completion Orchestration

## Purpose

Define the reusable evidence, state, delegation, recovery, and termination contract for the two-agent bounded completion pipeline.

## Trigger Conditions

Use when a repository task requires iterative implementation plus independent review and objective completion evidence. Do not use for simple deterministic edits where a normal single-agent workflow is sufficient.

## Authoritative State

Conversation memory is not authoritative. The active task contract, state, findings, verification logs, and artifact evidence live under `.agent-loop/` and are managed by `scripts/bounded-completion.py`.

The repository itself remains authoritative for code/configuration. The control plane stores evidence about that state and fingerprints it so stale verification/review cannot satisfy the gate after later changes.

## Workflow

1. Initialize or archive/reset active state.
2. Map stable acceptance-criterion IDs to expected evidence.
3. Obtain one independent plan challenge.
4. Implement coherent increments under one Integration Owner.
5. Advance loop counters only for genuine implementation/review cycles.
6. Run deterministic verification and persist full logs.
7. On repeated identical failures, require an independent diagnosis before repeating the same strategy.
8. Record structured findings and explicit dispositions.
9. Resolve accepted blocking findings with evidence.
10. Inspect actual visual artifacts for visual criteria.
11. Inspect the final diff and validation integrity.
12. Run verification after the last implementation change.
13. Obtain final independent review against the same current workspace fingerprint.
14. Evaluate the deterministic completion gate.
15. End only as `COMPLETE` or `ESCALATED`; otherwise continue while limits permit.

## Evidence Rules

Deterministic evidence outranks model confidence. Passing tests do not automatically satisfy every criterion. Reviewer agreement does not prove completion. Visual source inspection does not prove rendered appearance.

Freshness is enforced with a workspace fingerprint derived from Git `HEAD` plus changed/untracked workspace content while excluding `.agent-loop/`. A code/config/artifact change invalidates stale verification, final-review, final-diff, integrity, and visual-review evidence.

## Finding Rules

Each finding has stable identity, severity, blocking status, acceptance criterion, location, evidence/procedure, expected/actual behavior, correction, owner, hypothesis flag, observed/resolved iterations, disposition, and resolution evidence.

Allowed dispositions:

```text
accepted-blocking
accepted-non-blocking
rejected-with-evidence
duplicate-resolved
requires-user-input
deferred-out-of-scope
```

A resolved accepted blocker retains its accepted-blocking disposition plus resolution evidence; it is not relabeled as a duplicate merely to unblock completion.

## Delegation Rules

Native VS Code subagent delegation is allowed only to the `Bounded Completion Reviewer`. The lead remains Integration Owner. Because no exact qualified local model IDs are repository-discoverable, automatic delegation may inherit the lead model. A review counts as distinct-model evidence only when the model identity is independently confirmed by the operator or runtime.

## Bounded Recovery

Limits are centralized in `config/bounded-completion.json`; task overrides may only tighten them. Stop-hook continuation is also bounded and checks `stop_hook_active` before blocking another stop.

When a repeated failure reaches the diagnostic threshold, stop repeating the same strategy, obtain an independent diagnosis, create a discriminating test/observation, and try a materially different correction. Escalate when ceilings or unavailable required capabilities make further autonomous work unsafe or unproductive.

## Security

The control plane executes configured verification as argv arrays without shell evaluation. It does not install software, deploy, publish, access production, rotate secrets, force-push, or bypass approvals. Required external/production approvals must be declared in the task contract and recorded explicitly before the gate can pass.

## Completion Criteria

Completion requires a valid active contract, satisfied required criteria, fresh passing required verification, no unresolved blocking finding, resolution evidence for accepted blockers, current final diff and integrity inspections, current final review, real visual evidence where required, trusted provenance for all required approvals, and all configured limits respected.
