# Palmier Pro AI Generation Workflow

## Purpose

Provide a safe, practical workflow for using Palmier Pro's AI image, video, audio, and upscaling tools through MCP.

Use this skill to generate assets intentionally, preserve user approval boundaries, organize generated media, and avoid wasting credits on poor prompts or unsupported model choices.

## When To Use

Use this skill when the user asks to:

- generate b-roll
- generate an image, still, title background, or reference frame
- generate a video clip
- generate narration, music, SFX, or score
- upscale an image or video
- create consistent visual assets across a video
- build AI-generated sections inside an existing edit

Do not use this skill for normal timeline edits, captions, UI overlays, or source-media cleanup.

## Inputs Needed

Before generation or upscaling:

```text
get_timeline
get_media
list_models
```

Also inspect relevant source/reference media:

```text
inspect_media
```

Check:

- `get_timeline.canGenerate`
- available model types and model IDs
- supported durations
- supported aspect ratios
- supported resolutions
- reference limits
- audio voices or audio-input capabilities
- asset type support for upscaling

## Approval Rule

Generation and upscaling cost real credits and are not normal undoable timeline edits.

Always ask for explicit approval before calling:

```text
generate_image
generate_video
generate_audio
upscale_media
```

Approval request format:

```text
I can generate <asset type> with <model if known>, <duration/aspect/resolution>, using this prompt: "<prompt>". This may use Palmier credits. Approve generation?
```

Do not batch many paid generations unless the user approves the batch count and intent.

## Generation Readiness

If `canGenerate` is false:

```text
Palmier reports generation is unavailable in this session. Sign in or subscribe in Palmier Pro, then retry generation.
```

If a model capability is missing:

```text
That model does not support the requested reference/duration/aspect ratio. I can adjust the prompt or choose a compatible model from list_models.
```

If a generated/imported placeholder asset is still pending:

```text
The asset is still generating/importing. I can continue with other timeline edits and place it once it appears as ready in get_media.
```

Do not poll in a tight loop.

## Default Strategy

### Image-First Strategy

Use for:

- character consistency
- app/product hero shots
- branded visual style
- thumbnails/title cards that should become video starts
- precise composition

Workflow:

```text
1. define visual style in 15-30 words
2. generate_image after approval
3. wait for user review or asset readiness
4. use approved still as startFrameMediaRef or referenceMediaRefs
5. generate_video only after approval
```

### Direct Video Strategy

Use only when:

- the user explicitly asks for text-to-video
- the shot does not need a locked start frame
- rough b-roll is acceptable
- the motion matters more than exact composition

Video prompt formula:

```text
camera movement + subject action + mood/sound if relevant
```

Keep video prompts short and concrete.

### Audio Strategy

Use `generate_audio` for:

- text-to-speech
- music beds
- sound effects
- video-to-music/scoring when supported by the chosen model

Rules:

- For TTS, the prompt is the exact text to speak.
- For music, describe style, mood, genre, tempo, and vocals/instrumental intent.
- For lyrics-capable models, provide lyrics in the supported field or prompt as required by the model.
- For video-to-audio models, provide either a timeline span or source media as the model requires.

## Prompt Rules

### Image Prompts

Use 15-30 words.

Formula:

```text
subject + setting + shot type + lighting/mood + style constraint
```

Example:

```text
Developer desk with smartwatch app preview, close-up product shot, dark studio lighting, crisp cyan reflections, realistic tech aesthetic.
```

### Video Prompts

Use 8-20 words.

Formula:

```text
camera movement + subject action + audio/mood if persistent
```

Example:

```text
Slow push-in as the smartwatch dashboard lights up, subtle electronic ambience.
```

When using `startFrameMediaRef`, do not re-describe the still. Describe motion.

### Audio Prompts

For TTS:

```text
Exact narration text.
```

For music/SFX:

```text
Mood + genre + tempo + instrumentation + intensity + duration intent.
```

Example:

```text
Subtle futuristic synth bed, steady 90 BPM, light pulse, no vocals, clean tutorial background energy.
```

## What Not To Generate

Do not generate these with video models:

- readable UI screenshots
- code editor screens
- app interfaces
- terminal commands
- exact logo animations
- text overlays
- captions
- lower thirds
- title cards requiring readable text
- screen recordings

Use imported source media and editor text tools instead.

## Asset Organization

Use folders for related generations.

Workflow:

```text
1. call list_folders
2. reuse an existing relevant folder if present
3. create_folder only for a coherent concept group
4. pass folderId on generation/import calls
5. move_to_folder for existing assets when needed
```

Good folder names:

```text
Hero shot variations
AI b-roll - intro
Shorts captions assets
Generated music beds
Product demo stills
```

Avoid creating folders for unrelated one-off assets.

## Placement Workflow

After generation/import:

```text
1. call get_media later to check status
2. confirm asset is ready
3. inspect_media if visual/audio content matters
4. place with add_clips or insert_clips
5. inspect_timeline for important visual placement
```

For generated audio that auto-places based on a timeline span, verify timeline state instead of adding it again.

## Upscaling Workflow

Before `upscale_media`:

```text
1. get_media
2. inspect_media if needed
3. list_models type=upscale
4. confirm the selected model supports the asset type
5. ask for approval
6. call upscale_media
```

Upscale only when:

- delivery resolution requires it
- the user asks for quality improvement
- source quality is visibly insufficient
- the upscaled asset will actually be used

Do not upscale every asset by default.

## Expected Output

Before generation:

```text
I can generate a 6-second 9:16 b-roll clip from the approved smartwatch still. Prompt: "slow push-in as the watch UI pulses, clean tech ambience." This may use Palmier credits. Approve generation?
```

After starting generation:

```text
Generation started — Palmier returned a placeholder asset. I can keep editing and place it once it is ready in the media library.
```

## Quality Bar

- Calls `list_models` before generation/upscale.
- Checks `canGenerate`.
- Gets approval before spending credits.
- Uses compact, concrete prompts.
- Uses stills/references for consistency when needed.
- Organizes related assets into folders.
- Does not pretend async placeholder assets are complete.
- Places generated assets only after readiness is confirmed.
