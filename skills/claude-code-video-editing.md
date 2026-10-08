# Claude Code Video Editing Orchestration

## Purpose

This is the executable procedure for the local Claude Code YouTube editing stack. It takes a folder of raw footage through to a QC'd review render and a feedback loop.

Use with `agents/claude-code-video-editor-agent.md`, which defines the contract, gates, and degradation rules. Read `config/video-editing/channel-style.md` before planning pacing, graphics, captions, or sound.

```text
preflight -> probe -> Parakeet transcripts -> EDL (work/edit.json) -> plan warnings fixed
  -> rough render + QC -> evidence b-roll + HyperFrames graphics + licensed audio into the EDL
  -> review render + QC + stills viewed -> review notes -> timestamped feedback -> (optional) style learning
```

Commands below run from the AgentDefaults repository root. `$P` is the absolute path of the video project.

## Project Layout And Resume

```text
$P/
  raw/                      immutable source media; never written
  work/
    probe.json              edl.py probe output
    transcripts/<id>.json   one Parakeet transcript per source file
    edit.json               the EDL: cuts, overlays, evidence, audio (single source of truth)
    review-notes.md         capabilities, open decisions, unverified seams, placeholders, feedback log
    privacy-review.md        privacy categories/ranges and verification evidence; never sensitive values
  graphics/<name>/          one HyperFrames project per graphic
  broll/                    browser captures used as evidence
  audio/                    licensed music/SFX actually used
  renders/                  rough-vN / review-vN .mp4, each with a .json timeline sidecar; qc/ stills; .srt
```

Bootstrap: `mkdir -p "$P"/{work/transcripts,graphics,broll,audio,renders}`. Do not commit private footage.

Given a single file instead of a project, set `$P` to `<file dir>/<file stem>-edit` and point EDL `sources` at the original file in place. Never copy, move, or modify it.

**Resume:** artifacts are checkpoints. On resume, read `work/review-notes.md` first. Skip completed work when inputs and tool/model identities still match; file existence alone is not sufficient. The Parakeet helper validates a transcript's source size/mtime, backend and model identifier before skipping it. A missing or `.partial` render means the run was interrupted, so rerun that render. Both helpers write atomically, so a finished file is never truncated.

## 0. Preflight

```bash
ffmpeg -version | head -1 && ffprobe -version | head -1
node --version                                  # HyperFrames needs >= 22
# Prefer an explicit path, then the shared venv, then a pre-existing legacy .venv-video.
SHARED_VIDEO_VENV="${XDG_DATA_HOME:-$HOME/.local/share}/agentdefaults/video-venv"
if [ -z "${VIDEO_VENV:-}" ]; then
  if test -f "$SHARED_VIDEO_VENV/bin/activate"; then VIDEO_VENV="$SHARED_VIDEO_VENV"
  elif test -f ".venv-video/bin/activate"; then VIDEO_VENV="$PWD/.venv-video"
  else VIDEO_VENV="$SHARED_VIDEO_VENV"; fi
fi
test -f "$VIDEO_VENV/bin/activate" && source "$VIDEO_VENV/bin/activate"
# Reuse installed HyperFrames; no implicit npm download/update during preflight.
if command -v hyperframes >/dev/null 2>&1; then
  hyperframes doctor --json | jq -e '.ok'
else
  npx --no-install hyperframes doctor --json | jq -e '.ok'
fi
python -c "import parakeet_mlx" || python -c "import nemo.collections.asr"
```

Record what is available at the top of `work/review-notes.md`. Apply the agent's degradation table to anything missing. Do not promise a step whose tool failed preflight. Before any installation, inspect existing Python environments, installed tools, and persistent model caches. Use the one-time setup in `docs/quickstarts/claude-video-editing.md` if genuinely missing; never automatically run package upgrades, clear caches, or reinstall model weights per prompt.

## 1. Probe

```bash
python3 tools/video/edl.py probe "$P"/raw/* > "$P/work/probe.json"
```

