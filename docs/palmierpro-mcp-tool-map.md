# Palmier Pro MCP Tool Map

## Purpose

Provide a compact, current routing map for Palmier Pro's external MCP tools as used by Claude Code, OpenAI Codex, Cursor, or another MCP client.

Use the live MCP schemas as runtime truth. This map is a selection aid, not a substitute for current tool definitions.

## External MCP Boundary

Palmier Pro's external MCP server currently includes the editing tool set plus `manage_project`.

Palmier's in-app agent can expose additional skill-management capabilities. External Claude/Codex workflows must not depend on:

```text
read_skill
manage_skills
```

## Project / Timeline State

| Need | Tool | Notes |
|---|---|---|
| List/open/create/close session project | `manage_project` | External MCP project management. Do not guess among ambiguous projects. |
| Read timeline | `get_timeline` | Call at session start and after state-invalidating operations. |
| Inspect composited viewer output | `inspect_timeline` | Use for actual visible result, not raw source. |
| Create/copy a timeline | `create_timeline` | Preferred versioning primitive for broad edits; re-read state after copy. |
| Switch active timeline | `set_active_timeline` | Re-read timeline after switching. |
| Add/update/delete review marker | `manage_markers` | Use open/review/resolved status deliberately. |
| Change fps/aspect/resolution | `set_project_settings` | Project-level mutation; use intentionally. |
| Export | `export_project` | Queue render/interchange/package. |
| Inspect/cancel export jobs | `manage_exports` | Observe real status; do not infer completion/stall from time alone. |

## Media Library

| Need | Tool | Notes |
|---|---|---|
| List assets/folders/timelines | `get_media` | Source of exact `mediaRef` values/readiness. |
| Inspect source media | `inspect_media` | Raw source frames/transcript; overview is useful for long video. |
| Semantic search across media | `search_media` | Find spoken/visual proof moments without filename guessing. |
| Import media | `import_media` | Prefer approved local/user sources; respect privacy boundary. |
| Capture a frame | `capture_frame` | Use when current schema supports the needed still-frame workflow. |
| Organize/delete media/folders | `organize_media` | Deletion is destructive; confirm exact target first. |

## Tracks / Clips

| Need | Tool | Notes |
|---|---|---|
| Reorder/name/configure tracks | `manage_tracks` | Prefer stable `trackId` when supported. |
| Link/unlink A/V | `manage_clip_links` | Use deliberately for independent audio/video editing. |
| Add existing media | `add_clips` | Same-track overlap semantics may replace/trim content. |
| Insert and ripple | `insert_clips` | Use when existing content must shift rather than be overwritten. |
| Move clips | `move_clips` | Reposition in time/track. |
| Remove timeline clips | `remove_clips` | Safer than deleting source media. |
| Split clips | `split_clips` | Use when resulting sections need independent treatment. |
| Delete/ripple exact ranges | `ripple_delete_ranges` | Non-word-aligned ranges/visual-only gaps. |
| Swap clip source | `swap_clip_media` | Preserve edit intent while replacing underlying source when exposed. |
| Trim/speed/volume/transform | `set_clip_properties` | Use live schema for exact fields. |
| Copy clip settings | `copy_clip_settings` | Reuse styling/settings when exposed. |
| Animate supported properties | `set_keyframes` | Fades/motion/automation; verify visible result. |
| Apply PIP/stacked layout | `apply_layout` | Preferred for facecam + screenshare arrangements. |
| Waveform sync | `sync_clips` | Align related recordings; avoid forcing weak/ambiguous sync. |
| Undo latest shared action | `undo` | Only if latest editor action is known to be the one to revert; refresh state afterward. |

## Multicam

| Need | Tool |
|---|---|
| Create/manage multicam | `manage_multicam` |
| Switch camera/angle | `change_cam` |
| Inspect multicam state | `get_multicam` |

## Transcript / Pacing

