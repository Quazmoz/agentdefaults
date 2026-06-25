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

For a smaller cleanup-only workflow:

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/transcript-cleanup-pass.md
```

## Example 1: Full YouTube First Pass

```text
Use the Palmier Pro MCP stack from AgentDefaults.

The Palmier project is open and contains the raw footage for a YouTube technical demo.

Run a full first-pass edit:
- inspect the current project and media
- tighten the hook
- remove obvious filler, repeated starts, dead air, and duplicate takes
- preserve technical caveats, commands, repo names, model names, and exact numbers
- keep UI/screen-recording sections visible long enough to follow
- add captions
- add concise callouts where helpful
- verify important overlay placement
- do not use paid generation or upscaling unless you ask and I approve
- do not export yet

When done, summarize what changed and what I should review manually.
```

## Example 2: Transcript Cleanup Only

```text
Use the Palmier Pro transcript cleanup stack from AgentDefaults.

Clean the current timeline's spoken content only. Use get_transcript and remove_words. Re-read get_transcript after each remove_words call. Use balanced cut aggressiveness.

Remove filler, false starts, duplicate takes, and long pauses that hurt pacing. Keep exact technical details, commands, caveats, and useful pauses for demos. Do not add overlays, do not generate assets, and do not export.
```

## Example 3: Short-Form Clip

```text
Use the Palmier Pro short-form cutdown stack from AgentDefaults.

Find the strongest 30-60 second standalone moment in the current project for a YouTube Short or LinkedIn clip. Prioritize a clear hook, concrete proof/demo, and clean ending.

Tighten the clip, add captions, and add one short hook overlay if it improves clarity. Do not remove caveats that make the clip accurate. Do not export unless I ask.
```

## Example 4: AI B-Roll With Approval

```text
Use the Palmier Pro AI generation workflow from AgentDefaults.

I want one AI b-roll clip to support the section where I explain the app approval result. Inspect the timeline and source context first. Then propose a model, duration, aspect ratio, and prompt for the generated b-roll. Do not call generate_video or generate_image until I approve.
```

## Example 5: Export Review File

```text
Use the Palmier Pro MCP stack from AgentDefaults.

Inspect a few representative timeline frames to catch obvious overlay/caption issues. Then export a review video using H.264 at Match Timeline resolution. If no output path is specified, let Palmier write it to Downloads.
```

## Good Agent Completion Notes

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
- It produces concise, reviewable completion notes.
