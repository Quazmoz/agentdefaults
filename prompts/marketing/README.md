# Marketing Prompts

## Purpose

Copy/paste prompts for app marketing production. Each prompt is a plain `.txt` file that contains only the prompt text, so you can copy the whole file straight into a coding agent.

| Prompt | Use |
|---|---|
| [`app-promo-video.txt`](app-promo-video.txt) | Produce a finished vertical (9:16) promo MP4 for the Android phone and/or Wear OS app in the current repository. |

## App Promo Video

[`app-promo-video.txt`](app-promo-video.txt) has a coding agent (Claude Code, Codex, or similar) produce a finished, rendered vertical promo video for the Android phone and/or Wear OS app in the current repository. The agent discovers the app from the repo, proves every advertised claim against source, renders a 9:16 MP4 through a reproducible pipeline, and checks the real frames before it reports.

It produces local files only. It never publishes, uploads, or changes the app's release configuration.

Notes:

- A Google Play store-listing video is a YouTube URL with its own content rules. Check the current Play Console guidance before reusing this 9:16 cut there, and treat uploading it as a separate, explicitly authorized step.
- Pair with [`../implementation/wearos-app-development.md`](../implementation/wearos-app-development.md) when the watch UI itself needs fixing before capture.
