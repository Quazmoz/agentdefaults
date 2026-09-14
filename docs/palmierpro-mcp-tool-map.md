# Palmier Pro MCP Tool Map

## Purpose

Provide a compact, current routing map for Palmier Pro's MCP editing tools as used by Claude Code, OpenAI Codex, Cursor, or another MCP client.

Compatibility anchor: Palmier Pro v0.9.0 and current public documentation. Use the live MCP schemas as runtime truth. This map is a selection aid, not a substitute for current tool definitions.

## Agent Boundary

Palmier's in-app Agent and MCP-connected agents share the editing model/tool behavior. Skill installation/storage is client-specific.

External Claude/Codex/Cursor workflows should use AgentDefaults or their own installed skills and must not assume Palmier-managed skill operations are available unless the live schema actually exposes them.

## Project / Timeline State

| Need | Tool | Notes |
|---|---|---|
| List/open/create/close project | `manage_project` | Mainly useful to external MCP clients. Do not guess among ambiguous projects. |
| Read timeline/project structure | `get_timeline` | Session start and after state-invalidating operations. |
| Inspect composited viewer output | `inspect_timeline` | Use for what the viewer actually sees. |
| Create/copy a timeline | `create_timeline` | Preferred versioning primitive for broad edits; copied IDs change. |
| Switch active timeline | `set_active_timeline` | Re-read state after switching. |
| Change fps/aspect/resolution | `set_project_settings` | Structural mutation; may refit/rescale the edit. Use only when the target output requires it. |
| Add/update/delete review marker | `manage_markers` | Point/range feedback and Agent-review workflow; use status deliberately. |
| Undo latest shared action | `undo` | Only when the latest action is known; refresh state afterward. |
| Export | `export_project` | Queue video/interchange/package output. |
| Inspect/cancel export jobs | `manage_exports` | Observe real job state; never infer completion/stall from time alone. |

## Media Library

| Need | Tool | Notes |
|---|---|---|
| List assets/folders/timelines | `get_media` | Source of exact media refs/readiness. |
| Inspect source media | `inspect_media` | Raw source content; use before describing/editing it. |
| Semantic footage search | `search_media` | Find spoken/visual proof moments without filename guessing. |
| Import media | `import_media` | Prefer approved local/user sources; respect privacy boundary. |
| Capture current composited frame | `capture_frame` | Creates a still from the timeline when exposed by live schema. |
| Organize/delete media/folders | `organize_media` | Deletion is destructive; confirm exact targets first. |

## Tracks / Clips

| Need | Tool | Notes |
|---|---|---|
| Reorder/name/configure tracks | `manage_tracks` | Prefer stable track IDs. |
| Link/unlink A/V | `manage_clip_links` | Use deliberately for independent A/V editing. |
| Add existing media | `add_clips` | May overlap/replace depending on schema semantics. |
| Insert and ripple | `insert_clips` | Use when existing content must shift. |
| Move clips | `move_clips` | Reposition in time/track. |
| Remove timeline clips | `remove_clips` | Safer than deleting source media. |
| Split clips | `split_clips` | Use when sections need independent treatment. |
| Delete/ripple exact ranges | `ripple_delete_ranges` | Non-word-aligned/visual-only verified ranges. |
| Swap source while preserving edit | `swap_clip_media` | Use when exposed and semantically appropriate. |
| Trim/speed/volume/transform/fades | `set_clip_properties` | Live schema defines exact fields. |
| Copy compatible clip settings | `copy_clip_settings` | Reuse styling/settings when exposed. |
| Animate supported properties | `set_keyframes` | Volume, opacity, transform, crop, blur, etc.; verify visible result. |
| Apply common composition | `apply_layout` | Full-frame, split, PIP, sidebar, grid where supported. |

## Multicam / Synchronization

| Need | Tool | Notes |
|---|---|---|
| Align related recordings | `sync_clips` | Audio/timecode/auto as supported; do not force weak sync. |
| Create/dissolve/manage multicam | `manage_multicam` | Prefer purpose-built group workflow over manual simulation. |
| Read group/program state | `get_multicam` | Re-read after material group changes. |
| Switch program angle | `change_cam` | Verify representative switches and sync. |

## Transcript / Pacing / Rhythm

| Need | Tool | Notes |
|---|---|---|
| Read edited timeline speech | `get_transcript` | Segments for comprehension, words for cuts. |
| Cut by word | `remove_words` | Re-read transcript after every mutation because indices shift. |
| Remove quiet/speech-free pauses | `remove_silence` | Verify affected boundaries; do not force range cuts after a safe failure. |
| Detect music beats/downbeats | `detect_beats` | Use returned timing for intentional beat-synced edits; never estimate beats manually. |

## Text / Captions

| Need | Tool | Notes |
|---|---|---|
| Add titles/callouts | `add_texts` | Use current supported typography/style fields. |
| Update existing text/captions | `update_text` | Content/style/placement changes. |
| Add automatic/imported captions | `add_captions` | Short-form or explicit caption request; not default for long-form 16:9. |

