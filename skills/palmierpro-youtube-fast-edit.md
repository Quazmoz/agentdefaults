# Palmier Pro YouTube Fast Edit

## Purpose

Provide a repeatable, low-friction first-pass editing workflow for long-form YouTube videos edited through Palmier Pro MCP from Claude Code or OpenAI Codex.

The skill is optimized for technical creator footage: screen recordings, terminal/code demos, app walkthroughs, AI/DevOps workflows, product demonstrations, talking head plus screenshare, and proof/result-driven videos.

The objective is not cinematic perfection. The objective is a safe, coherent, watchable first cut that removes obvious waste, preserves technical truth, keeps important screens readable, and is ready for fast human review.

## Runtime Contract

Use this skill only when Palmier Pro MCP tools are available.

Palmier's current external MCP endpoint is:

```text
http://127.0.0.1:19789/mcp
```

Use the live MCP tool schemas as runtime truth. Repository examples are guidance, not permission to guess arguments.

For external Claude/Codex MCP sessions, do not depend on Palmier's in-app-only `read_skill` or `manage_skills` tools.

## Default Mode

When the user says any equivalent of:

```text
edit this video
clean this up
make a YouTube cut
make this watchable
quick first pass
```

and does not request a different style, use **Technical YouTube Fast Edit**:

- long-form 16:9 unless the current project clearly says otherwise
- proof/result-forward opening
- balanced speech cleanup
- no burned-in captions by default
- sparse titles/callouts only when they improve comprehension
- screenshare/code/UI readability over visual novelty
- no paid generation
- no source-media deletion
- no export unless requested
- one broad edit pass plus one verification pass, then return for review

## Preconditions

Before mutation:

1. Confirm Palmier MCP is reachable.
2. Resolve the target project without guessing.
3. Call `get_timeline`.
4. Call `get_media`.
5. Record the active timeline identity, fps, resolution/aspect, total duration, track types, clip IDs, linked A/V state, and available media.
6. If the task is a broad first-pass edit, preserve the original timeline before editing.

If no project is active and `manage_project` is available, use `manage_project` with `action=list`. Open a project only when the user's target is unambiguous; otherwise report the blocker.

## Preserve The Original

For a broad first-pass, structural rewrite, short-form variant, or other edit that could materially change pacing or order:

1. Get the exact active `timelineId` from current Palmier state.
2. Call `create_timeline` with `from=<active timelineId>` and a clear name such as `YouTube Fast Cut`.
3. Re-read `get_timeline` immediately because every copied clip and track receives new IDs.
4. Perform the edit on the copy.

Do not duplicate the timeline for a tiny, explicitly requested in-place adjustment.

## Inspection Strategy

Avoid blind editing and avoid loading unnecessary detail.

### Long recordings

Start with:

```text
get_transcript granularity=segments
```

Use sentence/segment-level transcript reading to understand structure cheaply. Drill into word mode only around ranges that need cuts.

For source visuals, use `inspect_media` with `overview=true` when available. Use targeted `startSeconds`/`endSeconds` windows for exact visual boundaries.

Use `search_media` when looking for a semantic moment such as:

- the successful demo
- the approval result
- the terminal output proving it worked
- the section about pricing
- the best intro take
- the app running on-device

Never infer media contents from filenames alone.

## Story Pass

For technical YouTube, identify these beats from the actual footage:

1. **Proof / hook** — what worked, changed, shipped, connected, or was learned.
2. **Problem / value** — why the viewer should care.
3. **Setup** — only what is required to reproduce or understand the demo.
4. **Build / workflow** — the useful implementation path.
5. **Proof / result** — concrete output, behavior, benchmark, approval, or working UI.
6. **Constraints / caveats** — requirements, limitations, cost, compatibility, or failure cases.
7. **Close** — only if the source contains a natural ending or the user asks for one.

Do not manufacture narration or claims. Reordering is allowed only when existing clips can form a truthful, coherent sequence.

## Cleanup Pass

### Capture pre-roll

Many technical recordings begin on OBS, QuickTime, a recorder window, or a moment before the intended screen appears. Inspect the start of each source recording and remove only the verified pre-roll.

Do not hard-code a 0.5-1 second cut. The boundary must come from inspection.

Use a word-aligned edit when speech is part of the unwanted pre-roll. Use `ripple_delete_ranges` for visual-only/non-word-aligned ranges.

### Silence

Use `remove_silence` for clear dead air when the user requested a cleanup pass and the selected clips represent one compatible A/V unit.

Keep pauses that viewers need to:

- read terminal output
- inspect code
- follow UI changes
- understand a complex caveat
- see an asynchronous operation complete

Do not remove every breath.

### Filler and retakes

Use `get_transcript` + `remove_words` for:

- obvious ums/uhs
- immediate false starts
- duplicated words
- abandoned fragments
- duplicate takes where one version is clearly superior
- repeated explanations that add no information

Rules:

