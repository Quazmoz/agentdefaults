# Palmier Pro Full Edit Pass Prompt

## Purpose

Use this prompt for a deeper first-pass edit of a technical YouTube video in an existing Palmier Pro project. It spends more effort on story structure and supporting visuals than `quick-youtube-edit.md`, under the same contract.

This prompt carries only the task and its deltas. Safety gates, the dialogue invariant, transitions, and verification live in the canonical stack.

## Prompt

```text
Load the AgentDefaults Palmier Pro MCP stack before acting: the files listed under "Recommended Stack" in
agents/palmierpro-mcp-video-editor-agent.md, plus config/video-editing/channel-style.md. Those files are the
contract. Where this prompt is silent, they decide.

TASK
Make a polished, reviewable first-pass long-form YouTube edit of the open Palmier project, on a copy of the
active timeline named "YouTube Full Cut".

BEYOND THE QUICK EDIT
- Story: rebuild toward the story defaults in the agent (proof/hook → why it matters → minimum setup →
  build/demo → result → caveats → natural close). Bring an existing proof moment forward when it materially
  improves the hook and continuity stays truthful.
- Visuals: make screenshare primary during explanation, use apply_layout for facecam/screenshare, and add a few
  restrained titles, lower thirds, or callouts where they aid comprehension. Use existing media as b-roll when it
  clearly helps.
- Cleanup: balanced, as in the quick edit. Run the Seam Audit after cleanup.
- Transitions: the canonical default only.
- Captions: none burned in.
- Privacy: if anything personal, secret, or a location I named must not appear, it is a release blocker. Follow
  "Privacy-Critical Editing" in the agent and the Privacy gate in skills/palmierpro-youtube-fast-edit.md.
- No paid generation, no source deletion, no user export. The FCPXML seam-QC file is allowed.
- Budget: one full edit pass and one targeted verification/fix pass, then stop.

<optional: target length, audience, sections that must stay, sponsor or legal sections>

FINAL RESPONSE (concise)
- story angle and the categories of edits made
- seam audit result (audited / fixed / marked)
- privacy status by category and timeline range, when privacy was required (never the values)
- review markers and manual checks
- promising Shorts moments
- confirm no generation or export ran
```

## Quality Bar

Same as the quick edit, plus a deliberate story structure and readable layouts verified with `inspect_timeline`. A replay against `tools/video/palmier_mock/` passes `trace_check.py --profile full-edit`.
