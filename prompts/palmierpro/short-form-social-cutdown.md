# Palmier Pro Short-Form Social Cutdown Prompt

## Purpose

Use this prompt to ask an MCP-connected agent to create a short-form cutdown from an existing Palmier Pro project.

This is best for YouTube Shorts, TikTok, Instagram Reels, LinkedIn short clips, and X video snippets derived from longer technical or creator content.

## Prompt

```text
You are connected to Palmier Pro through MCP. The Palmier project is already open and contains the long-form source media or edited timeline.

Goal: create a short-form social cutdown that is punchy, understandable without much context, and reviewable in the Palmier timeline.

Target format:
- Duration: 30-60 seconds unless the source only supports a shorter strong clip.
- Aspect ratio: preserve the project unless I explicitly ask for vertical reframing.
- Style: high-retention technical creator clip.

Workflow:
1. Call get_timeline and get_media.
2. Use get_transcript and/or search_media to find the strongest self-contained moment.
3. Select a segment with a clear hook, useful proof/demo, and clean ending.
4. Remove filler, dead air, repeated starts, and unnecessary context.
5. Add captions for spoken content.
6. Add short text hooks or callouts only where they improve clarity.
7. Verify key visual/caption placement with inspect_timeline.

Rules:
- Do not fabricate a hook that the source content does not support.
- Do not remove caveats that make the clip misleading.
- Do not use paid generation/upscale tools without explicit approval.
- Do not delete source media.
- Do not export unless I ask.

Suggested caption style:
- readable on mobile
- concise line lengths
- avoid covering app UI, code, terminal output, or important visuals

When done, tell me the selected topic, approximate duration, and what edits were made.
```

## Expected Output

```text
Done — created a 43-second cutdown around the Play Store approval result, tightened the intro, added captions, and placed one hook text overlay.
```

## Quality Bar

- Selects a coherent standalone moment.
- Preserves technical accuracy.
- Keeps the clip tight without making it misleading.
- Adds captions and verifies important visual placement.
- Avoids paid generation unless approved.
