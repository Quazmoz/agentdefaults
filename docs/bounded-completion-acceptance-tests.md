# Bounded Completion Acceptance Tests

## Purpose

Define the behavioral qualification cases for the bounded two-agent completion pipeline and map them to the executable validator `scripts/validate-bounded-completion.py`.

## Executable Scenarios

The validator uses temporary Git repositories and controlled fixture commands; it never damages user files or contacts production services.

1. Successful evidence set reaches `COMPLETE`.
2. CLI verification exits zero on success and nonzero on failure.
3. Replacing an active task archives prior state before initialization.
4. Manual mutation of the active task contract is detected.
5. Completion is blocked without confirmed distinct reviewer-model evidence.
6. Task-specific iteration settings can tighten but cannot widen repository ceilings.
7. Verification logs are retained only to the configured per-task limit while prior-task log directories remain preserved.
8. Repeated unchanged failures trigger independent-diagnosis state and diagnosis clears that requirement for a materially different attempt.
9. Verification, final review, diff inspection, and integrity evidence become stale after workspace changes.
10. The Stop hook emits valid JSON, blocks at most the configured continuation count, detects `stop_hook_active`, and escalates instead of recursively looping.
11. A required unavailable verification command causes `ESCALATED` rather than being treated as skipped/passed.
12. An unresolved critical blocker prevents completion; resolving an accepted blocker preserves its `accepted-blocking` disposition plus resolution evidence.
13. A required visual criterion cannot complete without an actual artifact inspection record.
14. Visual evidence becomes stale if the workspace changes after the artifact review.
15. Required approvals cannot be self-asserted by an agent; each recorded approval requires `operator-confirmed` or trusted `runtime-policy` provenance plus concrete evidence.

## Manual VS Code Checks

Because the repository cannot execute the user's local VS Code model picker in CI, the operator should also verify:

- `Bounded Completion Lead` and `Bounded Completion Reviewer` appear in the custom-agent picker.
- `/start-bounded-completion`, `/resume-bounded-completion`, and `/review-bounded-completion` appear for local VS Code extension-host agents.
- `chat.useCustomAgentHooks=true` enables the lead's scoped Stop hook.
- The lead can invoke only `Bounded Completion Reviewer` as a subagent.
- Selecting `Qwen3 Coder Next Q6` for the lead and `Qwen 3.6 35B Vision` for the manual reviewer handoff works with the user's installed local-model registrations.
- No review is recorded as distinct-model evidence solely because an agent says it used a different model.

These runtime-specific checks remain unverified until performed in the actual local VS Code environment.
