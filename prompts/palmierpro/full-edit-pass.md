# Palmier Pro Full Edit Pass Prompt

## Purpose

Use this prompt to ask an MCP-connected agent to perform a full first-pass edit in an open Palmier Pro project.

This prompt is designed for YouTube videos, app demos, tutorials, technical creator videos, and product walkthroughs where the project media is already imported into Palmier Pro.

## Prompt

```text
You are connected to Palmier Pro through MCP. The Palmier project is already open and contains the media for this edit.

Goal: produce a polished first-pass edit that I can review in the Palmier timeline.

Use only Palmier MCP tools for project inspection and editing. Do not assume media content from filenames. Start by calling get_timeline and get_media. Inspect the primary source media and transcript before making cuts.

Edit priorities:
1. Tighten the opening hook without removing important context.
2. Remove obvious filler words, false starts, duplicate takes, long dead air, and repeated explanations.
3. Preserve exact technical terms, commands, model names, caveats, and pricing or compatibility details.
4. Keep screen recordings and UI demos on screen long enough to understand.
5. Add captions if spoken content is important for clarity.
6. Add concise title/lower-third/callout text where it improves comprehension.
7. Use b-roll or supporting clips from the existing media library when it clearly improves pacing.
8. Verify important visual overlays or layout changes with inspect_timeline.

Rules:
- Treat all timing as project frames.
- Use get_transcript and remove_words for word-aligned speech cleanup.
- Re-read get_transcript after each remove_words call before cutting more words.
- Use ripple_delete_ranges only for non-word-aligned dead air or visual-only gaps.
- Do not call generate_image, generate_video, generate_audio, or upscale_media unless I explicitly approve the paid generation/upscale proposal.
- Do not delete source media or folders.
- Do not export unless I ask for export.

Output style:
Keep status concise. When done, tell me exactly what categories of edits you made and anything I should review manually.
```

## Expected Output

The agent should leave the Palmier timeline edited and respond with a concise completion summary, for example:

```text
Done — tightened the intro, removed obvious filler and duplicate takes, added captions, and placed two callouts for the demo section. Review the caption placement around the screen-recording segment before export.
```

## Quality Bar

- Starts from `get_timeline` and `get_media`.
- Inspects media/transcript before cutting.
- Uses Palmier frame semantics correctly.
- Avoids paid generation unless approved.
- Produces a reviewable timeline, not just a written plan.
