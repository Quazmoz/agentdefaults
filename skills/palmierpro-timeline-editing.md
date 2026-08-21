# Palmier Pro Timeline Editing

## Purpose

Provide reusable, provider-neutral rules for safe timeline-native editing in Palmier Pro through external MCP.

Use this skill for clip placement, trims, cuts, versioning, track/layout changes, linked A/V handling, text overlays, keyframes, sync, review markers, and viewer-facing verification.

For a fast long-form creator workflow, combine with:

```text
skills/palmierpro-youtube-fast-edit.md
```

For spoken cleanup, combine with:

```text
skills/palmierpro-transcript-cuts-and-captions.md
```

## Runtime Truth

Use Palmier's live MCP schema for exact arguments and enum values.

Do not assume a tool is available because it appears in an old example. Do not invent compatibility aliases when the schema changes.

## Inputs Needed

Start with:

```text
get_timeline
get_media
```

Use returned exact IDs for all mutations.

For visual understanding:

```text
inspect_media
search_media
inspect_timeline
```

For spoken content:

```text
get_transcript
```

## Versioning Before Broad Edits

Palmier timelines are the preferred versioning primitive for broad edits.

For a first-pass rewrite, alternate cut, or aspect-ratio derivative:

```text
create_timeline from=<active timelineId> name=<clear variant name>
get_timeline
```

The copy receives new clip/track IDs. Never keep using IDs from the source timeline after duplication.

For a tiny targeted edit, mutate in place unless the user requested a version copy or the risk justifies one.

## Timeline Model

Palmier timeline operations use project frames.

```text
frame = seconds * fps
seconds = frame / fps
```

Treat exact range semantics as defined by the live tool schema. Current timeline state commonly uses half-open ranges:

```text
[start, end)
```

Key concepts:

- timeline start/end/duration are project-frame values
- source trims are source-media offsets expressed according to Palmier's current schema
- track IDs are stable selectors when supported; indexes reflect current order
- video/audio tracks occupy separate zones
- linked A/V should remain linked unless independent treatment is intentional

## Tool Selection

### Project / Timeline

| Intent | Tool |
|---|---|
| Read current timeline | `get_timeline` |
| Inspect composited viewer output | `inspect_timeline` |
| Create/copy a timeline | `create_timeline` |
| Switch active timeline | `set_active_timeline` |
| Change fps/aspect/resolution | `set_project_settings` |
| Add/update review notes | `manage_markers` |

### Tracks / Clips

| Intent | Tool |
|---|---|
| Add existing media | `add_clips` |
| Insert and ripple existing content | `insert_clips` |
| Move clips | `move_clips` |
| Remove timeline clips | `remove_clips` |
| Split clips | `split_clips` |
| Delete known ranges and ripple | `ripple_delete_ranges` |
| Trim/speed/volume/opacity/transform | `set_clip_properties` |
| Arrange multi-clip layouts | `apply_layout` |
| Animate supported properties | `set_keyframes` |
| Configure/reorder tracks | `manage_tracks` |
| Link/unlink A/V deliberately | `manage_clip_links` |
| Reuse clip settings | `copy_clip_settings` when exposed |
| Replace a clip's source while preserving edit intent | `swap_clip_media` when exposed |
| Sync by waveform | `sync_clips` |
| Revert latest known action | `undo` |

Prefer the highest-level purpose-built tool that exactly represents the intent.

## Add vs Insert

Use `add_clips` when:

- placing media in clear space
- deliberate replacement/overlap behavior is intended
- the live tool semantics match the desired edit

Use `insert_clips` when:

- existing content must shift to make room
- overwriting the landing range would be wrong

Before either:

1. call/refresh `get_media`
2. confirm asset readiness
3. confirm media/track compatibility
4. calculate required project-frame placement
5. choose add vs insert intentionally

## Move / Reorder

Use `move_clips` for direct repositioning.

Do not split/remove/re-add just to move a clip.

After major track reordering, refresh state if subsequent operations depend on indexes.

## Link Discipline

Current Palmier can expose linked A/V groups.

Rules:

- preserve links for ordinary cuts and moves
- do not assume an audio partner is independent merely because it appears nested/folded in returned state
- use `manage_clip_links` before a true J-cut/L-cut or another edit that requires independent A/V treatment
- relink when the clips should move as one unit again

Never solve sync problems by casually unlinking media.

## Trim / Split / Ripple

Use `set_clip_properties` for simple trims/property changes when supported.

Use `split_clips` when independent treatment of the resulting sections is actually needed.

Use transcript-aware tools for speech cuts.

Use `ripple_delete_ranges` for specific non-word-aligned spans such as:

- visual-only pre-roll
- loading/waiting time with no useful speech
- a known gap between sections
- a visual mistake not aligned to transcript words

