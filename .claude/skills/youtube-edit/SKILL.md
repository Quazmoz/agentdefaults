---
name: youtube-edit
description: >
  Edit local YouTube creator footage with Claude Code using Parakeet timestamp
  transcription, FFmpeg rough cutting/finishing, HyperFrames motion graphics,
  evidence-backed browser b-roll, and optional Tella / licensed music tools.
  Use when the user asks Claude Code to edit, rough-cut, polish, caption,
  animate, or finish a YouTube video from local footage.
argument-hint: "[path-to-video-or-project] [optional editing goal]"
license: MIT
---

# YouTube Edit

Use the canonical AgentDefaults stack:

- `agents/claude-code-video-editor-agent.md`
- `skills/claude-code-video-editing.md`
- `config/video-editing/channel-style.md`
- `docs/quickstarts/claude-video-editing.md`

## Invocation

When the user runs `/youtube-edit`:

1. resolve the supplied local video/project path
2. keep raw media immutable
3. probe with ffprobe
4. transcribe with Parakeet timestamps
5. build a transcript-driven edit plan
6. rough cut with FFmpeg
7. use primary-source browser b-roll only where it adds real proof/context
8. use HyperFrames for motion graphics and validate with lint/check
9. use Tella/Epidemic Sound only if connected and appropriate
10. finish/QC with FFmpeg and targeted playback review
11. return the review render and concise notes

Do not merely write an editing plan when the user asked for an edit and the required local tools/files are available.

## Default Creator Profile

Assume technical creator content unless the footage/request says otherwise:

- AI / automation / DevOps / coding
- Android and Wear OS apps
- screen-recorded demos
- practical tutorials and product walkthroughs

Prefer proof-first storytelling, readable UI/code, restrained graphics, and accurate caveats over hype.

## Feedback Learning

If the user gives timestamped feedback, apply it to the current edit.

Only persist it to `config/video-editing/channel-style.md` when the user explicitly asks to learn/save/remember/apply the preference in future edits.

## Safety / Truth

- Never invent factual b-roll.
- Never use unknown-license music/media as if licensed.
- Never overwrite raw footage.
- Never claim visual/audio verification that was not performed.
- Do not silently replace Parakeet with another transcription engine.
