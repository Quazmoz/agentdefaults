# Marketing Prompts

## Purpose

Copy/paste prompts for app marketing production. Each prompt is a plain `.txt` file that contains only the prompt text, so you can copy the whole file straight into a coding agent.

| Prompt | Use |
|---|---|
| [`app-promo-video.txt`](app-promo-video.txt) | Produce a finished vertical (9:16) promo MP4 for the Android phone and/or Wear OS app in the current repository. |
| [`app-promo-video-real-usage.txt`](app-promo-video-real-usage.txt) | Produce a polished launch film with real emulator-recorded typing/taps, bespoke motion graphics, coherent scene flow, and a synchronized musical soundtrack. |

## App Promo Video

[`app-promo-video.txt`](app-promo-video.txt) has a coding agent (Claude Code, Codex, or similar) produce a finished, rendered vertical promo video for the Android phone and/or Wear OS app in the current repository. The agent discovers the app from the repo, proves every advertised claim against source, renders a 9:16 MP4 through a reproducible pipeline, and checks the real frames before it reports.

It produces local files only. It never publishes, uploads, or changes the app's release configuration.

For a promo that demonstrates how someone actually uses the app, copy [`app-promo-video-real-usage.txt`](app-promo-video-real-usage.txt). This standalone companion directs the agent to build and run the app on a local emulator, automate and record realistic interactions, and verify that entered values reach the real result screen. It requires real app footage for at least 60% of the video and progressive text entry when the chosen workflow has a text field. Static screenshots cannot satisfy those requirements. Its default output directory is `marketing/promo-video-real-usage/`.

The companion also requires a deliberate visual treatment, kinetic typography, layered device/graphic compositions, connected transitions, and a composed or appropriately licensed soundtrack arranged around the edit. It includes Reddit and YouTube references and a timed study of supplied local reference footage, with portrait adaptation, a continuous visual motif, contrast between chapters, readable motion holds, and waveform-checked music cues. HyperFrames is an optional render tool alongside the other supported approaches. It defaults to 60 fps and requires visual/musical preview and QC. Music is required unless the user explicitly requests silence; an unavailable soundtrack is a partial/blocked result.

On the marketing side, it requires a message strategy built around one outcome-led promise and three hook lines. Frame 0 must be readable, the brand must appear by about 5 s, and the end card must make the CTA clear. The film is checked against platform safe zones, and music rights must cover paid ads. Besides the master, it delivers two alternate-hook variants, a 15 s cutdown, a poster that reads in a 3:4 crop, and a `COPY.md` of claim-traced post captions. Each variant must pass a muted scroll test.

Notes:

- A Google Play store-listing video is a YouTube URL with its own content rules. Check the current Play Console guidance before reusing this 9:16 cut there, and treat uploading it as a separate, explicitly authorized step.
- Pair with [`../implementation/wearos-app-development.md`](../implementation/wearos-app-development.md) when the watch UI itself needs fixing before capture.