## Color / Effects / Masks / Audio

| Need | Tool | Notes |
|---|---|---|
| Inspect color/scopes | `inspect_color` | Measure before correction/grade. |
| Apply color/LUT/curves | `apply_color` | Intentional correction/look only. |
| Apply effect | `apply_effect` | Blur, sharpen, keying/stylization where supported; verify. |
| Create/adjust tracked or basic masks | `manage_masks` | Validate target identity; tracked masks may be long-running; verify visible isolation. |
| Denoise/enhance speech | `denoise_audio` | Use only when noise exists/requested. |

## Generation / Upscaling

| Need | Tool | Notes |
|---|---|---|
| Read current model capabilities | `list_models` | Required before generation/upscale proposal. Do not hard-code model capabilities/rankings. |
| Generate/transform image | `generate_image` | Paid/credit action; explicit approval required. |
| Generate/transform video | `generate_video` | Paid/credit action; validate first/last-frame and reference compatibility. |
| Generate speech/music/SFX/dubbing | `generate_audio` | Paid/credit action; use only current supported mode/input combinations. |
| Upscale/interpolate | `upscale_media` | Paid/credit action; explicit approval required. |

## Feedback

| Need | Tool | Notes |
|---|---|---|
| Report concrete Palmier limitation/bug | `send_feedback` | Use only for an actual product/tool issue, not as generic task output. |

## Task Completion Routing

### Quick / First-Pass Edit

```text
get_timeline
get_media
create_timeline from=<active timelineId>   # broad edit only
get_timeline                               # copied IDs changed
get_transcript granularity=segments
inspect/search source as needed
remove_silence / remove_words / ripple_delete_ranges
layout/text/audio/finishing only where useful
manage_markers for subjective decisions
inspect_timeline hook + representative demo + overlays
get_transcript verification
stop for user review
```

### End-to-End Editorial Request

```text
resolve project + live state
preserve source version when broad change warrants it
perform story/cleanup/visual/audio/finishing stages in scope
use multicam / beat / masks / color/effects only when the material/request warrants them
verify transcript + representative viewer-visible output
resolve or report blocking review items
if export explicitly requested: export_project -> manage_exports until authoritative terminal/current status
return completed/verified/review/blocked/export state
```

Do not insert an unnecessary confirmation pause between safe routine stages.

### Transcript Cleanup Only

```text
get_timeline
get_transcript
remove_words
get_transcript
remove_silence if appropriate
verify affected transcript/timeline boundaries
```

### YouTube Short From Long-Form

```text
get_timeline
get_media
create_timeline from=<active timelineId>
get_timeline
search_media / get_transcript for one strong proof moment
set_project_settings aspect/resolution only when requested/appropriate
assemble/tighten segment
add_captions
inspect_timeline for mobile framing/caption placement
```

### Multicam Rough Cut

```text
get_media
inspect/identify camera + microphone assets
sync_clips or manage_multicam with supported sync method
get_multicam
change_cam over editorial ranges
inspect_timeline representative switches
```

### Beat-Synced Montage

```text
get_media
inspect intended music asset
detect_beats
choose editorially useful beats/downbeats
place/move/split clips using returned timing
inspect_timeline representative cut sequence
```

### AI B-Roll / Transformation

```text
get_timeline
get_media
list_models
inspect source/reference media
validate exact supported reference/input combination
present generation proposal
WAIT FOR APPROVAL
generate_*
get_media to observe authoritative readiness
inspect result
place/swap asset only when ready
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
- Broad edits should preserve the source timeline with `create_timeline` when rollback/reviewability matters.
- Re-read state after timeline copy/switch/undo or stale-state errors.
- `set_project_settings` is structural; never use it casually.
- `remove_words` is primary for speech; re-read indices after mutation.
- `remove_silence` is for quiet/speech-free pauses and must fail safe.
- `detect_beats` supplies rhythm timing; editorial intent decides which beats become cuts.
- `inspect_timeline` answers what the viewer sees; `inspect_media` answers what raw source contains.
- Use purpose-built multicam/mask/generation tools rather than reproducing their workflows with low-level edits.
- `insert_clips` preserves existing content by rippling; `add_clips` may intentionally overlap/replace per live semantics.
- Preserve A/V links unless independent editing is intentional.
- Long-form does not get burned captions by default.
- Review markers record unresolved decisions; they are not automatically blockers.
- Confirm before paid generation/upscale, source-media deletion, overwrite/publishing, or other consequential side effects not already explicitly authorized.
- Export only when requested and report authoritative job state.
- For end-to-end requests, continue through safe stages instead of stopping after an arbitrary first-pass boundary.

## Quality Bar

Correct tool routing must preserve current state, use exact IDs, match the user's completion intent, avoid accidental overwrite/destruction/spend, preserve technical truth, keep important visuals readable, use current Palmier capabilities, and produce truthful verified output.
