# Claude Code Local Video Editing Quickstart

## Purpose

Operator setup and invocation for the AgentDefaults local Claude Code YouTube editing stack.

## Goal

Edit a folder of local recordings with Claude Code, following the role-based pattern from Christian Peverelli's Claude Code editing workflow (<https://youtu.be/HzXD4GVqXwM>):

- Claude Code coordinates.
- Parakeet transcribes. Claude cannot hear, so word timestamps are how it finds cuts.
- FFmpeg assembles and checks the edit through `tools/video/edl.py`, driven by one JSON edit decision list (EDL).
- HyperFrames animates.
- Browser tooling captures source-backed b-roll.
- Tella and a licensed sound library are optional.
- Timestamped feedback, when you ask, becomes persistent style rules.

The full procedure is in [`skills/claude-code-video-editing.md`](../../skills/claude-code-video-editing.md). The contract and approval gates are in [`agents/claude-code-video-editor-agent.md`](../../agents/claude-code-video-editor-agent.md).

## 1. Prerequisites

- Claude Code with local file access
- FFmpeg/ffprobe; required
- Python 3.10+
- Node.js 22+, for HyperFrames
- Disk space for renders. Review cuts at 1080p are cheap even from 4K sources.

```bash
ffmpeg -version | head -1 && node --version && python3 --version
```

## 2. Parakeet

```bash
python3 -m venv .venv-video && source .venv-video/bin/activate
python -m pip install -U pip

# Apple Silicon (MLX)
python -m pip install -U "parakeet-mlx>=0.5"

# NVIDIA / Linux (NeMo)
python -m pip install "nemo_toolkit[asr]>=2.2"
```

Then run:

```bash
python3 tools/video/parakeet_transcribe.py /path/project/raw/cam.mp4 -o /path/project/work/transcripts/cam.json
```

- **Input:** any media file. The helper extracts 16 kHz mono with ffmpeg.
- **Backend:** `--backend auto` uses MLX on Apple Silicon and NeMo elsewhere. Use `--backend mlx|nemo` to force one.
- **Default models:** `mlx-community/parakeet-tdt-0.6b-v3` (MLX) and `nvidia/parakeet-tdt-0.6b-v3` (NeMo). The helper rejects a model meant for the other backend.
- **Output:** schema 2 JSON with `text`, `segments`, and `words`. Each item has `text`, `start`, `end` (seconds, 3 dp), and optional `confidence`. MLX subword tokens are merged into real words.
- **Long recordings:** MLX is chunked at 120 s with 15 s overlap. NeMo switches to local attention past 20 minutes. Parakeet TDT v3 covers 25 European languages with automatic language detection.
- **Model download:** the first run downloads the model weights, so it needs network access once.

If no backend can run, the stack stops before speech editing and reports why. It does not quietly switch to another recognizer.

## 3. HyperFrames

In Claude Code:

```text
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

For agent or non-interactive installs and updates:

```bash
npx hyperframes skills update
npx --yes hyperframes doctor --json | jq -e '.ok'
```

Start a fresh Claude Code session after installing skills. The installed `/hyperframes` skills and `npx hyperframes <cmd> --help` are runtime truth.

The gate sequence:

1. `lint` while authoring.
2. `check --snapshots` as the final automated gate. It includes lint.
3. Inspect the snapshots.
4. `preview --background` gives you a Studio URL.
5. Render only after you approve.

Overlays render with transparency via `render --format mov`, which gives ProRes 4444.

## 4. Invoke

```text
/youtube-edit /absolute/path/to/project-or-video
Tight 8-10 minute technical video. Proof first. Keep the app UI readable. Restrained graphics.
```

Given a single file, the editor creates `<stem>-edit/` next to it. The EDL references the original file in place; it is never copied, moved, or modified.

### Unattended / overnight

```text
/youtube-edit /path/to/project
Run unattended overnight. You may render HyperFrames graphics for the review cut without waiting for preview approval.
```

The second sentence is what pre-authorizes draft graphics. Without it, graphics stay as previewable projects with placeholders in the cut.

Unattended runs never purchase, publish, download unlicensed media, or delete anything. In the morning, read `work/review-notes.md` and watch `renders/review-v1.mp4`.

## 5. What you get

```text
project/
  work/edit.json            every cut, overlay, evidence source, and audio license
  work/review-notes.md      open decisions, seams that need your ears, placeholders
  renders/review-v1.mp4     plus review-v1.mp4.json (timeline) and review-v1.srt
  renders/qc/review-v1/     stills Claude viewed during QC
```

## 6. Give feedback and teach the style

Timestamps refer to the render you watched:

```text
review-v1 0:04 title is too large
0:11 remove the whoosh
0:24 keep the app screen on 2 seconds longer
0:36 this source screenshot treatment is good
```

The editor maps each note through `review-v1.mp4.json` to the exact segment or overlay, applies it, and renders `review-v2`.

To make a preference permanent:

```text
Learn the reusable parts of those notes.
```

Only then does `config/video-editing/channel-style.md` change. Rules get IDs, scopes, and provenance. Contradictions are confirmed with you, and the file is capped at 40 active rules.

The source workflow trained its style hook-first. Edit short hooks with heavy feedback before handing over full videos.

## 7. Optional integrations

- **Browser:** whatever browser automation Claude Code has configured. Evidence captures are recorded inside the EDL, and `plan` rejects evidence without a URL, claim, and capture date.
- **Tella:** use the MCP when it is installed and the footage is Tella-native. Otherwise use Tella's exported files as ordinary sources.
- **Music/SFX:** Epidemic Sound or any library you license. Every audio item in the EDL needs a `license` note, and `plan` rejects items without one.

## Repository Validation

After changing this stack, run:

```bash
python3 tools/video/test_video_tools.py
python3 scripts/validate-claude-video-editing-stack.py
python3 scripts/validate-agentdefaults.py
```

The tests render tiny synthetic media with FFmpeg, and those cases are skipped when FFmpeg is absent. They exercise the Parakeet normalization with fake model output. They do not prove that a real Parakeet model, HyperFrames, browser automation, Tella, or licensed audio works on a given workstation.