Act on the warnings:

- **VFR:** typical of screen recorders. The render converts it to constant frame rate.
- **HDR:** phone footage. The render does not tone-map, so tell the user.
- **No audio stream:** the render pads silence.
- **Mixed resolution or fps:** the render scales and pads to the EDL output format.
- **Several audio streams** (for example, OBS with the mic on track 2): both helpers use the first audio stream. Remux the dialogue track first with `ffmpeg -i raw/x.mkv -map 0:v:0 -map 0:a:N -c copy work/x-dialogue.mkv` and use that file as the source.

Do not infer contents from filenames. Grab a still with `ffmpeg -ss <t> -i <file> -frames:v 1 -vf scale=960:-2 still.jpg` and view it.

## 2. Transcribe

```bash
python3 tools/video/parakeet_transcribe.py "$P/raw/cam.mp4" -o "$P/work/transcripts/cam.json"
python3 tools/video/edl.py transcript "$P/work/transcripts/cam.json"                          # segments view
python3 tools/video/edl.py transcript "$P/work/transcripts/cam.json" --words --from 1:10 --to 1:25
```

- Make one transcript per source file. Timestamps are relative to that file, so never transcribe a concatenation.
- **Reuse first:** on matching source fingerprint (size and nanosecond mtime), backend and model identifier, the helper exits without extracting audio, importing the model, or writing the transcript. Legacy/corrupt/mismatched outputs are regenerated. It does not infer that an upstream checkpoint changed under the same model identifier: after an approved model/runtime upgrade, run with `--force` to refresh that transcript.
- Parakeet MLX weights use the persistent Hugging Face cache (default `~/.cache/huggingface/hub`, configurable via `HF_HOME` / `HF_HUB_CACHE`); NeMo uses its own model cache. Preserve both between sessions, worktrees and videos. Cache lookup must precede downloads; unchanged model files should never be fetched again.
- The helper extracts 16 kHz mono itself. It chunks long audio on MLX (120 s chunks, 15 s overlap) and switches NeMo to local attention past 20 minutes.
- `words` are whole words on both backends. Each has `start`/`end` in seconds and optional `confidence`; treat low-confidence words around a cut with suspicion.
- Read segments for structure. Load word rows only for the windows you are about to cut, to keep context small.
- ASR misspells product names, commands, and acronyms. Fix them in captions and notes, never by editing transcript timestamps.
- An empty `words` list means no speech was recognized. Say so; do not invent text.

## 3. Edit Decisions (the EDL)

Write `$P/work/edit.json`. The format is documented in `tools/video/edl.py`'s docstring.

```json
{"output": {"width": 1920, "height": 1080, "fps": 30, "loudness": -14},
 "sources": {"cam": {"path": "../raw/cam.mp4", "transcript": "transcripts/cam.json"}},
 "segments": [{"source": "cam", "start": "2:14.32", "end": "2:31.05", "note": "hook: working build on watch"},
              {"source": "cam", "start": "0:08.90", "end": "0:41.60", "note": "why it matters"}]}
```

Segments play in list order. Reordering for a proof-first hook is allowed when continuity stays truthful. Every `note` should say why the range is kept.

### Choosing cut points

Transcript timestamps locate a cut; they do not prove the cut is acoustically clean.

1. Find the candidate boundary from word rows: the end of a complete sentence or clause.
2. Run `edl.py silences <source> --noise-db -35 --min 0.2` and put the boundary inside the pause between the last kept word's `end` and the next word's `start`. Prefer a point about 80–150 ms clear of both words.
3. Run `python3 tools/video/edl.py plan "$P/work/edit.json"` and resolve every warning:
   - `cuts inside word`: move the boundary. Never ship this.
   - `lands in active audio`: the 40 ms window around the cut is louder than −35 dBFS. Move the boundary into a pause, or list it in `review-notes.md` as an unverified seam for human listening.
   - `overlap ... content repeats`: intentional only for a deliberate callback.