- Default `cutAggressiveness=balanced` for long-form YouTube.
- Do not globally remove ambiguous words such as `like`, `so`, or `well`.
- Re-read `get_transcript` after every `remove_words` mutation because indices shift.
- Preserve technical terms, commands, versions, model names, prices, compatibility limits, warnings, caveats, and uncertainty language.
- Never create misleading speech through omission.

## Visual Pass

For technical videos:

- Keep screenshare, app UI, code, terminal, diagrams, Play Console, GitHub, or other proof visuals large enough to read.
- Prefer screenshare as the primary visual while the speaker explains something on-screen.
- Use facecam where it adds trust, reaction, or a natural human beat; do not cover important UI.
- Use `apply_layout` for common facecam/screenshare arrangements and verify with `inspect_timeline`.
- Use `add_texts` for concise titles, repo/app names, commands, section labels, and callouts.
- Use current text-style features such as outline, shadow, or background when supported by the live schema instead of duplicating text layers merely to fake legibility.
- Do not add decorative motion, zooms, or effects unless they improve comprehension.

### Long-form captions

Do not burn automatic captions into long-form 16:9 videos by default.

Use `add_captions` only when:

- the user explicitly asks for captions, or
- the output is a Short/Reel/TikTok-style vertical cut where captions are part of the requested format.

## Audio Pass

Priorities:

1. intelligible dialogue
2. intact A/V sync
3. no abrupt cut seams
4. consistent enough level for review

Use `denoise_audio` only when noise is actually present or the user requests cleanup. Do not apply audio processing by reflex.

When independent audio/video trims are needed, respect current link state and use `manage_clip_links` deliberately rather than assuming clips are safe to separate.

## Transitions

Technical YouTube defaults to clean cuts.

Use transitions sparingly at actual section boundaries. If a fade or dip is useful, implement it using the live keyframe/property schema and verify the result with `inspect_timeline`.

Do not spend the fast-edit pass building decorative transitions between routine cuts.

## Review Markers

When a choice is genuinely ambiguous but the rest of the edit can continue, prefer a persistent review marker over a risky guess.

Use `manage_markers` with an `open` marker for cases such as:

- two plausible takes with no objective winner
- an uncertain factual cut
- a section that may need a custom asset
- a visual that needs the user's brand preference
- a possible sponsor/legal/brand-sensitive removal

Only move a marker to `review` after the requested edit has been applied and verified. Mark it `resolved` only after explicit user approval or instruction.

## Paid Generation Boundary

Do not call:

```text
generate_image
generate_video
generate_audio
upscale_media
```

without explicit user approval for the specific generation/upscale action.

Before proposing generation:

1. call `list_models`
2. confirm `get_timeline.canGenerate`
3. state the intended asset, model/capability, duration/aspect when relevant, and prompt
4. wait for approval

Do not retry a failed paid generation blindly.

## Export Boundary

Do not export unless the user asks.

When the user asks for a normal YouTube review/final render and does not specify otherwise, use the live schema with these defaults:

```text
mode: video
codec: H.264
resolution: Match Timeline
overwrite: false
```

Omit `outputPath` unless the user provides one.

Use `manage_exports action=list` to report actual status. Never infer that a render succeeded or stalled from elapsed time alone.

## Failure Handling

For a failed tool call:

1. Read the actual error.
2. Check the live tool schema before changing arguments.
3. Re-read state when stale IDs, copied timelines, undo, manual user edits, or track changes could be involved.
4. Retry only when the correction is obvious and safe.
5. Stop after repeated identical failures instead of looping.
6. Never retry paid generation automatically.

After `undo`, timeline copy/switch, or any operation documented to invalidate IDs, re-read the required state before the next mutation.

## Verification Pass

Before declaring the fast edit complete:

1. `get_transcript` the edited timeline or relevant windows and check for dangling speech/meaning changes.
2. `inspect_timeline` the opening/hook.
3. `inspect_timeline` at least one representative technical/demo section.
4. `inspect_timeline` every important text/layout change.
5. Inspect the ending if it was modified.
6. Confirm no unintended caption track was added to long-form.
7. Confirm no paid generation occurred without approval.
8. Confirm the original timeline remains available when this was a broad edit.

Do not claim frame-perfect visual quality beyond what was actually inspected.

## Stop Conditions

The default fast-edit task ends after:

- one broad editing pass
- one targeted verification/fix pass
- unresolved subjective choices marked for review

Do not keep micro-polishing indefinitely. Return control to the user for timeline review.

## Output Contract

Keep the completion message compact:

```text
Done — created a YouTube Fast Cut, tightened the opening and retakes, removed verified dead air, kept the technical demo readable, and checked the hook plus key overlays. I left 2 review markers for subjective take choices. No paid generation or export was run.
```

If export was requested, additionally report the returned export job/destination and current status.

## Quality Bar

A successful fast edit:

- starts from live Palmier state
- preserves the original for broad changes
- uses current tool schemas and exact IDs
- improves pacing without changing technical meaning
- keeps code/UI/proof readable
- preserves A/V sync
- avoids default long-form burned captions
- uses review markers instead of guessing subjective decisions
- performs no unapproved paid generation or source deletion
- verifies representative viewer-visible output
- terminates after a bounded first-pass workflow
