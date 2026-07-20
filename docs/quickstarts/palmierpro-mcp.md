# Palmier Pro MCP Quickstart

## Purpose

Help users connect an AI agent to Palmier Pro through MCP and choose the right AgentDefaults stack for video-editing work.

## Requirements

- Palmier Pro installed on a Mac running macOS 26 (Tahoe) or later (see palmier.io for current requirements).
- Palmier Pro open with a project loaded.
- MCP enabled in Palmier Pro.
- An MCP-capable client such as Claude Code, Codex, Cursor, or Claude Desktop.

Palmier's current local MCP endpoint is:

```text
http://127.0.0.1:19789/mcp
```

The authoritative setup path is inside the app:

```text
Palmier Pro -> Help -> MCP Instructions
```

## Connect

Claude Code:

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
```

Codex:

```bash
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

Cursor manual config:

```json
{
  "mcpServers": {
    "palmier-pro": {
      "type": "http",
      "url": "http://127.0.0.1:19789/mcp"
    }
  }
}
```

Claude Desktop:

```text
Use Palmier Pro -> Help -> MCP Instructions -> Install in Claude Desktop.
```

## Recommended Stack

Copy the smallest stack that matches the task.

### General Palmier Editing

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
```

### Story Assembly From Project Media

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/story-assembly-from-project-media.md
```

### YouTube Short From Long-Form

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/youtube-short-from-long-form.md
```

### Paid AI Generation Inside Palmier

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-ai-generation-workflow.md
```

### Full First-Pass Edit

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/full-edit-pass.md
```

### Short-Form Cutdown

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
prompts/palmierpro/short-form-social-cutdown.md
```

## First Command To The Agent

Use this once Palmier Pro is open and connected:

```text
Use the Palmier Pro MCP stack from AgentDefaults. Start by calling get_timeline and get_media. Tell me briefly what project state you can see before making edits.
```

## Common Workflows

### Story Assembly From Project Media

Use:

```text
prompts/palmierpro/story-assembly-from-project-media.md
```

Best for:

- understanding all raw video files in the current Palmier project
- extracting the main points from scattered footage
- identifying the intended YouTube angle
- assembling a proof-first AI-engineering story arc
- deciding which clips to promote, cut, or demote before a full edit

### YouTube Short From Long-Form

Use:

```text
prompts/palmierpro/youtube-short-from-long-form.md
```

Best for:

- creating a 9:16 YouTube Short from a long-form Palmier project
- choosing one proof/demo moment instead of summarizing the whole video
- keeping screen recordings, code, terminal output, app UI, and Play Console screens readable on mobile
- placing Quinn's facecam safely around the screenshare without blocking captions or important UI
- creating a fast hook, proof, and clean ending from longer technical footage

### Full Edit Pass

Use:

```text
prompts/palmierpro/full-edit-pass.md
```

Best for:

- YouTube tutorial
- app demo
- product walkthrough
- technical creator video
- talking-head plus screen recording

### Transcript Cleanup Only

Use:

```text
prompts/palmierpro/transcript-cleanup-pass.md
```

Best for:

- filler removal
- repeated take cleanup
- pacing improvements
- preserving the existing edit layout

### Social Cutdown

Use:

```text
prompts/palmierpro/short-form-social-cutdown.md
```

Best for:

- TikTok
- Instagram Reels
- X/LinkedIn clips
- non-Shorts social variants
- extracting a proof/demo moment from a longer video

## Safety Rules To Keep

- The agent should call `get_timeline` and `get_media` before edits.
- The agent should inspect media before describing it.
- Timeline timing is in frames.
- Paid generation/upscale requires explicit user approval.
- Source media deletion requires explicit user approval.
- The agent should not export unless asked.
- The user should review the timeline before publishing.

## Troubleshooting

### MCP Not Reachable

Check:

```text
1. Palmier Pro is open.
2. A project is open.
3. MCP is enabled in Help -> MCP Instructions.
4. The MCP client points to http://127.0.0.1:19789/mcp.
```

### Agent Sees Tools But Cannot Generate

Check `get_timeline.canGenerate`.

If false, sign in or subscribe in Palmier Pro before using generation/upscale tools.

### Captions Look Wrong

Ask the agent to:

```text
inspect_timeline around the captioned section and adjust caption placement so it does not cover important UI or lower thirds.
```

### Cuts Feel Too Aggressive

Ask the agent to:

```text
undo the last cleanup pass and retry remove_words with cutAggressiveness=loose, preserving more breath between points.
```

## Related Files

```text
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
prompts/palmierpro/story-assembly-from-project-media.md
prompts/palmierpro/youtube-short-from-long-form.md
docs/palmierpro-mcp-tool-map.md
examples/palmierpro-mcp-workflow.md
```

## Quality Bar

A successful setup lets the agent read the project state, make safe timeline edits, and report a concise outcome without guessing media content or spending generation credits unexpectedly.