4. Retakes: the last complete take is usually best, but compare complete meaning first. If two takes are both plausible, choose one and record the alternative as an open decision.
5. Keep pauses that viewers need for reading code, terminal output, or UI changes, and for watching a result land.

The render adds 10 ms micro-fades at every seam to stop clicks. They do not repair a bad boundary.

### Multiple recordings

First classify the relationship.

**Sequential stop/restart recordings:** these are consecutive takes of one intended video, not synchronized multicam sources. Read both transcripts around the boundary, identify duplicated setup/explanation, false starts, and the strongest complete continuation, then place ordinary EDL segments from each source in narrative order. Do not concatenate blindly and do not force an offset.

**Synchronized camera/screen recordings:** these need an offset. Find the same spoken phrase in both transcripts; the difference in their word timestamps is the offset. Use the recording with the better microphone as `segments`. Add the other as a video overlay whose `start` is the matching source time and whose `box` sets the picture-in-picture or full-frame placement. Overlays are picture-only.

## 4. Rough Render And QC

```bash
python3 tools/video/edl.py render "$P/work/edit.json" -o "$P/renders/rough-v1.mp4" --preset veryfast --crf 23
python3 tools/video/edl.py qc "$P/renders/rough-v1.mp4" --frames "$P/renders/qc/rough-v1"
```

`render` refuses to overwrite an input. It writes `<output>.json`, a timeline sidecar mapping output time to source time for that exact render.

`qc` exits non-zero on hard issues: missing streams, duration, resolution, or fps not matching the plan, or audio and video stream lengths differing by more than 0.1 s. It also lists black and silence ranges and loudness for review.

View the stills it writes. Rendering 4K sources at 1080p output works as a proxy review cut. Use native resolution only for the final render.

## 4.5 Privacy-Critical Pass

Use this pass whenever the user specifies information that must not appear, or the footage contains screens where private/account/credential/location data could surface.

Privacy review happens against the **retained output timeline**, not just the raw transcript.

### 4.5.1 Define the policy in the EDL

Redactions are output-timeline entries. **Use `blur` by default for non-secret details** (emails, names, account IDs, location hints that are not independently prohibited, paths and notifications). Keep the blur as small as practical with adequate padding and motion coverage, so the video looks natural rather than obscured by conspicuous black boxes. Inspect encoded frames to ensure blurred text cannot be inferred from remaining pixels or surrounding context.

**For actionable secrets** (credentials, tokens, auth codes, private keys, recovery values), prefer **cutting the shot**. Never rely on blur for secrets. Use opaque `black` only as a last-resort fallback when the shot is essential and the sensitive region can be bounded safely. If the user's prohibited context is still clear after blurring, reframe or cut the scene instead.

For moving/scrolling information, keyframe `at` values are relative to the redaction start and must cover `0..duration`. The renderer covers the swept bounding region between consecutive keyframes plus padding, intentionally preferring excess coverage over a tracking miss. If the area cannot be safely bounded, cut the section.

Set `privacy.required=true`, keep `visual_reviewed=false` and `transcript_reviewed=false` until the corresponding reviews actually happen, and use `privacy.reviews` to record reviewed output intervals without copying sensitive values.

### 4.5.2 Audit spoken content

Search/read every retained transcript for the user's prohibited categories/terms plus contextual variants. A location-removal request is semantic: remove direct mentions and surrounding wording that still discloses the location.

Set `privacy.transcript_reviewed=true` only after this pass.

### 4.5.3 Audit visuals densely

Render the rough cut, then:

```bash
python3 tools/video/edl.py qc "$P/renders/rough-v1.mp4" --edl "$P/work/edit.json" \
  --frames "$P/work/privacy-frames/rough-v1" --privacy-step 0.5
```

Inspect **every generated privacy frame**, in batches. Also inspect/play intervals where notifications, scrolling, tab switching, terminal output, account menus, file paths, maps/weather/time-zone content, or other short-lived sensitive surfaces could appear. Dense cadence sampling does not prove safety for a flash shorter than the cadence.

