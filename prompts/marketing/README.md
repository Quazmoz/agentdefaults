# Marketing Prompts

## Purpose

Copy/paste prompts for app marketing production. Each prompt is a plain `.txt` file that contains only the prompt text, so you can copy the whole file straight into a coding agent.

| Prompt | Use |
|---|---|
| [`app-promo-video.txt`](app-promo-video.txt) | Produce a finished vertical (9:16) promo MP4 for the Android phone and/or Wear OS app in the current repository. |
| [`app-promo-video-real-usage.txt`](app-promo-video-real-usage.txt) | Produce a polished launch film with real emulator-recorded typing/taps, bespoke motion graphics, coherent scene flow, and a synchronized musical soundtrack. |
| [`app-launch-film.txt`](app-launch-film.txt) | Produce a 75–90 s narrated 16:9 YouTube launch film built entirely in code: rebuilt app UI on a 3D phone, local-TTS voiceover driving a word clock, locally composed music on a beat grid, and deterministic 60 fps rendering. |
| [`app-launch-film-v2.txt`](app-launch-film-v2.txt) | Revised launch film prompt that detects phone, watch, or phone + Wear OS companion, and adapts the story, device staging, and claims to that mode, with explicit QC gates. |

## App Promo Video

[`app-promo-video.txt`](app-promo-video.txt) has a coding agent (Claude Code, Codex, or similar) produce a finished, rendered vertical promo video for the Android phone and/or Wear OS app in the current repository. The agent discovers the app from the repo, proves every advertised claim against source, renders a 9:16 MP4 through a reproducible pipeline, and checks the real frames before it reports.

It produces local files only. It never publishes, uploads, or changes the app's release configuration.

For a promo that demonstrates how someone actually uses the app, copy [`app-promo-video-real-usage.txt`](app-promo-video-real-usage.txt). This standalone companion directs the agent to build and run the app on a local emulator, automate and record realistic interactions, and verify that entered values reach the real result screen. It requires real app footage for at least 60% of the video and progressive text entry when the chosen workflow has a text field. Static screenshots cannot satisfy those requirements. Its default output directory is `marketing/promo-video-real-usage/`.

The companion also requires a deliberate visual treatment, kinetic typography, layered device/graphic compositions, connected transitions, and a composed or appropriately licensed soundtrack arranged around the edit. It includes Reddit and YouTube references and a timed study of supplied local reference footage, with portrait adaptation, a continuous visual motif, contrast between chapters, readable motion holds, and waveform-checked music cues. HyperFrames is an optional render tool alongside the other supported approaches. It defaults to 60 fps and requires visual/musical preview and QC. Music is required unless the user explicitly requests silence; an unavailable soundtrack is a partial/blocked result.

On the marketing side, it requires a message strategy built around one outcome-led promise and three hook lines, with one selected for production and two retained as copy alternatives. Frame 0 must be readable, the brand must appear by about 5 s, and the end card must make the CTA clear. The film is checked against platform safe zones, and music rights must cover paid ads. By default it delivers exactly one final MP4, a poster that reads in a 3:4 crop, and a `COPY.md` of claim-traced post captions. Additional videos require an explicit request: hook variants need different messages and opening visuals, cutdowns need a real 15 s edit, and multiple creative videos need different featured workflows/benefits and scene sequences. Every delivered video must pass a muted scroll test; multiple videos also require decoded-frame comparisons and duration checks so duplicate exports cannot count as variants.

Regression cases for agent runs using the real-usage prompt:

| Request or observed output | Required outcome |
|---|---|
| Prompt used without a video-count override | Exactly one final MP4 in `out/`; two unused hook ideas remain copy only. |
| Master plus two hook variants and a 15 s cutdown explicitly requested | Four final MP4s; each hook changes its message and opening visuals; the cutdown is a separately edited 15 s story retaining the action, result, and ending. |
| Four different promo videos requested | Four creative edits with different hooks, featured workflows/benefits, and scene sequences. |
| Four exports show the same visuals despite different filenames, encodings, metadata, or music | Duplicate edits fail QC and cannot count toward delivery. |
| Requested differences cannot be produced within the budget | Preserve passing unique edits and report partial delivery with the missing count and reason. |

## App Launch Film

