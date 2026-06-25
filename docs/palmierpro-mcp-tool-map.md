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
| Recover last assistant edit | `undo` | Reverts assistant's latest timeline edit from this session. Re-read state after undo. |

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
| Remove tracks | `remove_tracks` | Use only when track cleanup is intentional. |
| Move/reorder clips | `move_clips` | Move in time and/or to compatible tracks. |
| Change clip properties | `set_clip_properties` | Trim, duration, speed, volume, opacity, transform, text properties. |
| Set animation/automation | `set_keyframes` | Keyframes for volume, opacity, rotation, position, scale, or crop. |
| Split clip | `split_clip` | Split at a frame strictly inside the clip range. |
| Delete ranges and close gaps | `ripple_delete_ranges` | Use for non-word-aligned spans or visual-only dead air. |
| Sync audio | `sync_audio` | Align target clips to a fixed reference clip by waveform. |

## Transcript and Captions

| Need | Tool | Notes |
|---|---|---|
| Read current timeline speech | `get_transcript` | Source of truth for edited timeline speech in project frames. |
| Cut by word | `remove_words` | Primary tool for filler, retakes, and speech cleanup. Re-read transcript after use. |
| Add automatic captions | `add_captions` | Preferred captioning path. Transcribes and creates styled caption clips. |
| Add manual text | `add_texts` | Titles, lower thirds, callouts, hook text, manual emphasis. |

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
| List folders | `list_folders` | Check before creating folders. |
| Create folder | `create_folder` | Group related generated/imported assets. |
| Move assets | `move_to_folder` | Organize media into existing or new folders. |
| Rename media | `rename_media` | Use for clear library names. |
| Rename folder | `rename_folder` | Use for cleanup. |
| Delete media | `delete_media` | Destructive; confirm first. Prefer timeline removal. |
| Delete folder | `delete_folder` | Destructive; confirm first. |

## Export and Feedback

| Need | Tool | Notes |
|---|---|---|
| Export deliverable | `export_project` | Video, XML, or Palmier package. Video renders in background. |
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
create_folder if useful
generate_image or generate_video
get_media later for readiness
add_clips or insert_clips
inspect_timeline
```

### Export Review File

```text
inspect_timeline important moments
export_project mode=video codec=H.264 resolution=Match Timeline
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
