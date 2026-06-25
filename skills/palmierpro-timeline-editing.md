# Palmier Pro Timeline Editing

## Purpose

Provide reusable rules for timeline-native editing in Palmier Pro through MCP.

Use this skill to make safe, coherent, frame-accurate edits: placing clips, trimming, splitting, rippling, layering overlays, syncing audio, applying properties, and verifying the visible result.

## When To Use

Use this skill when the user asks to:

- Build a first cut.
- Tighten a demo or tutorial.
- Add or reorder b-roll.
- Move clips between tracks.
- Trim beginnings/endings.
- Split clips at specific moments.
- Add overlays, lower thirds, title cards, or callouts.
- Sync external audio or multicam clips.
- Adjust opacity, volume, scale, position, crop, rotation, fades, or keyframes.

For spoken-word cleanup, combine with `skills/palmierpro-transcript-cuts-and-captions.md`.

## Inputs Needed

Minimum state:

```text
get_timeline -> fps, totalFrames, tracks, clips, canGenerate
get_media -> mediaRef, media type, generation/import status
```

For visual verification:

```text
inspect_timeline -> composited project preview frames
```

For source understanding:

```text
inspect_media -> source frames/transcript
search_media -> source moments by visual/spoken content
```

## Timeline Model

Palmier timeline operations use project frames.

```text
frame = seconds * fps
seconds = frame / fps
```

Definitions:

- `startFrame`: project/timeline frame where a clip begins.
- `durationFrames`: project/timeline length of a clip.
- `trimStartFrame`: source-media offset skipped from the start.
- `trimEndFrame`: source-media offset removed from the end.
- `speed`: `1.0` normal, `<1.0` longer/slower, `>1.0` shorter/faster.
- `trackIndex`: 0-based order from `get_timeline`.

Rules:

- Video, image, text, captions, and overlays belong on video tracks.
- Audio belongs on audio tracks.
- Track order controls visual layering.
- On the same track, clips are sequential; overlapping placements overwrite/trim/split existing material.
- Linked A/V clips should remain aligned unless the user explicitly wants detachment or offset.

## Editing Decision Tree

### Add Existing Media

Use `add_clips` when:

- Placing footage into empty space.
- Deliberately replacing material in the landing range.
- Auto-creating tracks is acceptable.

Use `insert_clips` when:

- The edit should open a gap.
- Existing clips must shift right.
- No existing content should be overwritten.

Before adding:

```text
1. call get_media
2. ensure the asset is ready
3. ensure asset type matches target track
4. calculate frame position and duration
5. choose add_clips or insert_clips
```

### Move or Reorder Clips

Use `move_clips` for:

- Repositioning clips.
- Moving a clip to another compatible track.
- Reordering sequence blocks.

Avoid manual split/remove/re-add loops when a move tool expresses the intent.

### Trim or Adjust Clip Properties

Use `set_clip_properties` for:

- `durationFrames`
- `trimStartFrame`
- `trimEndFrame`
- `speed`
- `volume`
- `opacity`
- `transform`
- text-style fields

Use separate calls when different clips need different property values.

### Split a Clip

Use `split_clip` only when:

- `atFrame` is strictly inside the clip's visible timeline range.
- A split is necessary for independent movement, styling, or removal.

Prefer higher-level tools when available:

- `remove_words` for transcript-aligned cuts.
- `ripple_delete_ranges` for range cuts with gap closure.
- `set_clip_properties` for simple trims.

### Ripple Delete

Use `ripple_delete_ranges` for:

- removing non-word-aligned spans
- visual dead air
- pauses without speech
- mistakes that span multiple clips on one track

Prefer batching all ranges in one call when the ranges are known.

### Sync Audio

Use `sync_audio` when:

- camera audio and external audio need alignment
- multicam clips share waveform content
- the user says audio is out of sync

Workflow:

```text
1. identify the reference clip that should stay fixed
2. identify target clip(s) to move
3. call sync_audio
4. verify confidence and timeline alignment
```

If confidence is weak, report it and avoid forcing the sync.

## Overlay Rules

Use `add_texts` for:

- large title text
- section headers
- lower thirds
- feature labels
- arrows/callouts when represented as text
- manual caption snippets

Use one overlay track per simultaneous text layer. If two text clips overlap on the same track, they can overwrite/trim each other.

Recommended normalized placement:

```text
center title:       centerX=0.5 centerY=0.5
upper label:        centerX=0.5 centerY=0.14
lower third:        centerX=0.5 centerY=0.82
caption-like text:  centerX=0.5 centerY=0.9
left callout:       centerX=0.24 centerY=0.5
right callout:      centerX=0.76 centerY=0.5
```

Keep overlays short and verify important overlays with `inspect_timeline`.

## Color, Effects, and Keyframes

Use `inspect_color` when evaluating current color state before applying corrections.

Use `apply_color` for broad correction or look adjustments only after inspecting or understanding the footage.

Use `apply_effect` for deliberate effects, not as a default polish step.

Use `set_keyframes` for:

- opacity fades
- scale/position motion
- picture-in-picture movement
- volume automation
- crop/rotation changes

Rules:

- Keyframe frames are clip-relative.
- Setting a scalar property such as volume/opacity through `set_clip_properties` can clear existing keyframes for that property.
- Do not add motion unless it improves clarity or pacing.

## Verification

Use `inspect_timeline` after:

- important overlays
- picture-in-picture placement
- scale/position/crop adjustments
- complex layering
- title cards
- color/effect changes
- transitions or fast sequences

Use `get_transcript` after transcript edits.

Use `get_timeline` after:

- undo
- edit failure
- suspected manual user changes
- stale ID/frame errors

## First-Cut Workflow

```text
1. get_timeline + get_media
2. inspect primary footage or get_transcript
3. identify intro, body, demo, proof, CTA, and dead areas
4. remove obvious bad takes/dead air
5. add or insert supporting clips/b-roll
6. add titles/lower thirds/callouts
7. add captions if requested or likely needed
8. inspect_timeline key moments
9. report concise completion
```

## YouTube/Tutorial Defaults

For a technical creator video:

- Keep the first 5-15 seconds tight.
- Remove long setup rambling before the hook.
- Preserve exact technical terms, model names, commands, and caveats.
- Keep screen recordings visible long enough to understand.
- Use callouts for important commands, repo names, or results.
- Avoid over-cutting sections where the viewer needs context.
- End with a clear CTA only if the source includes one or the user asks for it.

## Expected Output

After edits:

```text
Done — built a tighter first cut, added the product-name lower third, synced the external audio, and verified the title frame.
```

If blocked:

```text
I found the clip, but the target range overlaps an audio-only track. I need to place the visual on a video track or use insert_clips to ripple the existing edit.
```

## Quality Bar

- All timing is frame-correct.
- Track types are respected.
- Existing clips are not overwritten accidentally.
- Linked A/V remains aligned.
- Overlays are readable and placed intentionally.
- Complex visible edits are verified with `inspect_timeline`.
- Final status is concise and outcome-focused.
