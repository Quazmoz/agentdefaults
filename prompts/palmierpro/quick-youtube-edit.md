# Palmier Pro Quick YouTube Edit Prompt

## Purpose

Use this prompt when the media is already in an open Palmier Pro project and the goal is a fast, reviewable first cut for a technical YouTube video. It works from Claude Code, OpenAI Codex, or any MCP client connected to Palmier Pro.

This prompt carries only the task and its deltas from the defaults. Safety gates, the dialogue invariant, the transition default, and verification live in the canonical stack, so this prompt does not restate them. If you paste it into a client that has not loaded the stack, the first line tells the agent to load it.

## Prompt

```text
Load the AgentDefaults Palmier Pro MCP stack before acting: the files listed under "Recommended Stack" in
agents/palmierpro-mcp-video-editor-agent.md, including skills/palmierpro-youtube-fast-edit.md and
config/video-editing/channel-style.md. Those files are the contract. Where this prompt is silent, they decide.

TASK
Make a fast first-pass YouTube edit of the currently open Palmier project, on a copy of the active timeline
named "YouTube Fast Cut". Edit the timeline itself; do not return a written plan instead.

THIS RUN
- Profile: Technical YouTube Fast Edit (long-form 16:9 unless the project clearly says otherwise).
- Cleanup: balanced. Remove verified capture pre-roll, dead air, fillers, false starts, and duplicate takes.
- Transitions: the canonical default (subtle head fade-in and tail fade-out with matching audio fades; clean cuts elsewhere).
- Captions: none burned in.
- Seams: run the Seam Audit after cleanup; fix ERROR seams, mark unresolved WARN seams.
- No paid generation, no source deletion, no user export. The FCPXML seam-QC file is allowed.
- Budget: one broad edit pass and one targeted verification/fix pass, then stop.

<optional: target length, audience, the proof moment that must be in the hook, anything to keep or cut>

FINAL RESPONSE (concise)
- what changed and the resulting story angle
- seam audit: seams audited, errors fixed, markers left (or "not audited" and why)
- head/tail fades applied and inspected
- review markers and anything I should check
- obvious Shorts moments
- confirm no generation or export ran
```

## Minimal Invocation

Once the stack is loaded in the client:

```text
Palmier quick YouTube edit on the open project: safe copy, balanced cleanup, seam audit, default head/tail fades, stop after one fix pass.
```

## Quality Bar

The agent edits a copy of the Palmier timeline, leaves the original intact, passes the seam audit or marks the seams it could not clear, applies only the canonical transitions, and runs no paid generation or user export. A replay of this prompt against `tools/video/palmier_mock/` passes `trace_check.py --profile first-pass`.
