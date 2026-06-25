# Palmier Pro Transcript Cleanup Prompt

## Purpose

Use this prompt to ask an MCP-connected agent to clean spoken content in a Palmier Pro timeline without changing the broader edit structure.

This is best for talking-head videos, tutorials, demos, interviews, podcasts, and voiceover-heavy content.

## Prompt

```text
You are connected to Palmier Pro through MCP. The Palmier project is already open.

Goal: perform a transcript-focused cleanup pass only.

Start by calling get_timeline and get_transcript. Read the transcript as prose before cutting. Use remove_words for word-aligned cuts. Re-read get_transcript after each remove_words call before making another word-level cut.

Remove:
- obvious filler words
- false starts
- repeated single words
- duplicate takes where the later/clearer take survives
- abandoned fragments
- long dead air that hurts pacing

Keep:
- technical caveats
- commands
- repo names
- product names
- model names
- exact numbers, prices, dates, versions, and compatibility notes
- useful pauses where viewers need time to understand a demo
- personality beats that do not hurt clarity

Cut style: balanced unless I explicitly ask for tight shorts-style pacing.

Rules:
- Do not use paid generation/upscale tools.
- Do not add captions or overlays unless I ask.
- Do not reorder clips unless required to close a cleanup gap.
- Do not export.
- If a cut would change meaning, leave it in.

When finished, give a concise summary of what was cleaned and any sections that still need manual review.
```

## Expected Output

```text
Done — cleaned filler, removed two false starts, and kept the technical caveats around setup and compatibility intact.
```

## Quality Bar

- Uses `get_transcript` as the source of truth.
- Does not cut based on summary alone.
- Re-reads transcript after word removals.
- Preserves meaning and technical accuracy.
- Avoids unrelated timeline edits.
