# Palmier Pro Transcript Cuts and Captions

## Purpose

Provide a reusable workflow for transcript-driven editing, filler-word removal, retake cleanup, dead-air reduction, and caption creation in Palmier Pro through MCP.

Use this skill when the user wants a talking-head video, tutorial, demo, podcast segment, interview, or screen recording tightened without manually calculating every frame.

## When To Use

Use this skill for:

- removing filler words
- removing false starts
- removing repeated phrases
- removing duplicate takes
- cleaning stumbles
- tightening long pauses
- finding a quote or topic in spoken media
- creating captions
- verifying what remains audible after edits
- converting long-form footage into clean spoken segments

Do not use this skill to delete words that change meaning, remove important caveats, or create misleading speech.

## Inputs Needed

Minimum:

```text
get_timeline
get_transcript
```

Optional:

```text
inspect_media with wordTimestamps=true
search_media with scope=spoken
inspect_timeline for caption placement
```

## Core Distinction

Palmier has two transcript surfaces:

| Surface | Use |
|---|---|
| `inspect_media` | Understand one source asset in source seconds. Useful before placement or for media-library analysis. |
| `get_transcript` | Understand the current edited timeline in project frames. Required for timeline speech cleanup. |

For timeline cleanup, default to `get_transcript`.

## Safe Transcript Workflow

```text
1. call get_timeline
2. call get_transcript
3. read transcript as prose, not just isolated tokens
4. identify obvious removal candidates
5. call remove_words with current indices
6. call get_transcript again before the next remove_words call
7. verify pacing and meaning
```

Important: after `remove_words`, indices shift. Re-read `get_transcript` before another removal.

## What To Remove By Default

When the user asks for a cleanup pass, remove only clearly low-value material:

- ums, uhs, ahs, ers
- duplicated single words
- immediate false starts
- abandoned fragments
- repeated retakes where the later version is clearer
- long dead-air pauses that do not support pacing
- accidental mouth sounds or tiny verbal resets when represented in the transcript

Keep:

- technical caveats
- product names
- model names
- commands
- version numbers
- pricing details
- safety warnings
- jokes or personality beats unless they hurt pacing
- pauses that make a complex point understandable

## Cut Aggressiveness

Use `cutAggressiveness` intentionally:

| Mode | Use |
|---|---|
| `tight` | Shorts, ads, high-energy intros, obvious filler removal. |
| `balanced` | Default for YouTube/tutorial talking-head edits. |
| `loose` | Interviews, demos with complex points, reflective or natural pacing. |

Default to `balanced` unless the user asks for a punchy short-form style.

## Remove Words vs Ripple Ranges

Use `remove_words` for anything word-aligned.

Examples:

```text
remove filler words
cut the repeated intro take
remove the sentence where I restart
trim the verbal stumble before the demo
```

Use `ripple_delete_ranges` only for non-word-aligned spans.

Examples:

```text
remove 2 seconds of silence before the screen recording starts
cut the dead air while the page loads
remove a visual-only mistake between two spoken sections
```

## Retake Cleanup

When multiple takes exist:

1. Read the transcript surrounding all takes.
2. Preserve the clearest, most complete take.
3. Remove earlier false starts and repeated attempts.
4. Keep lead-in/out words that make the surviving take sound natural.
5. Re-read `get_transcript` after removal.

Do not remove a retake solely because wording is similar; compare meaning and clarity.

## Dead-Air Cleanup

For speech-adjacent pauses:

- Prefer `remove_words` if the pause belongs to removed filler or a false start.
- Use `ripple_delete_ranges` for actual silent spans.
- Avoid cutting every breath; overly tight tutorial edits can sound unnatural.

For technical demos:

- Keep enough pause for viewers to read code, settings, command output, or UI changes.
- Remove waiting time where nothing changes visually or verbally.

## Caption Workflow

When the user asks to caption the video:

```text
call add_captions
```

Prefer `add_captions` over manually converting transcript words into text clips.

Set language explicitly when the speech is not the system default language.

Useful defaults:

```text
fontName: Helvetica-Bold
fontSize: 48
centerX: 0.5
centerY: 0.9
textCase: auto
censorProfanity: user preference
```

For short-form social clips, consider larger captions and higher placement if platform UI would cover the bottom.

## Manual Text vs Captions

Use `add_texts` instead of `add_captions` for:

- title cards
- hooks
- lower thirds
- section labels
- manual emphasis words
- non-speech text
- app/repo/product labels
- CTAs

Do not use generated video models to render captions or title cards. Add text in the editor.

## Verification

After transcript cleanup:

```text
call get_transcript
```

Check:

- no obvious dangling fragments remain
- meaning is preserved
- technical claims still include their caveats
- cuts do not remove necessary context

After captioning:

```text
call inspect_timeline
```

Check:

- captions are visible
- captions do not collide with lower thirds or app UI
- captions are not too low for platform controls
- text is readable on mobile

## YouTube Technical Video Defaults

For developer/tutorial videos:

- Preserve command syntax exactly.
- Preserve tool names and model names exactly.
- Do not cut caveats like "experimental", "not production-ready", or "driver-dependent".
- Do not remove explanations needed for viewers to reproduce the workflow.
- Tighten rambling setup before the practical demo.
- Add captions when the video includes code, commands, or acronyms that benefit from text reinforcement.

## Expected Output

After a cleanup pass:

```text
Done — removed obvious filler, one repeated take, and the long silence before the demo while preserving the technical caveats.
```

When blocked:

```text
The transcript is not ready for the target clip yet. I can inspect the source media first, then retry transcript cleanup once Palmier has indexed it.
```

## Quality Bar

- Uses `get_transcript` for timeline speech edits.
- Re-reads transcript after each `remove_words` call.
- Preserves meaning, caveats, and technical accuracy.
- Uses `ripple_delete_ranges` only when word removal is not appropriate.
- Uses `add_captions` for automatic captions.
- Verifies caption visibility when placement matters.
