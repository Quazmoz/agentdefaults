# Palmier Pro AI Generation Workflow

## Purpose

Provide a safe, practical workflow for using Palmier Pro's AI image, video, audio, and upscaling tools through MCP.

Use this skill to generate assets intentionally, preserve approval boundaries, use current model/reference capabilities, organize generated media, and avoid wasting credits on poor prompts or unsupported combinations.

Compatibility anchor: Palmier Pro v0.9.0 and current public model/generation documentation. The live `list_models` output and generation schemas are authoritative.

## When To Use

Use this skill when the user asks to:

- generate b-roll
- generate an image, still, title background, or reference frame
- generate a video clip
- transform/reframe an existing video when supported
- generate narration, dubbing, music, SFX, or score
- clean/replace voice through a supported generation workflow
- upscale an image or video
- create consistent visual assets across a video
- build AI-generated sections inside an existing edit

Do not use this skill for normal timeline edits, captions, UI overlays, or source-media cleanup.

## Required Inputs

Before generation or upscaling:

```text
get_timeline
get_media
list_models
```

Inspect every source/reference asset that materially affects the prompt or result:

```text
inspect_media
```

Check current live capability data for:

- `get_timeline.canGenerate`
- model type and model ID/default behavior
- supported durations
- supported aspect ratios
- supported resolutions
- first/last-frame support
- image/video/audio reference support and limits
- video-to-video/reframe/lip-sync support
- audio workflow capabilities such as speech, dubbing, music, SFX, or cleanup
- asset type support for upscaling

Do not infer support from an old model name or previous Palmier release.

## Approval Rule

Generation and upscaling may consume Palmier credits and can cross an external processing boundary. They are not ordinary undoable timeline edits.

Always ask for explicit approval before calling:

```text
generate_image
generate_video
generate_audio
upscale_media
```

Approval request format:

```text
I can generate <asset type> using <current model/capability>, <duration/aspect/resolution>, with <reference summary if any> and this prompt: "<prompt>". This may use Palmier credits. Approve generation?
```

Do not batch multiple paid generations unless the user approves the batch count and intent.

## Model Selection

Treat `list_models` as a capability catalog, not a static ranking table.

Rules:

- choose a model only after matching required inputs/outputs to current capabilities
- do not hard-code a permanent preferred model
- when Palmier exposes a backend/default model choice and the user has no preference, do not override it without a concrete quality/capability reason
- if multiple models satisfy the request, prefer the simplest one that meets the stated constraints; explain a meaningful tradeoff only when it affects cost, duration, reference support, or output fidelity
- never fabricate unsupported reference types, durations, aspect ratios, or resolutions

## Reference Media Strategy

Palmier v0.9-era workflows support richer reference-driven generation. Use references intentionally rather than re-describing an existing asset in text.

Before using a reference:

1. resolve the exact current `mediaRef`
2. inspect the asset when content matters
3. confirm the selected model accepts that reference type/count
4. state the reference role in the approval request

Reference roles may include:

- first frame: lock the starting composition/subject
- last frame: target an ending composition when supported
- image reference: preserve subject/product/style
- video reference: preserve motion/content or transform an existing shot
- audio reference: preserve or condition sound/voice when supported

Do not attach private source media to cloud generation unless the user has explicitly approved the generation workflow that requires it.

## Generation Readiness

If `canGenerate` is false:

```text
Palmier reports generation is unavailable in this session. Sign in or enable the required Palmier generation access, then retry.
```

If a model capability is missing:

```text
That model does not support the requested input/reference/duration/aspect. I can adjust the request or choose a compatible model from list_models.
```

If a generated/imported placeholder asset is still pending:

```text
The asset is still generating/importing. I can continue with other safe timeline edits and place it once Palmier reports the media as ready.
```

Do not poll in a tight loop and do not treat a preview card/placeholder as a completed asset.

## Default Strategies

### Image-First Strategy

Use for:

- character consistency
- app/product hero shots
- branded visual style
- thumbnails/title-card backgrounds that may become video starts
- precise composition

Workflow:

```text
1. define the visual objective compactly
2. list_models and select a compatible image capability
3. generate_image only after approval
4. wait for readiness and inspect the result
5. use the approved still as first-frame/reference input when supported
6. generate_video only after a separate or clearly encompassing approval
```

### Direct Video Strategy

Use when:

- the user explicitly wants text-to-video
- the shot does not require a locked starting composition
- rough b-roll is acceptable
- motion matters more than exact image fidelity

