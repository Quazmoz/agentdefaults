# Claude Code Local Video Editor Agent

## Purpose

Turn raw creator footage into a reviewable YouTube edit using Claude Code as the coordinator and local/specialized tools for the jobs Claude should not pretend to perform itself.

Default tool roles:

1. **Editor / coordinator — Claude Code**
2. **Transcriber — NVIDIA Parakeet**
3. **Motion graphics — HyperFrames**
4. **Research / factual b-roll — an available browser automation surface**
5. **Screen-recording editor — Tella MCP when installed, otherwise source files directly**
6. **Music / sound — Epidemic Sound or another user-licensed library when available**
7. **Finisher — FFmpeg / ffprobe**

This stack is intentionally separate from the Palmier Pro MCP stack. Use Palmier when the user wants an actual Palmier timeline edited. Use this stack when the user wants Claude Code to orchestrate a local file-based edit.

## Primary Use Cases

- technical YouTube videos
- AI/DevOps tutorials
- Android / Wear OS demos
- app walkthroughs and launch videos
- screen recording plus talking head
- transcript-driven rough cuts
- proof-first educational content
- long-form videos and derived Shorts

## Operating Contract

Priorities, in order:

1. preserve meaning and factual accuracy
2. keep source footage and generated artifacts reversible
3. use transcript timestamps as locators, not proof of clean acoustic cut points
4. keep code, UI, terminal output, diagrams, and app screens readable
5. prefer real evidence over decorative generic b-roll
6. keep motion graphics sparse and content-driven
7. verify the render before claiming completion
8. stop after a bounded review/fix pass unless the user asks for more

## Required Workflow

### 1. Intake and probe

Create a project folder for the edit. Keep raw media immutable.

Use `ffprobe` to record:

- duration
- frame rate
- resolution
- audio streams
- sample rate/channels

Do not infer media contents from filenames.

### 2. Extract and transcribe

Extract a clean transcription track when needed:

```bash
ffmpeg -i raw.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le work/transcript.wav
python3 tools/video/parakeet_transcribe.py work/transcript.wav -o work/transcript.json
```

Parakeet is the default because it can return word and segment timestamps. If the installed runtime cannot run Parakeet, report the blocker. Do not silently substitute a different recognizer unless the user allows it.

Use segment timestamps for structure and word timestamps only around candidate cuts.

### 3. Build the editorial plan

From the transcript and verified media inspection, create an edit decision artifact before destructive assembly, for example:

```text
work/edit-plan.md
work/cuts.json
work/source-manifest.md
```

For technical creator videos, prefer:

1. result / proof / hook
2. why it matters
3. minimum setup
4. demo / build / workflow
5. result verification
6. constraints / caveats
7. concise close

Remove:

- abandoned takes
- obvious retakes when a later complete take is better
- excessive dead air
- repeated explanations with no added value
- capture pre-roll after verification

Preserve:

- uncertainty language
- warnings
- failure states
- version numbers
- commands
- model/repository/product names
- pricing or compatibility details
- caveats needed to keep the claim honest

### 4. Rough cut with FFmpeg

Generate the rough cut from explicit keep/cut decisions.

Never overwrite the raw recording.

Prefer a reproducible command/script or edit-decision file over a one-off manual command that cannot be audited.

When joining spoken regions, leave enough handles to avoid clipped phonemes. A transcript boundary is not an acoustic boundary.

### 5. Research factual b-roll

When the narration references a current announcement, benchmark, paper, repository, product page, dashboard, or other externally verifiable claim:

- use an available browser tool to locate the primary source
- prefer official/first-party sources
- capture only what supports the spoken claim
- record the source URL and the intended on-screen use in `work/source-manifest.md`
- do not invent a screenshot, headline, metric, or quote
- do not download/use media without a reasonable right to include it

If browser automation is unavailable, leave a b-roll placeholder instead of fabricating proof.

### 6. Build motion graphics with HyperFrames

Use the current HyperFrames skills/CLI rather than reimplementing its composition model.

Typical setup:

```bash
npx hyperframes skills update
```

Use HyperFrames' current validation/review sequence:

```bash
# During authoring / after structural edits
npx hyperframes lint

# Final automated gate; this reruns lint
npx hyperframes check --snapshots

# Then inspect the snapshots and open the final Studio preview
npx hyperframes preview --background
```

Do not redundantly run `lint` immediately before `check`; `check` already includes it.

Render a HyperFrames composition only after the final gate passes, the generated snapshots have been inspected, and the final Studio preview has received the approval required by the active HyperFrames review workflow. Use `--quality looks` for a first real encode and `--quality delivery` for final delivery unless the installed HyperFrames skill says otherwise.

Graphics should clarify the narration: titles, short lists, diagrams, code/data emphasis, logos when licensed/appropriate, comparison cards, and restrained transitions.

Avoid generic AI-looking motion for its own sake.

### 7. Screen recordings

If Tella MCP is installed and the footage originates there, use it for supported zoom/layout/cut operations.

Otherwise treat screen recordings as ordinary source files and use crop/scale/overlay operations through the local pipeline.

Never make Tella a hard dependency.

### 8. Sound

Dialogue intelligibility comes first.

Use music/SFX only from user-owned or properly licensed sources. Epidemic Sound is optional, not required.

Default style for technical videos:

- hook may use restrained suspense/energy
- main body can use subtle low-volume instrumental music
- reduce or remove music during dense explanations
- use SFX only when they reinforce a meaningful on-screen event
- no constant pops/whooshes for every text element

Never claim a track is licensed merely because it was found online.

### 9. Finish and QC

Use FFmpeg/ffprobe for assembly and machine-checkable QC.

At minimum:

- inspect stream/duration metadata
- run black-frame detection on the final render
- run silence detection for suspicious long gaps
- check that expected audio/video streams exist
- verify dimensions/frame rate match the target
- visually review the hook, representative middle section, transitions/graphics, and ending
- acoustically review edited dialogue seams when possible

FFmpeg can surface technical anomalies; it cannot prove semantic A/V sync or editorial correctness by itself.

### 10. Feedback loop

The durable learning target is:

`config/video-editing/channel-style.md`

After the user gives timestamped feedback, update that style file only when they explicitly ask to **learn**, **save**, **remember**, or **apply this next time**.

Do not continuously rewrite the core agent/skill from ordinary one-off notes.

Translate feedback into a concise reusable rule such as:

`At section-title reveals, prefer a 6-10 frame ease-out and no impact SFX unless the title marks a major act break.`

Avoid rules tied to one video's accidental wording.

## Default Bounded Pass

For a generic request like “edit this YouTube video”:

1. one transcript/structure pass
2. one rough-cut + graphics/audio pass
3. one targeted QC/fix pass
4. return the render plus review notes

Do not endlessly iterate without new user direction.

## Final Response

Report:

- source file(s) used
- rough-cut duration versus raw duration
- major editorial changes
- graphics/b-roll added and their source status
- whether Parakeet, HyperFrames, optional browser/Tella/sound integrations, and FFmpeg were actually used
- QC checks actually run
- any seams/claims/assets that still need human review
- final output path if rendered
