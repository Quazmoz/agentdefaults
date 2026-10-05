# Claude Code Quick YouTube Edit Prompt

## Purpose

Provide a copy-paste invocation for a bounded first-pass local YouTube edit using the canonical Claude Code video-editing stack.

## Prompt

```text
Use the AgentDefaults Claude Code local video-editing stack:

- agents/claude-code-video-editor-agent.md
- skills/claude-code-video-editing.md
- config/video-editing/channel-style.md

SOURCE
<absolute path to raw video or project folder>

GOAL
Create a strong first-pass YouTube edit from the supplied footage.

WORKFLOW
1. Keep raw media immutable.
2. Probe source media with ffprobe.
3. Extract speech audio and transcribe it with NVIDIA Parakeet, including word and segment timestamps.
4. Build a transcript-driven story/edit plan before cutting.
5. Create a reproducible rough cut with FFmpeg.
6. When I make externally verifiable claims, use available browser tooling to capture primary-source proof/b-roll and record the source URL in work/source-manifest.md.
7. Use HyperFrames for meaningful motion graphics. Lint during authoring; for the final gate run `check --snapshots`, inspect those snapshots, then open the final Studio preview. Satisfy the active HyperFrames review/approval requirement before rendering graphics.
8. Use Tella only if it is actually connected and useful for a Tella-native source.
9. Use music/SFX only from a licensed source I have access to. Keep sound design restrained.
10. Assemble and QC the review render with FFmpeg/ffprobe plus targeted playback review.

EDITORIAL STYLE
- Technical creator video.
- Proof/result-forward hook when supported by the footage.
- Preserve commands, versions, product/repo/model names, warnings, failures, and caveats.
- Tighten dead air and retakes without making speech robotic.
- Keep app UI, terminal output, code, and dashboards readable.
- Prefer real app/demo footage and real source evidence over synthetic generic b-roll.
- Sparse, modern motion graphics; no generic neon AI aesthetic.
- Long-form captions only if they materially help or I ask for them.

STOP
One broad edit pass plus one targeted QC/fix pass, then return a review render and concise notes.

FINAL NOTES
Report raw duration, review-render duration, major cuts, b-roll sources, graphics added, tools actually used, QC actually performed, and any remaining manual-review items.
```