Video prompt formula:

```text
camera movement + subject action + environment/audio intent when relevant
```

Keep prompts compact and concrete.

### Video Transformation Strategy

Use when current models support the requested operation:

- video-to-video transformation
- reframe to a new aspect ratio
- lip sync with replacement audio

Rules:

- inspect the source video first
- use only the visible trimmed range when the tool/schema supports timeline-range sourcing
- do not silently transform a larger source range than the user intended
- preserve truthful product/UI content; do not use generative transformation for exact readable UI, code, or terminal output

### Audio Strategy

Use `generate_audio` only for a current supported audio workflow such as:

- text-to-speech
- music
- sound effects
- dubbing
- voice cleanup/replacement when explicitly supported

Rules:

- For TTS, the script text must be exact.
- For dubbing, preserve source timing/meaning unless the user requests adaptation.
- For music, describe style, mood, genre, tempo, vocals/instrumental intent, and duration intent.
- For SFX, describe the sound event rather than a visual scene.
- For source-conditioned audio, provide only supported timeline/media inputs.

## Prompt Rules

### Image Prompts

Prefer concise prompts that specify:

```text
subject + setting + shot/composition + lighting/mood + style constraint
```

When a strong reference already defines the subject/style, prompt mainly for the desired change rather than redundantly re-describing everything.

### Video Prompts

Prefer concise prompts that specify:

```text
camera movement + subject action + temporal change + audio/mood when persistent
```

When using a first frame, describe motion/change rather than re-describing the still.

### Audio Prompts

For TTS:

```text
Exact narration text.
```

For music/SFX:

```text
Mood/event + genre/timbre + tempo/intensity + duration intent.
```

## What Not To Generate

Do not use generative video/image models for assets that require exact readable fidelity when native/imported/editor tools are appropriate:

- readable UI screenshots
- code editor screens
- app interfaces
- terminal commands/output
- exact logos/brand marks without appropriate source assets/permission
- text overlays
- captions
- lower thirds
- title cards requiring exact typography
- screen recordings

Use imported source media and Palmier editor text/layout tools instead.

## Asset Organization

Use folders for related generations.

Workflow:

```text
1. review existing folders in get_media
2. reuse an existing relevant folder when possible
3. create a folder only for a coherent concept group
4. pass folderId on generation/import calls when supported
5. move related assets into the folder when useful
```

Avoid creating folders for unrelated one-off assets.

## Placement Workflow

After generation/import:

```text
1. get_media later to check authoritative status
2. confirm asset is ready
3. inspect_media when content matters
4. place with add_clips or insert_clips if placement is not automatic
5. inspect_timeline for important visual/audio placement
```

If the generation workflow auto-places a result or returns a timeline mutation receipt, verify timeline state instead of adding it again.

## Upscaling Workflow

Before `upscale_media`:

```text
1. get_media
2. inspect_media if needed
3. list_models for current upscale capabilities
4. confirm asset type / resolution / frame-rate options
5. ask for approval
6. call upscale_media once
7. observe media readiness and inspect the result before swapping/placing it
```

Upscale only when the output requirement or visible source quality justifies it. Do not upscale every asset by default.

## Failure And Retry Policy

For failed paid generation/upscale:

1. capture the exact failure
2. inspect current job/media state before assuming nothing happened
3. do not automatically retry the paid call
4. if correction is needed, present the revised proposal and obtain approval again unless the prior approval clearly covered the corrected non-material retry

For timeouts after a possibly successful call, inspect authoritative media/job state before any retry to avoid duplicate spend.

## Expected Output

Before generation:

```text
I can generate a 6-second 9:16 b-roll clip using a current video model that supports this approved smartwatch still as the first frame. Prompt: "Slow push-in as the watch display comes alive, clean tech ambience." This may use Palmier credits. Approve generation?
```

After starting generation:

```text
Generation started — Palmier returned a pending media job/placeholder. I will treat it as incomplete until get_media reports the asset ready.
```

## Quality Bar

- Calls `list_models` before generation/upscale.
- Checks `canGenerate`.
- Uses only current supported reference/input combinations.
- Does not hard-code stale model rankings or capabilities.
- Gets explicit approval before spending credits.
- Uses compact prompts and references intelligently.
- Protects private source media at the generation boundary.
- Does not pretend pending/preview media is complete.
- Does not blindly retry paid calls.
- Places generated assets only after authoritative readiness is confirmed.
