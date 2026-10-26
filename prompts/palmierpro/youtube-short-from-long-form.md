# Palmier Pro YouTube Short From Long-Form Prompt

## Purpose

Use this prompt to have a Palmier Pro MCP-connected agent cut one YouTube Short from the long-form content in the open Palmier project, formatted correctly for vertical viewing.

Channel identity, hook style, and Shorts safe zones come from `config/video-editing/channel-style.md`. Safety gates, the dialogue invariant, and transitions come from the canonical Palmier stack. This prompt carries the Shorts-specific deltas.

## Prompt

```text
Load the AgentDefaults Palmier Pro MCP stack before acting: the files listed under "Recommended Stack" in
agents/palmierpro-mcp-video-editor-agent.md, plus config/video-editing/channel-style.md (Channel Profile and
Shorts Safe Zones). Those files are the contract. Where this prompt is silent, they decide.

TASK
Make one high-retention YouTube Short from the strongest self-contained moment in this project.

PROTECT THE LONG-FORM EDIT (do this first)
1. get_timeline and get_media. Note the active timelineId; that is the long-form edit and must not change.
2. create_timeline from=<that timelineId> named "Short - <angle>", then re-read get_timeline (all IDs are new).
3. Vertical format needs 9:16. Run the scope check in skills/palmierpro-mcp-setup-and-safety.md
   (Project Settings Guardrail) before calling set_project_settings:
   - per-timeline settings: change them on the Short copy only
   - project-wide or unclear: do NOT call set_project_settings here. Stop and tell me the Short needs its own
     Palmier project, and offer to create it with manage_project and import the same source media.

TARGET
- 9:16, 1080x1920 where supported. Ideally 18-35 s; never over 60 s unless I ask.
- Hook in the first 1-2 s, proof quickly, then a clean loop or an ending on the result or lesson.
- One idea, one proof point, one payoff. Pick the moment from the channel's "proof moments".
- If no strong Short exists, return the best candidate and say why it is weak instead of forcing a misleading clip.

FRAMING
- The screenshare, demo, code, or app carries the proof, so it is the primary visual. Reframe it with
  set_clip_properties (crop, scale, position) and set_keyframes so the active UI is readable on a phone; never
  squeeze a full 16:9 screen into 9:16.
- Use apply_layout for facecam plus screenshare. Keep facecam small (picture-in-picture beats a 50/50 split for
  code), eyes and mouth in frame, and inside the safe area.
- If captions sit in the lower third, put facecam in an upper corner. For dense screens, stack: screenshare as the
  large panel, facecam smaller above or below.
- Never cover platform status text, repo names, terminal commands, error messages, app controls, or the cursor.

CAPTIONS AND TEXT
- Burned-in captions with add_captions. Short lines, high contrast, inside the Shorts Safe Zones.
- At most one hook text in the first 1-2 s, in the channel's hook style and only if the footage supports it.
- No official logos unless they are already visible in the footage. Keep any caveat that keeps the Short accurate.

SPEECH
- Tight cut aggressiveness is fine for pauses, but the cut handles in
  skills/palmierpro-transcript-cuts-and-captions.md still apply. Short-form is where clipped words happen most.
- Run the Seam Audit on the Short; fix ERROR seams before reporting.
- Transitions: no head fade (the hook hits on frame 1); a tail fade only if the Short does not loop.

LIMITS
No paid generation, no source deletion, no user export. The FCPXML seam-QC file is allowed.
Verify layout, captions, facecam, and key UI with inspect_timeline at the hook, the proof, and the last frame.

FINAL RESPONSE
- Short angle, duration, and source moment used
- layout chosen and where captions and facecam sit relative to the safe area
- what was cut, and the seam audit result
- what I should review before export
```

## Expected Output

```text
Done. I made a 27-second Short on a copy ("Short - agent edits the timeline"); the long-form timeline is untouched. Palmier's aspect setting is per-timeline here, so only the copy is 9:16. The screenshare is the main visual, facecam is a small upper-right PIP, and captions sit at y≈1300, clear of the bottom UI and the action rail. Seam audit: 6 seams, 0 errors, 1 marked for a listen at 0:14. Check the crop around the timeline panel before export.
```

## Quality Bar

- The long-form timeline is never mutated, and project-wide settings are never changed in a shared project.
- One coherent standalone moment, readable on a phone, captions and facecam inside the safe zones.
- Seams audited, caveats kept, no unapproved generation or export.
- A replay against `tools/video/palmier_mock/` passes `trace_check.py --profile short`.
