# Palmier Pro Quick YouTube Edit Prompt

## Purpose

Use this prompt when the media is already in an open Palmier Pro project and the goal is a fast, high-quality first cut for a technical YouTube video.

It is intentionally provider-neutral: run it from Claude Code or OpenAI Codex after connecting Palmier Pro MCP.

## Prompt

```text
Use the AgentDefaults Palmier Pro MCP video-editor stack, including `skills/palmierpro-youtube-fast-edit.md`.

You are editing the currently selected Palmier Pro project through MCP.

PRIMARY GOAL
Create a fast, reviewable first-pass YouTube edit from the existing project media. Optimize for technical clarity, proof, pacing, truthfulness, and natural dialogue. Do not turn this into a generic hype video or spend time on decorative polish that does not help comprehension.

DEFAULT VIDEO STYLE
- Long-form YouTube / 16:9 unless current project state or my request clearly says otherwise.
- Technical creator video: AI, DevOps, automation, coding, app demos, MCP workflows, Wear OS/Android, terminal/code, product walkthroughs, or similar hands-on engineering content.
- Proof/result-forward opening when the footage supports it.
- Balanced pacing: remove waste, but leave enough time to read code, terminal output, UI, dashboards, diagrams, and results.
- Preserve complete spoken words, sentences, breaths, and natural cadence; never optimize for maximum cut density.
- No burned-in captions for long-form unless I explicitly ask.
- Sparse, useful callouts only.
- Clean cuts by default; transitions only when they solve a specific continuity or presentation need.

START WITH REAL STATE
1. Confirm Palmier MCP is reachable.
2. Call `get_timeline` and `get_media` before any mutation.
3. Use the live MCP tool schemas as source of truth; do not invent argument names or values from memory.
4. Do not infer media contents from filenames.
5. If the project is not active and `manage_project` is available, list projects and resolve the requested target without guessing.

PRESERVE THE ORIGINAL
For this broad edit, duplicate the active timeline with `create_timeline from=<active timelineId>` and edit the copy. Name it `YouTube Fast Cut` if a name is useful. Re-read `get_timeline` immediately after duplication because clip/track IDs change.

INSPECT EFFICIENTLY
- Read the current timeline transcript with `granularity=segments` first for structure.
- Drill into word-level transcript only around actual cut candidates.
- Treat transcript timestamps as semantic locators, not exact acoustic boundaries.
- Inspect the starts of source recordings so capture-software pre-roll is removed at the real boundary, not by a hard-coded duration.
- Use overview/source inspection and semantic media search when needed to find the best proof/demo moment.

STORY TARGET
Shape the existing material toward:
1. proof/hook
2. why it matters
3. only the setup needed
4. build/workflow/demo
5. concrete result/proof
6. real constraints/caveats
7. natural close if one exists

Do not fabricate narration, claims, or results. Reorder only when the existing footage remains truthful and coherent.

CLEANUP
- Remove verified capture pre-roll.
- Remove obvious dead air using the purpose-built silence tool when appropriate.
- Use `get_transcript` + `remove_words` for filler, false starts, repeated words, abandoned fragments, duplicate takes, and redundant explanations.
- Default to balanced cut aggressiveness.
- Re-read the transcript after every word-removal mutation before using indices again.
- Never globally remove ambiguous words like `like`, `so`, or `well`.
- Preserve commands, model names, repo names, versions, prices, compatibility details, warnings, limitations, caveats, and uncertainty language.
- Do not make speech misleading through omission.
- A harmless filler can remain if removing it would create a clipped or unnatural seam.

DIALOGUE BOUNDARY INVARIANT
Every edit that joins two spoken regions must preserve clean, complete speech.

Transcript timestamps identify candidate cuts only. The actual audio is authoritative for the final edit boundary.

For every speech-affecting mutation — including `remove_words`, `remove_silence`, `ripple_delete_ranges`, trims, clip removal, or retake replacement — verify the local seam against timeline/source audio as far as the available Palmier/client surface permits.

Never knowingly leave:
- a cut inside a word or syllable
- a clipped initial consonant/phoneme on the first kept word
- a clipped final consonant/phoneme or chopped natural decay on the last kept word
- a sentence or clause that becomes grammatically or semantically incomplete
- duplicated syllables/words
- accidental overlapping/double speech
- a click/pop or abrupt noise-floor discontinuity
- mechanically over-tightened cadence

Prefer complete sentence boundaries, then complete clause boundaries, then natural thought pauses/breaths. An intentional J-cut/L-cut is fine when the complete phrase remains intact.

For long-form YouTube, a small natural pause is better than a clipped phoneme.

If a speech seam is bad:
1. undo when the latest action can safely be attributed to that cut
2. refresh timeline/transcript state
3. retry with looser aggressiveness or a smaller target
4. recover source handles/pre-roll/post-roll where possible
5. use short audio fades only for clicks/noise-floor changes, never to smear overlapping speech

If the tool surface cannot reliably validate a speech seam acoustically, add/report a review marker rather than claiming it is clean.

START / END TRANSITIONS
- Add a short, subtle fade-in from black at the very beginning of the edited timeline.
- Add a short, subtle fade-out to black at the very end of the edited timeline.
- If audio begins or ends at those boundaries, apply matching short audio fades so there is no abrupt pop or cutoff.
- Target roughly 8-15 frames at the project frame rate unless the existing pacing clearly calls for something slightly different.
- Use only transition, effect, opacity, gain, or keyframe controls that are actually exposed by the live Palmier MCP schema; do not invent unsupported transition APIs.
- Do not add decorative transitions between normal cuts unless they solve a specific continuity problem.

VISUALS
- Keep code, terminal, app UI, dashboards, Play Console/GitHub screens, and other proof visuals readable.
- Make screenshare the primary visual when the narration is explaining the screen.
- Use facecam selectively for trust/reaction/personality; do not cover important UI.
- Use `apply_layout` when appropriate and verify important layouts with `inspect_timeline`.
- Add short title/lower-third/callout text only where it improves comprehension.
- If current text styling supports outline/shadow/background, use those rather than fake duplicate text layers.
- No default long-form caption track.
- No decorative effects/zooms just to make the timeline look busy.

AUDIO
- Preserve A/V sync.
- Preserve complete phoneme/word boundaries and natural cadence at every edited speech seam.
- Denoise only if noise is actually present or I asked for it.
- Respect current clip-link state; do not separate A/V casually.
- Do not use a crossfade to hide two overlapping spoken phonemes.

AMBIGUITY
If a subjective choice cannot be resolved from evidence, or if an acoustic speech seam cannot be validated with the available tool surface, continue the rest of the edit and add an open Palmier review marker instead of guessing.

PAID / DESTRUCTIVE ACTIONS
- Do not generate image/video/audio or upscale without my explicit approval for that exact action.
- Do not delete source media or folders.
- Do not export unless I ask.
- Do not overwrite an existing named export unless I explicitly approve it.

VERIFY
Before finishing:
- re-check the edited transcript for meaning/dangling fragments
- audit every speech-edit seam created by cleanup for complete words/phonemes, sentence continuity, no duplicated/overlapping speech, and natural cadence using actual audio where the connected tool surface permits
- inspect the opening/hook and verify the fade-in is subtle and clean
- inspect at least one representative demo/technical section
- inspect every important text/layout change
- inspect the ending and verify the fade-out is subtle and clean
- verify matching audio fades at the boundaries when applicable
- confirm A/V sync remains intact
- confirm the original timeline still exists
- confirm no unintended long-form captions were added

Transcript correctness alone is not proof that a dialogue seam is acoustically clean. Do not claim speech-seam verification unless it was actually checked.

STOP
Do one broad edit pass and one targeted verification/fix pass. Do not endlessly micro-polish. Return the timeline to me for review.

FINAL RESPONSE
Keep it concise. Tell me:
- what you changed
- the resulting story angle
- whether dialogue seams were acoustically verified or any were marked for review
- whether the opening/ending fades were applied and verified
- any review markers/manual checks
- promising Short(s) moments if obvious
- whether generation or export was run

Do not claim the video is visually or acoustically perfect unless that was actually verified.
```

## Minimal Invocation

Once the agent already knows this stack, the user can simply say:

```text
Use the Palmier quick YouTube edit profile on the open project. Make a safe first-pass cut, leave the original timeline intact, preserve complete natural dialogue boundaries at every speech edit, and add subtle fade-in/fade-out transitions at the beginning and end with matching audio fades when applicable.
```

## Quality Bar

The agent should edit the Palmier timeline, not merely return a written edit plan. The result should be a bounded, reviewable first cut with the original preserved, no known mid-word/mid-syllable dialogue cuts, and no unapproved paid generation or export.
