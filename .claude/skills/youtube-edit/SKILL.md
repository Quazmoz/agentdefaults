---
name: youtube-edit
description: >
  Edit local YouTube creator footage with Claude Code using Parakeet timestamp
  transcription, an FFmpeg-rendered JSON edit decision list, HyperFrames motion
  graphics, evidence-backed browser b-roll, and optional Tella / licensed music
  tools. Use when the user asks Claude Code to edit, rough-cut, polish, caption,
  animate, cut Shorts from, or finish a YouTube video from local footage.
argument-hint: "[path-to-video-or-project] [optional editing goal]"
license: MIT
---

# YouTube Edit

Thin router to the canonical AgentDefaults stack. Read these before acting:

- `agents/claude-code-video-editor-agent.md` covers the contract, approval gates, unattended runs, and degradation.
- `skills/claude-code-video-editing.md` is the executable procedure and helper commands.
- `config/video-editing/channel-style.md` is the channel taste profile and learned rules.
- `docs/quickstarts/claude-video-editing.md` covers setup.

## Invocation

When the user runs `/youtube-edit`:

1. Resolve the project or video path. Keep raw media immutable. If `work/review-notes.md` exists, resume from it.
2. Run the preflight and record which tools are available.
3. Probe sources with `tools/video/edl.py probe`.
4. Transcribe each source with Parakeet using `tools/video/parakeet_transcribe.py`.
5. Write the EDL (`work/edit.json`) and resolve every `edl.py plan` warning about word or active-audio boundaries.
6. Render a rough cut and run `edl.py qc` on it.
7. When private/account/location/prohibited information could appear, enable the EDL privacy gate, audit retained transcripts, create output-timeline redactions, run dense `qc --privacy-step 0.5` frames, and verify complete privacy-review coverage. Credentials/secrets use opaque black redaction or are cut; moving data uses full-interval keyframes/swept coverage.
7. Add primary-source evidence b-roll, recorded in the EDL with URL, claim, and capture date.
8. Make HyperFrames graphics: reuse the catalog and approved patterns first. Lint during authoring and run `check --snapshots` as the final gate. Inspect the snapshots, then open the final Studio preview.
9. Render HyperFrames graphics only after approval of that Studio preview, or as labeled unapproved drafts when an unattended request pre-authorized it.
10. Add licensed music or SFX only. Each audio item needs a license note.
11. Render the review cut, run `edl.py qc --frames`, and view the stills. Then write captions (SRT) and `work/review-notes.md`.
12. Return the review render and concise notes.

Do not merely write an editing plan when the user asked for an edit and the required local tools and files are available.

Shorts only when asked. Style rules are persisted only when the user says learn, save, remember, or apply next time.

## Safety / Truth

- Never invent factual b-roll, transcript text, or results.
- Never use unknown-license music or media.
- Never overwrite raw footage.
- Privacy-sensitive edits fail closed: uncertainty means redact/cut and report the unresolved interval; never mark an uninspected range clear.
- Never copy a sensitive value into logs or notes. Record only its category and timestamp.
- Never claim visual or audio verification that was not performed. An FFmpeg exit code of 0 is not QC.
- Do not silently replace Parakeet with another transcription engine.
