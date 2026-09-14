# Palmier Pro Full Edit Pass Prompt

## Purpose

Use this prompt for a deeper first-pass edit of a technical YouTube video in an existing Palmier Pro project.

For the fastest normal workflow, prefer:

```text
prompts/palmierpro/quick-youtube-edit.md
```

This full pass spends more effort on story structure and supporting visuals while preserving the same safety boundaries.

## Prompt

```text
Use the canonical AgentDefaults Palmier Pro MCP stack.

You are connected to Palmier Pro through external MCP from Claude Code, OpenAI Codex, or another MCP client. The same editing contract applies regardless of provider.

PRIMARY GOAL
Produce a polished, reviewable first-pass long-form YouTube edit from the media already in the Palmier project. Preserve natural, complete spoken dialogue while tightening pacing.

STYLE
This is technical creator content: AI/DevOps workflows, coding agents, MCP demos, local AI, Android/Wear OS apps, Google Play, terminals, code, product walkthroughs, automation, or similar hands-on engineering material.

Favor real proof, real constraints, reproducibility, and natural speech. Do not turn the edit into generic AI hype or aggressively compress dialogue at the expense of intelligibility.

SOURCE OF TRUTH
- Start with `get_timeline` and `get_media`.
- Use live MCP tool schemas for exact arguments/enums.
- Do not infer media contents from filenames.
- Preserve exact technical terms, commands, model names, repo names, product/platform names, prices/usage details, compatibility constraints, caveats, uncertainty, and review outcomes.
- Treat transcript timestamps as semantic locators, not authoritative acoustic cut points. Actual spoken audio governs dialogue boundaries.

PRESERVE THE ORIGINAL
This is a broad edit. Duplicate the active timeline with `create_timeline from=<active timelineId>` and edit the copy. Use a clear name such as `YouTube Full Cut`. Re-read `get_timeline` immediately because copied clip/track IDs are new.

INSPECT EFFICIENTLY
- Read the timeline transcript at segment granularity first for story structure when supported.
- Drill into word-level transcript only around actual cut candidates.
- Inspect source overviews and targeted windows for visual and dialogue boundaries.
- Use semantic media search for proof/demo/result moments.

STORY TARGET
Shape truthful existing footage toward:
1. strong proof/result/hook
2. why the viewer should care
3. only the setup needed
4. implementation/build/demo
5. concrete result
6. limitations/cost/compatibility/caveats
7. natural close if recorded

Move material earlier only when the existing footage remains coherent and truthful. Do not fabricate narration or claims.

EDIT PRIORITIES
1. Tighten the opening.
2. Bring an existing strong proof/result moment forward when it materially improves the hook.
3. Inspect each source recording's start and remove verified OBS/QuickTime/capture pre-roll at the real boundary. Do not apply one hard-coded trim duration to every clip.
4. Remove obvious filler, false starts, duplicate takes, abandoned fragments, redundant explanations, and low-value dead air.
5. Use `remove_silence` for appropriate bulk quiet/speech-free gaps; keep pauses needed to read code/UI/terminal/results and preserve natural speech cadence.
6. Use `get_transcript` + `remove_words` for word-aligned cleanup, and re-read transcript after every word mutation before reusing indices.
7. Default long-form speech cleanup to balanced aggressiveness.
8. After every speech-affecting edit, verify the local seam against actual timeline/source audio as far as the available Palmier/client surface permits. Never knowingly leave a mid-word/mid-syllable cut, clipped initial/final phoneme, semantically incomplete sentence, duplicated syllable/word, overlap, or mechanically over-tight cadence.
9. Prefer complete sentence boundaries, then complete clause boundaries, then natural thought pauses/breaths. A small natural pause is preferable to a clipped phoneme.
10. Keep screenshare/code/app UI/proof visuals readable long enough to understand.
11. Use facecam selectively; during technical explanation, screenshare is usually primary.
12. Use `apply_layout` for facecam/screenshare arrangements and verify important layouts.
13. Add only useful titles/lower thirds/callouts. Check the live text schema; use supported outline/shadow/background styling directly when helpful.
14. Prefer clean cuts. Add fades/dips only at real section boundaries and verify keyframed transitions with `inspect_timeline`.
15. Use existing media as b-roll when it clearly helps. Do not generate paid b-roll without approval.
16. If a decision is subjective, brand-sensitive, or an acoustic dialogue seam cannot be reliably validated, add an open Palmier review marker instead of guessing.

DIALOGUE REPAIR RULES
If a transcript/silence/range operation creates a bad speech seam:
- undo when the latest action is safely attributable to that cut
- refresh current timeline/transcript state
- retry with looser aggressiveness or a narrower target
- recover source handles/pre-roll/post-roll where possible
- use short audio fades only for clicks or noise-floor discontinuities, never to smear overlapping speech
- leave a review marker if the connected tool surface cannot reliably validate the acoustic result

A harmless filler may remain if deleting it would create a clipped or unnatural seam. Natural speech outranks maximum cut density.

LONG-FORM CAPTION RULE
Do not add a burned automatic caption track to this 16:9 long-form edit unless I explicitly ask for captions. Use `add_texts` for sparse titles/callouts instead.

AUDIO
- Preserve A/V link state and sync.
- Preserve complete phoneme/word boundaries and natural cadence at every edited speech seam.
- Do not casually unlink clips.
- Denoise only if noise is actually present or I request it.
- Do not over-process audio in the first pass.
- Do not use crossfades to conceal overlapping speech; fix the underlying boundary instead.

PAID / DESTRUCTIVE BOUNDARIES
- Do not call `generate_image`, `generate_video`, `generate_audio`, or `upscale_media` without my explicit approval for the exact proposed action.
- Do not delete source media or folders.
- Do not export unless I ask.
- Do not overwrite an existing named export unless I explicitly approve it.

VERIFY
Before finishing:
- re-read the edited transcript or relevant windows
- audit every speech-edit seam created by cleanup for complete phonemes/words, complete sentence/clause meaning, natural cadence, no duplicate/overlapping speech, and no obvious click/pop; use actual audio/playback where the connected surface supports it
- inspect the opening/hook
- inspect at least one representative technical/demo section
- inspect every important title/layout/transition change
- inspect the ending if modified
- confirm the original timeline still exists
- confirm no long-form caption track was added unless requested

Transcript correctness alone is not proof of acoustic correctness. Do not claim a dialogue seam is verified unless the actual seam was checked with the available audio/playback surface. If not, mark/report it for review.

BOUND EXECUTION
Do one full edit pass and one targeted verification/fix pass. Do not continue micro-polishing indefinitely. Leave unresolved subjective decisions and acoustically unverifiable dialogue seams as review markers.

FINAL RESPONSE
Keep it concise and report:
- resulting story angle
- categories of edits actually made
- dialogue-seam verification status and any acoustic review markers
- review markers/manual checks
- obvious promising Shorts moments
- whether any paid generation ran
- whether export ran

Do not claim frame-perfect visual or acoustic quality beyond the sections actually inspected.
```

## Expected Output

Example:

```text
Done — created `YouTube Full Cut`, rebuilt the opening around the working demo, removed repeated setup/retakes and verified dead air, preserved complete dialogue boundaries and natural cadence, kept the terminal/app sections readable, and added two restrained callouts. I left one open review marker on the choice between two intro takes. Strong Short candidate: the proof moment where the agent changes the timeline. No paid generation or export was run.
```

## Quality Bar

- Uses live project state and schemas.
- Preserves the original timeline.
- Inspects before cutting.
- Refreshes transcript indices after word edits.
- Treats transcript timestamps as candidate boundaries rather than authoritative acoustic cut points.
- Preserves complete phonemes, words, sentence meaning, natural cadence, and technical truth/caveats.
- Keeps proof/code/UI readable.
- Avoids default long-form burned captions.
- Uses current text-style capabilities.
- Marks subjective uncertainty and acoustically unverifiable seams.
- Avoids unapproved paid/destructive actions.
- Produces an edited reviewable timeline, not merely a plan.
- Stops after a bounded edit/verification cycle.