Record only categories and ranges in `work/privacy-review.md`; never copy the sensitive value.

After each reviewed contiguous interval, add a `privacy.reviews` entry with `start`, `end`, `status` (`clear` or `redacted`), and the actual review `method`. The ranges must cover the complete retained output. Set `privacy.visual_reviewed=true` only after that coverage is real.

Run `python3 tools/video/edl.py plan "$P/work/edit.json"`. The plan must fail while privacy review coverage has gaps.

### 4.5.4 Final privacy gate

After graphics, evidence b-roll, layout changes, and redactions are all present, render the final review cut and repeat the dense privacy sweep. Verify the beginning/middle/end of every redaction and every moving-redaction slice.

Do not reuse a rough-cut privacy approval after compositing changed. If any user-prohibited context remains or a region cannot be conclusively cleared, redact/cut it and re-run the affected review range.

## 5. Evidence B-roll

Use this when the narration makes an externally verifiable claim, such as an announcement, release, benchmark, paper, repository, pricing, or a post.

1. Find the primary source (first-party page, repository, release notes, paper, or original post) with the available browser tool.
2. Capture only what supports the claim into `$P/broll/`. Scroll recordings and highlight/zoom treatments are best built as a HyperFrames composition around the capture.
3. View the capture. It must establish the claim as spoken, not a neighboring claim.
4. Add it to the EDL so the chain *spoken claim → source → capture → timeline usage* is machine-checked:

```json
{"file": "../broll/release-notes.png", "at": 41.2, "duration": 4, "kind": "evidence",
 "evidence": {"claim": "<claim as spoken> (seg 4)", "url": "https://...", "title": "Release notes", "captured": "2026-10-05"},
 "box": [960, 120, 900, 840]}
```

`plan` refuses an evidence overlay without `claim`, `url`, and `captured`, and a `broll` overlay without `license`.

Do not download third-party video or images without a usage basis. Without a browser or network, record a placeholder.

## 6. HyperFrames Graphics

Setup: in Claude Code, `claude plugin marketplace add heygen-com/hyperframes` then `claude plugin install hyperframes@hyperframes`. For agent or non-interactive installs, `npx hyperframes skills update`. The installed `/hyperframes` skills and the CLI's `--help` are runtime truth over this file.

Per graphic:

1. Reuse first. Check the approved motion patterns in `channel-style.md`, then run `npx hyperframes catalog --query <words>` and `npx hyperframes add <block>`. Hand-author only when nothing fits.
2. `cd "$P/graphics" && npx hyperframes init <name> --non-interactive --resolution landscape`. Use `portrait` for Shorts. `init` creates `index.html` and `hyperframes.json` but no `compositions/` or `assets/` directories.
3. Author. Run `npx hyperframes lint` after the first pass and after structural edits.
4. Run `npx hyperframes check --snapshots` as the final gate. It reruns lint, so do not run a standalone lint right before it. A static composition fails with `sweep_static`, so add motion or shorten it. View the PNGs under `snapshots/`.
5. Run `npx hyperframes preview --background`, confirm the URL answers, and give it to the user.
6. Render only after approval, or as an unattended draft under the agent's rules:
   - overlay with transparency: `npx hyperframes render --quality looks --format mov --output ../../renders/graphics/<name>.mov` (ProRes 4444 with alpha)
   - full-frame card: `--format mp4`
   - final delivery: `--quality delivery`
7. Run `test -s` on the output, then add it to the EDL as `"kind": "graphic"` with `at`, an optional `box`, and an optional `fade`.

Graphics clarify the narration: titles, short lists, diagrams, code or number emphasis, comparison cards, and authentic logos. They never cover the UI being discussed.

## 7. Sound

Every EDL `audio` item needs a `license` note, such as `"Epidemic Sound subscription, track <id>"` or `"own recording"`. `plan` refuses items without one.