Use `remove_silence` for bulk quiet/speech-free cleanup rather than manually manufacturing many silence ranges.

## Recording Pre-Roll

Do not apply a fixed trim to all recordings.

For each source that may begin on OBS/QuickTime/capture software:

1. inspect the source start
2. locate the real intended visual/speech boundary
3. remove only verified pre-roll

If speech is part of the unwanted range, use transcript-aware cutting when possible.

## Layouts

Use `apply_layout` for:

- facecam + screenshare
- side-by-side comparison
- stacked media
- picture-in-picture

Then use property/keyframe tools only for necessary fine-tuning.

Technical creator default:

- screen/code/app UI dominates during explanation
- facecam does not block important interface areas
- avoid constant visual motion

Always verify important layouts with `inspect_timeline`.

## Text Overlays

Use `add_texts` for:

- titles
- section headers
- lower thirds
- app/repo/model names
- concise commands
- callouts
- CTAs when source/user intent supports them

Use `update_text` for existing text/caption style or content changes when supported.

Do not assume text styling is limited to plain color/font. Check the live schema. Current Palmier versions can expose richer style fields such as outline, shadow, and background; use them directly when supported instead of fake duplicate-text shadows.

Keep overlay copy short and mobile-readable.

## Captions

Do not add automatic captions merely because a transcript exists.

- Long-form 16:9: no burned captions by default.
- Short-form/vertical: captions are often appropriate when requested or part of the chosen format.
- Explicit user caption request overrides these defaults.

Verify caption placement with `inspect_timeline` when important UI or platform controls may collide.

## Transitions

Clean cuts are the default for technical YouTube.

Use fades/dips only at meaningful section boundaries or when requested.

If no dedicated transition tool is exposed, use supported keyframed opacity/overlap techniques and verify the actual composited result.

Do not add a transition to every cut.

## Color, Effects, Audio

Use:

- `inspect_color` before meaningful correction/grade
- `apply_color` only when the visual problem or requested look justifies it
- `apply_effect` sparingly
- `denoise_audio` only when noise is actually present or explicitly requested

Do not make broad aesthetic changes in a fast editing pass without evidence they improve the result.

## Sync / Multicam

Use `sync_clips` when clips share waveform content and need alignment.

For true multicam, use the dedicated multicam tool set exposed by the live schema.

If sync confidence is weak or returned alignment is ambiguous, report/mark the problem rather than forcing an edit.

## Review Markers

Use `manage_markers` to persist unresolved or ready-for-review edit notes in the timeline.

Good marker cases:

- subjective take choice
- uncertain factual removal
- visual needing user brand preference
- sponsor/legal-sensitive section
- missing asset

Status discipline:

```text
open     -> unresolved
review   -> edit applied and verified, waiting for user
resolved -> user approved/instructed resolution
```

## Verification

Use `inspect_timeline` after:

- important layout/PIP changes
- title/lower-third/callout placement
- transitions/keyframes
- crop/scale/position changes
- color/effect changes
- complex layering

Use `get_transcript` after transcript edits.

Use `get_timeline` after:

- timeline copy/switch
- undo
- stale ID/frame error
- manual user change
- any operation documented to invalidate IDs

## Undo

`undo` reverses the latest shared editor action, which may have been made by the user.

Call it only when the latest action is known to be the one that should be reverted.

Refresh state after undo before more mutation.

## First-Cut Workflow

```text
1. get_timeline + get_media
2. duplicate timeline for a broad edit
3. re-read timeline state
4. inspect transcript/media efficiently
5. remove verified pre-roll/dead air/retakes
6. structure existing clips around hook -> value -> demo -> proof -> caveats -> close
7. arrange supporting visuals and sparse text
8. inspect key viewer-visible sections
9. mark subjective choices
10. stop for user review
```

## YouTube Technical Defaults

- Hook/proof should arrive quickly when source footage supports it.
- Do not cut technical prerequisites needed for reproducibility.
- Preserve caveats and negative results.
- Leave enough dwell time for code/UI/terminal reading.
- Do not add a long-form caption track by default.
- Use clean cuts more than decorative transitions.
- Do not fabricate a CTA that was never recorded/requested.

## Failure Handling

On mutation failure:

1. read the exact error
2. verify live schema
3. refresh state if IDs/indexes may be stale
4. retry only with an obvious safe correction
5. stop after repeated identical failures

Do not use delays as a correctness mechanism.

## Quality Bar

- Broad edits preserve the original timeline.
- Exact current IDs are used.
- Frame/range semantics follow live schema.
- A/V links and sync are preserved.
- Tool choice matches editing intent.
- Important screen content remains readable.
- Text/caption policy matches the target format.
- Complex viewer-visible edits are verified.
- Subjective uncertainty is marked rather than guessed.
- Execution remains bounded and reviewable.
