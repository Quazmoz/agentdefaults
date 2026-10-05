# Claude Code Local Video Editing Quickstart

## Purpose

Provide the operator setup and invocation path for the AgentDefaults local Claude Code YouTube editing stack.

## Goal

Edit a local YouTube recording with Claude Code using the same role-based pattern demonstrated in Christian Peverelli's Claude Code editing workflow:

- Claude Code coordinates
- Parakeet transcribes
- HyperFrames animates
- browser tooling researches/captures factual b-roll
- Tella can handle Tella-native screen recordings when connected
- a licensed sound library can supply music/SFX
- FFmpeg assembles and performs technical QC

## 1. Prerequisites

Core:

- Claude Code with local project/file access
- Node.js 22+
- FFmpeg / ffprobe
- Python environment capable of running a supported Parakeet backend (MLX on Apple Silicon or NeMo elsewhere)
- enough disk space for intermediate renders

Verify:

```bash
node --version
ffmpeg -version
ffprobe -version
python3 --version
```

## 2. HyperFrames

Use the current HyperFrames skills:

```bash
npx hyperframes skills update
```

Alternative interactive installation:

```bash
npx skills add heygen-com/hyperframes
```

Start a fresh Claude Code session after skill installation if the commands are not discovered.

## 3. Parakeet

AgentDefaults includes:

`tools/video/parakeet_transcribe.py`

The helper supports two Parakeet runtimes and normalizes both to the same transcript JSON:

- **Apple Silicon:** prefer `parakeet-mlx`, which uses MLX and exposes aligned sentence/token timestamps.
- **Other supported systems / NVIDIA-oriented environments:** use NVIDIA NeMo ASR.

Apple Silicon setup:

```bash
python3 -m venv .venv-video
source .venv-video/bin/activate
python -m pip install --upgrade pip
python -m pip install -U parakeet-mlx
```

NeMo setup:

```bash
python3 -m venv .venv-video
source .venv-video/bin/activate
python -m pip install --upgrade pip
python -m pip install "nemo_toolkit[asr]"
```

Run:

```bash
ffmpeg -i raw/input.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le work/transcript.wav
python3 tools/video/parakeet_transcribe.py work/transcript.wav -o work/transcript.json
```

Default models:

```text
MLX:  mlx-community/parakeet-tdt-0.6b-v3
NeMo: nvidia/parakeet-tdt-0.6b-v3
```

`--backend auto` is the default: it selects MLX on Apple Silicon and NeMo elsewhere. Use `--backend mlx` or `--backend nemo` to force one explicitly.

The helper writes a normalized JSON object with full text, segment timestamps, and word/token timestamps.

If the local OS/hardware cannot support the chosen Parakeet runtime, stop and report the environment issue rather than pretending transcription succeeded.

## 4. Invoke the native Claude skill

From this repository:

```text
/youtube-edit /absolute/path/to/video.mp4
```

Or be explicit:

```text
/youtube-edit /path/to/video.mp4
Make this a tight 6-8 minute technical YouTube video. Keep the real app/demo footage readable, use primary-source proof when I reference external claims, and keep motion graphics restrained.
```

## 5. HyperFrames review loop

Inside each HyperFrames project, use lint while iterating, then the final gate/review flow:

```bash
# Fast iteration check after the first pass and structural edits
npx hyperframes lint

# Final automated gate; includes lint
npx hyperframes check --snapshots

# Inspect the generated snapshots, then review the final Studio project
npx hyperframes preview --background
```

Do not run a redundant `lint` immediately before `check`. After the final Studio preview has received the approval required by the installed HyperFrames review workflow, render:

```bash
npx hyperframes render --quality looks --output ../../renders/graphics-section.mp4
test -s ../../renders/graphics-section.mp4
ffprobe -v error -show_format -show_streams ../../renders/graphics-section.mp4
```

Use `--quality delivery` for the final delivery encode when appropriate. Treat the installed HyperFrames skill as runtime truth if its CLI/review contract changes.

## 6. Optional integrations

### Browser research

Use whatever browser automation Claude Code has actually been configured to access.

Record sources in:

`work/source-manifest.md`

### Tella

Use Tella MCP only when installed and the source recording/workflow benefits from its native operations. The editing stack must still work without it.

### Music / SFX

Epidemic Sound is a good fit when the account/connector is available, but any user-licensed library is acceptable. Never pull random online audio into the edit and label it safe.

## 7. Teach the style

Give timestamped notes, for example:

```text
0:04 title is too large
0:11 remove the whoosh
0:24 keep the app screen on 2 seconds longer
0:36 this source screenshot is good; use this treatment again
```

Then, only when you want the preference persisted:

```text
Apply those notes, then learn the reusable parts and update config/video-editing/channel-style.md.
```

This keeps one-off feedback out of the permanent rules while allowing the editor to improve over time.

## 8. Final QC

Before calling a video done:

```bash
ffprobe -v error -show_streams -show_format renders/final.mp4
ffmpeg -i renders/final.mp4 -vf "blackdetect=d=0.20:pix_th=0.10" -an -f null -
ffmpeg -i renders/final.mp4 -af "silencedetect=n=-50dB:d=1.0" -vn -f null -
```

Review the detected ranges; some black/silence is intentional.

Also manually/playback-check:

- hook
- edited speech seams
- dense screen-demo sections
- graphics
- researched proof/b-roll
- final 20-30 seconds

Machine checks supplement playback review; they do not replace it.


## Repository Validation

After changing this stack, run:

```bash
python3 scripts/validate-claude-video-editing-stack.py
python3 scripts/validate-agentdefaults.py
```

These repository validators check stack structure and invariants. They do not prove that local NeMo/Parakeet, HyperFrames, browser automation, Tella, or licensed-audio integrations are installed and operational on a particular workstation.