| Use | Typical `gain_db` | Notes |
|---|---|---|
| Music bed under instruction | −28 to −34 | Use fades. Stop or drop it for dense explanations. |
| Hook or suspense bed | −22 to −26 | Only where the style profile asks for it. |
| SFX on a meaningful visual event | −12 to −20 | Not on every text pop. |

Beds are fixed-gain with no sidechain ducking, so keep them low. Set `output.loudness` (−14 LUFS is a common YouTube target) and confirm the measured value in `qc`.

When the user asks to audition sounds, render short hook variants (`review-hook-sfx-a.mp4`, `-b`, and so on) from copies of the EDL rather than guessing. Record the choice.

## 8. Review Render, Captions, Notes

```bash
python3 tools/video/edl.py render  "$P/work/edit.json" -o "$P/renders/review-v1.mp4"
python3 tools/video/edl.py qc      "$P/renders/review-v1.mp4" --frames "$P/renders/qc/review-v1"
python3 tools/video/edl.py captions "$P/work/edit.json" -o "$P/renders/review-v1.srt"   # --max-chars 20 for Shorts
```

- View the stills for the hook, every overlay, a sample of seams, and the ending.
- When privacy is required, run dense final privacy frames, inspect every generated frame plus redaction boundaries, and ensure `edl.py plan` has no privacy coverage errors.
- Captions are remapped from source transcripts to output time. Words cut partway are dropped.
- Long-form gets an SRT for upload, not burned-in captions, unless the user asks. Correct technical terms in the SRT text.
- If the user asks to burn captions and `ffmpeg -filters` lacks `subtitles`, use the HyperFrames `embedded-captions` workflow instead.
- `work/review-notes.md` lists open decisions, unverified seams (output timestamps), placeholders, unapproved-draft graphics, and evidence URLs.

## 9. Timestamped Feedback

Feedback timestamps refer to a specific render. Map them with that render's sidecar (`renders/review-vN.mp4.json`). Find the segment where `out_start <= t < out_end`; then `source_t = start + (t - out_start)`. Overlays and audio carry their own `at` values.

Log every note in `review-notes.md`:

```text
| render | t | note | target | action | persist? |
| review-v1 | 0:11 | remove the whoosh | audio 2 | removed | no |
| review-v1 | 0:04 | title too large | overlay 0 (title.mov) | box 1200→900 wide | asked: yes -> R-014 |
```

Apply the notes to the EDL and graphics, re-render as `review-v2`, and run QC again. That is one targeted fix pass.

## 10. Style Learning

Persist only what the user explicitly asks to learn, save, remember, or apply next time. Follow the rule format and pruning rules in `config/video-editing/channel-style.md`:

- give each rule an ID, a scope, and provenance
- update or supersede an existing rule instead of adding a near-duplicate
- keep the active rule count under the cap

If a new request contradicts an active rule, ask whether it is a one-off or a new rule before persisting it.

## Shorts (only when requested)

1. From the long-form segment transcript, list 3–5 candidate moments of 20–60 s. Each must stand alone: a hook in the first 2 s, one idea, and a payoff. Give output timestamps and a one-line reason. Let the user pick unless they asked you to choose.
2. Write `work/short-NN.json` with output `1080x1920` and per-segment `crop: [x, y, w, h]` reframing the important region. Use a 9:16 window over the face, the UI, or a code region.
3. Keep captions and graphics inside the central area, clear of the bottom quarter and the right edge where platform UI sits. Check this on the stills.
4. Make captions with `captions --max-chars 20`. Burn them through HyperFrames `embedded-captions`, or with FFmpeg when `subtitles` is available.
5. Render and run QC the same way as long-form.

## Stop Rule

A first-pass edit ends after one broad pass and one targeted QC/fix pass. Further creative refinement needs user feedback or a failed acceptance check. Repeated identical tool failures end with a concise blocker, not a retry loop.
