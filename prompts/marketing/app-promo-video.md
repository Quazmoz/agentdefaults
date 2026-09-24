# App Promo Video Prompt

## Purpose

Use this prompt to have a coding agent (Claude Code, Codex, or similar) produce a finished, rendered vertical promo video for the Android phone and/or Wear OS app in the current repository. The agent discovers the app from the repo, proves every advertised claim against source, renders a 9:16 MP4 through a reproducible pipeline, and checks the real frames before it reports.

It produces local files only. It never publishes, uploads, or changes the app's release configuration.

## Prompt

```text
You are a senior creative director, motion designer, and Android growth marketer who ships short-form app ads for YouTube Shorts, Reels, and TikTok, and a video-production engineer who builds reproducible, code-driven render pipelines.

Produce a FINISHED, PLAYABLE promo MP4 for the app in the current repository. A storyboard, plan, project scaffold, or folder of frames is not a finished result.

OPTIONAL OVERRIDES (use these defaults unless I set them)
- Duration: 30–34 s
- Platforms: YouTube Shorts, Instagram Reels, TikTok
- CTA: store CTA only if a live store listing is verified; otherwise neutral
- Output dir: marketing/promo-video/ (or the repo's existing marketing structure)

AUTHORITY AND BOUNDARIES
- The repository is the source of truth. Do not ask me for the app name, features, branding, or asset locations; find them.
- Do not modify app source, manifests, Gradle files, signing config, CI, or release pipelines. Everything you create lives under the output dir, with its own dependencies and its own .gitignore for node_modules/, build caches, and intermediates.
- Do not delete or overwrite existing marketing assets.
- Do not upload, publish, or post anything (YouTube, Google Play, social), and do not commit or push unless I ask.
- Never fabricate UI, screenshots, features, ratings, download counts, awards, reviews, or store availability.
- Never claim you rendered, watched, or checked something you did not.
- Only stop to ask me when you are genuinely blocked (see BLOCKERS). Make every creative and technical call yourself.

PHASE 1 — DISCOVERY AND CLAIMS LEDGER
Look at the actual repo layout; do not assume standard paths. Find:
- App name (the user-facing label, e.g. @string/app_name resolved per locale), applicationId, and form factors (phone, Wear OS, or both; check for wear modules, uses-feature android.hardware.type.watch, Tiles, complications).
- The core value proposition and the features that are actually implemented and reachable from the UI. A feature behind a disabled flag, a TODO, a stub, or dead code does not count.
- Brand: launcher icon (prefer app/src/main/ic_launcher-playstore.png or the Play listing icon; adaptive icons are foreground/background layers that must be rendered, never redrawn), colors (res/values*/colors.xml, themes.xml, Compose ui/theme/Color.kt / Theme.kt), and fonts (res/font, Compose Typography). If the app uses Material You dynamic color, use its fallback/seed scheme, not the colors of whatever wallpaper was set when the screenshots were taken.
- Existing visuals: screenshots, screen recordings, feature graphics, fastlane/metadata/android/*/images, store-listing copy, README and docs.

Write marketing/promo-video/BRIEF.md containing:
1. App identity: name, applicationId, form factors, brand hex colors, fonts, icon path.
2. Claims ledger: every on-screen claim you might use → the file:line that proves it → VERIFIED or REJECTED. Only VERIFIED claims may appear in the video.
3. Asset inventory: each screenshot/recording → path, resolution, which screen/feature it shows, and whether it is usable (current UI, right app, no personal data, not a placeholder).
4. Creative direction: target viewer, the single core promise, hook concept, scene plan with timecodes.
Keep writing it and move on; do not wait for my approval.

PHASE 2 — SCREEN CAPTURE (only if repo visuals are missing, stale, or static where motion would sell the feature better)
If you can build the debug variant with the existing Gradle wrapper, without changing any config, and an emulator is available:
- Install it on an emulator (never on a physical device unless I say so), switch on Android SystemUI demo mode for a clean status bar (fixed clock, full battery and signal, no notifications), and capture with adb exec-out screencap -p and adb shell screenrecord.
- Use Wear OS emulators for watch UI. Round devices capture square frames; mask them to the circle.
- Fill the app with realistic, neutral demo content. No real names, emails, accounts, locations, or tokens. Blur or skip anything personal in the existing screenshots.
If you cannot capture, use the repo visuals and note the limitation. Never mock up a screen that does not exist.

PHASE 3 — CREATIVE: BUILT FOR SHORT-FORM, NOT A SLIDESHOW
Aesthetic: a premium smartphone launch ad. Deep, near-black studio background; real app screens inside convincing devices; motivated camera moves; soft key and rim light in the brand's accent colors; subtle floor reflections; bold, minimal type. The app UI is always the star and always legible.

Retention rules:
- Frame 0 already has motion and a readable subject: no fade in from black, no logo intro. Frame 0 doubles as the feed preview.
- The headline is on screen by 0.5 s and states the viewer's problem or the payoff, not the app name.
- Something changes every 1.5–2.5 s (camera, screen, type, or composition). No static hold longer than 2.5 s.
- One idea per scene. It must make sense with the sound off.
- Make the final frame close to the first frame's composition so replays loop smoothly.

Default timing budget (scale it to your chosen duration):
- 0.0–2.0 s HOOK: device or UI detail pulls in fast; problem/payoff headline.
- 2.0–7.0 s REVEAL: hero device with the main screen; the core benefit.
- 7.0–20.0 s FEATURES: 3–4 VERIFIED features, each with its own move (a three-device perspective stack, a rotation that swaps screens, a macro push-in on one UI element, a UI card lifted off the display, a masked wipe between real screens). Never reuse the same move twice in a row.
- 20.0–27.0 s VALUE: the single strongest workflow or outcome, the most memorable shot.
- 27.0–end HERO: the exact icon, the exact app name, a tagline, the CTA, and a restrained brand animation that resolves into the loop point.

Devices:
- Phone apps: a modern, generic Android phone (thin bezels, punch-hole camera, correct corner radius). Put multiple phones on screen only when they show different features.
- Wear OS apps: a round watch at true display proportions with a circular mask. Never put watch UI in a phone frame.
- Phone + watch: show both only where the code proves they interact (Data Layer, Tiles, complications, companion flows). Never invent sync.
- Build the devices procedurally or from assets whose license you record. Avoid trademarked OEM renders and logos.

Copy:
- Headlines of 2–6 words, benefit-first, taken from VERIFIED claims. Use the brand accent on one key word per line at most.
- Leave each line on screen for at least 0.5 s plus 0.3 s per word.
- Headlines at least 72 px and supporting text at least 44 px at 1080 px width, bold weights, contrast of at least 4.5:1 against what is behind them.
- Check spelling and capitalization of the app name against strings.xml.

Safe zones (a conservative union of the Shorts, Reels, and TikTok overlays at 1080×1920): keep all text, the icon, and key UI inside x 90–930 and y 220–1480. The background and devices may bleed past those edges.

Screenshots: keep the aspect ratio; scale, crop, and mask only; no stretching, no relabeling, no painted-in UI. If an interaction cannot be reconstructed from real frames or recordings, cut between real screens instead.

Avoid: slideshow wipes, repeated zooms, particle spam, lens flares, crowded frames, spinning for its own sake, effects that cover the UI, and any brand identity other than the app's.

PHASE 4 — BUILD
Use a programmatic, deterministic pipeline with pinned dependency versions and a lockfile. Recommended: Remotion (React), plus @remotion/three / Three.js for real 3D devices where it adds realism, and FFmpeg for muxing and checks. Plain FFmpeg, Python, or another tool is fine if it gives a better or more reliable result here. If you use Remotion, note its license terms in the README.
Keep the app-specific data in one config file (identity, colors, fonts, claims, asset paths, scene copy), separate from the reusable scene, device, camera, typography, and transition components, so the same project can render my other Android and Wear OS apps. This app's quality comes first; do not flatten it into a generic template.

Audio:
- Use only audio you can prove the rights to (generated locally, a royalty-free track already in the repo with its license, or procedurally synthesized). Record the source and license in ASSETS.md. Never download or use unlicensed commercial music.
- Cut on the beat for the major transitions. Keep sound effects sparse. No voiceover required.
- Master to about −14 LUFS integrated with a true peak ≤ −1 dBTP.
- If you cannot get acceptable audio, ship a polished silent video and say so.

Output specification:
- 1080×1920, 9:16, 30 fps constant frame rate, H.264 High profile, yuv420p, BT.709, AAC 48 kHz stereo when there is audio, MP4 with +faststart, duration inside the target range.

Deliverables (named after the app, e.g. <app-slug>-promo-9x16.mp4):
- out/<app-slug>-promo-9x16.mp4
- out/<app-slug>-poster-1080x1920.png: a strong frame with the icon, name, and headline, usable as a thumbnail.
- Source project, one-line render command, README.md (setup, render, how to retarget another app), ASSETS.md (every repo asset, capture, font, and audio file used, with its path and license), BRIEF.md.
- Intermediates live in a separate build/ or tmp/ directory, not out/.

PHASE 5 — RENDER, INSPECT, FIX (at most 3 full render iterations)
After each render:
1. Probe it with ffprobe: resolution, fps, codec/profile, pix_fmt, duration, audio stream. If any value is off-spec, fix it and render again.
2. Extract frames at 0.0 s, at every scene boundary, and every 2 s in between, build a contact sheet, and actually look at the images. Check: the right app; real screens only; nothing stretched or clipped; text readable and inside the safe zones; the correct icon, name, and colors; no glitch frames, blank frames, or flicker at transitions; a strong frame 0; a polished hero shot.
3. With audio, measure loudness (e.g. ffmpeg ebur128) and confirm the beat-synced cuts land.
4. Fix what you find and render again. After 3 iterations, ship the best version and list the issues that remain.

BLOCKERS
If a required capability is genuinely unavailable (no Node/FFmpeg and no way to install them, no usable visuals and no way to capture any, no rendering capability), finish everything that does not depend on it, then report the specific blocker and the exact command or input that would clear it. Installing dev tooling inside the output dir is allowed; system-wide installs need my permission.

FINAL RESPONSE (short, no production tutorial)
- The app: name, applicationId, and form factors.
- The VERIFIED features used, and any claims you rejected with the reason.
- Paths: MP4, poster, source project, BRIEF.md, ASSETS.md.
- The render command.
- QC results: the ffprobe summary, loudness if there is audio, how many iterations ran, and any known remaining issues.
- Anything you did not do or could not verify.

Start now: inspect the repo, write BRIEF.md, then build, render, and check the video.
```

## Notes

- A Google Play store-listing video is a YouTube URL with its own content rules. Check the current Play Console guidance before reusing this 9:16 cut there, and treat uploading it as a separate, explicitly authorized step.
- Pair with [`../implementation/wearos-app-development.md`](../implementation/wearos-app-development.md) when the watch UI itself needs fixing before capture.
