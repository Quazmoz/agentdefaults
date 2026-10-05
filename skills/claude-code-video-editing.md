# Claude Code Video Editing Orchestration

## Purpose

Provide the reusable task behavior for the local Claude Code YouTube editing stack.

Use with:

`agents/claude-code-video-editor-agent.md`

The canonical pipeline is:

```text
raw media
  -> ffprobe intake
  -> audio extraction
  -> Parakeet timestamp transcript
  -> transcript/media-driven edit plan
  -> FFmpeg rough cut
  -> primary-source browser b-roll where useful
  -> HyperFrames motion graphics
  -> optional Tella and licensed music/SFX integrations
  -> FFmpeg assembly + QC
  -> human review
```

## Tool Selection

### Required core

- Claude Code with local file access
- FFmpeg / ffprobe
- NVIDIA Parakeet runtime capable of timestamp output
- HyperFrames for code-authored motion graphics

### Optional

- browser automation for factual research/capture
- Tella MCP for Tella-native screen edits
- Epidemic Sound or another licensed audio library
- image/video generation only when the user asks for it and the provider/cost/licensing boundary is understood

A missing optional tool must degrade gracefully to a placeholder/manual-review note.

## Project Layout

Prefer:

```text
video-project/
  raw/                  immutable source media
  work/
    transcript.wav
    transcript.json
    edit-plan.md
    cuts.json
    source-manifest.md
  graphics/             HyperFrames projects/renders
  audio/                licensed music/SFX actually used
  renders/
    rough.mp4
    review.mp4
    final.mp4
```

Do not commit private raw footage unless the user explicitly wants it versioned.

## Transcript Rules

- Prefer segment timestamps for story analysis.
- Use word timestamps only for precise candidate cut ranges.
- Never assume timestamp text alone proves a clean speech seam.
- Keep complete ideas and technical caveats.
- When multiple takes exist, prefer the last complete/best take only when context supports that choice.
- Preserve user personality; do not remove every filler or pause.

## Graphics Rules

Use HyperFrames for meaningful editorial graphics, not filler.

Before final render:

```bash
npx hyperframes lint
npx hyperframes check
```

Preview targeted changes instead of repeatedly rendering the entire finished video when a partial/isolated render is sufficient.

Use the current HyperFrames skill router and CLI semantics as runtime truth.

## Evidence B-roll Rules

A claim-specific b-roll item should have:

- source URL
- source/title
- capture date when currentness matters
- transcript claim it supports
- file path in the project
- notes on crop/highlight/scroll treatment

Prefer a first-party product page, repository, release note, paper, benchmark source, or original post over a secondary summary.

Do not show a screenshot as “proof” if it does not actually establish the narration's claim.

## Sound Rules

- voice first
- music below instructional speech
- no unlicensed web audio
- no SFX spam
- use silence strategically
- normalize/limit conservatively; avoid crushing dynamics

## Style Learning

Read:

`config/video-editing/channel-style.md`

before planning graphics, pacing, captions, and sound.

When the user explicitly asks to persist feedback, add or revise the smallest general rule in that file. Include a short provenance note with the date and the type of edit that produced the lesson; do not include private transcript text unnecessarily.

## Verification

Do not call an edit finished merely because a render command exited successfully.

Verify:

- no accidental black sections
- no unexpected silent spans
- expected streams/dimensions/frame rate
- readable graphics at normal playback
- factual b-roll matches narration
- no obvious caption/transcript errors when captions are used
- representative speech cuts sound natural
- source media remained intact

## Stop Rule

A first-pass edit ends after one targeted QC/fix pass. Additional creative refinement requires user feedback or a clearly failed acceptance check.
