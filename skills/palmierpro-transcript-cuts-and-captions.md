# Palmier Pro Transcript Cuts and Captions

## Purpose

Provide a reusable, provider-neutral workflow for transcript-driven editing, filler/retake cleanup, dead-air reduction, and caption creation in Palmier Pro through external MCP.

Use this skill from Claude Code or OpenAI Codex when tightening talking-head, tutorial, demo, podcast/interview, or screen-recording footage.

## Core Principle

Use transcript editing to remove low-value speech while preserving meaning.

Do not optimize for the maximum number of cuts. Optimize for a natural, accurate, watchable result.

Transcript timestamps are semantic locators, not guaranteed acoustic cut points. The actual spoken audio is authoritative for dialogue boundaries.

## Runtime Truth

Use the live Palmier MCP schema for exact arguments and limits.

Do not assume transcript shape, index limits, caption styling fields, or tool availability from stale examples.

## Source Transcript vs Timeline Transcript

Palmier exposes two different concepts:

| Surface | Use |
|---|---|
| `inspect_media` | Understand one raw source asset in source-time context. |
| `get_transcript` | Understand what is currently audible on the edited timeline in project frames. |

For timeline speech cleanup, default to `get_transcript`.

For long-form comprehension, use segment-level transcript granularity first when supported. Use word-level data only where cuts are needed.

## Safe Transcript Workflow

```text
1. get_timeline
2. get_transcript granularity=segments   # structure/comprehension when useful
3. identify candidate ranges
4. get_transcript in word mode for the target window
5. remove_words using current exact indices
6. get_transcript again
7. verify the local dialogue seam against actual audio/source handles where the tool surface permits
8. repeat only where needed
9. verify meaning, cadence, and word integrity
```

Critical invariant: every successful `remove_words` mutation can shift later word indices. Re-read before another index-based word cut.

A transcript that looks grammatically complete is not proof that the audio seam is clean. A cut can still clip an initial consonant, final consonant, syllable, breath, or word decay.

## Dialogue Boundary Integrity

Every edit that closes a gap in spoken dialogue must preserve complete speech boundaries. This applies to:

- `remove_words`
- `remove_silence`
- `ripple_delete_ranges`
- manual trim/split/remove operations
- retake replacement
- clip removal that joins two spoken regions

For each resulting seam, verify as far as the available Palmier/client surface permits:

### Before the cut

- the final kept word is fully audible
- its final phoneme/consonant is not truncated
- the natural word decay is not chopped unnaturally
- the sentence or clause is semantically complete unless the next clip deliberately continues it

### After the cut

- the first kept word begins cleanly
- its initial consonant/phoneme and first syllable are intact
- required pre-roll/breath is retained when needed for natural delivery

### Across the seam

- there is no duplicated syllable or word
- there is no accidental overlap/double speech
- there is no click/pop or abrupt noise-floor discontinuity
- the rhythm sounds like intentional human speech rather than an aggressively compressed transcript edit

Never knowingly cut:

- inside a word or syllable
- before the final consonant of a word has finished
- after only the attack of a word has begun
- in the middle of a sentence when the removed remainder is required for grammatical or semantic completion
- so tightly that the speech sounds mechanically truncated even if every transcript token is technically present

Prefer natural dialogue boundaries in this order when practical:

1. end of a complete sentence
2. end of a complete clause
3. natural pause between thoughts
4. clean breath/pause
5. intentional J-cut/L-cut that preserves the complete phrase

For long-form technical YouTube, restoring a small natural pause is preferable to clipping a phoneme or creating an unnatural cadence.

If a seam is bad:

1. undo if the latest shared action is safely attributable to that cut
2. refresh current timeline/transcript state
3. retry with looser aggressiveness or a narrower targeted edit
4. recover source handles/pre-roll/post-roll where possible
5. use a short fade only for clicks or room-tone discontinuities, never to smear overlapping speech

If the connected tool surface cannot reliably validate the actual acoustic seam, do not claim the cut is acoustically verified. Leave a review marker or report the exact seam for human listening.

## What To Remove By Default

For a normal cleanup pass, remove only clearly low-value material:

- obvious `um`, `uh`, `er`, `ah` fillers
- duplicated single words
- immediate false starts
- abandoned fragments
- verbal resets
- repeated takes when one version is clearly better
- redundant explanations that add no new information
- long dead air that carries no visual/readability value

Do not globally remove ambiguous conversational words such as:

```text
like
so
well
right
just
```

unless the user explicitly requests it and the resulting speech is reviewed.

A harmless filler may remain when deleting it would create a clipped or unnatural seam.

## Preserve Technical Truth

Always preserve information needed for accurate understanding:

- commands
- model/product/repo names
- version numbers
- prices/usage terms
- compatibility requirements
- prerequisites
- caveats and warnings
- uncertainty language
- negative results or failed attempts that materially qualify the conclusion

Never cut a statement so that it becomes stronger, safer, cheaper, more compatible, or more successful than the speaker actually claimed.

## Retake Selection

When multiple takes exist:

1. read enough surrounding transcript to compare complete meaning
2. prefer the clearest complete take
3. preserve natural lead-in/out words and source handles needed for clean speech boundaries
4. remove abandoned/repeated attempts
5. re-read the edited transcript
6. verify the new speech seam acoustically where possible

If two takes are both plausible and the choice is subjective, prefer a Palmier review marker over silently deleting one as if the decision were objective.

## Cut Aggressiveness

Use current live options. Where Palmier exposes `tight`, `balanced`, and `loose`:

| Mode | Default use |
|---|---|
| `tight` | Shorts, ads, high-energy opening, explicit punchy style |
| `balanced` | Default long-form YouTube/tutorial cleanup |
| `loose` | Interviews, reflective delivery, sections needing breathing room |

