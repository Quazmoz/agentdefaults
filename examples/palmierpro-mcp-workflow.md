# Palmier Pro MCP Workflow Example

## Purpose

Show how to compose the Palmier Pro MCP AgentDefaults files into practical video-editing workflows.

Use this example when you want to copy a small stack into an agent chat or repo-aware AI tool without reading every canonical file.

## Recommended Copy-Paste Stack

```text
Use these AgentDefaults files as behavior:

agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
```

For a smaller story-assembly workflow:

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/story-assembly-from-project-media.md
```

For a YouTube Short from long-form content:

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/youtube-short-from-long-form.md
```

For a smaller cleanup-only workflow:

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/transcript-cleanup-pass.md
```

## Example 1: Story Assembly From All Project Video Media

```text
Use the Palmier Pro story assembly prompt from AgentDefaults.

The Palmier project is open and contains all source video files for this YouTube edit. I am an AI and DevOps engineer, so preserve exact technical terms, tools, commands, repo names, model names, caveats, and implementation details.

Inspect all relevant video files in the current Palmier project. Infer the intended video from the actual footage and transcripts, not filenames. Extract the main points, identify the strongest proof/demo moments, and propose the best YouTube story arc.

Do not edit the timeline yet. Return the likely intent, best YouTube angle, main points, suggested timeline, clips to cut/demote, Shorts opportunities, and manual review items.
```

## Example 2: YouTube Short From Long-Form Project

```text
Use the Palmier Pro YouTube Short from long-form prompt from AgentDefaults.

The Palmier project is open and contains the long-form video footage or edited timeline. Create one 9:16 YouTube Short from the strongest self-contained proof/demo moment.

Requirements:
- target 18-35 seconds unless the moment truly needs more time
- keep the screen recording, code, app UI, Play Console, GitHub view, terminal, or editor timeline readable on mobile
- place my facecam as picture-in-picture only where it does not cover captions or important UI
- use a fast hook in the first 1-2 seconds
- preserve exact technical terms and caveats
- do not imply free, unlimited, guaranteed approval, or unsupported performance claims
- do not export yet

When done, tell me the Short angle, approximate duration, source moment, facecam/screenshare layout, caption placement, and what I should review before export.
```

## Example 3: Full YouTube First Pass

```text
Use the Palmier Pro MCP stack from AgentDefaults.

The Palmier project is open and contains the raw footage for a YouTube technical demo.

Run a full first-pass edit:
- inspect the current project and media
- tighten the hook
- move the strongest proof/result/demo earlier if the raw recording starts too slowly
- remove obvious filler, repeated starts, dead air, duplicate takes, loading pauses, and repeated explanations
- preserve technical caveats, commands, repo names, model names, exact numbers, compatibility details, and platform/review outcomes
- keep UI/screen-recording sections visible long enough to follow
- add captions
- add concise callouts where helpful
- verify important overlay placement
- identify any strong YouTube Shorts candidates
- do not use paid generation or upscaling unless you ask and I approve
- do not export yet

When done, summarize what changed, Shorts candidates, and what I should review manually.
```

## Example 4: Transcript Cleanup Only

```text
Use the Palmier Pro transcript cleanup stack from AgentDefaults.

Clean the current timeline's spoken content only. Use get_transcript and remove_words. Re-read get_transcript after each remove_words call. Use balanced cut aggressiveness.

Remove filler, false starts, duplicate takes, and long pauses that hurt pacing. Keep exact technical details, commands, caveats, and useful pauses for demos. Do not add overlays, do not generate assets, and do not export.
```

## Example 5: Short-Form Clip

```text
Use the Palmier Pro short-form cutdown stack from AgentDefaults.

Find the strongest standalone proof/demo moment in the current project for a social clip. Prioritize a clear hook, concrete proof/demo, and clean ending. For YouTube Shorts, use the dedicated YouTube Short prompt instead.

Tighten the clip, add captions, and add one short hook overlay if it improves clarity. Do not remove caveats that make the clip accurate. Do not export unless I ask.
```

## Example 6: AI B-Roll With Approval

```text
Use the Palmier Pro AI generation workflow from AgentDefaults.

I want one AI b-roll clip to support the section where I explain the app approval result. Inspect the timeline and source context first. Then propose a model, duration, aspect ratio, and prompt for the generated b-roll. Do not call generate_video or generate_image until I approve.
```

## Example 7: Export Review File

```text
Use the Palmier Pro MCP stack from AgentDefaults.

Inspect a few representative timeline frames to catch obvious overlay/caption issues. Then export a review video using H.264 at Match Timeline resolution. If no output path is specified, let Palmier write it to Downloads.
```

## Good Agent Completion Notes

```text
Done — mapped the project footage into a proof-first AI-engineering story arc, identified the main demo and caveat sections, and marked repeated setup takes for removal.
```

```text
Done — created a 27-second 9:16 Short from the agent-timeline proof moment. The screenshare is the main visual, your facecam is upper-right to avoid captions and timeline controls, and the hook appears in the first second. Review the crop around the terminal/editor area before export.
```

```text
Done — tightened the first 18 seconds, removed obvious filler and two repeated takes, added captions, and placed a repo-name callout during the demo. Review the caption position around the terminal section before exporting.
```

```text
Generation proposal ready: 6-second 9:16 tech b-roll using a clean smartwatch UI still as the start frame. Prompt: "slow push-in as the watch dashboard pulses, subtle electronic ambience." This may use Palmier credits. Approve generation?
```

```text
Export started — Palmier is rendering an H.264 review file to Downloads and should notify you when it finishes.
```

## Quality Bar

- The agent edits the open Palmier project, not just a plan.
- It reads state before acting.
- It does not spend credits without approval.
- It preserves technical accuracy.
- It keeps facecam, captions, and screenshare layout readable for mobile when making Shorts.
- It produces concise, reviewable completion notes.