| Need | Tool | Notes |
|---|---|---|
| Read edited timeline speech | `get_transcript` | Use segments for comprehension, words for cuts. |
| Cut by word | `remove_words` | Primary text-based editing; re-read transcript after mutation. |
| Remove quiet/speech-free pauses | `remove_silence` | Purpose-built bulk dead-air cleanup. |
| Detect beats | `detect_beats` | Music/rhythm workflows when relevant. |

## Text / Captions

| Need | Tool | Notes |
|---|---|---|
| Add titles/callouts | `add_texts` | Check current style fields; modern schemas may support outline/shadow/background. |
| Update existing text/captions | `update_text` | Content/style updates. |
| Add automatic captions | `add_captions` | Short-form or explicit caption request; not default for long-form 16:9. |

## Color / Effects / Audio

| Need | Tool | Notes |
|---|---|---|
| Inspect color | `inspect_color` | Read before correction/grade. |
| Apply color | `apply_color` | Intentional correction/look only. |
| Apply effect | `apply_effect` | Use sparingly; verify. |
| Denoise audio | `denoise_audio` | Use only when noise is present/requested. |

## Generation / Upscaling

| Need | Tool | Notes |
|---|---|---|
| List current model capabilities | `list_models` | Required before generation/upscale proposal. |
| Generate video | `generate_video` | Paid/credit action; explicit approval required. |
| Generate image | `generate_image` | Paid/credit action; explicit approval required. |
| Generate audio | `generate_audio` | Paid/credit action; explicit approval required. |
| Upscale | `upscale_media` | Paid/credit action; explicit approval required. |

## Feedback

| Need | Tool |
|---|---|
| Report concrete Palmier tool limitation/bug | `send_feedback` |

## High-Leverage Workflows

### Fast Long-Form YouTube Edit

```text
get_timeline
get_media
create_timeline from=<active timelineId>   # broad edit copy
get_timeline                               # IDs changed
get_transcript granularity=segments
inspect_media/search_media as needed
remove_silence / remove_words / ripple_delete_ranges
apply_layout / add_texts only where useful
manage_markers for subjective decisions
inspect_timeline hook + representative demo + overlays
get_transcript verification
stop for user review
```

Do not add a long-form caption track by default.

### Transcript Cleanup Only

```text
get_timeline
get_transcript
remove_words
get_transcript
remove_silence if appropriate
get_transcript verification
```

### YouTube Short From Long-Form

```text
get_timeline
get_media
create_timeline from=<active timelineId>
get_timeline
search_media / get_transcript to find one strong proof moment
set_project_settings aspectRatio=9:16 only when requested/appropriate
assemble/tighten segment
add_captions
inspect_timeline for safe mobile framing/caption placement
```

### AI B-Roll

```text
get_timeline
get_media
list_models
inspect references
present exact generation proposal
WAIT FOR APPROVAL
generate_*
get_media to observe readiness
place asset
inspect_timeline
```

### Normal YouTube Export

Current guidance, subject to live schema:

```text
export_project
  mode=video
  codec=H.264
  resolution=Match Timeline
  overwrite=false
manage_exports action=list
```

Omit `outputPath` unless the user supplies one.

## Decision Rules

- Live MCP schema overrides this document if they differ.
- Broad edits should preserve the source timeline with `create_timeline`.
- Re-read state after timeline copy/switch/undo or stale-state errors.
- `remove_words` is primary for speech; re-read indices after mutation.
- `remove_silence` is primary for bulk dead air.
- `inspect_timeline` answers what the viewer sees.
- `inspect_media` answers what raw source contains.
- `insert_clips` preserves existing content by rippling; `add_clips` may intentionally replace/overlap.
- Preserve A/V links unless independent editing is intentional.
- Long-form does not get burned captions by default.
- Use review markers for unresolved subjective choices.
- Confirm before paid generation/upscale or source-media deletion.
- Export only when requested, with overwrite protection by default.

## Quality Bar

Correct tool routing must preserve current state, use exact IDs, match the user's edit intent, avoid accidental overwrite/destruction, preserve technical truth, keep important visuals readable, and produce a bounded reviewable timeline.