[`app-launch-film.txt`](app-launch-film.txt) is the long-form, landscape companion. The agent rebuilds the app's screens in HTML/CSS from source and maps them onto a Three.js phone. It tells a "the old way → the app way → breadth → outro" story with narration, and renders a deterministic `render(t)` page through Playwright at 60 fps, one capture per output frame. Everything is free: an open-weight, commercially licensed TTS for the voice, and music and sound effects synthesized in code. Text and events follow a faster-whisper word clock, and cards follow a librosa beat grid.

Because the UI is rebuilt rather than recorded, the prompt adds fidelity gates. Every rebuilt screen is compared side by side with an emulator screenshot of the same state, UI text comes from `strings.xml`, and other apps or people in the story are fictional, with no real brands or trade dress. It delivers one MP4, captions (`.srt`/`.vtt`), a 1280×720 thumbnail, audio stems, and a `COPY.md` with chapters.

The motion system (easing roles, named springs, morph handoffs, camera breath, word-by-word reveals), the `render(t)` purity rule, scene-range re-render, and the stills-after-every-change loop are shared with the two vertical prompts. The vertical prompts also supersample at 4× for motion blur, which the launch film skips. All three prompts allow any free tool from the internet (HyperFrames, Remotion, open-weight models, CC0 assets) but forbid anything that incurs a cost: paid APIs, plans, credits, purchases, or trials that need payment details.

[`app-launch-film-v2.txt`](app-launch-film-v2.txt) replaces the phone-first assumptions. It first classifies the repository as `PHONE`, `WATCH`, `PAIR_INDEPENDENT`, or `PAIR_CONNECTED` from manifests, Wear dependencies, and Data Layer code, then picks a hero device. Sync, "send to watch", and "works without your phone" claims need a runtime capture on paired or unpaired emulators, not only a code trace. A failed pairing drops the cross-device scenes instead of faking them. The story budget adds up to 84 s, and in pair modes the second device gets a full workflow and at least 25% of in-device screen time. It also covers round-watch UI fidelity (TimeText, list scaling, rotary, tiles, complications), believable phone-to-watch scale, and gates G1–G5 recorded in a resumable `BRIEF.md`.

Its craft principles draw on Apple's app and device ads ("Privacy. That's iPhone.", "Relax, it's iPhone.", the iPhone + Apple Watch "Big Fish" spot) and Apple's App Store app preview guidance. The film has to prove one written proposition. The story is built around the viewer's moment rather than a feature list, and in pair modes it stages a "why the wrist" moment. Abstract claims become concrete metaphors, each checked for misreading. The prompt also requires a narration-free hold at the payoff, a muted-first hook with a muted test, and in-screen motion limited to the app's real transitions. It ends on a reusable lockup line, discloses paid features, and leaves out prices and dated references. These are principles to learn from, not Apple's trade dress or typefaces to copy.

Before anything is rendered, the prompt checks licenses for each TTS voice (not just the engine) and for the app's font, uses Google's badge and trademark rules, and runs a WCAG 2.3.1 flash-safety scan. `COPY.md` gets a Play promo upload checklist. An optional `CHECKPOINTS` setting stops for approval after the script (`script`), and also after the voice bake-off (`script+voice`).

The voiceover is built to sound like a human narrator. The prompt gives a commercially licensed model shortlist (Chatterbox, Qwen3-TTS, Kokoro as the baseline) and lists the non-commercial models to avoid (XTTS v2, F5-TTS weights, Fish Audio, VibeVoice, and others). It runs a blind bake-off and synthesizes each beat or paragraph rather than each line, so intonation carries across sentences. Each chunk gets 3–5 takes scored on transcript accuracy, rate, pitch movement, and artifacts. Scripts are written for the ear, processing stays light, and pauses vary with meaning. Because an agent may not be able to hear audio, it reports naturalness as UNVERIFIED unless someone actually listened.

Notes:

- A Google Play store-listing video is a YouTube URL with its own content rules. Check the current Play Console guidance before reusing this 9:16 cut there, and treat uploading it as a separate, explicitly authorized step.
- Pair with [`../implementation/wearos-app-development.md`](../implementation/wearos-app-development.md) when the watch UI itself needs fixing before capture.
