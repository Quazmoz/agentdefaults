# Palmier Pro MCP Quickstart

## Purpose

Connect Claude Code or OpenAI Codex to Palmier Pro and route video-editing work into the canonical AgentDefaults Palmier stack.

The default use case is fast technical YouTube editing while preserving the original timeline and avoiding unapproved paid generation or export.

## Requirements

Current Palmier requirements should be checked against Palmier's own release/docs. At the time this quickstart was hardened, Palmier's official repository documented:

- macOS 26 (Tahoe)
- Apple Silicon
- Palmier Pro running locally
- external MCP at `http://127.0.0.1:19789/mcp`

The authoritative product setup path is:

```text
Palmier Pro -> Help -> MCP Instructions
```

## Connect Claude Code

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
```

Then use the canonical stack:

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-youtube-fast-edit.md
```

## Connect OpenAI Codex

```bash
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

Use the same canonical stack. Do not maintain a separate Codex editing policy.

## External MCP Boundary

Palmier's external MCP and its in-app agent are not identical surfaces.

The external Claude/Codex workflow must not depend on Palmier in-app-only:

```text
read_skill
manage_skills
```

AgentDefaults supplies the canonical external agent/skills instead.

## Recommended Stack

### Fast YouTube First Cut — Default

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-youtube-fast-edit.md
prompts/palmierpro/quick-youtube-edit.md
```

Use for:

- AI/DevOps demos
- coding/terminal walkthroughs
- MCP tutorials
- Android/Wear OS app demos
- Play Console/GitHub/product videos
- talking head + screenshare
- one-shot creator recordings that need quick cleanup

### Full Story/Edit Pass

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/full-edit-pass.md
```

### Transcript Cleanup Only

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/transcript-cleanup-pass.md
```

### Story Assembly From Existing Media

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/story-assembly-from-project-media.md
```

### YouTube Short From Long-Form

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/youtube-short-from-long-form.md
```

### Paid AI Generation

Add only when generation is actually requested:

```text
skills/palmierpro-ai-generation-workflow.md
```

Generation/upscale still requires explicit approval for the exact paid action.

## Fastest First Command

After connecting and opening/importing the media:

```text
Use `agents/palmierpro-mcp-video-editor-agent.md` and the Palmier YouTube fast-edit skill. Make a safe first-pass YouTube cut of the current project. Preserve the original timeline, use live MCP schemas, do not add long-form burned captions, do not use paid generation, and do not export unless I ask.
```

Or use the reusable prompt:

```text
prompts/palmierpro/quick-youtube-edit.md
```

## Expected Default Behavior

For a broad YouTube edit, the agent should:

1. call `get_timeline`
2. call `get_media`
3. duplicate the active timeline using `create_timeline from=<active timelineId>`
4. re-read `get_timeline` because copied IDs changed
5. inspect transcript/media efficiently
6. remove verified pre-roll/dead air/retakes/filler without changing technical meaning
7. keep code/UI/demo visuals readable
8. add only useful sparse titles/callouts
9. use review markers for genuinely subjective choices
10. inspect the hook + representative demo + important overlays
11. stop after one edit pass and one verification/fix pass
12. leave export/generation alone unless requested/approved

## Caption Defaults

Long-form 16:9:

```text
No burned automatic captions unless explicitly requested.
```

Short-form/vertical:

```text
Captions are usually appropriate when requested/part of the format.
```

Use live text/caption styling. Current Palmier versions may expose outline, shadow, and background fields; do not assume text requires fake duplicate layers for contrast.

## Export Defaults

When the user explicitly asks for a normal YouTube render and provides no conflicting settings, use the live schema. Current guidance is:

```text
mode: video
codec: H.264
resolution: Match Timeline
overwrite: false
```

Omit `outputPath` unless supplied.

After queueing, use:

```text
manage_exports action=list
```

to observe actual status.

## Project Selection

If MCP is reachable but no project is active and `manage_project` is available:

```text
manage_project action=list
```

Open a project only when the intended target is unambiguous.

## Troubleshooting

### MCP Not Reachable

Verify:

```text
1. Palmier Pro is running.
2. MCP is enabled/configured.
3. Client points to http://127.0.0.1:19789/mcp.
4. Re-check Palmier Pro -> Help -> MCP Instructions.
```

### Agent Sees Stale IDs

Refresh state after:

- timeline copy
- timeline switch
- undo
- manual user edit
- stale-ID/frame error

Do not reuse old copied-timeline IDs.

### Generation Unavailable

Check:

```text
get_timeline.canGenerate
list_models
```

If generation is unavailable, do not repeatedly call paid tools.

### Cuts Feel Too Aggressive

If the latest edit is known to be the unwanted one, use `undo`, refresh transcript/timeline state, and retry with less aggressive current settings.

### Captions Cover UI

For short-form captions, inspect the actual composited timeline and move/restyle them so they do not obscure important controls/code/UI.

## Acceptance Tests

Use:

```text
docs/palmierpro-mcp-acceptance-tests.md
```

This includes provider parity, original-timeline preservation, transcript-index invalidation, technical-truth preservation, caption policy, paid-action gating, current export enum examples, and bounded termination.

## Related Files

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-youtube-fast-edit.md
skills/palmierpro-ai-generation-workflow.md
prompts/palmierpro/quick-youtube-edit.md
prompts/palmierpro/full-edit-pass.md
prompts/palmierpro/transcript-cleanup-pass.md
prompts/palmierpro/youtube-short-from-long-form.md
docs/palmierpro-mcp-tool-map.md
docs/palmierpro-mcp-acceptance-tests.md
examples/palmierpro-mcp-workflow.md
```

## Quality Bar

A successful setup gives Claude or Codex the same canonical Palmier behavior, reads live project state before edits, preserves the original for broad changes, uses current schemas, makes a bounded reviewable YouTube cut, and avoids unapproved paid/destructive actions.