Do not use `tight` across a full technical tutorial by default.

Aggressiveness never overrides dialogue integrity. Even a requested tight edit must retain complete phonemes/words and intelligible sentence meaning.

## Remove Words vs Silence vs Range Deletion

Use `remove_words` for word-aligned speech cleanup.

Use `remove_silence` for broad quiet/speech-free dead air when the selected clips/links satisfy Palmier's current constraints.

Use `ripple_delete_ranges` for known non-word-aligned spans such as:

- visual-only capture pre-roll
- loading/waiting gaps
- a visual mistake between spoken sections
- silence that needs a precisely controlled frame range

Do not manufacture many manual range cuts when a purpose-built transcript/silence tool can express the edit.

After any of these operations joins two spoken regions, apply the Dialogue Boundary Integrity checks above.

## Dead-Air Policy For Technical Videos

Keep pauses that viewers need to:

- read code
- inspect terminal output
- see a UI transition
- understand a command result
- absorb a caveat
- watch an async operation complete when the result matters
- preserve natural speech cadence and breathing

Remove waiting time where nothing useful changes visually or verbally.

Do not cut every breath.

## Capture Pre-Roll

Do not hard-code a fixed duration.

Inspect each source start. If the recording begins on OBS/QuickTime/capture software before the intended content:

- use transcript-aware removal if unwanted speech is part of the pre-roll
- use a range cut for visual-only/non-word-aligned pre-roll
- retain enough source handle before the first kept word that its initial phoneme is fully audible

## Caption Policy

### Long-form YouTube / 16:9

Do not add burned-in automatic captions by default.

Add captions only when the user explicitly requests them.

For normal long-form technical videos, use `add_texts` for sparse titles, commands, labels, and callouts instead.

### Short-form / vertical

Automatic captions are often appropriate for Shorts/Reels/TikTok-style output when requested or part of the chosen format.

Use:

```text
add_captions
```

rather than manually rebuilding every spoken word as text clips.

## Caption Styling

Use the live text/caption schema.

Do not assume Palmier lacks outline, shadow, or background styling. Current versions may expose these directly.

When styling captions:

- keep lines short enough for mobile
- avoid platform UI regions
- avoid covering app/code/UI proof
- use adequate contrast
- preserve brand restraint

After important caption changes:

```text
inspect_timeline
```

Verify actual composited placement.

## Manual Text vs Captions

Use `add_texts` for:

- title cards
- hooks
- section labels
- lower thirds
- app/repo/product names
- commands
- non-speech emphasis
- CTAs

Use `add_captions` for speech-following caption tracks.

Do not render text into generated video merely to create captions or title cards.

## Long Transcript Efficiency

For long projects:

- use `granularity=segments` for story comprehension where available
- narrow `startFrame`/`endFrame` windows for detailed edits
- page results when the live schema reports a continuation boundary/limit
- avoid repeatedly loading the entire word-level transcript after every small edit when only one local window changed

Correctness still wins over token savings: refresh any indices/state that became invalid and inspect the local seam after speech-affecting edits.

## Speaker / Multi-Track Caution

If Palmier refuses a word-removal request spanning incompatible/unlinked tracks:

- do not force the call
- edit one compatible track/link unit at a time
- preserve sync/link semantics
- use `manage_clip_links` only when link changes are actually required

## Verification

After speech cleanup:

```text
get_transcript
```

Check:

- no dangling fragments
- no accidental repeated seams
- meaning remains accurate
- technical caveats remain
- no stale-index assumptions

Then inspect/listen to each speech seam created by the cleanup, as the connected Palmier/client surface permits. Check:

- no word begins late
- no word ends early
- no syllable or phoneme is clipped
- sentence/clause completion remains natural
- no duplicated word/syllable or accidental overlap exists
- cadence and breathing remain human
- no click/pop or obvious noise-floor jump was introduced

Transcript correctness alone is not sufficient evidence of acoustic correctness.

After captions/text changes:

```text
inspect_timeline
```

Check:

- legibility
- safe placement
- no collision with UI/lower thirds
- no unintended long-form caption track

## Failure Handling

If transcription is unavailable/incomplete:

1. inspect the tool error/status
2. inspect source media if that can unblock understanding
3. retry only when the stated condition is likely transient and no paid side effect is involved
4. do not invent transcript text

If a word-removal mutation produces an obviously bad seam:

- use `undo` only if the latest shared editor action is known to be that cut
- refresh transcript/timeline state
- retry with corrected current indices and looser/more targeted boundaries
- recover source handles when possible
- mark for review if the acoustic result cannot be validated safely

## Expected Output

Long-form cleanup:

```text
Done — removed the obvious fillers, one false start, and two repeated takes while keeping complete word boundaries, natural cadence, technical caveats, and readable demo pauses. No caption track was added.
```

Short-form caption pass:

```text
Done — tightened the selected Short, kept speech boundaries intact, added mobile-readable captions, and verified they do not cover the key UI.
```

## Quality Bar

- Uses edited-timeline transcript for timeline speech cuts.
- Treats transcript timestamps as candidate boundaries rather than authoritative acoustic cut points.
- Uses segment-level reading where it improves long-context efficiency.
- Refreshes indices after each word mutation.
- Preserves complete phonemes, words, sentence meaning, and natural cadence at edited speech seams.
- Preserves technical meaning and qualifying language.
- Uses silence/range tools for the correct class of cut.
- Does not over-tighten technical reading pauses or normal breathing.
- Does not add long-form burned captions by default.
- Uses current live styling capabilities.
- Verifies caption placement when relevant.
- Marks subjective retake decisions or acoustically unverifiable seams rather than pretending certainty.
