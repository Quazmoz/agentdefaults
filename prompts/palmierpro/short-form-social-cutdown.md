# Palmier Pro Short-Form Social Cutdown Prompt

## Purpose

Use this prompt for a short-form cutdown for TikTok, Instagram Reels, LinkedIn, or X from an existing Palmier Pro project. For YouTube Shorts, use [`youtube-short-from-long-form.md`](youtube-short-from-long-form.md), which this prompt follows apart from the platform.

## Prompt

```text
Load the AgentDefaults Palmier Pro MCP stack before acting: the files listed under "Recommended Stack" in
agents/palmierpro-mcp-video-editor-agent.md, plus config/video-editing/channel-style.md.

TASK
Make one short-form cutdown for <platform> from the strongest self-contained proof moment in this project.

Follow prompts/palmierpro/youtube-short-from-long-form.md exactly (protect the long-form edit, the settings scope
check, framing, captions, speech, limits, and final response), with these differences:
- Aspect: the platform's native format (9:16 for TikTok and Reels; 1:1 or 4:5 for LinkedIn and X feed when I ask).
  Run the same scope check before any set_project_settings call.
- Safe zones: use the platform's own UI (TikTok and Reels have a larger bottom caption area and a right action
  rail similar to Shorts). For square and 4:5 feed video, keep 5% margins.
- Duration: 18-35 s, up to 60 s only if the moment truly needs it.
```

## Expected Output

```text
Done. I made a 28-second 9:16 cutdown for Reels on a copy; the long-form timeline is untouched. It's built around the Play Store approval result, with captions in the safe area and one hook text. Seam audit clean. Check the crop around the Play Console status before export.
```

## Quality Bar

Same as the YouTube Short prompt. A replay against `tools/video/palmier_mock/` passes `trace_check.py --profile short`.
