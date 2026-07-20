# Palmier Pro MCP Tool Map

## Purpose

Provide a compact map of Palmier Pro MCP tools and the editing workflows they support.

Use this guide when an agent needs to choose the correct Palmier tool without re-reading every tool description.

## Source Notes

This guide is based on Palmier Pro's public documentation and open-source MCP tool names available at the time this file was added.

Palmier's own app instructions remain the source of truth when newer versions change behavior:

```text
Palmier Pro -> Help -> MCP Instructions
```

## Setup and Project State

| Need | Tool | Notes |
|---|---|---|
| Read timeline state | `get_timeline` | Call at session start. Returns fps, resolution, tracks, clips, totalFrames, and canGenerate. |
| Read media library | `get_media` | Call before referencing assets. Watch generation/import status. |
| Change project settings | `set_project_settings` | Use deliberately; affects project-level output. |
| Recover last edit | `undo` | Reverts the most recent action from the shared editor undo history (may be a user action, not only an assistant edit). Re-read state after undo. |

## Media Understanding

| Need | Tool | Notes |
|---|---|---|
| Inspect a source asset | `inspect_media` | Use before describing or editing user-supplied media. Supports frames and transcript. |
| Inspect final preview | `inspect_timeline` | Use for composited visuals, overlay placement, layer order, and transformations. |
| Search library by content | `search_media` | Use for visual or spoken semantic search across media. |
| Import media | `import_media` | Supports HTTPS URL, absolute local path, or small base64 bytes. |

## Timeline Editing

| Need | Tool | Notes |
|---|---|---|
| Place media | `add_clips` | Places existing assets; same-track overlap overwrites/clears landing range. |
| Insert media | `insert_clips` | Ripples existing timeline material to open a gap. |
| Remove clips | `remove_clips` | Timeline removal, safer than deleting source media. |
| Manage tracks (reorder/configure/remove) | `manage_tracks` | Use only when track cleanup or reordering is intentional. |
| Move/reorder clips | `move_clips` | Move in time and/or to compatible tracks. |
| Change clip properties | `set_clip_properties` | Trim, duration, speed, volume, opacity, transform, text properties. |
| Arrange picture-in-picture / stacked layouts | `apply_layout` | Purpose-built for facecam+screenshare and multi-clip layouts; fall back to `set_clip_properties` transform + `set_keyframes` for fine control. |
| Set animation/automation | `set_keyframes` | Keyframes for volume, opacity, rotation, position, scale, or crop. |
| Split clips | `split_clips` | Split at a frame strictly inside the clip range. |
| Delete ranges and close gaps | `ripple_delete_ranges` | Use for specific non-word-aligned spans or visual-only dead air. |
| Remove silent spans | `remove_silence` | Bulk dead-air / speech-free cleanup; prefer over manual `ripple_delete_ranges` for silence. |
| Sync clips | `sync_clips` | Align target clips to a fixed reference clip by waveform. For multicam, use `manage_multicam` / `change_cam` / `get_multicam`. |

## Transcript and Captions

| Need | Tool | Notes |
|---|---|---|
| Read current timeline speech | `get_transcript` | Source of truth for edited timeline speech in project frames. |
| Cut by word | `remove_words` | Primary tool for filler, retakes, and speech cleanup. Re-read transcript after use. |
| Add automatic captions | `add_captions` | Preferred captioning path. Transcribes and creates styled caption clips. |
| Add manual text | `add_texts` | Titles, lower thirds, callouts, hook text, manual emphasis. |
| Edit existing text | `update_text` | Change content or style of an existing text clip; use `add_texts` only to create new overlays. |
| Clean up noisy audio | `denoise_audio` | Reduce background noise on captured audio before finalizing. |

## AI Generation and Upscaling

| Need | Tool | Notes |
|---|---|---|
| List model capabilities | `list_models` | Required before generation/upscale. Check type, duration, references, voices, assets. |
| Generate video | `generate_video` | Async, returns placeholder asset. Costs credits; confirm first. |
| Generate image | `generate_image` | Async, returns placeholder asset. Costs credits; confirm first. |
| Generate audio | `generate_audio` | TTS, music, SFX, or video-to-audio depending on model. Confirm first. |
| Upscale media | `upscale_media` | Async. Costs credits; confirm first. |

## Color and Effects

| Need | Tool | Notes |
|---|---|---|
| Inspect color state | `inspect_color` | Use before correction or look changes. |
| Apply color changes | `apply_color` | Use for intentional correction or grade. Verify with `inspect_timeline`. |
| Apply effect | `apply_effect` | Use sparingly and deliberately. Verify visible result. |

## Library Organization

| Need | Tool | Notes |
|---|---|---|
| Organize media and folders (create/move/rename/delete) | `organize_media` | Single tool for folder and media organization. Deletion is destructive; confirm first, and prefer timeline `remove_clips` over deleting source media. |

## Export and Feedback

| Need | Tool | Notes |
|---|---|---|
| Export deliverable | `export_project` | Modes: `video`, `xml` (Premiere/Resolve), `fcpxml` (Final Cut; set `fcpxmlTarget`), and `palmier` package. Video renders in background. |
| Check/manage export jobs | `manage_exports` | Inspect or manage background export jobs. |
| Report tool issue | `send_feedback` | Use for concrete Palmier limitation, bug, or product suggestion. |

## High-Leverage Workflows

### First-Pass YouTube Edit

```text
get_timeline
get_media
inspect_media primary footage
get_transcript
remove_words / ripple_delete_ranges
add_captions
add_texts for title/callouts
inspect_timeline key sections
```

### Short-Form Cutdown

```text
get_timeline
get_transcript
search_media for proof/demo/hook moment
insert_clips or move_clips to assemble segment
remove_words with tight/balanced pacing
add_captions
inspect_timeline
```

### AI B-Roll Generation

```text
get_timeline
get_media
list_models
inspect reference media
ask approval with model + prompt + duration/aspect
organize_media if a folder is useful
generate_image or generate_video
get_media later for readiness
add_clips or insert_clips
inspect_timeline
```

### Export Review File

```text
inspect_timeline important moments
export_project mode=video codec=h.264 resolution=matchtimeline
```

## Decision Rules

- Use `remove_words` before manual frame cuts for speech.
- Use `add_captions` before manual caption text creation.
- Use `inspect_timeline` for what the viewer sees.
- Use `inspect_media` for raw source assets.
- Use `insert_clips` when preserving existing timeline content matters.
- Use `add_clips` when replacing/placing on a track is intentional.
- Confirm before generation, upscaling, source deletion, or overwrite exports.

## Quality Bar

A tool choice is correct when it matches the user's editing intent, respects Palmier's frame-based timeline model, avoids unnecessary destructive actions, and leaves a reviewable timeline state.
