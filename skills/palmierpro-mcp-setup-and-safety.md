# Palmier Pro MCP Setup and Safety

## Purpose

Provide a reusable setup and safety layer for agents working with Palmier Pro through MCP.

Use this skill to connect the agent to Palmier Pro correctly, confirm the project state, avoid unsafe assumptions, and protect the user from unintended paid generation, destructive media deletion, or misleading edit status.

## When To Use

Use this skill before any Palmier Pro MCP workflow, especially when:

- A user is opening Palmier Pro for the first time with an agent.
- The agent needs Claude Code, Codex, Cursor, Claude Desktop, or another MCP client to connect.
- The project may have changed manually since the last tool call.
- The user asks for generation, upscaling, export, deletion, or broad cleanup.
- The agent is about to edit real user media.

## Connection Defaults

Palmier Pro exposes MCP over local HTTP while the app is open.

```text
http://127.0.0.1:19789/mcp
```

Common setup commands:

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

Cursor configuration:

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

The preferred setup source is always:

```text
Palmier Pro -> Help -> MCP Instructions
```

Use the app's one-click installers when available.

## Preflight Checklist

Before editing:

```text
1. Palmier Pro is open.
2. The target project is open.
3. MCP is enabled in Palmier Pro.
4. The agent can list Palmier tools.
5. The agent calls get_timeline.
6. The agent calls get_media.
7. The agent confirms canGenerate before generation/upscale.
```

If any of these fail, stop editing and state the smallest corrective action.

## Safety Classes

### Safe Without Extra Confirmation

These are usually reversible, inspectable, or low-risk:

- `get_timeline`
- `get_media`
- `inspect_media`
- `inspect_timeline`
- `search_media`
- `get_transcript`
- `list_models`
- `list_folders`
- `add_clips` when placing existing media non-destructively into clear space
- `insert_clips`
- `move_clips`
- `set_clip_properties`
- `split_clip`
- `remove_words` for obvious cleanup requested by the user
- `ripple_delete_ranges` for requested dead-air cleanup
- `add_captions`
- `add_texts`
- `sync_audio` when the user asked for sync/alignment
- `undo`

### Confirm First

Ask for explicit approval before:

- `generate_image`
- `generate_video`
- `generate_audio`
- `upscale_media`
- broad deletion of timeline clips not clearly covered by the user's request
- `delete_media`
- `delete_folder`
- overwriting a named export destination
- exporting a final deliverable when the user only asked for a draft/edit pass

### Never Guess

Never guess:

- `clipId`
- `mediaRef`
- `folderId`
- `captionGroupId`
- track type
- project fps
- exact cut frames
- source-media content from filenames
- whether a generated asset has completed
- whether a paid-generation account is available

## Project-State Rules

Call `get_timeline`:

- at the start of a session
- after a user changes the timeline manually
- after an edit failure that suggests stale clip/track state
- after undo before making another edit

Do not call `get_timeline` after every edit you made if mutation tools already returned the changed IDs/frames.

Call `get_media`:

- before referencing any media asset
- after import/generation when checking whether a placeholder asset is ready
- before placing generated/imported media

Call `list_models`:

- before any generation
- before upscaling
- when model capabilities matter for duration, aspect ratio, references, voices, or asset type

## Paid Generation Guardrail

Generation and upscaling cost real credits and are not normal undoable timeline edits.

Before generation, present a compact proposal:

```text
I can generate this as a 6-second 9:16 b-roll clip using the model Palmier reports as available. Prompt: "slow push-in on the smartwatch app dashboard, clean tech lighting". Approve generation?
```

Only call the generation/upscale tool after the user approves.

If `canGenerate` is false:

```text
Palmier reports generation is unavailable for this project/session. Sign in or subscribe in Palmier Pro, then retry generation.
```

## Destructive Action Guardrail

Use timeline edits before library deletion.

Prefer:

- `remove_clips` over `delete_media`
- hiding/muting/removing timeline clips over deleting source media
- `undo` over manual reconstruction
- exporting a copy rather than overwriting an existing named file

Do not delete source media or folders unless the user clearly asks for library cleanup.

## Privacy and External Media

Treat user footage, transcripts, and generated media prompts as private project content.

When importing media:

- Prefer local `path` for user-owned files already on disk.
- Use HTTPS URLs only when the user provided or approved the source.
- Avoid embedding large media as base64 unless the asset is small and no better route exists.
- Do not upload user media to third-party services unless the user explicitly requests it and the tool requires it.

## Failure Handling

When a tool fails:

1. Read the error.
2. Determine whether state is stale, parameters are invalid, a capability is missing, or the user needs to act.
3. Retry only when the correction is obvious and safe.
4. Re-read state when IDs/frames may have changed.
5. Use `send_feedback` only for actual Palmier tool limitations, clearly wrong behavior, or concrete product suggestions.

Do not retry paid generation blindly.

## Expected Output

A connected agent should produce concise status like:

```text
Connected — I can see a 30fps 1080p timeline with 4 clips and 2 audio/video tracks.
```

When blocked:

```text
Palmier MCP is not reachable at 127.0.0.1:19789. Open Palmier Pro, open the project, then enable MCP from Help -> MCP Instructions.
```

## Quality Bar

- Uses the local MCP endpoint correctly.
- Reads project state before editing.
- Honors frame-based timing.
- Confirms paid generation and destructive deletion.
- Avoids speculative descriptions of media.
- Reports blockers with one clear next step.
