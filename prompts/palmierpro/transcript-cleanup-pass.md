# Palmier Pro Transcript Cleanup Prompt

## Purpose

Use this prompt to ask an MCP-connected agent to clean spoken content in a Palmier Pro timeline without changing the broader edit structure.

This is best for talking-head videos, tutorials, demos, interviews, podcasts, and voiceover-heavy content.

## Prompt

```text
You are connected to Palmier Pro through MCP. The Palmier project is already open.

Goal: perform a transcript-focused cleanup pass only while preserving natural, complete spoken dialogue.

Start by calling get_timeline and get_transcript. Read the transcript as prose before cutting. Use remove_words for word-aligned cuts. Re-read get_transcript after each remove_words call before making another word-level cut.

Important: transcript timestamps are candidate edit locations, not guaranteed acoustic cut points. The actual spoken audio is authoritative for cut boundaries.

Remove:
- obvious filler words
- false starts
- repeated single words
- duplicate takes where the later/clearer take survives
- abandoned fragments
- long dead air that hurts pacing

Keep:
- complete word beginnings/endings and full syllables
- complete sentence/clause meaning
- natural cadence, breaths, and small pauses needed for intelligibility
- technical caveats
- commands
- repo names
- product names
- model names
- exact numbers, prices, dates, versions, and compatibility notes
- useful pauses where viewers need time to understand a demo
- personality beats that do not hurt clarity

Dialogue-boundary rules:
- Never knowingly cut inside a word or syllable.
- Never truncate the initial consonant/phoneme of the first kept word after a cut.
- Never truncate the final consonant/phoneme or natural decay of the last kept word before a cut.
- Never create a grammatically or semantically incomplete sentence unless the next clip deliberately continues that exact thought.
- Do not optimize for minimum silence; for long-form, a small natural pause is better than a clipped phoneme.
- A harmless filler may remain if removing it would create an unnatural or clipped seam.
- After every speech-affecting edit, inspect/listen to the local seam using the actual timeline/source audio as far as the available Palmier/client surface permits. Transcript text alone is not sufficient proof that the seam is clean.
- Check for duplicated syllables/words, overlap, clicks/pops, abrupt room-tone changes, and mechanical pacing.
- If a cut sounds clipped, undo when safe, refresh state, and retry with looser aggressiveness, a smaller target, or recovered source handles.
- Use micro-fades only for clicks/noise-floor discontinuities, never to smear overlapping speech.
- If the connected tool surface cannot reliably validate the acoustic seam, add a review marker/report the exact seam instead of claiming it is verified.

Cut style: balanced unless I explicitly ask for tight shorts-style pacing. Even in tight mode, complete phonemes/words and intelligible sentence meaning are mandatory.

Rules:
- Do not use paid generation/upscale tools.
- Do not add captions or overlays unless I ask.
- Do not reorder clips unless required to close a cleanup gap.
- Do not export.
- If a cut would change meaning, leave it in.

When finished, perform a dialogue-continuity QC pass over every speech seam you created. Confirm there are no known mid-word, mid-syllable, clipped sentence, duplicate-word, overlap, or abrupt cadence problems. If any seam cannot be acoustically verified, flag it explicitly.

Then give a concise summary of what was cleaned and any sections that still need manual review.
```

## Expected Output

```text
Done — cleaned filler and retakes while preserving complete word boundaries, natural cadence, and technical caveats. I left one review marker where the available tool surface could not fully validate the acoustic seam.
```

## Quality Bar

- Uses `get_transcript` as the source of truth for spoken content, but not as the sole authority for acoustic cut boundaries.
- Does not cut based on summary alone.
- Re-reads transcript after word removals.
- Preserves complete phonemes, words, sentence meaning, and natural cadence.
- Preserves meaning and technical accuracy.
- Audits every created dialogue seam where the available tool surface permits.
- Does not claim a seam is acoustically clean based on transcript text alone.
- Avoids unrelated timeline edits.
