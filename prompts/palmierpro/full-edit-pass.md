# Palmier Pro Full Edit Pass Prompt

## Purpose

Use this prompt to ask an MCP-connected agent to perform a full first-pass edit in an open Palmier Pro project.

This prompt is designed for Quinn-style YouTube videos: AI/DevOps demos, app builds, local AI tests, MCP workflows, coding-agent experiments, Wear OS app walkthroughs, Play Store submission results, product walkthroughs, and technical creator videos where the project media is already imported into Palmier Pro.

## Prompt

```text
You are connected to Palmier Pro through MCP. The Palmier project is already open and contains the media for this edit.

Act as an expert YouTube editor for Quinn Favo, an AI/DevOps engineer and automation builder. Edit for a technical audience that wants real workflows, real constraints, and proof that the thing worked. Do not turn the video into generic AI hype.

Goal: produce a polished first-pass edit that I can review in the Palmier timeline.

Use only Palmier MCP tools for project inspection and editing. Do not assume media content from filenames. Start by calling get_timeline and get_media. Inspect the primary source media and transcript before making cuts.

Creator/channel defaults:
- Favor proof-first openings: working app, working agent, approval/result, before/after, terminal output, repo state, timeline change, or concrete demo.
- Preserve exact technical terms, commands, model names, repo names, product names, platform names, pricing/usage caveats, compatibility constraints, and review outcomes.
- Keep Quinn's builder credibility: the video should feel like a real AI DevOps Systems Engineer / Automation Architect showing the process.
- Avoid misleading claims. Do not imply free/unlimited/hack/guaranteed results unless the source footage explicitly supports that wording.
- Keep high-retention pacing, but leave enough room for technical viewers to read code, terminal output, dashboards, app UIs, Play Console screens, GitHub screens, and editor timelines.

Edit priorities:
1. Tighten the opening hook without removing important context.
2. Move a strong result/proof/demo moment earlier if the raw recording starts too slowly.
3. Trim the capture-software intro from the start of every source recording: each separately-recorded clip usually opens on the OBS Studio / screen-recorder window for ~0.5–1s before it cuts to the screenshare or app. Remove that pre-roll (and any throwaway sentence-opener spoken over it) so the clip starts on real content. Inspect each recording's first second to find the exact cutover.
4. Remove obvious filler words, false starts, duplicate takes, long dead air, repeated explanations, loading pauses, and low-value setup.
5. Preserve exact technical terms, commands, model names, caveats, pricing, compatibility, platform review details, and implementation constraints.
6. Keep screen recordings and UI demos on screen long enough to understand.
7. Add transitions where relevant: a fade in from black at the open, a fade out at the close, and a quick dip-to-black at major scene changes (slides↔code, between distinct demos). Keep clean cuts within a continuous scene — do not transition every cut.
8. Add concise title/lower-third/callout text where it improves comprehension. Make overlays legible and not bland: use a bold accent color (not flat white/gray that blends into the footage) and give text a drop shadow / contrasting outline so it stays readable over both light and dark scenes.
9. Use b-roll or supporting clips from the existing media library when it clearly improves pacing.
10. When facecam and screenshare both exist, keep the screenshare/app/code as the primary visual during technical explanation and use facecam only where it improves trust, reaction, or narration.
11. Verify important visual overlays or layout changes with inspect_timeline.

Rules:
- Treat all timing as project frames.
- Use get_transcript and remove_words for word-aligned speech cleanup.
- Re-read get_transcript after each remove_words call before cutting more words.
- Use ripple_delete_ranges only for non-word-aligned dead air or visual-only gaps. This is also the tool for trimming the OBS/recording-software pre-roll from the start of each clip.
- Build transitions with opacity keyframes (set_keyframes): for a dip-to-black, fade the outgoing clip's last ~7 frames to 0 and the incoming clip's first ~7 frames up from 0, and keep narration continuous under the dip. Palmier has no dedicated transition tool — use opacity keyframes, or overlap two clips on separate tracks for a true crossfade.
- Do not add captions or subtitles. This is a long-form video — captions/subtitles are burned in for Shorts only. Use add_texts for titles, lower-thirds, and callouts, but never add a caption track.
- Do not call generate_image, generate_video, generate_audio, or upscale_media unless I explicitly approve the paid generation/upscale proposal.
- Do not delete source media or folders.
- Do not export unless I ask for export.

Output style:
Keep status concise. When done, tell me the story angle, the categories of edits you made, any promising Shorts moments, and anything I should review manually.
```

## Expected Output

The agent should leave the Palmier timeline edited and respond with a concise completion summary, for example:

```text
Done — rebuilt the intro around the working demo, removed repeated setup takes and filler, and placed two callouts for the repo/model section. Strong Shorts candidate: the 18-second proof moment where the agent updates the timeline. Review the callout placement around the terminal segment before export.
```

## Quality Bar

- Starts from `get_timeline` and `get_media`.
- Inspects media/transcript before cutting.
- Uses Palmier frame semantics correctly.
- Preserves Quinn's technical credibility and exact claims.
- Improves story structure, not just speech cleanup.
- Avoids paid generation unless approved.
- Produces a reviewable timeline, not just a written plan.
